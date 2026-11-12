import json
import os
from typing import Any, TypedDict

from app.retrieval import get_relevant_context
from app.schemas import (
    AgentAuditMetadata,
    DecisionStatus,
    PolicyResponse,
    RiskLevel,
)
from dotenv import load_dotenv
from groq import Groq
from langgraph.graph import END, StateGraph

load_dotenv()

# Initialize Groq Client
_groq_api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=_groq_api_key) if _groq_api_key else None

# Production defaults for Groq
# MODEL_NAME = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
MODEL_NAME = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
CRITIC_MODEL = os.getenv("GROQ_CRITIC_MODEL", "openai/gpt-oss-20b")

# --- 1. DEFINE AGENT STATE ---
class AgentState(TypedDict):
    question: str
    domain: str
    search_query: str
    context_text: str
    retrieved_sources: list[str]
    draft_response: dict[str, Any] | None
    critique_feedback: str | None
    retry_count: int
    is_approved: bool


# --- 2. AGENT NODES ---

def policy_scout_node(state: AgentState) -> dict[str, Any]:
    """Node 1: Retrieves context. Uses refined query if Auditor triggered a retry."""
    query_to_use = state.get("search_query") or state["question"]
    domain_to_use = state.get("domain", "Unified")

    context_text, sources = get_relevant_context(query_to_use, domain=domain_to_use)

    # Accumulate distinct sources across retries
    existing_sources = set(state.get("retrieved_sources", []))
    existing_sources.update(sources)

    # Accumulate context without losing prior evidence if a loop occurred
    previous_context = state.get("context_text", "")
    combined_context = (
        f"{previous_context}\n\n[ADDITIONAL RETRIEVAL]:\n{context_text}"
        if previous_context and context_text != previous_context
        else context_text
    )

    return {
        "context_text": combined_context,
        "retrieved_sources": list(existing_sources),
    }


def reasoner_node(state: AgentState) -> dict[str, Any]:
    """Node 2: Generates CoT reasoning and operational recommendation."""
    if not client:
        raise ValueError("GROQ_API_KEY environment variable is not configured.")

    critique_instruction = ""
    if state.get("critique_feedback"):
        critique_instruction = (
            f"\n\nCRITICAL FIX REQUIRED FROM PREVIOUS AUDIT:\n"
            f"{state['critique_feedback']}\n"
            "Adjust your reasoning to strictly address this gap."
        )

    system_prompt = (
        "You are an expert HR and Compliance Advisor. "
        "Formulate a clear, direct, and structured decision based ONLY on the internal context provided."
        f"\n\n### CONTEXT:\n{state.get('context_text', '')}"
        f"{critique_instruction}\n\n"
        "### TONE & FORMAT STYLE FOR RECOMMENDATION:\n"
        "- Write the final 'recommendation' in plain, direct English that any employee or manager can immediately understand and follow.\n"
        "- Focus on practical, operational actions, concrete rules, and plain guidance rather than legalistic jargon.\n"
        "- Keep the detailed technical citations, sources, and quotes strictly inside the 'reasoning_trace'.\n\n"
        "### OUTPUT FORMAT REQUIREMENT:\n"
        "Return valid JSON matching this schema:\n"
        "{\n"
        '  "reasoning_trace": [{"step_number": 1, "title": "...", "analysis": "...", "evidence": "...", "source_file": "..."}],\n'
        '  "recommendation": "...",\n'
        '  "confidence_score": 0.0 - 1.0\n'
        "}"
    )

    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": state["question"]},
        ],
        response_format={"type": "json_object"},
        temperature=0.1,
    )

    try:
        raw_data = json.loads(completion.choices[0].message.content or "{}")
    except json.JSONDecodeError:
        raw_data = {
            "reasoning_trace": [],
            "recommendation": completion.choices[0].message.content or "",
            "confidence_score": 0.5,
        }

    return {"draft_response": raw_data}


def auditor_node(state: AgentState) -> dict[str, Any]:
    """Node 3: Fast Critic checking factual grounding and policy adherence."""
    if not client:
        raise ValueError("GROQ_API_KEY environment variable is not configured.")

    draft = state.get("draft_response") or {}
    context = state.get("context_text", "")

    system_prompt = (
        "You are an impartial Policy Compliance Auditor. Verify the draft decision:\n"
        "1. Is every quote in 'evidence' actually present in the context?\n"
        "2. Does the recommendation contradict any retrieved policy rule?\n\n"
        "Return JSON format:\n"
        '{"passed": true, "critique": "Explanation if failed", "revised_search_query": "better terms to search if context was missing"}'
    )

    audit_payload = {
        "context": context,
        "draft_reasoning": draft.get("reasoning_trace", []),
        "recommendation": draft.get("recommendation", ""),
    }

    completion = client.chat.completions.create(
        model=CRITIC_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(audit_payload)},
        ],
        response_format={"type": "json_object"},
        temperature=0.0,
    )

    try:
        eval_result = json.loads(completion.choices[0].message.content or "{}")
    except json.JSONDecodeError:
        eval_result = {"passed": True, "critique": "", "revised_search_query": state["question"]}

    passed = eval_result.get("passed", False)
    critique = eval_result.get("critique", "")
    new_query = eval_result.get("revised_search_query", state["question"])

    return {
        "is_approved": passed,
        "critique_feedback": critique if not passed else None,
        "search_query": new_query if not passed else state.get("search_query", state["question"]),
        "retry_count": state.get("retry_count", 0) + 1,
    }


# --- 3. CONDITIONAL ROUTING LOGIC ---

def should_continue(state: AgentState) -> str:
    """Decides whether to finalize or trigger self-correction."""
    if state.get("is_approved", False) or state.get("retry_count", 0) >= 2:
        return "finalize"
    return "re_retrieve"


# --- 4. BUILD THE GRAPH ---

def build_policy_agent_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("scout", policy_scout_node)
    workflow.add_node("reasoner", reasoner_node)
    workflow.add_node("auditor", auditor_node)

    workflow.set_entry_point("scout")
    workflow.add_edge("scout", "reasoner")
    workflow.add_edge("reasoner", "auditor")

    workflow.add_conditional_edges(
        "auditor",
        should_continue,
        {
            "re_retrieve": "scout",
            "finalize": END,
        },
    )

    return workflow.compile()


policy_agent = build_policy_agent_graph()


# --- 5. EXECUTION ENTRY POINT ---

def evaluate_policy_with_groq(question: str, domain: str = "Unified") -> PolicyResponse:
    """Invokes the Agentic Graph and maps output to PolicyResponse."""
    initial_state: AgentState = {
        "question": question,
        "domain": domain,
        "search_query": question,
        "context_text": "",
        "retrieved_sources": [],
        "draft_response": None,
        "critique_feedback": None,
        "retry_count": 0,
        "is_approved": False,
    }

    try:
        final_state = policy_agent.invoke(initial_state)
        data = final_state.get("draft_response") or {}
        data["retrieved_sources"] = final_state.get("retrieved_sources", [])

        is_passed = final_state.get("is_approved", False)
        retries = final_state.get("retry_count", 1)
        critique = final_state.get("critique_feedback")

        # Map agentic audit metadata directly into Pydantic schema
        data["audit_metadata"] = AgentAuditMetadata(
            verification_passed=is_passed,
            iterations=retries,
            critique_notes=critique,
            risk_level=RiskLevel.LOW if is_passed else RiskLevel.HIGH,
            requires_human_approval=not is_passed,
        )

        if not is_passed:
            data["status"] = DecisionStatus.FLAGGED_FOR_REVIEW
            data["confidence_score"] = min(data.get("confidence_score", 0.5), 0.4)
            data["recommendation"] = (
                f"[ESCALATION REQUIRED - FAILED VERIFICATION]: {data.get('recommendation', '')}"
            )
        else:
            data["status"] = DecisionStatus.APPROVED

        return PolicyResponse.model_validate(data)

    except Exception as exc:  # noqa: BLE001
        print(f"❌ Agent Execution Error: {exc}")
        error_data = {
            "reasoning_trace": [
                {
                    "step_number": 1,
                    "title": "Agent Execution Error",
                    "analysis": f"Workflow failed: {exc}",
                    "evidence": "N/A",
                    "source_file": "System",
                }
            ],
            "recommendation": "System Error: Unable to complete agentic evaluation.",
            "confidence_score": 0.0,
            "retrieved_sources": [],
            "status": DecisionStatus.REJECTED,
            "audit_metadata": AgentAuditMetadata(
                verification_passed=False,
                iterations=0,
                critique_notes=str(exc),
                risk_level=RiskLevel.CRITICAL,
                requires_human_approval=True,
            ),
        }
        return PolicyResponse.model_validate(error_data)


# --- MANUAL CLI TEST BLOCK ---
if __name__ == "__main__":
    test_q = "What are the rules regarding daily working hours and overtime approval?"
    test_d = "Unified"

    print(f"Evaluating Question: {test_q}")
    print(f"Target Domain: {test_d}")

    result = evaluate_policy_with_groq(test_q, test_d)

    print("\n" + "=" * 50)
    print("AUDIT SUMMARY")
    print("=" * 50)
    print(f"STATUS         : {result.status}")
    print(f"RECOMMENDATION : {result.recommendation}")
    print(f"CONFIDENCE     : {result.confidence_score}")
    print(f"SOURCES        : {result.retrieved_sources}")

    print("\nREASONING STEPS:")
    for step in result.reasoning_trace:
        print(f"\n[{step.step_number}] {step.title}")
        print(f"   Analysis : {step.analysis}")
        print(f'   Evidence : "{step.evidence}"')
        print(f"   Source   : {step.source_file}")
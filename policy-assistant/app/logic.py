import os
import json
from groq import Groq
from dotenv import load_dotenv

# --- RAG & Training Imports ---
from app.schemas import PolicyResponse
from app.retrieval import get_relevant_context

# Load environment variables
load_dotenv()

# --- CRITICAL: SILENCE TELEMETRY ---
os.environ['ANONYMIZED_TELEMETRY'] = 'False'
os.environ['CHROMA_TELEMETRY_NOOP'] = 'True'

# Initialize Groq Client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Enforce Few-Shot Prompting via fallback if training_data.py is missing
try:
    from app.training_data import FEW_SHOT_EXAMPLES
except ImportError:
    # Injecting Few-Shot Examples as required by Chain-of-Thought methodology
    # UPDATED: These examples now show the AI exactly how to cite evidence and source files
    FEW_SHOT_EXAMPLES = [
        {
            "question": "Should we approve vendor X given their risk profile shows a past data breach?",
            "reasoning_trace": [
                {
                    "step_number": 1,
                    "title": "Review Vendor Risk Management Policy",
                    "analysis": "The policy states that vendors with past breaches require a Level 3 Security Audit.",
                    "evidence": "Any vendor with a documented past data breach must undergo a Level 3 Security Audit before onboarding.",
                    "source_file": "Vendor_Risk_Management_v2.pdf"
                },
                {
                    "step_number": 2,
                    "title": "Evaluate Vendor X Audit Status",
                    "analysis": "Checked if Vendor X has completed a Level 3 Audit. The provided context indicates they have not.",
                    "evidence": "Vendor X Audit Status: Pending Level 3 verification.",
                    "source_file": "Vendor_Database_Export.txt"
                }
            ],
            "recommendation": "We cannot approve Vendor X yet. A Level 3 Security Audit must be initiated first.",
            "confidence_score": 0.9
        },
        {
            "question": "What compliance steps must we follow before launching product Y in region Z?",
            "reasoning_trace": [
                {
                    "step_number": 1,
                    "title": "Analyze Regional Compliance Framework",
                    "analysis": "Region Z requires strict data localization laws.",
                    "evidence": "All user data belonging to citizens of Region Z must be stored physically within the region's borders.",
                    "source_file": "Regional_Compliance_Framework.pdf"
                },
                {
                    "step_number": 2,
                    "title": "Verify Product Y Infrastructure",
                    "analysis": "Determined if Product Y utilizes local servers in Region Z.",
                    "evidence": "Product Y currently routes all data to central servers in Region A.",
                    "source_file": "Product_Y_Architecture.txt"
                }
            ],
            "recommendation": "Product Y must ensure all user data is stored on servers physically located within Region Z before launch.",
            "confidence_score": 0.85
        }
    ]

def evaluate_policy_with_groq(question: str, domain: str) -> PolicyResponse:
    """
    Analyzes a policy question by:
    1. Retrieving domain-specific context from Vector DB.
    2. Constructing a Chain-of-Thought prompt aligned with India AI Sutras (2026).
    3. Enforcing strict JSON output for the PolicyResponse schema.
    """
    
    # 1. RETRIEVAL STEP: Get context + unique source filenames from ChromaDB
    context_text, source_files = get_relevant_context(question, domain=domain)
    
    # 2. FEW-SHOT PREPARATION (Teaches the model the desired 'Reasoning Trace' style)
    examples_str = json.dumps(FEW_SHOT_EXAMPLES, indent=2)

    # 3. CONSTRUCT THE SYSTEM PROMPT 
    system_prompt = (
        f"You are a Senior Policy Auditor for the {domain} department. "
        "Your mission is to provide an EXPLAINABLE and TRUSTED recommendation based ONLY on the provided context.\n\n"
        
        "### AUDIT PRINCIPLES:\n"
        "- TRUST IS THE FOUNDATION: Do not hallucinate. Use only the provided text.\n"
        "- UNDERSTANDABLE BY DESIGN: Every step in your reasoning_trace must be clear.\n"
        "- INNOVATION OVER RESTRAINT: Be practical but strictly compliant.\n\n"

        "### INTERNAL POLICY CONTEXT:\n"
        f"{context_text if context_text else 'ALERT: No internal policy context was retrieved. You must escalate.'}\n\n"
        
        "### HOW TO REASON (STYLE EXAMPLES):\n"
        f"{examples_str}\n\n"
        
        "### FINAL INSTRUCTIONS:\n"
        "1. PERFORM A THOROUGH SEARCH: Scan the context for keywords before concluding info is missing.\n"
        "2. REASONING TRACE: Create a step-by-step audit trail (List of objects).\n"
        "3. EVIDENCE: For EACH step, you MUST provide a direct quote in the 'evidence' field and list the exact document name in the 'source_file' field. Do not use 'N/A'.\n"
        "4. ESCALATION: If the specific answer is NOT in the text, set recommendation to 'Escalate' and state 'Information not found in internal knowledge base'.\n"
        "5. CONFIDENCE: Set confidence_score to 1.0 for exact matches, 0.5-0.8 for interpretations.\n"
        "6. OUTPUT: Return valid JSON ONLY. Do not include markdown formatting like ```json."
    )

    # Use the model from .env or default to Llama 3 70B
    model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    try:
        # Call Groq API
        completion = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"User Question: {question}"}
            ],
            response_format={"type": "json_object"},
            temperature=0.0  # Zero temperature ensures consistent, reproducible audit results
        )

        # Extract and parse content
        content_str = completion.choices[0].message.content
        data = json.loads(content_str)

        # Inject the actual source list found by ChromaDB for UI verification
        data["retrieved_sources"] = source_files

        # 4. VALIDATE & RETURN
        # This uses Pydantic to ensure the LLM didn't skip any required fields
        return PolicyResponse.model_validate(data)

    except Exception as e:
        print(f"❌ Policy Reasoning Error: {e}")
        # Return a safe error response if the LLM or Network fails
        error_data = {
            "reasoning_trace": [{
                "step_number": 1,
                "title": "System Error",
                "analysis": f"Internal error during reasoning: {str(e)}",
                "evidence": "N/A",
                "source_file": "System"
            }],
            "recommendation": "System Error: Please contact support.",
            "confidence_score": 0.0,
            "retrieved_sources": source_files if 'source_files' in locals() else []
        }
        return PolicyResponse.model_validate(error_data)

# --- MANUAL CLI TEST BLOCK ---
if __name__ == "__main__":
    # Sample test matching the documents you have ingested (e.g., DPDP or SEBI Guidelines)
    test_q = "Should we approve vendor X given their risk profile?"
    test_d = "Unified" 
    
    print(f"🧐 Evaluating Question: {test_q}")
    print(f"📁 Target Domain: {test_d}")
    
    result = evaluate_policy_with_groq(test_q, test_d)
    
    print("\n" + "="*50)
    print("📋 AUDIT SUMMARY")
    print("="*50)
    print(f"RECOMMENDATION : {result.recommendation}")
    print(f"CONFIDENCE     : {result.confidence_score}")
    print(f"SOURCES        : {result.retrieved_sources}")
    
    print("\n🧠 REASONING STEPS:")
    for step in result.reasoning_trace:
        print(f"\n[{step.step_number}] {step.title}")
        print(f"   Analysis : {step.analysis}")
        print(f"   Evidence : \"{step.evidence}\"")
        print(f"   Source   : {step.source_file}")
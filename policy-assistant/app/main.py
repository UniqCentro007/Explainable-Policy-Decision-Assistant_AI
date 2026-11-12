import os
import shutil
import time
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session

# Load Environment Variables
load_dotenv()

# Silence Telemetry
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY_NOOP"] = "True"

# --- INTERNAL MODULE IMPORTS ---
from app.database import PolicyAudit, SessionLocal, User, UserFeedback, init_db
from app.logic import evaluate_policy_with_groq
from app.retrieval import ingest_policy_file
from app.schemas import (
    AdminMetrics,
    FeedbackRequest,
    HumanApprovalRequest,
    LoginRequest,
    PolicyRequest,
    PolicyResponse,
)

POLICIES_DIR = Path("./policies")


# --- LIFESPAN CONTEXT MANAGER ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown events for the application."""
    print("✨ Starting Policy Assistant Backend (Agentic Engine)...")
    POLICIES_DIR.mkdir(parents=True, exist_ok=True)
    init_db()
    print("✅ System Ready: Unified Terminal & PostgreSQL Database Initialized.")
    yield


# --- APP INITIALIZATION ---
app = FastAPI(
    title="PolicyAudit Enterprise Backend",
    description="Agentic XAI Policy Decision System with Autonomous Audit & HITL.",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS CONFIGURATION
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# DB Session Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DbSession = Annotated[Session, Depends(get_db)]


# --- 1. AUTHENTICATION ---
@app.post("/api/auth/login")
def login(request: LoginRequest, db: DbSession):
    """Verifies user credentials against PostgreSQL user records."""
    user = db.query(User).filter(User.username == request.username).first()

    if not user:
        raise HTTPException(
            status_code=401, detail="Access Denied: Identity not recognized."
        )

    if not user.verify_password(request.password):
        raise HTTPException(status_code=401, detail="Invalid Credentials")

    return {
        "status": "authorized",
        "user_id": user.username,
        "role": user.role,
        "full_name": user.full_name,
    }


# --- 2. CORE EVALUATION (Agentic Policy Workflow) ---
@app.post("/api/policy/evaluate", response_model=PolicyResponse)
async def evaluate(request: PolicyRequest, db: DbSession):
    """Triggers the Agentic Graph to evaluate policies with self-critique."""
    try:
        start_time = time.time()

        ai_result = evaluate_policy_with_groq(request.question, request.domain)

        process_latency = time.time() - start_time
        current_model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

        audit_id = str(uuid.uuid4())
        db_record = PolicyAudit(
            id=audit_id,
            user_id=request.user_id,
            question=request.question,
            reasoning_trace=[step.model_dump() for step in ai_result.reasoning_trace],
            recommendation=ai_result.recommendation,
            confidence_score=ai_result.confidence_score,
            latency=round(process_latency, 3),
            model_used=current_model,
        )
        db.add(db_record)
        db.commit()

        ai_result.id = audit_id
        return ai_result

    except Exception as exc:
        db.rollback()
        print(f"❌ Evaluation Error: {exc}")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


# --- 3. HUMAN-IN-THE-LOOP (HITL) GOVERNANCE ---
@app.post("/api/policy/review")
def review_decision(payload: HumanApprovalRequest, db: DbSession):
    """Allows an auditor to approve or override flagged agent recommendations."""
    audit_record = db.query(PolicyAudit).filter(PolicyAudit.id == payload.query_id).first()

    if not audit_record:
        raise HTTPException(status_code=404, detail="Audit record not found.")

    if payload.action.upper() == "OVERRIDE" and payload.modified_recommendation:
        audit_record.recommendation = (
            f"[HUMAN OVERRIDE by {payload.reviewer_id}]: {payload.modified_recommendation}"
        )
    elif payload.action.upper() == "APPROVE":
        audit_record.recommendation = (
            f"[HUMAN VERIFIED by {payload.reviewer_id}]: {audit_record.recommendation}"
        )

    db.commit()
    return {
        "status": "success",
        "query_id": payload.query_id,
        "action_taken": payload.action,
        "updated_recommendation": audit_record.recommendation,
    }


# --- 4. MANAGER-ONLY POLICY INGESTION ---
@app.post("/api/admin/upload-policy")
def upload_policy(file: Annotated[UploadFile, File()]):
    """Saves PDF/TXT and triggers immediate vector ingestion into ChromaDB."""
    try:
        destination_path = POLICIES_DIR / (file.filename or "uploaded_policy.pdf")

        with destination_path.open("wb") as file_object:
            shutil.copyfileobj(file.file, file_object)

        ingest_policy_file(str(destination_path), "Unified")

        return {
            "status": "success",
            "message": f"'{file.filename}' successfully ingested and vectorized.",
        }
    except Exception as exc:  
        print(f"❌ Ingestion Error: {exc}")
        raise HTTPException(
            status_code=500, detail=f"Training Failed: {exc}"
        ) from exc


# --- 5. ADMIN METRICS & AUDIT LOGS ---
@app.get("/api/admin/metrics", response_model=AdminMetrics)
def get_metrics(db: DbSession):
    """Calculates query, latency, and clarity metrics for the dashboard."""
    total_queries = db.query(PolicyAudit).count()
    avg_latency = db.query(func.avg(PolicyAudit.latency)).scalar() or 0.0

    total_feedback = db.query(UserFeedback).count()
    positive_feedback = (
        db.query(UserFeedback).filter(UserFeedback.clarity_rating.is_(True)).count()
    )

    feedback_score = (
        (positive_feedback / total_feedback * 100) if total_feedback > 0 else 0.0
    )

    return AdminMetrics(
        total_queries=total_queries,
        average_latency_seconds=round(float(avg_latency), 2),
        user_clarity_score_percent=round(feedback_score, 1),
        system_status="Operational",
        agent_refinement_rate_percent=0.0,
        pending_human_reviews=0,
    )


@app.get("/api/policy/history")
def get_history(db: DbSession):
    """Retrieves audit trail logs ordered by newest first."""
    return db.query(PolicyAudit).order_by(PolicyAudit.created_at.desc()).all()


# --- 6. FEEDBACK RECEPTION ---
@app.post("/api/policy/feedback")
def submit_feedback(request: FeedbackRequest, db: DbSession):
    """Records user clarity ratings."""
    try:
        new_feedback = UserFeedback(
            query_id=request.query_id,
            clarity_rating=request.clarity_rating,
            comments=request.comments,
        )
        db.add(new_feedback)
        db.commit()
        return {"status": "success", "message": "Feedback registered."}
    except Exception as exc:  
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database Error: {exc}") from exc


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8080, reload=True)
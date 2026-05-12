import os
import uuid
import time
import shutil
from datetime import datetime
from typing import List

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from dotenv import load_dotenv

# --- INTERNAL MODULE IMPORTS ---
from app.schemas import PolicyRequest, PolicyResponse, FeedbackRequest, LoginRequest
from app.logic import evaluate_policy_with_groq
from app.database import SessionLocal, PolicyAudit, UserFeedback, User, init_db
# Import the ingestion tool to allow training via Frontend
from app.retrieval import ingest_policy_file 

# Load Environment Variables
load_dotenv()

# Telemetry Tweaks
os.environ['ANONYMIZED_TELEMETRY'] = 'False'
os.environ['CHROMA_TELEMETRY_NOOP'] = 'True'

# --- APP INITIALIZATION ---
app = FastAPI(
    title="PolicyAudit Enterprise Backend",
    description="Authorized-only RAG Policy Assistant with Unified Ingestion.",
    version="1.4.0"
)

# CORS CONFIGURATION
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    print("✨ Starting Policy Assistant Backend...")
    # Ensure policy directory exists for uploads
    if not os.path.exists("./policies"):
        os.makedirs("./policies")
    init_db()
    print("✅ System Ready: Unified Terminal & Admin Sync Enabled.")

# DB Session Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 1. AUTHENTICATION ---
@app.post("/api/auth/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Verifies user credentials against the MySQL whitelist."""
    # 1. Fetch user by username
    user = db.query(User).filter(User.username == request.username).first()
    
    # 2. Check if user exists
    if not user:
        raise HTTPException(status_code=401, detail="Access Denied: Identity not recognized.")
    
    # 3. FIXED: Use the verify_password method from our User model
    # This handles the comparison between the plain-text input and the stored hash.
    if not user.verify_password(request.password):
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    
    return {
        "status": "authorized",
        "user_id": user.username,
        "role": user.role,
        "full_name": user.full_name
    }

# --- 2. CORE EVALUATION (Unified RAG Brain) ---
@app.post("/api/policy/evaluate", response_model=PolicyResponse)
async def evaluate(request: PolicyRequest, db: Session = Depends(get_db)):
    """Triggers RAG to analyze policies globally (Domain removed for Unified Terminal)."""
    try:
        start_time = time.time()
        
        # We pass "Unified" as the domain hardcode to ensure global search 
        # in the retrieval.py logic we updated earlier.
        ai_result = evaluate_policy_with_groq(request.question, "Unified")
        
        process_latency = time.time() - start_time
        current_model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        
        # Save to MySQL Audit Trail
        audit_id = str(uuid.uuid4())
        db_record = PolicyAudit(
            id=audit_id,
            user_id=request.user_id,
            question=request.question,
            domain="Unified", 
            reasoning_trace=[step.model_dump() for step in ai_result.reasoning_trace],
            recommendation=ai_result.recommendation,
            confidence_score=ai_result.confidence_score,
            latency=round(process_latency, 3),
            model_used=current_model
        )
        db.add(db_record)
        db.commit()
        
        ai_result.id = audit_id
        return ai_result
        
    except Exception as e:
        db.rollback()
        print(f"❌ Evaluation Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- 3. MANAGER-ONLY INTELLIGENCE SYNC (Training via Frontend) ---
@app.post("/api/admin/upload-policy")
async def upload_policy(file: UploadFile = File(...)):
    """
    Saves PDF/TXT and triggers immediate Vector Ingestion (Training).
    Matches the populate_db.py logic.
    """
    try:
        file_location = f"./policies/{file.filename}"
        
        # 1. Save file to disk
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)
        
        # 2. Trigger Ingestion (Training)
        # This adds chunks to ChromaDB immediately
        ingest_policy_file(file_location, "Unified")
        
        return {
            "status": "success", 
            "message": f"'{file.filename}' successfully ingested and vectorized."
        }
    except Exception as e:
        print(f"❌ Ingestion Error: {e}")
        raise HTTPException(status_code=500, detail=f"Training Failed: {str(e)}")

# --- 4. ADMIN & HISTORY ---
@app.get("/api/admin/metrics")
async def get_metrics(db: Session = Depends(get_db)):
    """Calculates metrics for the Admin dashboard."""
    total_queries = db.query(PolicyAudit).count()
    avg_latency = db.query(func.avg(PolicyAudit.latency)).scalar() or 0
    
    total_feedback = db.query(UserFeedback).count()
    positive_feedback = db.query(UserFeedback).filter(UserFeedback.clarity_rating == True).count()
    
    feedback_score = (positive_feedback / total_feedback * 100) if total_feedback > 0 else 0

    return {
        "total_queries": total_queries,
        "average_latency_seconds": round(avg_latency, 2),
        "user_clarity_score_percent": round(feedback_score, 1),
        "status": "Operational",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/policy/history")
async def get_history(db: Session = Depends(get_db)):
    """Retrieves audit log for the History tab."""
    return db.query(PolicyAudit).order_by(PolicyAudit.created_at.desc()).all()

# --- 5. FEEDBACK RECEPTION ---
@app.post("/api/policy/feedback")
async def submit_feedback(request: FeedbackRequest, db: Session = Depends(get_db)):
    """Records clarity ratings."""
    try:
        new_feedback = UserFeedback(
            query_id=request.query_id,
            clarity_rating=request.clarity_rating,
            comments=request.comments
        )
        db.add(new_feedback)
        db.commit()
        return {"status": "success", "message": "Feedback registered."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")

if __name__ == "__main__":
    # Note: Running with port 8080 as specified
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
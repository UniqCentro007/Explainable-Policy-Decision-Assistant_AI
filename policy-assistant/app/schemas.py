from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime

# --- 1. Reasoning Components ---
class ReasoningStep(BaseModel):
    """Individual step in the AI's logical chain for RAG transparency."""
    step_number: int = Field(..., description="The sequence order of the reasoning")
    title: str = Field(..., min_length=1, max_length=100, description="Short summary of the step")
    analysis: str = Field(..., description="The detailed policy logic applied in this step")
    evidence: Optional[str] = Field(None, description="The specific quote from documents")
    source_file: Optional[str] = Field(None, description="The filename retrieved from vector store")

# --- 2. Main API Response ---
class PolicyResponse(BaseModel):
    """The structured output returned to the React UI."""
    model_config = ConfigDict(from_attributes=True)

    id: Optional[str] = None  # <--- ADD THIS LINE
    reasoning_trace: List[ReasoningStep]
    recommendation: str
    confidence_score: float
    retrieved_sources: List[str] = Field(default_factory=list)

# --- 3. Input Requests ---
class PolicyRequest(BaseModel):
    """The audit query sent from the frontend."""
    question: str = Field(..., min_length=10, max_length=1000)
    domain: str
    user_id: str = Field(default="MAGESH_DEV")

class LoginRequest(BaseModel):
    """Authentication credentials for the MySQL check."""
    username: str
    password: str

class FeedbackRequest(BaseModel):
    """Captures user ratings on AI clarity."""
    query_id: str
    clarity_rating: bool
    comments: Optional[str] = None

# --- 4. History & Admin Schemas ---
class HistoryResponse(BaseModel):
    """Past audit records for the History tab."""
    model_config = ConfigDict(from_attributes=True)

    id: str # Use str if UUID, int if MySQL auto-increment
    user_id: str
    question: str
    domain: str
    recommendation: str
    confidence_score: float
    created_at: datetime

class AdminMetrics(BaseModel):
    """System performance data for the Manager Dashboard."""
    total_queries: int
    average_latency_seconds: float
    user_clarity_score_percent: float
    system_status: str = "Operational"
import os
from datetime import UTC, datetime

from dotenv import load_dotenv
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, relationship, sessionmaker
from sqlalchemy_utils import create_database, database_exists
from werkzeug.security import check_password_hash, generate_password_hash

# Load environment variables
load_dotenv()

# --- 1. DATABASE CONFIGURATION ---
DATABASE_URL = os.getenv("DATABASE_URL")

# Fallback for local development if DB URL is not provided
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./policy_assistant.db"
    print("⚠️ WARNING: DATABASE_URL not found. Falling back to Local SQLite.")

# --- 2. ENGINE & SESSION CONFIGURATION ---
is_sqlite = DATABASE_URL.startswith("sqlite")
connect_args = {"check_same_thread": False} if is_sqlite else {}

engine = create_engine(
    DATABASE_URL,
    pool_recycle=3600,
    pool_pre_ping=True,
    connect_args=connect_args,
)

print(
    f"🚀 [DB INIT] Connected to: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else 'Local SQLite'}"
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


# --- 3. MODELS ---

class User(Base):
    """The Gatekeeper Model: Defines authorized personnel."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="employee")  # 'manager' or 'employee'
    full_name = Column(String(100))
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute.")

    @password.setter
    def password(self, plain_password):
        self.password_hash = generate_password_hash(plain_password)

    def verify_password(self, plain_password):
        return check_password_hash(self.password_hash, plain_password)


class PolicyAudit(Base):
    """The Audit Trail Model: Stores RAG reasoning traces, decisions, and metadata."""

    __tablename__ = "policy_queries"

    id = Column(String(100), primary_key=True, index=True)  # Manual UUID
    user_id = Column(String(100), index=True)
    question = Column(Text, nullable=False)

    # RAG Outputs
    reasoning_trace = Column(JSON)
    recommendation = Column(Text, nullable=False)
    confidence_score = Column(Float)

    # Performance Metadata
    latency = Column(Float)
    model_used = Column(String(100))
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

    # Relationship to Feedback
    feedbacks = relationship(
        "UserFeedback", back_populates="parent_query", cascade="all, delete-orphan"
    )


class UserFeedback(Base):
    """The Explainability Model: Stores user ratings for AI clarity."""

    __tablename__ = "user_feedback"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    query_id = Column(String(100), ForeignKey("policy_queries.id"))
    clarity_rating = Column(Boolean)
    comments = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

    parent_query = relationship("PolicyAudit", back_populates="feedbacks")


# --- 4. FASTAPI DEPENDENCY ---

def get_db():
    """Dependency generator for FastAPI endpoints."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- 5. INITIALIZATION UTILITIES ---

def init_db():
    """Creates database and tables if they do not exist."""
    try:
        if not is_sqlite and not database_exists(engine.url):
            create_database(engine.url)
            print("✅ Database created successfully.")

        Base.metadata.create_all(bind=engine)
        print("✅ Database tables (users, policy_queries, user_feedback) verified/created.")
    except Exception as exc:  # noqa: BLE001
        print(f"❌ Database initialization failed: {exc}")


if __name__ == "__main__":
    init_db()
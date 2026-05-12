import os
from sqlalchemy import Column, String, Float, JSON, DateTime, Boolean, ForeignKey, Integer, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy_utils import database_exists, create_database

# Load environment variables (ensure DATABASE_URL is in your .env file)
load_dotenv()

# --- 1. DATABASE CONFIGURATION ---
# Expected Format: mysql+pymysql://user:password@localhost:3306/policy_db
DATABASE_URL = os.getenv("DATABASE_URL")

# Fallback for local development if MySQL is not reachable
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./policy_assistant.db"
    print("⚠️ WARNING: DATABASE_URL not found. Falling back to Local SQLite.")

# --- 2. ENGINE & SESSION CONFIGURATION ---
# Logic: 'check_same_thread' is ONLY for SQLite. MySQL will crash if it's included.
is_sqlite = DATABASE_URL.startswith("sqlite")
connect_args = {"check_same_thread": False} if is_sqlite else {}

engine = create_engine(
    DATABASE_URL,
    pool_recycle=3600,
    pool_pre_ping=True,
    connect_args=connect_args
)

print(f"🚀 [DB INIT] Connected to: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else 'Local SQLite'}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- 3. MODELS ---

class User(Base):
    """
    The Gatekeeper Model: Defines authorized personnel.
    Matches the 'users' table in MySQL.
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    
    # Stores the secure Werkzeug hash
    password_hash = Column(String(255), nullable=False) 
    
    role = Column(String(20), default="employee")  # 'manager' or 'employee'
    full_name = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Property to handle hashing automatically
    @property
    def password(self):
        """Prevent the plain text password from being read."""
        raise AttributeError("Password is not a readable attribute.")

    @password.setter
    def password(self, plain_password):
        """Hashes the password automatically when assigned."""
        self.password_hash = generate_password_hash(plain_password)

    def verify_password(self, plain_password):
        """Returns True if the password matches the hash, False otherwise."""
        return check_password_hash(self.password_hash, plain_password)

class PolicyAudit(Base):
    """
    The Audit Trail Model: Stores RAG reasoning traces and metadata.
    Matches the 'policy_queries' table in MySQL.
    """
    __tablename__ = "policy_queries"
    
    id = Column(String(100), primary_key=True, index=True) # Stores manual UUIDs
    user_id = Column(String(100), index=True) 
    question = Column(String(500))
    domain = Column(String(100))
    
    # RAG Outputs
    reasoning_trace = Column(JSON) 
    recommendation = Column(String(1000))
    confidence_score = Column(Float)
    
    # Performance Metadata
    latency = Column(Float)
    model_used = Column(String(100)) 
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to Feedback
    feedbacks = relationship("UserFeedback", back_populates="parent_query", cascade="all, delete-orphan")

class UserFeedback(Base):
    """
    The Explainability Model: Stores user ratings for AI clarity.
    Matches the 'user_feedback' table with AUTO_INCREMENT ID.
    """
    __tablename__ = "user_feedback"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    query_id = Column(String(100), ForeignKey("policy_queries.id"))
    clarity_rating = Column(Boolean) 
    comments = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Back-reference to the original audit
    parent_query = relationship("PolicyAudit", back_populates="feedbacks")

# --- 4. INITIALIZATION UTILITIES ---

def init_db():
    """
    Automatic Schema Synchronization.
    Creates tables and the database in MySQL if they do not already exist.
    """
    try:
        # Check if the database exists (e.g., policy_db), create it if it doesn't
        if not database_exists(engine.url):
            create_database(engine.url)
            print("✅ Database created successfully.")
            
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables (users, policy_queries, user_feedback) verified/created.")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")

if __name__ == "__main__":
    # Run 'python database.py' to manually trigger table creation
    init_db()
import os

# --- CRITICAL: SILENCE TELEMETRY ---
# Setting these flags before imports prevents the "capture()" positional argument error.
os.environ['ANONYMIZED_TELEMETRY'] = 'False'
os.environ['CHROMA_TELEMETRY_NOOP'] = 'True'

from datetime import datetime
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader

# --- CONFIGURATION ---

APP_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(APP_DIR)

DB_DIR = os.path.join(PROJECT_ROOT, "policy_vector_db")
# Lightweight, high-performance model for CPU (downloads on first run)
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Initialize Global Components
embeddings = SentenceTransformerEmbeddings(model_name=EMBEDDING_MODEL)

# Initialize Persistent Vector Store
vector_db = Chroma(
    persist_directory=DB_DIR, 
    embedding_function=embeddings
)

def ingest_policy_file(file_path: str, domain: str = "Unified"):
    """
    Reads a policy file, applies metadata, prevents duplicates, 
    and splits text for RAG. Domain defaults to 'Unified'.
    """
    if not os.path.exists(file_path):
        print(f"❌ Error: File {file_path} not found.")
        return

    filename = os.path.basename(file_path)

    # 1. DUPLICATE PROTECTION
    try:
        # Deletes existing chunks from this specific file to allow for clean updates
        vector_db.delete(where={"source": filename})
        print(f"🧹 Cleaned existing records for: {filename}")
    except Exception:
        pass

    # 2. SELECT LOADER
    if file_path.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    else:
        loader = TextLoader(file_path, encoding='utf-8')
    
    documents = loader.load()

    # 3. SEMANTIC CHUNKING
    # Increased overlap slightly to maintain context for better AI reasoning
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200, 
        chunk_overlap=300,
        separators=["\n### ", "\n## ", "\n# ", "\n\n", "\n", ". ", " "]
    )
    
    chunks = text_splitter.split_documents(documents)

    # 4. ENRICH METADATA
    for chunk in chunks:
        # We store 'Unified' or the passed domain, but retrieval will be global
        chunk.metadata["domain"] = domain
        chunk.metadata["source"] = filename
        chunk.metadata["ingested_at"] = datetime.utcnow().isoformat()

    # 5. ADD TO VECTOR DB (With Batching Fix)
    batch_size = 100
    total_chunks = len(chunks)
    
    for i in range(0, total_chunks, batch_size):
        batch = chunks[i : i + batch_size]
        vector_db.add_documents(batch)
        if total_chunks > batch_size:
            print(f"   📤 Uploaded batch {min(i + batch_size, total_chunks)}/{total_chunks}...")

    print(f"✅ Successfully Indexed {total_chunks} chunks from {filename}")

def get_relevant_context(question: str, domain: str = "Unified", k: int = 5):
    """
    Unified Retrieval Logic: Searches the entire DB regardless of domain.
    'k' is increased to 5 to provide more evidence for the AI to analyze.
    """
    try:
        # We remove the hard 'filter' to allow the AI to search across all policies
        # This supports your "Unified Terminal" requirement.
        search_results = vector_db.similarity_search(
            question, 
            k=k
        )
        
        if not search_results:
            print(f"⚠️ No context found in the Vector DB.")
            return "", []

        context_blocks = []
        unique_sources = set()

        for i, doc in enumerate(search_results):
            source_name = doc.metadata.get("source", "Unknown Policy")
            # Clean content for the LLM
            content = doc.page_content.replace("\n", " ").strip()
            
            # Formatted block helps the LLM distinguish "Evidence" for Option A
            context_blocks.append(f"[SOURCE: {source_name}]\nQUOTE: {content}")
            unique_sources.add(source_name)

        return "\n\n".join(context_blocks), list(unique_sources)
    
    except Exception as e:
        print(f"⚠️ Retrieval Error: {e}")
        return "", []

def get_db_status():
    """Returns total number of chunks currently stored in the DB."""
    count = vector_db._collection.count()
    return {"total_chunks": count}

# --- TEST BLOCK ---
if __name__ == "__main__":
    os.makedirs("./policies", exist_ok=True)
    
    print("--- Policy Vector DB Status ---")
    status = get_db_status()
    print(f"Total Chunks in System: {status['total_chunks']}")
    
    test_query = "What are the rules regarding data protection?"
    
    print(f"\n🔍 Testing Global Retrieval for: '{test_query}'")
    ctx, src = get_relevant_context(test_query)
    
    if src:
        print(f"📍 Sources Found: {src}")
        print(f"📄 Top Snippet Preview:\n{ctx[:250]}...")
    else:
        print("❌ No matching policies found. Please run populate_db.py first.")
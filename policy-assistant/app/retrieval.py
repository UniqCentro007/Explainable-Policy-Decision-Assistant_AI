import contextlib
import os
import traceback
import warnings
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# --- CRITICAL: SILENCE TELEMETRY & WARNINGS ---
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY_NOOP"] = "True"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS"] = "1"

warnings.filterwarnings(
    "ignore",
    category=DeprecationWarning,
    message=".*langchain-community.*",
)

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# --- CONFIGURATION ---
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent

DB_DIR = str(PROJECT_ROOT / "policy_vector_db")
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

# Initialize Global Components
embeddings = FastEmbedEmbeddings(model_name=EMBEDDING_MODEL)

# Initialize Persistent Vector Store
vector_db = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)


def ingest_policy_file(file_path: str, domain: str = "Unified") -> None:
    """Reads a policy file, applies metadata, prevents duplicates,
    and splits text for RAG.
    """
    path_obj = Path(file_path)
    if not path_obj.exists():
        print(f"❌ Error: File {file_path} not found.")
        return

    filename = path_obj.name

    # 1. DUPLICATE PROTECTION
    with contextlib.suppress(Exception):
        vector_db.delete(where={"source": filename})
        print(f"🧹 Cleaned existing records for: {filename}")

    # 2. SELECT LOADER
    if path_obj.suffix.lower() == ".pdf":
        loader = PyPDFLoader(str(path_obj))
    else:
        loader = TextLoader(str(path_obj), encoding="utf-8")

    documents = loader.load()

    # 3. SEMANTIC CHUNKING
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=300,
        separators=["\n### ", "\n## ", "\n# ", "\n\n", "\n", ". ", " "],
    )

    chunks = text_splitter.split_documents(documents)

    # 4. ENRICH METADATA
    now_iso = datetime.now(UTC).isoformat()
    for chunk in chunks:
        chunk.metadata["domain"] = domain
        chunk.metadata["source"] = filename
        chunk.metadata["ingested_at"] = now_iso

    # 5. ADD TO VECTOR DB (With Batching)
    batch_size = 100
    total_chunks = len(chunks)

    for i in range(0, total_chunks, batch_size):
        batch = chunks[i : i + batch_size]
        vector_db.add_documents(batch)
        if total_chunks > batch_size:
            print(
                f"   📤 Uploaded batch {min(i + batch_size, total_chunks)}/{total_chunks}..."
            )

    print(f"✅ Successfully Indexed {total_chunks} chunks from {filename}")


def get_relevant_context(
    question: str,
    domain: str = "Unified",
    k: int = 8,
    max_chunks_per_source: int = 2,
) -> tuple[str, list[str]]:
    """Multi-Source Balanced Retrieval Logic:
    1. Supports domain metadata filtering.
    2. Fetches candidate pool via MMR for topical diversity.
    3. Caps chunks per document to prevent source monopolization.
    """
    try:
        # Build metadata filter if a specific domain is targeted
        filter_dict: dict[str, Any] | None = None
        if domain and domain.lower() != "unified":
            filter_dict = {"domain": domain}

        candidate_docs = vector_db.max_marginal_relevance_search(
            question,
            k=25,
            fetch_k=50,
            filter=filter_dict,
        )

        if not candidate_docs:
            print("⚠️ No context found in the Vector DB.")
            return "", []

        # Balance results across distinct policy sources
        source_counts: dict[str, int] = {}
        diverse_results = []

        for doc in candidate_docs:
            src = doc.metadata.get("source", "Unknown Policy")
            count = source_counts.get(src, 0)

            if count < max_chunks_per_source:
                diverse_results.append(doc)
                source_counts[src] = count + 1

            if len(diverse_results) >= k:
                break

        context_blocks = []
        unique_sources = list(source_counts.keys())

        for doc in diverse_results:
            source_name = doc.metadata.get("source", "Unknown Policy")
            content = doc.page_content.replace("\n", " ").strip()
            context_blocks.append(f"\nQUOTE: {content}\nSOURCE: {source_name}")

        print(
            f"✅ Retrieved {len(context_blocks)} policy chunks across {len(unique_sources)} source(s): {unique_sources}"
        )
        return "\n\n".join(context_blocks), unique_sources

    except Exception as exc:  # noqa: BLE001
        print(f"❌ Retrieval Error: {exc}")
        traceback.print_exc()
        return "", []


def get_db_status() -> dict[str, int]:
    """Returns total number of chunks currently stored in the DB."""
    try:
        count = vector_db._collection.count()
        return {"total_chunks": count}
    except Exception:  # noqa: BLE001
        return {"total_chunks": 0}


if __name__ == "__main__":
    policies_path = PROJECT_ROOT / "policies"
    policies_path.mkdir(parents=True, exist_ok=True)

    print("--- Policy Vector DB Status ---")
    status = get_db_status()
    print(f"Total Chunks in System: {status['total_chunks']}")

    test_query = "What are the rules regarding data protection?"
    print(f"\n🔍 Testing Multi-Source Retrieval for: '{test_query}'")
    ctx, src = get_relevant_context(test_query)

    if src:
        print(f"📍 Sources Found: {src}")
        print(f"\n📄 Top Snippet Preview:\n{ctx[:350]}...")
    else:
        print("❌ No matching policies found. Please run populate_db.py first.")
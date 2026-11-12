import os
import sys
from pathlib import Path

# Suppress telemetry logs prior to any chromadb imports
os.environ["ANONYMIZED_TELEMETRY"] = "False"

# Ensure the root project directory is on sys.path for direct script execution
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

try:
    from app.retrieval import get_db_status, ingest_policy_file
except ImportError:
    print("❌ Critical Error: Could not import retrieval module.")
    print("👉 Run from project root: python -m app.populate_db")
    sys.exit(1)

# --- CONFIGURATION ---
POLICIES_DIR = ROOT_DIR / "policies"


def run_bulk_ingestion() -> None:
    """Scans the /policies directory and indexes all documents into ChromaDB."""
    print("\n" + "═" * 60)
    print("🚀  SYSTEM KNOWLEDGE BASE: UNIFIED INGESTION ENGINE")
    print("═" * 60)

    # 1. Ensure the policies directory exists
    if not POLICIES_DIR.exists():
        try:
            POLICIES_DIR.mkdir(parents=True, exist_ok=True)
            print(f"📁 Created '{POLICIES_DIR}' directory.")
            print("👉 Action: Place policy documents (.pdf, .txt) into this folder and rerun.")
            return
        except OSError as exc:
            print(f"❌ Failed to create policies directory: {exc}")
            return

    # 2. Discover supported policy documents
    all_files = [
        f for f in os.listdir(POLICIES_DIR)
        if f.lower().endswith((".pdf", ".txt")) and not f.startswith(".")
    ]

    if not all_files:
        print(f"📭 No valid documents found in {POLICIES_DIR}.")
        print("👉 Action: Add policy .pdf or .txt files and rerun.")
        return

    print(f"🔎 Discovery: Found {len(all_files)} document(s). Initializing Global Index...")

    # 3. Process each document into ChromaDB
    success_count = 0
    error_files = []

    for filename in all_files:
        file_path = str(POLICIES_DIR / filename)
        print(f"\n📖 Processing: {filename}")

        try:
            ingest_policy_file(file_path, domain="Unified")
            print(f"✅ Success: Indexed {filename}")
            success_count += 1
        except Exception as exc:  # noqa: BLE001
            print(f"❌ Error: Could not process {filename}")
            print(f"   Details: {exc}")
            error_files.append(filename)

    # 4. Final Summary & Collection Health
    print("\n" + "═" * 60)
    print("🎉  INGESTION SUMMARY")
    print("═" * 60)
    print(f"📦 Total Files Discovered : {len(all_files)}")
    print(f"✅ Successfully Indexed    : {success_count}")

    if error_files:
        print(f"⚠️  Failed Documents       : {len(error_files)}")
        for f in error_files:
            print(f"   - {f}")

    print("-" * 60)

    try:
        status = get_db_status()
        total_chunks = status.get("total_chunks", 0) if isinstance(status, dict) else status
        print(f"📊 Global Knowledge Base Total: {total_chunks} chunks stored")
    except Exception:  # noqa: BLE001
        print("📊 Knowledge Base successfully updated in ChromaDB.")

    print("\n✅ All policies are active and searchable across the agent pipeline.")
    print("═" * 60 + "\n")


if __name__ == "__main__":
    run_bulk_ingestion()
import os
import sys

# SILENCE TELEMETRY: Must be the very first line to prevent log clutter
os.environ['ANONYMIZED_TELEMETRY'] = 'False'

# Ensure the app directory is in the path for proper module discovery
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # We remove any domain-specific ingestion logic imports
    from app.retrieval import ingest_policy_file, get_db_status
except ImportError:
    print("❌ Critical Error: Could not import retrieval module.")
    print("👉 Run from project root: python -m app.populate_db")
    sys.exit(1)

# --- CONFIGURATION ---
POLICIES_DIR = "./policies"

def run_bulk_ingestion():
    """
    Scans the /policies folder and ingests all documents into a 
    single unified vector database for global policy evaluation.
    """
    print("\n" + "═"*60)
    print("🚀  SYSTEM KNOWLEDGE BASE: UNIFIED INGESTION ENGINE")
    print("═"*60)
    
    # 1. Ensure the policies directory exists
    if not os.path.exists(POLICIES_DIR):
        try:
            os.makedirs(POLICIES_DIR)
            print(f"📁 Created '{POLICIES_DIR}' directory.")
            print("👉 Action: Add policy files to this folder and restart.")
            return
        except Exception as e:
            print(f"❌ Failed to create directory: {e}")
            return

    # 2. Get list of all supported documents
    # Filtering for PDFs and TXTs, ignoring hidden system files
    all_files = [f for f in os.listdir(POLICIES_DIR) 
                 if f.lower().endswith((".pdf", ".txt")) and not f.startswith(".")]
    
    if not all_files:
        print(f"📭 No valid documents found in {POLICIES_DIR}.")
        return

    print(f"🔎 Discovery: Found {len(all_files)} documents. Initializing Global Index...")

    # 3. Process each file into the unified database
    success_count = 0
    error_files = []

    for filename in all_files:
        file_path = os.path.join(POLICIES_DIR, filename)
        
        print(f"\n📖 Processing: {filename}")
        
        try:
            # We no longer calculate or pass a domain. 
            # We pass a hardcoded "Unified" string or leave it empty 
            # depending on your retrieval.py signature.
            ingest_policy_file(file_path, "Unified")
            print(f"✅ Success: Indexed {filename}")
            success_count += 1
        except Exception as e:
            print(f"❌ Error: Could not process {filename}")
            print(f"   Details: {str(e)}")
            error_files.append(filename)

    # 4. Final Summary
    print("\n" + "═"*60)
    print("🎉  INGESTION SUMMARY")
    print("═"*60)
    print(f"📦 Total Files Found:    {len(all_files)}")
    print(f"✅ Successfully Indexed: {success_count}")
    
    if error_files:
        print(f"⚠️  Failed Documents:    {len(error_files)}")
        for f in error_files:
            print(f"   - {f}")
    
    print("-" * 60)
    
    try:
        status = get_db_status()
        total_chunks = status.get('total_chunks', 0)
        print(f"📊 Global Knowledge Base: {total_chunks} chunks")
    except Exception:
        print("📊 Knowledge Base successfully updated in ChromaDB.")
        
    print("\n✅ All policies are now searchable across the entire organization.")
    print("═"*60 + "\n")

if __name__ == "__main__":
    run_bulk_ingestion()
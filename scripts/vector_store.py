import os
import chromadb
from chromadb.utils import embedding_functions

# ── Setup ChromaDB ────────────────────────────────────────────────────────────

CHROMA_PATH = os.path.join(os.path.dirname(__file__), "..", "chroma_db")

def get_chroma_client():
    """Create a persistent ChromaDB client."""
    return chromadb.PersistentClient(path=os.path.abspath(CHROMA_PATH))


def get_collection(client, collection_name: str = "documents"):
    """Get or create a ChromaDB collection using default embeddings."""
    embedding_fn = embedding_functions.DefaultEmbeddingFunction()
    return client.get_or_create_collection(
        name=collection_name,
        embedding_function=embedding_fn
    )


# ── Store Document ────────────────────────────────────────────────────────────

def store_document(file_name: str, text: str, metadata: dict):
    """
    Store a document's cleaned text as a vector in ChromaDB.
    - file_name: unique ID for the document
    - text: cleaned text to embed
    - metadata: extracted fields (vendor, amount, date, etc.)
    """
    try:
        client = get_chroma_client()
        collection = get_collection(client)

        # Use file_name as unique document ID
        doc_id = file_name.replace(" ", "_").replace(".txt", "")

        # Clean metadata - ChromaDB only accepts str/int/float/bool values
        clean_meta = {}
        for k, v in metadata.items():
            if v is None:
                clean_meta[k] = ""
            elif isinstance(v, (str, int, float, bool)):
                clean_meta[k] = v
            else:
                clean_meta[k] = str(v)

        collection.upsert(
            ids=[doc_id],
            documents=[text],
            metadatas=[clean_meta]
        )
        print(f"  CHROMA STORED: {doc_id}")
        return True
    except Exception as e:
        print(f"  CHROMA ERROR: {e}")
        return False


# ── Search Similar Documents ──────────────────────────────────────────────────

def search_similar(query: str, n_results: int = 3):
    """
    Search for documents similar to the query text.
    Returns the most semantically similar documents.
    """
    try:
        client = get_chroma_client()
        collection = get_collection(client)

        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results
    except Exception as e:
        print(f"  CHROMA SEARCH ERROR: {e}")
        return None


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    clean_text_folder = os.path.join(base_dir, "clean_text")
    json_folder = os.path.join(base_dir, "json_output")

    print("\nStoring documents in ChromaDB...\n")

    for txt_file in os.listdir(clean_text_folder):
        if not txt_file.endswith(".txt"):
            continue

        # Read cleaned text
        txt_path = os.path.join(clean_text_folder, txt_file)
        with open(txt_path, "r", encoding="utf-8") as f:
            text = f.read()

        # Load matching JSON metadata
        json_file = txt_file.replace(".txt", ".json")
        json_path = os.path.join(json_folder, json_file)

        metadata = {}
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)

        store_document(txt_file, text, metadata)

    # Test semantic search
    print("\n--- Semantic Search Test ---")
    queries = [
        "software training payment",
        "invoice from sliced invoices",
        "full stack course receipt"
    ]

    for query in queries:
        print(f"\nQuery: '{query}'")
        results = search_similar(query, n_results=2)
        if results and results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                meta = results["metadatas"][0][i]
                print(f"  Match {i+1}: {meta.get('file_name', 'unknown')} "
                      f"| vendor: {meta.get('vendor_name', '')} "
                      f"| amount: {meta.get('amount_paid') or meta.get('total_amount', '')}")

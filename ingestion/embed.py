import json
from pathlib import Path
import chromadb
from langchain_community.embeddings import HuggingFaceBgeEmbeddings

PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"
VECTOR_STORE_DIR = Path(__file__).parent.parent / "data" / "vector_store"

def run_embedding():
    input_file = PROCESSED_DIR / "chunks.json"
    if not input_file.exists():
        print(f"Error: {input_file} not found. Run chunker.py first.")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    if not chunks:
        print("No chunks found to embed.")
        return

    print("Initializing embedding model (BAAI/bge-small-en-v1.5)...")
    # Using the standard BGE small model
    model_name = "BAAI/bge-small-en-v1.5"
    model_kwargs = {'device': 'cpu'}
    encode_kwargs = {'normalize_embeddings': True}
    embeddings = HuggingFaceBgeEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs,
        query_instruction="Represent this sentence for searching relevant passages: "
    )

    VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Initializing ChromaDB client at {VECTOR_STORE_DIR}...")
    client = chromadb.PersistentClient(path=str(VECTOR_STORE_DIR))
    
    # Create or get the collection
    collection_name = "mutual_fund_faq"
    try:
        # Clear existing collection if we are re-running
        client.delete_collection(name=collection_name)
    except Exception:
        pass
        
    collection = client.create_collection(name=collection_name)

    print(f"Embedding and storing {len(chunks)} chunks into ChromaDB...")
    
    # Prepare data for ChromaDB
    documents = [chunk["text"] for chunk in chunks]
    metadatas = [chunk["metadata"] for chunk in chunks]
    ids = [f"{chunk['metadata']['fund_id']}_{chunk['metadata']['section']}" for chunk in chunks]

    # Generate embeddings
    embedded_vectors = embeddings.embed_documents(documents)

    # Add to collection
    collection.add(
        ids=ids,
        embeddings=embedded_vectors,
        metadatas=metadatas,
        documents=documents
    )

    print("Successfully completed embedding and vector storage!")
    print(f"Total documents in collection '{collection_name}': {collection.count()}")

if __name__ == "__main__":
    run_embedding()

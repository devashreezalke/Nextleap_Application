import os
import re
import chromadb
from pathlib import Path
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Initialize API and paths
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
VECTOR_STORE_DIR = Path(__file__).parent.parent / "data" / "vector_store"

# Initialize local embedding model for query embedding
embeddings = HuggingFaceBgeEmbeddings(
    model_name="BAAI/bge-small-en-v1.5",
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True},
    query_instruction="Represent this sentence for searching relevant passages: "
)

# Initialize ChromaDB client
client = chromadb.PersistentClient(path=str(VECTOR_STORE_DIR))
collection = client.get_collection(name="mutual_fund_faq")

# Initialize Groq client
groq_client = Groq(api_key=GROQ_API_KEY)

# --- Entity Mapping for Hybrid Retrieval ---
# We map common user queries to the specific fund_id metadata tags
FUND_ALIASES = {
    "mid cap": "hdfc-mid-cap-fund-direct-growth",
    "mid-cap": "hdfc-mid-cap-fund-direct-growth",
    "midcap": "hdfc-mid-cap-fund-direct-growth",
    "large cap": "hdfc-large-cap-fund-direct-growth",
    "large-cap": "hdfc-large-cap-fund-direct-growth",
    "largecap": "hdfc-large-cap-fund-direct-growth",
    "small cap": "hdfc-small-cap-fund-direct-growth",
    "small-cap": "hdfc-small-cap-fund-direct-growth",
    "smallcap": "hdfc-small-cap-fund-direct-growth",
    "gold": "hdfc-gold-etf-fund-of-fund-direct-plan-growth",
    "defence": "hdfc-defence-fund-direct-growth",
    "defense": "hdfc-defence-fund-direct-growth"
}

def extract_fund_id(query: str) -> str:
    """Identify which fund the user is asking about."""
    query_lower = query.lower()
    for alias, fund_id in FUND_ALIASES.items():
        if alias in query_lower:
            return fund_id
    return None

def detect_advisory_intent(query: str) -> bool:
    """Detect if the user is asking for investment advice."""
    advisory_keywords = ["should i", "recommend", "best fund to invest", "where to invest", "good investment", "my portfolio"]
    query_lower = query.lower()
    for keyword in advisory_keywords:
        if keyword in query_lower:
            return True
    return False

def get_answer(query: str) -> str:
    # 1. Intent Routing (Guardrails)
    if detect_advisory_intent(query):
        return ("I can only provide factual data about mutual funds and cannot offer investment advice. "
                "Please consult a certified financial advisor or visit the AMFI educational portal for guidance.")

    # 2. Hybrid Retrieval
    fund_id = extract_fund_id(query)
    query_vector = embeddings.embed_query(query)
    
    if fund_id:
        # Strict Metadata Filtering
        results = collection.query(
            query_embeddings=[query_vector],
            n_results=3,
            where={"fund_id": fund_id}
        )
    else:
        # Standard Semantic Search
        results = collection.query(
            query_embeddings=[query_vector],
            n_results=3
        )

    if not results['documents'] or not results['documents'][0]:
        return "I could not find any relevant information for your query."

    # Combine context
    retrieved_chunks = results['documents'][0]
    metadatas = results['metadatas'][0]
    
    context = "\n".join(retrieved_chunks)
    
    # 3. LLM Generation (Strict Constraints)
    system_prompt = (
        "You are a strict, factual assistant for HDFC Mutual Funds. "
        "Answer the user's question ONLY using the provided context. "
        "Do NOT use outside knowledge. Do NOT provide investment advice. "
        "Keep your answer strictly to 3 sentences maximum."
    )
    
    user_prompt = f"Context:\n{context}\n\nUser Question: {query}"
    
    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0,
            max_tokens=150
        )
        answer = completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Error contacting language model: {e}"

    # 4. Programmatic Citations (Mandatory compliance)
    top_metadata = metadatas[0]
    source_url = top_metadata.get("source_url", "Unknown")
    fetch_timestamp = top_metadata.get("fetch_timestamp", "Unknown")
    
    citation = f"\n\n---\n**Source:** [Link]({source_url})\n**Last Updated:** {fetch_timestamp}"
    
    return answer + citation

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        print(get_answer(query))
    else:
        print(get_answer("What is the exit load for the defence fund?"))

# Mutual Fund FAQ Assistant: Phase-Wise Implementation Plan

Based on the architecture and problem statement, this document outlines the step-by-step phases required to build the Facts-Only Mutual Fund FAQ Assistant.

## Phase 1: Environment Setup & Infrastructure
**Objective:** Initialize the repository, configure the environment, and establish the foundational architecture.
* **1.1 Version Control & Structure:** Set up the Git repository and define the folder structure (`backend/`, `frontend/`, `data/`, `Docs/`).
* **1.2 Environment Management:** Define `requirements.txt` (FastAPI, BeautifulSoup, LangChain, ChromaDB, Sentence-Transformers, Groq) and create `.env` templates for API keys.
* **1.3 CI/CD & Linting:** Set up basic code formatting (e.g., `black`, `flake8`) to ensure code quality.

## Phase 2: Data Ingestion & Scraping Pipeline
**Objective:** Programmatically acquire and parse official mutual fund data from the 5 target HDFC/Groww URLs.
* **2.1 Web Scraper (`scraper.py`):** Build a robust `BeautifulSoup` scraper to download HTML content from the target URLs.
* **2.2 Boilerplate Removal:** Implement logic to strip out non-essential web elements (navigation bars, scripts, footers, third-party ads) to isolate the core mutual fund data.
* **2.3 Data Extraction & Cleaning:** Parse the remaining text to cleanly extract metrics (Expense Ratio, Exit Load, Minimum SIP, Riskometer, Fund Management Data).
* **2.4 Local Fallback Mechanism:** Save the scraped HTML as local snapshots in `data/snapshots/` to ensure the system can function offline or if the target website goes down.

## Phase 3: Embedding & Vector Store Setup
**Objective:** Chunk the extracted text and build the semantic search database.
* **3.1 Context-Enriched Section Chunking (`ingestion/chunker.py`):** Bypass generic text splitters. Create exactly one chunk per JSON section and prepend the Fund Name and Metric Name to the value (e.g., "Fund Name: HDFC Mid-Cap Fund. Expense Ratio: 0.76%."). This explicit context injection ensures highly accurate retrieval.
* **3.2 Local Embedding:** Integrate the `BAAI/bge-small-en-v1.5` model via Sentence-Transformers to convert text chunks into dense vectors.
* **3.3 Vector Database Integration:** Initialize `ChromaDB` to store the vectors locally in `data/vector_store/`. ChromaDB is specifically chosen over FAISS because of its robust native support for metadata filtering, which is critical for isolating funds.
* **3.4 Metadata Tagging:** Ensure every chunk is tagged with its source URL and extraction timestamp to support mandatory citations.

## Phase 4: LLM Integration & Guardrails
**Objective:** Connect the language model and enforce the strict facts-only compliance rules.
* **4.1 Groq / Llama-3 Integration:** Set up the LLM client to route queries to the `llama3-8b-8192` model.
* **4.2 Retrieval Logic:** Build the semantic search function to retrieve the Top-$K$ (e.g., 3) most relevant chunks from ChromaDB based on the user's query.
* **4.3 Prompt Engineering:** Design the system prompt to enforce the following constraints:
  * Answer strictly using the provided context.
  * Maximum 3 sentences per response.
  * Polite refusal for any queries requesting investment advice.
* **4.4 Refusal Routing:** Implement a programmatic check that detects advisory queries and defaults to the refusal template + AMFI educational link.

## Phase 5: Formatting & API Layer
**Objective:** Format the final output and serve it via a backend API.
* **5.1 Citation Engine:** Extract the source URL from the metadata of the retrieved context and append it as a clickable link.
* **5.2 Footer Appender:** Automatically append `“Last updated from sources: <date>”` to every factual response.
* **5.3 Backend Endpoints (`main.py`):** Expose a FastAPI REST endpoint (e.g., `/api/chat`) that accepts user queries and returns the formatted response.

## Phase 6: Minimalist User Interface
**Objective:** Build a clean, user-friendly frontend to interact with the backend API.
* **6.1 UI Framework Setup:** Initialize a lightweight frontend (Streamlit or basic HTML/JS) to serve the chat interface.
* **6.2 Layout Implementation:**
  * Add the visible disclaimer: `“Facts-only. No investment advice.”`
  * Add 3 clickable example queries.
  * Build the chat input and message history display.
* **6.3 Integration:** Connect the frontend to the FastAPI `/api/chat` endpoint.

## Phase 7: Testing & Compliance Verification
**Objective:** Ensure the assistant rigorously adheres to all constraints.
* **7.1 Factual Testing:** Verify the assistant accurately answers specific mutual fund queries (e.g., "What is the exit load for HDFC Defence Fund?") using only the 5 URLs.
* **7.2 Refusal Testing:** Attempt to ask "Should I invest in the HDFC Mid Cap fund?" to verify the refusal logic triggers correctly.
* **7.3 Constraint Verification:** Programmatically check that responses never exceed 3 sentences, always include exactly one citation, and always have the timestamp footer.

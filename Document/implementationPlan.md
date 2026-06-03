# Project Implementation Plan: AI-Powered Restaurant Recommendation System

This document outlines the phase-wise development roadmap for the AI-Powered Restaurant Recommendation System based on the system specifications defined in [context.md](./context.md) and [architecture.md](./architecture.md).

---

## Phase 1: Setup & Data Ingestion
**Goal:** Setup dependencies, config rules, and download the Hugging Face dataset, preprocessing it to standard formats.

1.  **Initialize Project Structure:**
    *   Create base files: `requirements.txt`, `.env.example`, `.env`, and config loader `src/app/config.py`.
    *   Create standard folder structure:
        *   `src/app/ingestion/`
        *   `src/app/data/`
        *   `src/app/services/`
        *   `src/app/api/`
        *   `static/`
        *   `tests/`
        *   `scripts/`
2.  **Dataset Fetcher (`src/app/ingestion/loader.py`):**
    *   Download `ManikaSaini/zomato-restaurant-recommendation` using the HF `datasets` library.
3.  **Data Preprocessing & Normalization (`src/app/ingestion/normalizer.py`):**
    *   Map dataset column headers (e.g. `Restaurant Name` $\rightarrow$ `name`, `Aggregate rating` $\rightarrow$ `rating`).
    *   Standardize locality/city strings.
    *   Convert cuisine comma-separated lists into standardized python arrays.
    *   Map `Average Cost for two` to budget classes (`low` $\le 500$, `medium` $500\text{-}1500$, `high` $> 1500$).
4.  **Pipeline Orchestrator (`src/app/ingestion/pipeline.py` & `scripts/ingest.py`):**
    *   Write normalized records into a processed Parquet file: `data/processed/restaurants.parquet`.

---

## Phase 2: Domain Logic & Filtering Layer
**Goal:** Develop data structures, data repositories, and the deterministic candidate extraction layer.

1.  **Data Schemas (`src/app/models/schemas.py`):**
    *   Define Pydantic schema structures for inputs (`UserPreferences`) and outputs (`RecommendationResponse`).
2.  **Data Access Layer (`src/app/data/repository.py`):**
    *   Create `RestaurantRepository` reading preprocessed Parquet datasets into memory at boot.
    *   Expose metadata helper methods for autocomplete selectors (unique cuisines and cities).
3.  **Filtering System (`src/app/services/filter_service.py`):**
    *   Implement query logic matching target preferences: location, budget category, cuisine, and minimum rating criteria.
    *   Pre-sort matched candidates by rating and total votes.
    *   Truncate candidates list to `MAX_CANDIDATES` (e.g. 25) before passing them to the generative model.

---

## Phase 3: Integration & LLM Orchestration
**Goal:** Configure the Groq API connection (strictly using Groq Llama-3 models; OpenAI is not used), construct grounded prompt templates, and process structured outputs.

1.  **Groq SDK Client (`src/app/services/llm_client.py`):**
    *   Wrap calls to Groq API client (`groq>=0.5.0` package) using `Llama-3-8b-8192` or other Groq models (OpenAI is excluded from this system).
2.  **Structured Prompt Engine (`src/app/services/prompt_builder.py`):**
    *   Construct prompts embedding candidate properties and user requirements.
    *   Enforce response format structure: LLM returns only valid JSON matching target recommendation lists, and prohibits recommending restaurants not in the input set.
3.  **Response Parser & Merger (`src/app/services/response_parser.py` & `src/app/services/orchestrator.py`):**
    *   Validate the LLM's response schema.
    *   Join LLM ranking/explanations with database details by ID.
    *   Implement fallback mapping if LLM returns bad formats or fails (e.g., fallback ranking matching filtered dataset).

---

## Phase 4: API Endpoints (FastAPI)
**Goal:** Deploy web service routing for recommendations and metadata helpers.

1.  **Service Router (`src/app/api/routes.py`):**
    *   Endpoint `POST /api/v1/recommendations` parsing user criteria.
    *   Endpoints `GET /api/v1/metadata/locations` and `GET /api/v1/metadata/cuisines` for autocompletion inputs.
    *   Health check.
2.  **Application Entrypoint (`src/app/main.py`):**
    *   Initialize FastAPI app, setup CORS policies, mount static UI assets, and trigger data repository loading on start.

---

## Phase 5: Web UI Development
**Goal:** Create a visually striking, highly interactive user interface with Vanilla HTML, CSS, and JS.

1.  **Interface Structure (`static/index.html`):**
    *   Header panel, sticky layout, and preference inputs (Location, Budget, Cuisine, Minimum Rating, and Free-text preferences).
    *   Structured display container for recommendations.
2.  **Visual Styling (`static/styles.css`):**
    *   Design: Harmonious deep dark theme, soft glassmorphism blur backgrounds, smooth fade-in animations on load, and interactive states.
3.  **Interaction Scripts (`static/app.js`):**
    *   Perform search suggestions querying endpoints for Location/Cuisine.
    *   Submit requests asynchronously, display loading skeletons, and render detailed recommendation cards.

---

## Phase 6: Testing & Quality Assurance
**Goal:** Verify components and check edge case robustness.

1.  **Unit & Integration Tests (`tests/`):**
    *   Create test scripts using `pytest` verifying data normalizations, Pandas filtering service queries, and response json parser schemas.
2.  **System Verification:**
    *   Verify offline dataset load times and latency.
    *   Verify LLM grounding and hallucination resistance.

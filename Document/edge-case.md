# Edge Cases and Error Handling: AI Restaurant Recommendation System

This document outlines the potential edge cases across all system layers of the **AI-Powered Restaurant Recommendation System** and details the corresponding handling and mitigation strategies.

---

## 1. Data Ingestion & Preprocessing

### Edge Case 1.1: Missing or Empty Schema Fields
*   **Scenario:** Raw restaurant rows from the Hugging Face dataset contain null values or empty strings in fields such as `Restaurant Name`, `City`, or `Cuisine`.
*   **Handling:**
    *   If `Restaurant Name` or `City` is missing, the row is discarded.
    *   If `Cuisine` is empty, it is default-mapped to `["Various"]`.
    *   If `Aggregate rating` is missing or null, it defaults to `0.0`.

### Edge Case 1.2: Rating is Non-Numerical or Unrated
*   **Scenario:** The rating is marked as `"NEW"`, `"-"`, or `"No Rating"`.
*   **Handling:** 
    *   The `normalizer.py` converts these string values to `0.0` to prevent mathematical/parsing failures, ensuring they only appear when the user requests low minimum ratings.

### Edge Case 1.3: Non-Numeric Cost Values
*   **Scenario:** The cost field contains commas (e.g., `1,200`), symbols, or string prefixes.
*   **Handling:**
    *   Sanitize the string by removing non-numeric characters (except decimals) before parsing to `float`.
    *   If cost is missing, default to a mid-point rating class or map to `low` to avoid exclusion, but flag it in metadata.

---

## 2. Filtering & Domain Layer

### Edge Case 2.1: Zero Candidates Match (Empty Set)
*   **Scenario:** The combination of location, budget, cuisine, and rating returns zero matches.
*   **Handling:**
    *   The orchestrator detects the empty list *before* calling the LLM.
    *   The LLM call is skipped entirely to save API costs and reduce response latency.
    *   The API returns a `200 OK` empty recommendations response with metadata indicating which filter query caused the mismatch, enabling the UI to suggest relaxing parameters.

### Edge Case 2.2: Too Many Candidates Match
*   **Scenario:** A query (e.g., location `"Delhi"` and cuisine `"North Indian"`) matches hundreds of records.
*   **Handling:**
    *   Apply a deterministic pre-filter ranking: sort candidates by `rating` descending, then by `votes` descending.
    *   Truncate the list to a hard-capped limit of `MAX_CANDIDATES` (e.g., 25 items). This bounds token costs and prevents LLM context exhaustion.

### Edge Case 2.3: Broad or Empty Cuisine Input
*   **Scenario:** The user selects "Any" or leaves the cuisine search field empty.
*   **Handling:**
    *   The `FilterService` skips the cuisine check entirely and processes other filters (location, rating, budget) normally.

---

## 3. LLM Integration & Orchestration

### Edge Case 3.1: LLM Generates Hallucinated Restaurants
*   **Scenario:** The LLM recommends a restaurant that is not in the provided candidate set or invents names/IDs.
*   **Handling:**
    *   The `RecommendationMerger` joins LLM outputs back to candidate records using their unique IDs.
    *   Any recommendation returned by the LLM containing an ID not present in the input candidate list is dropped.

### Edge Case 3.2: Malformed or Invalid JSON from LLM
*   **Scenario:** The LLM returns raw text, markdown blocks, or corrupted JSON that violates the requested Pydantic schema.
*   **Handling:**
    *   **Regex Extraction:** The parser attempts to locate and extract the JSON block using a regex selector (matching `{...}`).
    *   **Fallback Ranking:** If extraction fails, trigger a deterministic fallback: take the top-K restaurants sorted by rating directly from the filtered list, and generate generic system explanations (e.g., *"Recommended based on your rating preference of 4.0+ in Delhi"*).

### Edge Case 3.3: API Key Configuration Errors / Invalidation
*   **Scenario:** The Groq API key is missing or revoked, returning `401 Unauthorized` or connection errors.
*   **Handling:**
    *   The server logs the error details, bypasses the LLM execution layer, and falls back to deterministic rating-based outputs accompanied by a visual warning banner in UI metadata indicating *"AI generator is currently offline"*.

### Edge Case 3.4: Rate Limits (HTTP 429) & Timeouts
*   **Scenario:** The Groq service is overloaded or rate limits the API key.
*   **Handling:**
    *   Implement retries with exponential backoff and jitter (up to 2 attempts).
    *   Return the fallback rating-based result if the timeout limit (e.g. 5.0 seconds) is reached.

---

## 4. UI / Presentation Layer

### Edge Case 4.1: High Completion Latency
*   **Scenario:** LLM completions require 1.5 to 5 seconds to respond.
*   **Handling:**
    *   Display full-width loading skeleton cards representing restaurant details.
    *   Show dynamic loading state messages (e.g., *"Finding matching spots..."*, *"Generating AI summaries..."*).

### Edge Case 4.2: Extremely Long User Input (Prompt Injection Defense)
*   **Scenario:** The user inputs an excessively long string in the `additional_preferences` field or tries to override system prompts.
*   **Handling:**
    *   Enforce a strict character cap (e.g., maximum 200 characters) on the frontend input.
    *   Sanitize the string on the backend before prompt interpolation, stripping control characters.

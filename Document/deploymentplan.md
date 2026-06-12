# Deployment Plan: Zomato AI Restaurant Recommender

This plan details the steps to deploy the AI Restaurant Recommendation System. Two deployment strategies are outlined:
1. **Split Deployment (Recommended)**: React Frontend on **Vercel** + FastAPI Backend on **Railway**.
2. **Unified Deployment (Simpler)**: Entire FastAPI app (serving built static files) on **Railway**.

---

## Strategy 1: Split Deployment (Vercel + Railway)

This strategy separates the frontend client from the backend API, leveraging Vercel's global CDN for the React frontend and Railway's container runner for the Python backend.

### Part A: Deploying the Backend on Railway

1. **Create a `Procfile`**:
   Create a file named `Procfile` in the root of the project with the following content:
   ```text
   web: uvicorn src.app.main:app --host 0.0.0.0 --port $PORT
   ```

2. **Add to GitHub**:
   Commit and push all changes to your Git repository.

3. **Initialize Railway Project**:
   * Go to [Railway.app](https://railway.app) and sign in.
   * Click **New Project** -> **Deploy from GitHub repo** and select your repository.

4. **Configure Environment Variables**:
   In your Railway project settings, go to the **Variables** tab and add:
   * `GROQ_API_KEY`: *Your Groq API key secret*
   * `LLM_MODEL`: `llama-3.1-8b-instant`
   * `DATA_PATH`: `data/processed/restaurants.parquet`
   * `LOG_LEVEL`: `info`

5. **Expose Public URL**:
   Under the **Settings** tab in Railway, click **Generate Domain** under the *Networking* section to get your backend URL (e.g. `https://zomato-backend.up.railway.app`).

---

### Part B: Deploying the Frontend on Vercel

1. **Make API Fetch Paths Dynamic**:
   Modify `frontend/src/App.tsx` to read the API base URL from Vite environment variables. 
   Define the base URL as follows:
   ```typescript
   const API_BASE = import.meta.env.VITE_API_BASE_URL || "";
   ```
   Update fetch queries:
   * `fetch("/api/v1/...")` -> `fetch(`${API_BASE}/api/v1/...`)`

2. **Add Vercel Config (Optional)**:
   You can add a `vercel.json` in the `frontend` directory to handle SPA routing redirects if needed:
   ```json
   {
     "rewrites": [{ "source": "/(.*)", "destination": "/" }]
   }
   ```

3. **Deploy on Vercel**:
   * Sign in to [Vercel.com](https://vercel.com).
   * Click **Add New** -> **Project** and select your GitHub repository.
   * Set **Root Directory** to `frontend`.
   * Under **Build and Development Settings**:
     * Build Command: `npm run build`
     * Output Directory: `static` (Vite config outputs to `../static` by default; make sure it outputs to a relative `static/` directory when compiled standalone on Vercel).
   * Under **Environment Variables**, add:
     * `VITE_API_BASE_URL`: *Your Railway public domain* (e.g., `https://zomato-backend.up.railway.app`).

4. **Deploy**:
   Click **Deploy**. Vercel will build the React bundle and host it on a public domain.

---

## Strategy 2: Unified Deployment (Railway Only)

This strategy deploys a single container on Railway. FastAPI serves the pre-compiled React static assets directly from `/static`, requiring no separate Vercel setup.

1. **Pre-build Frontend Locally**:
   Before pushing, compile the frontend assets to the backend's `/static` folder:
   ```bash
   cd frontend
   npm run build
   ```
   Verify that `static/index.html` and `static/assets/` are updated.

2. **Create a `Procfile`**:
   Create a file named `Procfile` in the root of the project:
   ```text
   web: uvicorn src.app.main:app --host 0.0.0.0 --port $PORT
   ```

3. **Deploy on Railway**:
   * Deploy the repository directly to a new Railway service.
   * Add the required backend variables (`GROQ_API_KEY`, `LLM_MODEL`, `DATA_PATH`).
   * Generate a domain.
   * Navigate to your generated domain—the FastAPI server will serve the React app directly at the root `/` URL.

---

## 🔒 Production Security & CORS

In `src/app/main.py`, CORS is currently open to any origin (`allow_origins=["*"]`). For a production release, lock this down to only allow requests from your Vercel frontend domain:

```python
# In src/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-app.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

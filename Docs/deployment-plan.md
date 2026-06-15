# Deployment Plan: Mutual Fund FAQ Assistant

This document outlines the strategy for deploying the **Facts-Only Mutual Fund FAQ Assistant** to production. The system consists of a statically served frontend, a Python FastAPI backend, a local ChromaDB vector database, and a GitHub Actions automated ingestion pipeline.

---

## 1. Architecture Overview

- **Frontend**: Lightweight Vanilla HTML/CSS/JS interface.
- **Backend**: FastAPI web server running Python 3.10+, Langchain, and Groq SDK.
- **Database**: Local ChromaDB persistence stored in the `data/` directory.
- **Automation**: GitHub Actions CI/CD cron job fetching and committing new data daily.

---

## 2. Environment Preparation

Before deploying, ensure you have your production environment variables ready.

### Backend Secrets
- `GROQ_API_KEY`: Your production Groq API key for Llama 3.1 inference.

### Security Configurations
- Update the **CORS configuration** in `backend/main.py` from `allow_origins=["*"]` to explicitly allow only your production frontend URL (e.g., `https://my-mutual-fund-app.vercel.app`).
- Update the **API Fetch URL** in `frontend/index.html` from `http://localhost:8000/api/chat` to your production backend URL (e.g., `https://my-fastapi-backend.up.railway.app/api/chat`).

---

## 3. Frontend Deployment (Vercel / Netlify)

Because the frontend is entirely static, it can be hosted for free on a CDN-backed static host.

**Steps using Vercel:**
1. Connect your GitHub repository to [Vercel](https://vercel.com/).
2. Select the repository and configure the **Root Directory** to `frontend/`.
3. Ensure no build command is specified (as it is Vanilla JS).
4. Click **Deploy**. Vercel will provide a live URL instantly.

---

## 4. Backend Deployment (Railway)

The backend requires a Python runtime. [Railway.app](https://railway.app/) is an excellent choice for hosting native Python applications.

**Steps using Railway:**
1. Create a new Project on Railway and select **Deploy from GitHub repo**.
2. Select your repository.
3. Railway will automatically detect `requirements.txt` and install dependencies.
4. Go to **Variables** and add your `GROQ_API_KEY`.
5. Go to **Settings > Deploy > Custom Start Command** and set it to:
   ```bash
   uvicorn backend.main:app --host 0.0.0.0 --port $PORT
   ```
6. Go to the **Networking** tab and generate a public domain for your service.

> [!WARNING] 
> **Ephemeral Storage Notice:** Cloud platforms like Railway often use ephemeral disk storage. This means if the server restarts, local modifications to the `data/` folder are lost. 
> 
> *However*, because our **GitHub Action** natively commits the updated ChromaDB back to the `main` branch every morning at 10:00 AM IST, the backend will automatically pull the freshest database on every deployment/restart!

---

## 5. Automated Data Ingestion (GitHub Actions)

The ingestion pipeline is fully decoupled from the live backend server.

1. The GitHub Action `.github/workflows/ingestion_scheduler.yml` runs daily at 10:00 AM IST.
2. It executes `fetch.py`, `parse.py`, `chunker.py`, and `embed.py`.
3. It updates the `data/` directory and pushes the commit directly to GitHub.
4. **Important**: If you connect Railway or Vercel to auto-deploy on push to `main`, the daily ingestion commit will trigger a fresh deployment. This ensures the live server always spins up with the latest ChromaDB data.

---

## 6. Post-Deployment Verification

1. **Test the UI**: Visit the live frontend URL and click the suggestion chips.
2. **Verify CORS**: Check the browser console to ensure the POST request to the backend isn't blocked by CORS policies.
3. **Trigger the Action**: Manually trigger the GitHub Action in the "Actions" tab to ensure it successfully completes a run in the CI/CD environment and pushes a commit.

---
**Deployment Readiness:** **100%**

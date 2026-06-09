import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.data.repository import RestaurantRepository
from app.services.llm_client import GroqClient
from app.services.orchestrator import RecommendationOrchestrator
from app.api.routes import router as api_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan handler:
    1. Loads processed Parquet records into in-memory repository cache.
    2. Initializes Groq client.
    3. Builds and injects the recommendation orchestrator into application state.
    """
    logger.info("Executing startup lifespan event hook...")
    
    # Initialize repository
    repository = RestaurantRepository()
    app.state.repository = repository
    
    # Initialize LLM Client
    llm_client = GroqClient()
    
    # Initialize Orchestrator
    orchestrator = RecommendationOrchestrator(repository=repository, llm_client=llm_client)
    app.state.orchestrator = orchestrator
    
    logger.info("Startup complete. Data cached and Groq orchestrator ready.")
    yield
    logger.info("Shutting down application server...")

# Instantiate FastAPI server
app = FastAPI(
    title="AI Restaurant Recommendation Engine",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS policies for offline development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes prefix namespaces
app.include_router(api_router, prefix="/api/v1")

# Mount Static Front-End Presentation Assets
static_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../static"))
if not os.path.exists(static_path):
    os.makedirs(static_path, exist_ok=True)
    logger.warning(f"Static resources directory missing, creating: '{static_path}'")

app.mount("/", StaticFiles(directory=static_path, html=True), name="static")

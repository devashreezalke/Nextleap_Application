import logging
from typing import List
from fastapi import APIRouter, Request, HTTPException
from app.models.schemas import UserPreferences, RecommendationResponse

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(request: Request, preferences: UserPreferences):
    """
    Generate personalized dining recommendations from structured user preferences.
    """
    logger.info(f"Received recommendation request for location: '{preferences.location}'")
    
    # Retrieve orchestrator from app state
    orchestrator = getattr(request.app.state, "orchestrator", None)
    if not orchestrator:
        logger.critical("RecommendationOrchestrator not found in FastAPI application state.")
        raise HTTPException(status_code=503, detail="Orchestration service is unavailable.")
        
    try:
        response = orchestrator.execute(preferences)
        return response
    except Exception as e:
        logger.error(f"Failed to generate recommendations: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while generating recommendations.")

@router.get("/metadata/locations", response_model=List[str])
async def get_locations(request: Request):
    """
    Returns unique locations list populated from current database.
    """
    repository = getattr(request.app.state, "repository", None)
    if not repository:
        raise HTTPException(status_code=503, detail="Data repository is unavailable.")
    return repository.get_locations()

@router.get("/metadata/cuisines", response_model=List[str])
async def get_cuisines(request: Request):
    """
    Returns unique cuisines list populated from current database.
    """
    repository = getattr(request.app.state, "repository", None)
    if not repository:
        raise HTTPException(status_code=503, detail="Data repository is unavailable.")
    return repository.get_cuisines()

@router.get("/health")
async def health():
    """
    Basic health and readiness check endpoint.
    """
    return {"status": "ok"}

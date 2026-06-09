import os
import sys
import pandas as pd
import pytest
from unittest.mock import MagicMock

# Ensure src/ is in the import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from app.models.schemas import UserPreferences, RecommendationResponse
from app.data.repository import RestaurantRepository
from app.services.llm_client import GroqClient
from app.services.orchestrator import RecommendationOrchestrator

@pytest.fixture
def mock_repository(tmp_path):
    test_data = {
        "id": ["zom_1", "zom_2"],
        "name": ["Sushi House", "Curry Leaf"],
        "location": ["Bangalore", "Bangalore"],
        "cuisines": [["Japanese", "Sushi"], ["South Indian"]],
        "rating": [4.6, 4.2],
        "estimated_cost": [1800.0, 300.0],
        "budget_band": ["high", "low"],
        "votes": [420, 150],
        "address": ["MG Road", "Jayanagar"]
    }
    df = pd.DataFrame(test_data)
    parquet_file = tmp_path / "test_restaurants.parquet"
    df.to_parquet(parquet_file, index=False)
    return RestaurantRepository(data_path=str(parquet_file))

def test_orchestrator_empty_candidates_bypass(mock_repository):
    # Location "Delhi" has zero matching candidates
    prefs = UserPreferences(
        location="Delhi",
        budget="low",
        cuisine=None,
        min_rating=1.0,
        top_k=5
    )
    
    mock_llm = MagicMock(spec=GroqClient)
    orchestrator = RecommendationOrchestrator(mock_repository, mock_llm)
    
    response = orchestrator.execute(prefs)
    
    # Assertions
    assert isinstance(response, RecommendationResponse)
    assert len(response.recommendations) == 0
    assert "Sorry, we couldn't find" in response.summary
    assert response.meta["candidates_considered"] == 0
    
    # Verify LLM was NOT called
    mock_llm.complete.assert_not_called()

def test_orchestrator_successful_flow(mock_repository):
    prefs = UserPreferences(
        location="Bangalore",
        budget="high",
        cuisine="Japanese",
        min_rating=4.0,
        top_k=1
    )
    
    mock_llm = MagicMock(spec=GroqClient)
    # Mock LLM successful JSON output
    mock_llm.complete.return_value = """
    {
      "summary": "Here is an excellent high budget Japanese recommendation.",
      "recommendations": [
        {
          "id": "zom_1",
          "rank": 1,
          "explanation": "Sushi House offers top-tier Japanese food."
        }
      ]
    }
    """
    
    orchestrator = RecommendationOrchestrator(mock_repository, mock_llm)
    response = orchestrator.execute(prefs)
    
    # Assertions
    assert len(response.recommendations) == 1
    assert response.recommendations[0].restaurant.id == "zom_1"
    assert response.recommendations[0].explanation == "Sushi House offers top-tier Japanese food."
    assert response.meta["fallback"] is False
    assert response.meta["candidates_considered"] == 1
    
    # Verify LLM was called once
    mock_llm.complete.assert_called_once()

def test_orchestrator_llm_failure_fallback(mock_repository):
    prefs = UserPreferences(
        location="Bangalore",
        budget="high",
        cuisine="Japanese",
        min_rating=4.0,
        top_k=1
    )
    
    mock_llm = MagicMock(spec=GroqClient)
    # Simulate API Key expired / connection timeout
    mock_llm.complete.side_effect = RuntimeError("Groq Connection Timeout")
    
    orchestrator = RecommendationOrchestrator(mock_repository, mock_llm)
    response = orchestrator.execute(prefs)
    
    # Assertions: Should auto-recover and use rating-based recommendations
    assert len(response.recommendations) == 1
    assert response.recommendations[0].restaurant.id == "zom_1"
    assert "Recommended option" in response.recommendations[0].explanation
    assert response.meta["fallback"] is True
    assert response.meta["candidates_considered"] == 1

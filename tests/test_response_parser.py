import os
import sys
import pytest

# Ensure src/ is in the import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from app.models.schemas import Restaurant, UserPreferences
from app.services.response_parser import (
    clean_json_string,
    parse_llm_recommendations,
    generate_fallback_recommendations
)

@pytest.fixture
def mock_candidates():
    return [
        Restaurant(
            id="r1",
            name="Cafe Coffee Day",
            location="Delhi",
            cuisines=["Cafe", "Beverages"],
            rating=4.0,
            estimated_cost=400.0,
            budget_band="low",
            votes=120,
            address="Kashmere Gate"
        ),
        Restaurant(
            id="r2",
            name="Starbucks",
            location="Delhi",
            cuisines=["Cafe", "Coffee"],
            rating=4.2,
            estimated_cost=800.0,
            budget_band="medium",
            votes=340,
            address="Connaught Place"
        )
    ]

@pytest.fixture
def mock_preferences():
    return UserPreferences(
        location="Delhi",
        budget="medium",
        cuisine="Cafe",
        min_rating=3.5,
        top_k=2
    )

def test_clean_json_string():
    # Markdown json code block
    raw_markdown = "```json\n{\n  \"summary\": \"hello\"\n}\n```"
    assert clean_json_string(raw_markdown) == "{\n  \"summary\": \"hello\"\n}"
    
    # Conversational text surrounding JSON
    raw_conversation = "Here is the response:\n{\n  \"summary\": \"ok\"\n}\nHave a nice day!"
    assert clean_json_string(raw_conversation) == "{\n  \"summary\": \"ok\"\n}"
    
    # Raw JSON string
    raw_plain = "{\"test\": 1}"
    assert clean_json_string(raw_plain) == "{\"test\": 1}"

def test_parse_valid_llm_recommendations(mock_candidates, mock_preferences):
    raw_json = """
    {
      "summary": "Here are some good coffee spots.",
      "recommendations": [
        {
          "id": "r2",
          "rank": 1,
          "explanation": "Starbucks fits your medium budget and coffee preference."
        },
        {
          "id": "r1",
          "rank": 2,
          "explanation": "Cafe Coffee Day is a cheaper option."
        }
      ]
    }
    """
    result = parse_llm_recommendations(raw_json, mock_candidates, mock_preferences)
    
    assert result["fallback"] is False
    assert result["summary"] == "Here are some good coffee spots."
    assert len(result["recommendations"]) == 2
    assert result["recommendations"][0]["restaurant"].id == "r2"
    assert result["recommendations"][0]["rank"] == 1
    assert result["recommendations"][0]["explanation"] == "Starbucks fits your medium budget and coffee preference."

def test_parse_hallucination_grounding_filter(mock_candidates, mock_preferences):
    # Output contains r3 (which doesn't exist in mock_candidates)
    raw_json = """
    {
      "summary": "Coffee options",
      "recommendations": [
        {
          "id": "r2",
          "rank": 1,
          "explanation": "Starbucks works."
        },
        {
          "id": "r3",
          "rank": 2,
          "explanation": "Hallucinated Bistro fits your preferences."
        }
      ]
    }
    """
    result = parse_llm_recommendations(raw_json, mock_candidates, mock_preferences)
    
    # The hallucinated restaurant 'r3' should be dropped from recommendation list
    assert result["fallback"] is False
    assert len(result["recommendations"]) == 1
    assert result["recommendations"][0]["restaurant"].id == "r2"

def test_parse_malformed_json_fallback(mock_candidates, mock_preferences):
    raw_corrupted = "This is not JSON at all, error!"
    result = parse_llm_recommendations(raw_corrupted, mock_candidates, mock_preferences)
    
    # Parser should automatically trigger rating-based fallback
    assert result["fallback"] is True
    assert len(result["recommendations"]) == 2
    assert "sorted by ratings" in result["summary"]
    # Sorted by rating descending: Starbucks (4.2) -> Cafe Coffee Day (4.0)
    assert result["recommendations"][0]["restaurant"].id == "r2"

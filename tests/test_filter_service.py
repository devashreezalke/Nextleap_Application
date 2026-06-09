import os
import sys
import pandas as pd
import pytest

# Ensure src/ is in the import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from app.models.schemas import UserPreferences
from app.data.repository import RestaurantRepository
from app.services.filter_service import filter_restaurants

@pytest.fixture
def mock_repository(tmp_path):
    # Setup a mock Parquet dataset
    test_data = {
        "id": ["zom_1", "zom_2", "zom_3", "zom_4", "zom_5"],
        "name": ["Pasta Palace", "Baking Point", "Tikka Town", "Curry Leaf", "Noodle Box"],
        "location": ["Bangalore", "Bangalore", "Delhi", "Bangalore", "Bangalore"],
        "cuisines": [
            ["Italian", "Pizza"],
            ["Bakery", "Desserts"],
            ["North Indian"],
            ["South Indian", "North Indian"],
            ["Chinese", "Asian"]
        ],
        "rating": [4.5, 3.8, 4.2, 4.0, 4.5],
        "estimated_cost": [1200.0, 400.0, 600.0, 300.0, 800.0],
        "budget_band": ["medium", "low", "medium", "low", "medium"],
        "votes": [120, 50, 200, 150, 300],
        "address": ["Indiranagar", "Koramangala", "CP", "Jayanagar", "Whitefield"]
    }
    
    df = pd.DataFrame(test_data)
    parquet_file = tmp_path / "test_restaurants.parquet"
    df.to_parquet(parquet_file, index=False)
    
    # Initialize repository loading from the mock Parquet
    repo = RestaurantRepository(data_path=str(parquet_file))
    return repo

def test_filter_by_location_and_budget(mock_repository):
    # Find Italian/Pizza, Bangalore, Medium budget
    prefs = UserPreferences(
        location="Bangalore",
        budget="medium",
        cuisine="Italian",
        min_rating=1.0,
        top_k=5
    )
    
    result = filter_restaurants(prefs, mock_repository)
    candidates = result["candidates"]
    
    # Verify matches
    assert result["total_before_cap"] == 1
    assert len(candidates) == 1
    assert candidates[0].name == "Pasta Palace"
    assert "location" in result["applied_filters"]
    assert "budget" in result["applied_filters"]

def test_filter_by_cuisine_case_insensitive(mock_repository):
    # Find North Indian, Delhi, Medium budget
    prefs = UserPreferences(
        location="Delhi",
        budget="medium",
        cuisine="north indian",
        min_rating=1.0,
        top_k=5
    )
    
    result = filter_restaurants(prefs, mock_repository)
    assert result["total_before_cap"] == 1
    assert result["candidates"][0].name == "Tikka Town"

def test_filter_by_rating_threshold(mock_repository):
    # Bangalore, Low budget, rating >= 4.0
    prefs = UserPreferences(
        location="Bangalore",
        budget="low",
        cuisine=None,
        min_rating=4.0,
        top_k=5
    )
    
    result = filter_restaurants(prefs, mock_repository)
    # Baking Point (3.8) should be excluded, Curry Leaf (4.0) should match
    assert result["total_before_cap"] == 1
    assert result["candidates"][0].name == "Curry Leaf"

def test_sort_order_ranking(mock_repository):
    # Bangalore, Medium budget, no cuisine constraint
    prefs = UserPreferences(
        location="Bangalore",
        budget="medium",
        cuisine=None,
        min_rating=1.0,
        top_k=5
    )
    
    result = filter_restaurants(prefs, mock_repository)
    candidates = result["candidates"]
    
    # Matching rows: zom_1 (rating: 4.5, votes: 120), zom_5 (rating: 4.5, votes: 300)
    # zom_5 should be ranked first due to higher vote counts
    assert len(candidates) == 2
    assert candidates[0].id == "zom_5"
    assert candidates[1].id == "zom_1"

def test_candidate_capping_limit(mock_repository):
    prefs = UserPreferences(
        location="Bangalore",
        budget="medium",
        cuisine=None,
        min_rating=1.0,
        top_k=5
    )
    
    # Run with a max cap of 1 candidate
    result = filter_restaurants(prefs, mock_repository, max_candidates=1)
    assert result["total_before_cap"] == 2
    assert len(result["candidates"]) == 1
    assert result["candidates"][0].id == "zom_5"

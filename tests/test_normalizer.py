import os
import sys
import pandas as pd
import pytest

# Ensure src/ is in the import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from app.ingestion.normalizer import (
    clean_rating,
    clean_cost,
    clean_cuisines,
    map_budget_band,
    normalize_dataset
)

def test_clean_rating():
    # Standard ratings
    assert clean_rating("4.2/5") == 4.2
    assert clean_rating("3.8") == 3.8
    assert clean_rating(4.5) == 4.5
    
    # Missing / New ratings
    assert clean_rating("NEW") == 0.0
    assert clean_rating("-") == 0.0
    assert clean_rating("") == 0.0
    assert clean_rating(None) == 0.0
    
    # Out of bounds
    assert clean_rating("6.5") == 0.0

def test_clean_cost():
    # Clean integer and float representations
    assert clean_cost("1,200") == 1200.0
    assert clean_cost(" 500 ") == 500.0
    assert clean_cost(800) == 800.0
    assert clean_cost("Rs. 1,500") == 1500.0
    
    # Nulls / Invalid representations
    assert clean_cost(None) == 0.0
    assert clean_cost("") == 0.0
    assert clean_cost("abc") == 0.0

def test_clean_cuisines():
    assert clean_cuisines("Italian, Continental") == ["Italian", "Continental"]
    assert clean_cuisines("North Indian") == ["North Indian"]
    
    # Empty inputs
    assert clean_cuisines(None) == ["Various"]
    assert clean_cuisines("") == ["Various"]
    assert clean_cuisines("  ") == ["Various"]

def test_map_budget_band():
    # Based on default thresholds: Low <= 500, Medium <= 1500, High > 1500
    assert map_budget_band(350.0) == "low"
    assert map_budget_band(500.0) == "low"
    assert map_budget_band(800.0) == "medium"
    assert map_budget_band(1500.0) == "medium"
    assert map_budget_band(1600.0) == "high"

def test_normalize_dataset():
    # Test dataset with various columns and cases
    raw_data = {
        "Restaurant Name": ["Le Bistro", "Spice Club", ""],
        "City": ["Bangalore", "Delhi", "Delhi"],
        "Cuisines": ["French, Cafe", "North Indian", "Chinese"],
        "Average Cost for two": ["1,200", "450", "800"],
        "Aggregate rating": ["4.3", "NEW", "3.9"],
        "Votes": ["250", "0", "120"],
        "Address": ["Koramangala", "Connaught Place", "Rajouri Garden"]
    }
    
    df_raw = pd.DataFrame(raw_data)
    df_normalized = normalize_dataset(df_raw)
    
    # Check that rows with empty Restaurant Names are discarded
    assert len(df_normalized) == 2
    
    # Verify first row values
    row1 = df_normalized.iloc[0]
    assert row1["name"] == "Le Bistro"
    assert row1["location"] == "Bangalore"
    assert row1["cuisines"] == ["French", "Cafe"]
    assert row1["estimated_cost"] == 1200.0
    assert row1["budget_band"] == "medium"
    assert row1["rating"] == 4.3
    assert row1["votes"] == 250
    assert row1["address"] == "Koramangala"
    assert row1["id"] == "zom_0"
    
    # Verify second row values
    row2 = df_normalized.iloc[1]
    assert row2["name"] == "Spice Club"
    assert row2["rating"] == 0.0  # 'NEW' mapped to 0.0
    assert row2["budget_band"] == "low"

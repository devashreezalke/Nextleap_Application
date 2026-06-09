import logging
import re
import pandas as pd
from typing import List, Optional
from app.config import settings

logger = logging.getLogger(__name__)

def find_column(df: pd.DataFrame, options: List[str]) -> Optional[str]:
    """
    Finds a column in the DataFrame matching any of the options case-insensitively.
    """
    for option in options:
        for col in df.columns:
            if col.strip().lower() == option.lower():
                return col
    return None

def clean_rating(val) -> float:
    """
    Extracts numerical rating from string (e.g. '4.1/5' -> 4.1, 'NEW' -> 0.0).
    """
    if pd.isna(val):
        return 0.0
    val_str = str(val).strip().upper()
    if val_str in ("NEW", "-", "", "NO RATING"):
        return 0.0
    
    # Try to find a decimal number (like 4.1 or 4)
    match = re.search(r"([0-9]+(?:\.[0-9]+)?)", val_str)
    if match:
        try:
            rating = float(match.group(1))
            # Bound check
            if 0.0 <= rating <= 5.0:
                return rating
        except ValueError:
            pass
    return 0.0

def clean_cost(val) -> float:
    """
    Extracts numerical cost from string (e.g. '1,200' -> 1200.0, '500' -> 500.0).
    """
    if pd.isna(val):
        return 0.0
    val_str = str(val).strip()
    # Remove all non-numeric characters
    cleaned = re.sub(r"[^\d]", "", val_str)
    try:
        return float(cleaned) if cleaned else 0.0
    except ValueError:
        return 0.0

def clean_cuisines(val) -> List[str]:
    """
    Splits cuisines comma-separated string into a list of cleaned strings.
    """
    if pd.isna(val) or not str(val).strip():
        return ["Various"]
    return [c.strip().title() for c in str(val).split(",") if c.strip()]

def map_budget_band(cost: float) -> str:
    """
    Maps estimated cost to budget bands based on config thresholds.
    """
    if cost <= settings.BUDGET_LOW_MAX:
        return "low"
    elif cost <= settings.BUDGET_MEDIUM_MAX:
        return "medium"
    else:
        return "high"

def normalize_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalizes the raw DataFrame to standard schema:
    id, name, location, cuisines, rating, estimated_cost, budget_band, votes, address
    """
    logger.info("Starting schema normalization...")
    
    # Identify key columns using flexible mappings
    name_col = find_column(df, ["name", "restaurant name", "restaurant_name"])
    rating_col = find_column(df, ["rate", "rate (out of 5)", "rating", "aggregate rating", "aggregate_rating"])
    votes_col = find_column(df, ["votes", "vote_count"])
    location_col = find_column(df, ["location", "city", "locality", "listed_in(city)"])
    cuisines_col = find_column(df, ["cuisines", "cuisine"])
    cost_col = find_column(df, ["approx_cost(for two people)", "approx_cost", "cost", "average cost for two", "average_cost_for_two", "estimated_cost"])
    address_col = find_column(df, ["address"])

    logger.debug(f"Detected columns - name: {name_col}, rating: {rating_col}, location: {location_col}, cuisines: {cuisines_col}, cost: {cost_col}")

    # Build normalized dataframe
    normalized_data = []
    
    for idx, row in df.iterrows():
        # Extracted values with fallbacks
        raw_name = row[name_col] if name_col else None
        raw_location = row[location_col] if location_col else None
        
        # Discard row if missing critical name or location
        if pd.isna(raw_name) or not str(raw_name).strip() or pd.isna(raw_location) or not str(raw_location).strip():
            continue
            
        name = str(raw_name).strip()
        location = str(raw_location).strip().title()
        address = str(row[address_col]).strip() if (address_col and not pd.isna(row[address_col])) else ""
        
        # Process metrics
        rating = clean_rating(row[rating_col]) if rating_col else 0.0
        votes = int(row[votes_col]) if (votes_col and not pd.isna(row[votes_col]) and str(row[votes_col]).isdigit()) else 0
        cost = clean_cost(row[cost_col]) if cost_col else 0.0
        
        # Map cuisines and budget
        cuisines = clean_cuisines(row[cuisines_col]) if cuisines_col else ["Various"]
        budget_band = map_budget_band(cost)
        
        # Unique ID representation
        restaurant_id = f"zom_{idx}"
        
        normalized_data.append({
            "id": restaurant_id,
            "name": name,
            "location": location,
            "cuisines": cuisines,
            "rating": rating,
            "estimated_cost": cost,
            "budget_band": budget_band,
            "votes": votes,
            "address": address
        })
        
    normalized_df = pd.DataFrame(normalized_data)
    
    # Deduplicate to keep only unique restaurants per location
    if not normalized_df.empty:
        # Sort so that we keep the entry with highest rating and votes
        normalized_df = normalized_df.sort_values(by=["rating", "votes"], ascending=[False, False])
        normalized_df = normalized_df.drop_duplicates(subset=["name", "location"], keep="first")
        # Re-assign sequential unique IDs
        normalized_df = normalized_df.reset_index(drop=True)
        normalized_df["id"] = [f"zom_{i}" for i in range(len(normalized_df))]
        
    logger.info(f"Schema normalization complete. Unique records retained: {len(normalized_df)} / {len(df)}")
    return normalized_df

import logging
import pandas as pd
from typing import List, Dict, Any
from app.models.schemas import UserPreferences, Restaurant
from app.data.repository import RestaurantRepository

logger = logging.getLogger(__name__)

def filter_restaurants(
    preferences: UserPreferences, 
    repository: RestaurantRepository, 
    max_candidates: int = 25
) -> Dict[str, Any]:
    """
    Applies deterministic filters to the restaurant database.
    Sorts matched restaurants by rating/votes and caps the candidate list.
    """
    logger.info(f"Applying filters for location: {preferences.location}, budget: {preferences.budget}, cuisine: {preferences.cuisine}, min_rating: {preferences.min_rating}")
    
    df = repository.get_df()
    if df.empty:
        logger.warning("Repository is empty. Returning zero filter candidates.")
        return {
            "candidates": [],
            "total_before_cap": 0,
            "applied_filters": []
        }
        
    applied_filters = []
    filtered_df = df.copy()
    
    # 1. Location matching (case-insensitive exact match)
    if "location" in filtered_df.columns:
        filtered_df = filtered_df[
            filtered_df["location"].str.strip().str.lower() == preferences.location.lower()
        ]
        applied_filters.append("location")
        
    # 2. Budget band matching
    if "budget_band" in filtered_df.columns:
        filtered_df = filtered_df[
            filtered_df["budget_band"] == preferences.budget
        ]
        applied_filters.append("budget")
        
    # 3. Cuisine matching (checks if preferred cuisine is present in cuisines array)
    if preferences.cuisine and "cuisines" in filtered_df.columns:
        cuisine_query = preferences.cuisine.lower()
        
        # Check if the user's cuisine matches any item in the restaurant's cuisines list
        def cuisine_matches(cuisines_list) -> bool:
            if not isinstance(cuisines_list, (list, tuple, pd.Series)):
                return False
            return any(cuisine_query in str(c).lower() for c in cuisines_list)
            
        filtered_df = filtered_df[filtered_df["cuisines"].apply(cuisine_matches)]
        applied_filters.append("cuisine")
        
    # 4. Rating filter
    if "rating" in filtered_df.columns:
        filtered_df = filtered_df[
            filtered_df["rating"] >= preferences.min_rating
        ]
        applied_filters.append("min_rating")
        
    total_before_cap = len(filtered_df)
    logger.info(f"Filter stage complete. Matches found: {total_before_cap}")
    
    if filtered_df.empty:
        return {
            "candidates": [],
            "total_before_cap": 0,
            "applied_filters": applied_filters
        }
        
    # Sort by rating descending, then by votes count descending
    sort_cols = []
    ascending_flags = []
    
    if "rating" in filtered_df.columns:
        sort_cols.append("rating")
        ascending_flags.append(False)
    if "votes" in filtered_df.columns:
        sort_cols.append("votes")
        ascending_flags.append(False)
        
    if sort_cols:
        filtered_df = filtered_df.sort_values(by=sort_cols, ascending=ascending_flags)
        
    # Cap candidates
    capped_df = filtered_df.head(max_candidates)
    
    # Map rows to Pydantic models
    candidates = []
    for _, row in capped_df.iterrows():
        row_dict = row.to_dict()
        if isinstance(row_dict.get("cuisines"), (list, tuple, pd.Series)):
            row_dict["cuisines"] = list(row_dict["cuisines"])
        candidates.append(Restaurant(**row_dict))
        
    logger.info(f"Capped candidate list returned with size: {len(candidates)}")
    return {
        "candidates": candidates,
        "total_before_cap": total_before_cap,
        "applied_filters": applied_filters
    }

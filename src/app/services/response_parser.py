import json
import logging
import re
from typing import List, Dict, Any
from app.models.schemas import Restaurant, UserPreferences

logger = logging.getLogger(__name__)

def clean_json_string(raw_text: str) -> str:
    """
    Cleans markdown code blocks or surrounding text from raw LLM output.
    """
    text = raw_text.strip()
    
    # Check for ```json ... ``` code blocks
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
        
    # Locate outer curly braces if nested
    match_braces = re.search(r"(\{.*\})", text, re.DOTALL)
    if match_braces:
        return match_braces.group(1).strip()
        
    return text

def parse_llm_recommendations(
    raw_response: str, 
    candidates: List[Restaurant], 
    preferences: UserPreferences
) -> Dict[str, Any]:
    """
    Extracts and maps raw LLM responses. Falls back to rating-based recommendations on error.
    """
    candidates_map = {r.id: r for r in candidates}
    
    try:
        cleaned_json = clean_json_string(raw_response)
        parsed = json.loads(cleaned_json)
        
        if not isinstance(parsed, dict) or "recommendations" not in parsed:
            raise ValueError("LLM response is not a valid dictionary or is missing 'recommendations' key.")
            
        summary = parsed.get("summary", f"Here are the best dining options for you in {preferences.location}.")
        recommendations_list = []
        
        seen_ids = set()
        rank = 1
        for item in parsed["recommendations"]:
            # Check for id / restaurant_id variations
            rest_id = item.get("id") or item.get("restaurant_id")
            explanation = item.get("explanation", "")
            
            if not rest_id:
                continue
                
            # Grounding verification: candidate must exist and not be duplicated
            if rest_id in candidates_map and rest_id not in seen_ids:
                seen_ids.add(rest_id)
                recommendations_list.append({
                    "rank": item.get("rank") or rank,
                    "restaurant": candidates_map[rest_id],
                    "explanation": explanation or f"Highly rated option matching your {preferences.budget} budget."
                })
                rank += 1
                
        if not recommendations_list:
            raise ValueError("No matching grounded candidate IDs found in LLM recommendations list.")
            
        # Apply slice limit to match request
        recommendations_list = recommendations_list[:preferences.top_k]
        
        return {
            "summary": summary,
            "recommendations": recommendations_list,
            "fallback": False
        }
        
    except Exception as e:
        logger.error(f"JSON parsing or mapping failed: {e}. Falling back to database sorting rules.")
        return generate_fallback_recommendations(candidates, preferences)

def generate_fallback_recommendations(
    candidates: List[Restaurant], 
    preferences: UserPreferences
) -> Dict[str, Any]:
    """
    Generates structured recommendations directly from pre-sorted candidates without calling the LLM.
    """
    selected = candidates[:preferences.top_k]
    recommendations_list = []
    
    for idx, r in enumerate(selected):
        cuisine_str = ", ".join(r.cuisines)
        explanation = (
            f"Recommended option in {r.location} featuring a {r.rating} rating ({r.votes} votes). "
            f"Serves {cuisine_str} cuisines at an estimated cost of Rs. {r.estimated_cost} for two."
        )
        recommendations_list.append({
            "rank": idx + 1,
            "restaurant": r,
            "explanation": explanation
        })
        
    summary = f"Top options in {preferences.location} matching your criteria, sorted by ratings."
    
    return {
        "summary": summary,
        "recommendations": recommendations_list,
        "fallback": True
    }

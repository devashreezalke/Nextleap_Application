from typing import List, Tuple
from app.models.schemas import UserPreferences, Restaurant

SYSTEM_PROMPT = """You are a professional local restaurant recommendation advisor.
Your goal is to rank the candidate restaurants and provide personalized explanations based on user preferences.

CRITICAL RULES:
1. Grounding Rule: You MUST ONLY recommend restaurants that are in the provided "Candidate Restaurants" list. Never hallucinate or recommend restaurants outside of this list.
2. ID Matching: In your output, you MUST provide the exact "id" corresponding to each recommended restaurant from the candidate list.
3. Response Format: Return your response strictly as a JSON object matching the JSON Schema below. Do not add markdown backticks (such as ```json) or any other conversational text.

JSON Schema structure:
{
  "summary": "A friendly one-sentence summary of the recommendation set.",
  "recommendations": [
    {
      "id": "restaurant_id",
      "rank": 1,
      "explanation": "Personalized reason detailing why this restaurant fits the user's specific preferences, cost targets, ratings, or free-text preferences."
    }
  ]
}
"""

def build_recommendation_prompt(preferences: UserPreferences, candidates: List[Restaurant]) -> Tuple[str, str]:
    """
    Serializes the preferences and candidates list to construct the user prompt and system prompt.
    """
    candidates_list_str = ""
    for r in candidates:
        cuisines_str = ", ".join(r.cuisines)
        candidates_list_str += (
            f"- ID: {r.id}\n"
            f"  Name: {r.name}\n"
            f"  Location: {r.location}\n"
            f"  Cuisines: {cuisines_str}\n"
            f"  Rating: {r.rating} ({r.votes} votes)\n"
            f"  Estimated Cost: {r.estimated_cost} ({r.budget_band} budget)\n"
            f"  Address: {r.address}\n\n"
        )
        
    user_prompt = (
        "USER PREFERENCES:\n"
        f"- Location: {preferences.location}\n"
        f"- Budget level: {preferences.budget}\n"
        f"- Preferred Cuisine: {preferences.cuisine or 'Any'}\n"
        f"- Min Rating: {preferences.min_rating}\n"
        f"- Special preferences / requests: {preferences.additional_preferences or 'None'}\n"
        f"- Target Count (Top K): {preferences.top_k}\n\n"
        "CANDIDATE RESTAURANTS:\n"
        f"{candidates_list_str}"
        "Please select, rank, and explain the top recommendations matching these preferences. Return only raw JSON."
    )
    
    return user_prompt, SYSTEM_PROMPT

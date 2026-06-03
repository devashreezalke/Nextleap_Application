import logging
from app.models.schemas import UserPreferences, RecommendationResponse, Recommendation
from app.data.repository import RestaurantRepository
from app.services.filter_service import filter_restaurants
from app.services.prompt_builder import build_recommendation_prompt
from app.services.llm_client import GroqClient
from app.services.response_parser import parse_llm_recommendations, generate_fallback_recommendations

logger = logging.getLogger(__name__)

class RecommendationOrchestrator:
    def __init__(self, repository: RestaurantRepository, llm_client: GroqClient):
        self.repository = repository
        self.llm_client = llm_client

    def execute(self, preferences: UserPreferences) -> RecommendationResponse:
        """
        Runs the recommendation query flow.
        """
        logger.info(f"Beginning orchestration loop for preferences: {preferences}")
        
        # 1. Filter dataset to find candidate restaurants
        filter_result = filter_restaurants(preferences, self.repository)
        candidates = filter_result["candidates"]
        
        # Empty set optimization: skip LLM and return immediately
        if not candidates:
            logger.info("Skipping LLM request because zero candidates matched the parameters.")
            return RecommendationResponse(
                summary=f"Sorry, we couldn't find any restaurants in {preferences.location} that match your preferences. Try relaxing your filters.",
                recommendations=[],
                meta={
                    "candidates_considered": 0,
                    "applied_filters": filter_result["applied_filters"],
                    "fallback": False
                }
            )
            
        # 2. Build system and user prompt strings
        user_prompt, system_prompt = build_recommendation_prompt(preferences, candidates)
        
        # 3. Call LLM and parse the output
        try:
            raw_response = self.llm_client.complete(user_prompt, system_prompt)
            results = parse_llm_recommendations(raw_response, candidates, preferences)
        except Exception as e:
            logger.error(f"Upstream LLM failure occurred: {e}. Executing immediate safety fallback.")
            results = generate_fallback_recommendations(candidates, preferences)
            
        # 4. Map parsed results to Recommendation schema objects
        recommendations = []
        for item in results["recommendations"]:
            recommendations.append(Recommendation(
                rank=item["rank"],
                restaurant=item["restaurant"],
                explanation=item["explanation"]
            ))
            
        logger.info(f"Orchestration execution finished. Recommendations returned: {len(recommendations)}")
        return RecommendationResponse(
            summary=results["summary"],
            recommendations=recommendations,
            meta={
                "candidates_considered": len(candidates),
                "total_matched": filter_result["total_before_cap"],
                "applied_filters": filter_result["applied_filters"],
                "fallback": results["fallback"]
            }
        )

import logging
from typing import Optional
from groq import Groq
from app.config import settings

logger = logging.getLogger(__name__)

class GroqClient:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GROQ_API_KEY
        self.model = model or settings.LLM_MODEL
        
        if not self.api_key:
            logger.warning("GROQ_API_KEY not found in environment settings. LLM operations will fail unless key is provided.")
            self.client = None
        else:
            self.client = Groq(api_key=self.api_key)

    def complete(self, prompt: str, system_message: str) -> str:
        """
        Sends completion request to Groq server using JSON mode.
        """
        if not self.client:
            raise ValueError("Groq client is not initialized because GROQ_API_KEY is missing.")

        try:
            logger.info(f"Invoking Groq model: '{self.model}' with JSON format format constraint...")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2, # Stable rankings
                response_format={"type": "json_object"} # Enforces JSON outputs
            )
            result = response.choices[0].message.content
            logger.debug(f"Raw completion result from Groq: {result}")
            return result
        except Exception as e:
            logger.error(f"Groq API call execution failed: {e}")
            raise

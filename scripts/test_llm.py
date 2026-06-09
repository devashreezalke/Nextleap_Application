import os
import sys

# Resolve src directory relative to scripts folder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from app.config import settings
from app.services.llm_client import GroqClient

def main():
    print("Initializing Groq client...")
    try:
        client = GroqClient()
        if not client.api_key:
            print("Error: GROQ_API_KEY is not defined in config/environment. Make sure .env is populated.")
            sys.exit(1)
            
        print(f"Using model: '{client.model}'")
        print(f"API key loaded: {client.api_key[:10]}... (length: {len(client.api_key)})")
        
        prompt = "Return a JSON object with a key 'message' saying 'Groq connection successful'."
        system_message = "You are a helpful assistant. You must respond strictly in JSON format."
        
        print("Sending prompt to Groq API...")
        response = client.complete(prompt=prompt, system_message=system_message)
        print("\nResponse received successfully!")
        print("-" * 40)
        print(response)
        print("-" * 40)
        print("Test PASSED! LLM integration is working.")
        
    except Exception as e:
        print(f"\nTest FAILED with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

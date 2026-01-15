
import os
import logging
from litellm import completion
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_gemini_pro():
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        logger.error("GEMINI_API_KEY not found in env.")
        return

    logger.info(f"Testing Gemini Pro with key: {gemini_key[:5]}...")
    
    try:
        # Attempt: gemini-pro with explicit provider
        logger.info("Attempt: model='gemini-pro', custom_llm_provider='gemini'")
        response = completion(
            model="gemini-pro", # provider prefix removed since we pass custom_llm_provider
            custom_llm_provider="gemini",
            messages=[{"role": "user", "content": "Hello"}],
            api_key=gemini_key
        )
        logger.info("Attempt Success!")
        print(response)
        return
    except Exception as e:
        logger.error(f"Attempt Failed: {e}")

if __name__ == "__main__":
    test_gemini_pro()

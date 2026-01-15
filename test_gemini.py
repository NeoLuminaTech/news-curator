
import os
import logging
from litellm import completion
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_gemini():
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        logger.error("GEMINI_API_KEY not found in env.")
        return

    logger.info(f"Testing Gemini with key: {gemini_key[:5]}...")
    
    try:
        # Attempt 1: As configured currently
        logger.info("Attempt 1: model='gemini/gemini-1.5-flash'")
        response = completion(
            model="gemini/gemini-1.5-flash",
            messages=[{"role": "user", "content": "Hello"}],
            api_key=gemini_key
        )
        logger.info("Attempt 1 Success!")
        print(response)
        return
    except Exception as e:
        logger.error(f"Attempt 1 Failed: {e}")

    try:
        # Attempt 2: Explicit provider
        logger.info("Attempt 2: model='gemini-1.5-flash', custom_llm_provider='gemini'")
        response = completion(
            model="gemini-1.5-flash",
            custom_llm_provider="gemini",
            messages=[{"role": "user", "content": "Hello"}],
            api_key=gemini_key
        )
        logger.info("Attempt 2 Success!")
        print(response)
        return
    except Exception as e:
        logger.error(f"Attempt 2 Failed: {e}")

if __name__ == "__main__":
    test_gemini()

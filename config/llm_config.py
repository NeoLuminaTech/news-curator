import os
import logging
from litellm import completion

logger = logging.getLogger(__name__)

def configure_llm():
    """
    Configures the LLM provider with 3-step fallback logic:
    1. Try Gemini (gemini/gemini-1.5-flash) using GEMINI_API_KEY.
    2. Fallback to OpenAI (gpt-4o) using OPENAI_API_KEY.
    3. Fallback to OpenRouter (mistralai/mistral-7b-instruct:free).
    
    Sets the necessary environment variables for CrewAI to pick up the winner.
    """
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    openrouter_base = os.getenv("OPENROUTER_API_BASE")
    
    # 1. Try Gemini (Primary)
    if gemini_key:
        logger.info("Attempting to connect to Gemini (gemini/gemini-1.5-flash)...")
        try:
            # Litellm format for Gemini is usually gemini/model-name
            # We pass custom_llm_provider="gemini" explicitly to avoid "Provider NOT provided" errors
            # And we MUST use the model name without prefix when provider is explicit
            response = completion(
                model="gemini-1.5-flash",
                custom_llm_provider="gemini",
                messages=[{"role": "user", "content": "Hello"}],
                api_key=gemini_key
            )
            logger.info("Successfully connected to Gemini.")
            
            # Set env vars for CrewAI
            os.environ["GEMINI_API_KEY"] = gemini_key
            os.environ["OPENAI_MODEL_NAME"] = "gemini/gemini-1.5-flash"
            
            # Clear OpenAI specific vars to avoid confusion if they exist
            if "OPENAI_API_BASE" in os.environ:
                del os.environ["OPENAI_API_BASE"]
            return
        except Exception as e:
            logger.warning(f"Failed to connect to Gemini: {e}")
    else:
        logger.warning("GEMINI_API_KEY not found.")

    # 2. Try OpenAI (Fallback 1)
    if openai_key:
        logger.info("Falling back to OpenAI (gpt-4o)...")
        try:
            response = completion(
                model="gpt-4o",
                messages=[{"role": "user", "content": "Hello"}],
                api_key=openai_key
            )
            logger.info("Successfully connected to OpenAI.")
            # Ensure env vars are set for CrewAI
            os.environ["OPENAI_API_KEY"] = openai_key
            os.environ["OPENAI_MODEL_NAME"] = "gpt-4o"
            if "OPENAI_API_BASE" in os.environ:
                del os.environ["OPENAI_API_BASE"]
            return
        except Exception as e:
            logger.warning(f"Failed to connect to OpenAI: {e}")
    else:
        logger.warning("OPENAI_API_KEY not found.")

    # 3. Try OpenRouter (Fallback 2)
    if openrouter_key:
        logger.info("Falling back to OpenRouter (openrouter/mistralai/mistral-7b-instruct:free)...")
        try:
            response = completion(
                model="openrouter/mistralai/mistral-7b-instruct:free",
                messages=[{"role": "user", "content": "Hello"}],
                api_key=openrouter_key,
                api_base=openrouter_base
            )
            logger.info("Successfully connected to OpenRouter.")
            
            # Set env vars for CrewAI to use this provider
            os.environ["OPENAI_API_KEY"] = openrouter_key
            os.environ["OPENAI_API_BASE"] = openrouter_base
            os.environ["OPENAI_MODEL_NAME"] = "openrouter/mistralai/mistral-7b-instruct:free"
            return
        except Exception as e:
             logger.error(f"Failed to connect to OpenRouter: {e}")
    else:
        logger.warning("OPENROUTER_API_KEY not found.")

    # 4. Exit if all failed
    logger.critical("All LLM providers failed. Exiting application.")
    raise SystemExit("Fatal Error: Could not connect to any LLM provider.")

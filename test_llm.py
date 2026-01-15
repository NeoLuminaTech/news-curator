import os
from dotenv import load_dotenv
from litellm import completion

load_dotenv()

model = os.getenv("OPENAI_MODEL_NAME")
api_base = os.getenv("OPENAI_API_BASE")
api_key = os.getenv("OPENAI_API_KEY")

print(f"Testing model: {model}")
print(f"Base URL: {api_base}")
# print(f"Key: {api_key}") # Don't print secret

try:
    response = completion(
        model=model,
        messages=[{"role": "user", "content": "Hello, are you working?"}],
        api_base=api_base
        # api_key is implicit from env
    )
    print("Success!")
    print(response.choices[0].message.content)
except Exception as e:
    print(f"Error: {e}")

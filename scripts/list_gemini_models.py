import os
from google import genai
from src.helpers.config import Settings

settings = Settings()

def list_models():
    api_key = settings.gemini_api_key
    client = genai.Client(api_key=api_key)
    print("Available Gemini Models:")
    for model in client.models.list():
        print(f" - {model.name}")

if __name__ == "__main__":
    list_models()

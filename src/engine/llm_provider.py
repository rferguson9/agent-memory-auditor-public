import os
import json
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from src.helpers.config import Settings

# Initialize settings
settings = Settings()

class BaseLLMProvider(ABC):
    @abstractmethod
    def generate_json(self, prompt: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def generate_text(self, prompt: str) -> str:
        pass

class GeminiProvider(BaseLLMProvider):
    def __init__(self, model_name: Optional[str] = None):
        from google import genai
        api_key = settings.gemini_api_key
        if not api_key:
            raise ValueError("No Gemini API key found in settings")
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name or settings.gemini_model_name

    def generate_json(self, prompt: str) -> Dict[str, Any]:
        from google.genai import types
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        return json.loads(response.text)

    def generate_text(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt
        )
        return response.text.strip().strip("```json").strip("```")

class OpenAIProvider(BaseLLMProvider):
    def __init__(self, model_name: Optional[str] = None, base_url: Optional[str] = None, api_key: Optional[str] = None):
        from openai import OpenAI
        actual_key = api_key or settings.openai_api_key
        if not actual_key:
            raise ValueError("No API key found for OpenAI-compatible provider")
        
        self.client = OpenAI(api_key=actual_key, base_url=base_url)
        self.model_name = model_name or settings.open_ai_model_name

    def generate_json(self, prompt: str) -> Dict[str, Any]:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)

    def generate_text(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip().strip("```json").strip("```")

class GroqProvider(OpenAIProvider):
    """Groq uses the OpenAI SDK, just with a different base_url and key."""
    def __init__(self, model_name: Optional[str] = None):
        super().__init__(
            model_name=model_name or settings.groq_model_name,
            base_url="https://api.groq.com/openai/v1",
            api_key=settings.groq_api_key
        )

class LocalProvider(OpenAIProvider):
    """Local LLMs (Ollama, vLLM) often provide an OpenAI-compatible endpoint."""
    def __init__(self, model_name: Optional[str] = None):
        super().__init__(
            model_name=model_name or settings.local_model_name,
            base_url=settings.local_model_endpoint,
            api_key="none"  # Local providers usually don't need a real key
        )

class AnthropicProvider(BaseLLMProvider):
    def __init__(self, model_name: Optional[str] = None):
        # Implementation note: Requires 'anthropic' package
        try:
            import anthropic
            api_key = settings.anthropic_api_key
            if not api_key:
                raise ValueError("No Anthropic API key found in settings")
            self.client = anthropic.Anthropic(api_key=api_key)
            self.model_name = model_name or settings.anthropic_model_name
        except ImportError:
            raise ImportError("Anthropic SDK not installed. Please run 'pip install anthropic'.")

    def generate_json(self, prompt: str) -> Dict[str, Any]:
        # Anthropic doesn't have a native 'json_object' mode in the same way, 
        # so we rely on prompt engineering or the 'messages' tool use API.
        # For simplicity, we use a standard text completion and strip markdown.
        response = self.generate_text(prompt)
        return json.loads(response)

    def generate_text(self, prompt: str) -> str:
        response = self.client.messages.create(
            model=self.model_name,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )
        # Handle message content list
        return response.content[0].text.strip().strip("```json").strip("```")

def get_llm_provider(provider: str, model: Optional[str] = None) -> BaseLLMProvider:
    provider_map = {
        "gemini": GeminiProvider,
        "openai": OpenAIProvider,
        "groq": GroqProvider,
        "local": LocalProvider,
        "anthropic": AnthropicProvider
    }
    
    provider_class = provider_map.get(provider.lower())
    if not provider_class:
        raise ValueError(f"Unsupported provider: {provider}. Choose from: {list(provider_map.keys())}")
    
    return provider_class(model)

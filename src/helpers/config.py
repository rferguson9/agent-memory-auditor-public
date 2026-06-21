from os import PathLike
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    repo_root_path: PathLike = Path(__file__).resolve().parents[2]
    data_directory: PathLike = repo_root_path / "data"

    model_config = SettingsConfigDict(
        env_file=repo_root_path / ".env",
        env_file_encoding="utf-8",
    )

    gemini_api_key: str
    gemini_model_name: str = "gemini-2.5-flash"
    google_application_credentials: str

    openai_api_key: str
    open_ai_model_name: str = "gpt-4.1"

    anthropic_api_key: Optional[str] = None
    anthropic_model_name: str = "claude-3-5-sonnet"

    groq_api_key: Optional[str] = None
    groq_model_name: str = "llama-3.1-70b-versatile"

    local_model_endpoint: str = "http://localhost:11434/v1"  # Default for Ollama
    local_model_name: str = "llama3"

    ## maybe log stuff such as max_retries, log_level, etc later

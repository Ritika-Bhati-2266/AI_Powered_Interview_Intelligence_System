from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Interview Intelligence System"
    API_V1_STR: str = "/api/v1"
    
    # CORS Origins (Allowed origins for frontend connection)
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]
    
    # Local LLM Service (Ollama) url
    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434", validation_alias="OLLAMA_BASE_URL")
    
    # Offline STT model path inside 'models/' registry
    VOSK_MODEL_PATH: str = Field(default="../models/vosk_models/vosk-model-small-en-us-0.15", validation_alias="VOSK_MODEL_PATH")
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()

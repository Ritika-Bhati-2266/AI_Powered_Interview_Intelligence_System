import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Application Config
    APP_NAME: str = "Offline Interview Intelligence API"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///./interview_intel.db"
    
    # Security
    # In production, this should be loaded from secure environment variables
    SECRET_KEY: str = "NEON_CYBER_PUNK_SECURE_TOKEN_SECRET_98374982374982374"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    
    # AI Models config (Local/Offline paths or names)
    WHISPER_MODEL_SIZE: str = "base"  # options: tiny, base, small, medium
    WHISPER_DEVICE: str = "cpu"      # options: cpu, cuda
    WHISPER_COMPUTE_TYPE: str = "int8" # options: int8, float16, float32
    
    SENTENCE_TRANSFORMER_MODEL: str = "all-MiniLM-L6-v2"
    SPACY_MODEL: str = "en_core_web_sm"
    
    # Upload limits and paths
    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")
    
    class Config:
        env_prefix = "INTERVIEW_INTEL_"
        case_sensitive = True

settings = Settings()

# Ensure directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

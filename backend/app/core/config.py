import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Interview Intelligence System"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = "super_secret_jwt_signing_key_for_local_ai_interviewer_agent_2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    STORAGE_DIR: str = os.path.join(DATA_DIR, "local_storage")
    UPLOAD_DIR: str = os.path.join(STORAGE_DIR, "uploads")
    
    # Database
    DATABASE_URL: str = f"sqlite:///{os.path.join(STORAGE_DIR, 'interviewer.db')}"

    class Config:
        case_sensitive = True

settings = Settings()

# Ensure directories exist
os.makedirs(settings.DATA_DIR, exist_ok=True)
os.makedirs(settings.STORAGE_DIR, exist_ok=True)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

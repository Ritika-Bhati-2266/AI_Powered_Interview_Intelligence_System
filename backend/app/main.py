import os
import json
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.models.question import Question
from app.models.user import User
from app.models.interview import InterviewSession, InterviewResponse
from app.api.api import api_router

# Setup logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# Create database tables
try:
    logger.info("Initializing SQLite database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully.")
except Exception as e:
    logger.critical(f"Database initialization failed: {e}")

# Database Seeding helper
def seed_database():
    db = SessionLocal()
    try:
        # Check if questions already exist
        q_count = db.query(Question).count()
        if q_count == 0:
            logger.info("Question bank is empty. Seeding questions from data/questions.json...")
            json_path = os.path.join(settings.DATA_DIR, "questions.json")
            if os.path.exists(json_path):
                with open(json_path, "r", encoding="utf-8") as f:
                    questions_data = json.load(f)
                    
                for q_item in questions_data:
                    # Ignore 'id' from JSON to let DB auto-increment
                    db_question = Question(
                        role=q_item["role"],
                        category=q_item["category"],
                        difficulty=q_item["difficulty"],
                        question_text=q_item["question"],
                        ideal_answer=q_item["ideal_answer"],
                        keywords=q_item["keywords"]
                    )
                    db.add(db_question)
                db.commit()
                logger.info(f"Successfully seeded {len(questions_data)} questions in the database.")
            else:
                logger.warning(f"Default questions.json not found at {json_path}. Skipping database seed.")
        else:
            logger.info(f"Database question bank already seeded with {q_count} questions.")
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

# Execute database seed
seed_database()

# Initialize FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Local AI Interview Mock Platform with Whisper, spaCy, and librosa.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Policy Config
# Allow localhost react client to call APIs
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For local testing, allow all; can restrict to ["http://localhost:5173"] in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static uploads directory for potential file playing/downloads
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

@app.get("/", tags=["Health System"])
def system_root():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "api_docs": "/docs",
        "local_whisper_cache": "~/.cache/whisper"
    }

# Register major consolidated routes
app.include_router(api_router, prefix=settings.API_V1_STR)

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from .database import engine, Base
from .dependencies import get_db, get_current_user
from .config import settings
from . import models
from .routes import auth as auth_routes

# Initialize Database tables if not already present
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="Offline AI Interview Intelligence platform backend processing service with JWT protection.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to the web application domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Authentication Router
app.include_router(auth_routes.router)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "app": settings.APP_NAME,
        "features": {
            "authentication": "JWT Token",
            "transcription": "faster-whisper",
            "embeddings": "sentence-transformers",
            "linguistics": "spaCy",
            "audio_processing": "librosa"
        }
    }

# Seed endpoint: Public so people can test easily or bootstrap the system
@app.post("/api/seed", status_code=status.HTTP_201_CREATED)
def seed_database(db: Session = Depends(get_db)):
    """
    Seeds a default test user and demo interviews in SQLite for testing offline.
    """
    # 1. Create Default User if not exists
    user = db.query(models.User).filter(models.User.email == "test@antigravity.ai").first()
    if not user:
        # Hashed password for "password123"
        from .auth import get_password_hash
        hashed_pw = get_password_hash("password123")
        user = models.User(
            email="test@antigravity.ai",
            hashed_password=hashed_pw
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # 2. Add sample interview if user has none
    existing_interviews = db.query(models.Interview).filter(models.Interview.user_id == user.id).all()
    if not existing_interviews:
        interview1 = models.Interview(
            user_id=user.id,
            title="Senior Full-Stack AI Engineer Role",
            status="completed",
            performance_score=85.5,
            overall_feedback="Excellent alignment with high-performance architectures. Candidate demonstrates robust knowledge of offline LLMs, FastAPI async concurrency, and local transcription systems, though pacing could be tightened."
        )
        db.add(interview1)
        db.commit()
        db.refresh(interview1)

        # Questions for Interview 1
        q1 = models.Question(
            interview_id=interview1.id,
            text="Explain your approach to implementing offline transcription engines locally. What constraints do you optimize for?",
            expected_keywords="faster-whisper, concurrency, float16, memory, VRAM, thread",
            order=1
        )
        q2 = models.Question(
            interview_id=interview1.id,
            text="How do you handle real-time audio streams and split them into silence-detection frames?",
            expected_keywords="librosa, VAD, soundfile, threshold, decibel, numpy",
            order=2
        )
        db.add_all([q1, q2])
        db.commit()
        db.refresh(q1)
        db.refresh(q2)

        # Mock Answers
        a1 = models.InterviewAnswer(
            question_id=q1.id,
            transcribed_text="I prefer to deploy faster-whisper locally with a quantized float16 model configuration on local hardware. We optimize strictly for low latency and memory utilization. Multi-threading assists concurrent requests.",
            audio_duration=12.4,
            relevance_score=92.0,
            sentiment="confident",
            feedback="Strong structural knowledge. Excellent mention of float16 quantization and memory footprints."
        )
        a2 = models.InterviewAnswer(
            question_id=q2.id,
            transcribed_text="We utilize librosa's voice activity detection or WebRTC VAD to split on silence thresholds. Raw numpy buffers allow us to analyze sound levels fast.",
            audio_duration=8.9,
            relevance_score=88.5,
            sentiment="focused",
            feedback="Great description of numpy frame splitting. Solid operational knowledge of silence threshold mechanics."
        )
        db.add_all([a1, a2])
        db.commit()

        # Create a second, pending interview to simulate simulator flows
        interview2 = models.Interview(
            user_id=user.id,
            title="Machine Learning Systems Architect Screen",
            status="pending"
        )
        db.add(interview2)
        db.commit()
        db.refresh(interview2)

        q3 = models.Question(
            interview_id=interview2.id,
            text="Describe the difference between cross-encoders and bi-encoders for local semantic search.",
            expected_keywords="sentence-transformers, cosine similarity, cross-encoder, latency, re-ranking",
            order=1
        )
        db.add(q3)
        db.commit()

    return {
        "message": "Database seeded with a cyberpunk sample interview portfolio! Use credentials: test@antigravity.ai / password123"
    }

# PROTECTED ROUTE: Dashboard Summary Stats
@app.get("/api/dashboard", response_model=Dict[str, Any])
def get_dashboard(
    current_user: models.User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    Dashboard API returning summary stats and list of interviews owned by the active JWT user session.
    """
    total_interviews = db.query(models.Interview).filter(models.Interview.user_id == current_user.id).count()
    completed_interviews = db.query(models.Interview).filter(
        models.Interview.user_id == current_user.id,
        models.Interview.status == "completed"
    ).all()
    pending_interviews = db.query(models.Interview).filter(
        models.Interview.user_id == current_user.id,
        models.Interview.status == "pending"
    ).all()
    
    avg_score = 0.0
    if completed_interviews:
        scores = [intv.performance_score for intv in completed_interviews if intv.performance_score is not None]
        if scores:
            avg_score = round(sum(scores) / len(scores), 1)

    interviews_list = []
    all_interviews = db.query(models.Interview).filter(
        models.Interview.user_id == current_user.id
    ).order_by(models.Interview.created_at.desc()).all()
    
    for intv in all_interviews:
        q_count = db.query(models.Question).filter(models.Question.interview_id == intv.id).count()
        interviews_list.append({
            "id": intv.id,
            "title": intv.title,
            "status": intv.status,
            "performance_score": intv.performance_score,
            "created_at": intv.created_at.isoformat(),
            "questions_count": q_count
        })

    return {
        "stats": {
            "total_interviews": total_interviews,
            "completed": len(completed_interviews),
            "pending": len(pending_interviews),
            "average_score": avg_score
        },
        "interviews": interviews_list
    }

# PROTECTED ROUTE: Detailed Interview Evaluations
@app.get("/api/interviews/{interview_id}", response_model=Dict[str, Any])
def get_interview_detail(
    interview_id: int, 
    current_user: models.User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    Detailed interview evaluation metrics (speech evaluations/relevances) belonging to active user.
    """
    interview = db.query(models.Interview).filter(
        models.Interview.id == interview_id,
        models.Interview.user_id == current_user.id
    ).first()
    
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Interview session not found or you do not have permission to view it."
        )

    questions_data = []
    for q in interview.questions:
        ans_data = None
        if q.answer:
            ans_data = {
                "id": q.answer.id,
                "transcribed_text": q.answer.transcribed_text,
                "audio_duration": q.answer.audio_duration,
                "relevance_score": q.answer.relevance_score,
                "sentiment": q.answer.sentiment,
                "feedback": q.answer.feedback,
                "created_at": q.answer.created_at.isoformat()
            }
        questions_data.append({
            "id": q.id,
            "text": q.text,
            "expected_keywords": q.expected_keywords,
            "order": q.order,
            "answer": ans_data
        })

    return {
        "id": interview.id,
        "title": interview.title,
        "status": interview.status,
        "performance_score": interview.performance_score,
        "overall_feedback": interview.overall_feedback,
        "created_at": interview.created_at.isoformat(),
        "questions": questions_data
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)

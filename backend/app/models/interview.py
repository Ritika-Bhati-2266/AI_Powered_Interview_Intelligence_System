from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class InterviewSession(Base):
    __tablename__ = "interview_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String, index=True, nullable=False)
    difficulty = Column(String, index=True, nullable=False)
    overall_score = Column(Float, default=0.0)
    overall_feedback = Column(Text, nullable=True)
    status = Column(String, default="in_progress")  # 'in_progress', 'completed'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", backref="sessions")
    responses = relationship("InterviewResponse", back_populates="session", cascade="all, delete-orphan")

class InterviewResponse(Base):
    __tablename__ = "interview_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    
    transcript = Column(Text, nullable=True)
    audio_path = Column(String, nullable=True)
    
    # NLP scores
    similarity_score = Column(Float, default=0.0)
    technical_score = Column(Float, default=0.0)
    
    # Audio analytics scores
    communication_score = Column(Float, default=0.0)
    
    # Combined / Gaze metrics scores
    confidence_score = Column(Float, default=0.0)
    eye_contact_score = Column(Float, default=0.0)
    attention_score = Column(Float, default=0.0)
    smile_score = Column(Float, default=0.0)
    
    feedback = Column(Text, nullable=True)
    answered_at = Column(DateTime, default=datetime.utcnow)
    
    session = relationship("InterviewSession", back_populates="responses")
    question = relationship("Question")

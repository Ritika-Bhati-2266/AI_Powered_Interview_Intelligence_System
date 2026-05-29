import datetime
from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    interviews = relationship("Interview", back_populates="user", cascade="all, delete-orphan")


class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending, recording, analyzing, completed, failed
    audio_file_path = Column(String, nullable=True)
    performance_score = Column(Float, nullable=True)
    overall_feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="interviews")
    questions = relationship("Question", back_populates="interview", cascade="all, delete-orphan", order_by="Question.order")


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"), nullable=False)
    text = Column(Text, nullable=False)
    expected_keywords = Column(String, nullable=True)  # Comma-separated or JSON
    order = Column(Integer, default=0)

    # Relationships
    interview = relationship("Interview", back_populates="questions")
    answer = relationship("InterviewAnswer", uselist=False, back_populates="question", cascade="all, delete-orphan")


class InterviewAnswer(Base):
    __tablename__ = "interview_answers"

    id = Column(Integer, primary key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), unique=True, nullable=False)
    transcribed_text = Column(Text, nullable=True)
    audio_duration = Column(Float, nullable=True)
    relevance_score = Column(Float, nullable=True)
    sentiment = Column(String, nullable=True)  # positive, neutral, negative, confident, hesitant
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    question = relationship("Question", back_populates="answer")

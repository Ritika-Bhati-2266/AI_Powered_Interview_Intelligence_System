from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.core.database import Base

class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    role = Column(String, index=True, nullable=False)
    category = Column(String, index=True, nullable=False)
    difficulty = Column(String, index=True, nullable=False)
    question_text = Column(Text, nullable=False)
    ideal_answer = Column(Text, nullable=False)
    keywords = Column(String, nullable=True)  # Store as comma-separated string
    created_at = Column(DateTime, default=datetime.utcnow)

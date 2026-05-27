from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class QuestionBase(BaseModel):
    role: str
    category: str
    difficulty: str
    question_text: str
    ideal_answer: str
    keywords: Optional[str] = None  # Comma-separated strings

class QuestionCreate(QuestionBase):
    pass

class QuestionResponse(QuestionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

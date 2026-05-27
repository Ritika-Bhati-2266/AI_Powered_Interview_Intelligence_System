from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class InterviewStart(BaseModel):
    role: str
    difficulty: str

class InterviewSessionResponse(BaseModel):
    id: int
    user_id: int
    role: str
    difficulty: str
    overall_score: float
    overall_feedback: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class InterviewResponseCreate(BaseModel):
    session_id: int
    question_id: int
    eye_contact_score: float = 0.0
    attention_score: float = 0.0
    smile_score: float = 0.0

class InterviewResponseDetail(BaseModel):
    id: int
    session_id: int
    question_id: int
    transcript: Optional[str] = None
    audio_path: Optional[str] = None
    
    similarity_score: float
    technical_score: float
    communication_score: float
    confidence_score: float
    eye_contact_score: float
    attention_score: float
    smile_score: float
    
    feedback: Optional[str] = None
    answered_at: datetime

    class Config:
        from_attributes = True

class InterviewSessionDetailResponse(InterviewSessionResponse):
    responses: List[InterviewResponseDetail] = []

    class Config:
        from_attributes = True

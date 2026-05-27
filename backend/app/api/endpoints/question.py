from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import json
import os

from app.core.database import get_db
from app.models.question import Question
from app.schemas.question import QuestionCreate, QuestionResponse
from app.api.endpoints.auth import get_current_admin, get_current_user

router = APIRouter()

@router.get("/", response_model=List[QuestionResponse])
def get_questions(
    role: Optional[str] = None,
    difficulty: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    List all questions with optional filters.
    """
    query = db.query(Question)
    if role:
        query = query.filter(Question.role == role)
    if difficulty:
        query = query.filter(Question.difficulty == difficulty)
    if category:
        query = query.filter(Question.category == category)
    return query.all()

@router.get("/categories", response_model=List[str])
def get_categories(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """
    Return all unique question categories.
    """
    categories = db.query(Question.category).distinct().all()
    return [c[0] for c in categories if c[0]]

@router.get("/roles", response_model=List[str])
def get_roles(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """
    Return all unique question roles.
    """
    roles = db.query(Question.role).distinct().all()
    return [r[0] for r in roles if r[0]]

@router.post("/", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
def create_question(
    question_in: QuestionCreate, 
    db: Session = Depends(get_db),
    admin_user=Depends(get_current_admin)
):
    """
    Add a new question to the bank (Admin Only).
    """
    new_question = Question(**question_in.model_dump())
    db.add(new_question)
    db.commit()
    db.refresh(new_question)
    return new_question

@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_question(
    question_id: int, 
    db: Session = Depends(get_db),
    admin_user=Depends(get_current_admin)
):
    """
    Delete a question by ID (Admin Only).
    """
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    db.delete(question)
    db.commit()
    return

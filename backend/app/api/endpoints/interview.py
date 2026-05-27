import os
import shutil
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
import random

from app.core.database import get_db
from app.core.config import settings
from app.models.interview import InterviewSession, InterviewResponse
from app.models.question import Question
from app.schemas.interview import InterviewStart, InterviewSessionResponse, InterviewSessionDetailResponse
from app.api.endpoints.auth import get_current_user
from app.services.stt_service import transcribe_audio
from app.services.feedback_service import evaluate_response

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/start", response_model=dict)
def start_interview(
    payload: InterviewStart,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Starts a new interview session and selects a pool of 3 relevant questions.
    Returns the session ID and the selected question sequence.
    """
    logger.info(f"Starting interview session for user {current_user.email} (Role: {payload.role})")
    
    # 1. Query matching questions
    questions = db.query(Question).filter(
        Question.role == payload.role,
        Question.difficulty == payload.difficulty
    ).all()
    
    # Fallback to category overlap if no direct matches
    if not questions:
        questions = db.query(Question).filter(Question.difficulty == payload.difficulty).all()
        
    # Ultimate fallback to any questions
    if not questions:
        questions = db.query(Question).all()
        
    if not questions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No questions loaded in database question bank."
        )
        
    # Select up to 3 questions randomly
    selected_questions = random.sample(questions, min(3, len(questions)))
    
    # 2. Create session
    session = InterviewSession(
        user_id=current_user.id,
        role=payload.role,
        difficulty=payload.difficulty,
        status="in_progress"
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    
    # Serialize questions for response
    serialized_questions = []
    for q in selected_questions:
        serialized_questions.append({
            "id": q.id,
            "category": q.category,
            "difficulty": q.difficulty,
            "question_text": q.question_text,
            "ideal_answer": q.ideal_answer,
            "keywords": q.keywords
        })
        
    return {
        "session_id": session.id,
        "role": session.role,
        "difficulty": session.difficulty,
        "questions": serialized_questions
    }

@router.post("/submit", status_code=status.HTTP_201_CREATED)
def submit_answer(
    session_id: int = Form(...),
    question_id: int = Form(...),
    eye_contact_score: float = Form(0.0),
    attention_score: float = Form(0.0),
    smile_score: float = Form(0.0),
    audio: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Submits answer audio, transcribes it, runs local NLP and CV evaluations,
    and returns immediate technical & speech feedback.
    """
    # 1. Verify session exists
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id,
        InterviewSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found or access denied.")
        
    # 2. Verify question exists
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found in database.")
        
    # 3. Save uploaded audio to disk
    file_extension = audio.filename.split(".")[-1] if "." in audio.filename else "wav"
    audio_filename = f"session_{session_id}_q_{question_id}.{file_extension}"
    audio_path = os.path.join(settings.UPLOAD_DIR, audio_filename)
    
    try:
        with open(audio_path, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)
        logger.info(f"Audio saved to: {audio_path}")
    except Exception as e:
        logger.error(f"Error saving uploaded audio: {e}")
        raise HTTPException(status_code=500, detail="Error saving recording file locally.")
        
    # 4. Speech-to-Text
    transcript = transcribe_audio(audio_path)
    logger.info(f"Transcribed text: '{transcript}'")
    
    # 5. Evaluate response
    evaluation = evaluate_response(
        question_text=question.question_text,
        ideal_answer=question.ideal_answer,
        keywords=question.keywords,
        transcript=transcript,
        audio_path=audio_path,
        eye_contact_score=eye_contact_score,
        attention_score=attention_score,
        smile_score=smile_score
    )
    
    # 6. Save response record
    response = InterviewResponse(
        session_id=session_id,
        question_id=question_id,
        transcript=transcript,
        audio_path=audio_path,
        similarity_score=evaluation["similarity_score"],
        technical_score=evaluation["technical_score"],
        communication_score=evaluation["communication_score"],
        confidence_score=evaluation["confidence_score"],
        eye_contact_score=eye_contact_score,
        attention_score=attention_score,
        smile_score=smile_score,
        feedback=evaluation["feedback"]
    )
    
    db.add(response)
    db.commit()
    db.refresh(response)
    
    return {
        "response_id": response.id,
        "transcript": transcript,
        "scores": {
            "technical": evaluation["technical_score"],
            "communication": evaluation["communication_score"],
            "confidence": evaluation["confidence_score"],
            "overall": evaluation["overall_score"]
        },
        "feedback": evaluation["feedback"],
        "audio_metrics": evaluation["audio_metrics"],
        "nlp_metrics": evaluation["nlp_metrics"]
    }

@router.post("/{session_id}/end", response_model=InterviewSessionDetailResponse)
def end_interview(
    session_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Concludes the session, computes aggregate averages, compiles final reports, and seals the record.
    """
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id,
        InterviewSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found.")
        
    responses = db.query(InterviewResponse).filter(InterviewResponse.session_id == session_id).all()
    
    if not responses:
        # If no answers were completed
        session.status = "completed"
        session.overall_score = 0.0
        session.overall_feedback = "Interview ended without any answered questions."
        db.commit()
        db.refresh(session)
        return session
        
    # Calculate aggregate scores
    avg_tech = sum(r.technical_score for r in responses) / len(responses)
    avg_comm = sum(r.communication_score for r in responses) / len(responses)
    avg_conf = sum(r.confidence_score for r in responses) / len(responses)
    
    overall_score = round((avg_tech + avg_comm + avg_conf) / 3.0, 1)
    
    # Generate high-level summary review
    strong_points = []
    critique = []
    
    if avg_tech >= 75:
        strong_points.append("Technical understanding of the chosen role was exceptional.")
    else:
        critique.append("Review basic and intermediate definitions of standard questions in this field.")
        
    if avg_comm >= 75:
        strong_points.append("Vocal pacing and articulation were standard and engaging.")
    else:
        critique.append("Work on minimizing hesitations and pacing your speaking to ideal speeds (~130 WPM).")
        
    if avg_conf >= 75:
        strong_points.append("Maintained high focus and eye-contact rates during the webcam preview.")
    else:
        critique.append("Remember to look straight into your webcam lens to maintain a confident visual presence.")

    summary_text = (
        f"Mock Interview Summary for the position of **{session.role}** ({session.difficulty} level):\n\n"
        f"### Performance Breakdown:\n"
        f"- **Overall Assessment Score**: **{overall_score}%**\n"
        f"- **Average Technical Grade**: {round(avg_tech, 1)}%\n"
        f"- **Average Communication Grade**: {round(avg_comm, 1)}%\n"
        f"- **Average Confidence Grade**: {round(avg_conf, 1)}%\n\n"
        f"### Key Highlights:\n"
        + "".join([f"- **Strength**: {s}\n" for s in strong_points])
        + "".join([f"- **Action Required**: {c}\n" for c in critique]) + "\n"
        f"Keep practicing! Repeated mock sessions with our real-time feedback helps build reliable behavioral and vocal habits."
    )
    
    session.status = "completed"
    session.overall_score = overall_score
    session.overall_feedback = summary_text
    
    db.commit()
    db.refresh(session)
    return session

@router.get("/{session_id}", response_model=InterviewSessionDetailResponse)
def get_session_detail(
    session_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Returns full individual details, questions, transcripts, and feedbacks for a completed session.
    """
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id,
        InterviewSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found.")
    return session

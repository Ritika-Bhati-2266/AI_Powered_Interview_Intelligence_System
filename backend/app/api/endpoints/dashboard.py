from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models.interview import InterviewSession, InterviewResponse
from app.models.question import Question
from app.api.endpoints.auth import get_current_user
from app.schemas.interview import InterviewSessionResponse

router = APIRouter()

@router.get("/stats")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Returns aggregated KPIs, topic weaknesses, and categorical scores
    to feed React dashboard Recharts visual graphs.
    """
    sessions = db.query(InterviewSession).filter(
        InterviewSession.user_id == current_user.id,
        InterviewSession.status == "completed"
    ).order_by(InterviewSession.created_at.asc()).all()

    if not sessions:
        return {
            "total_interviews": 0,
            "average_overall_score": 0.0,
            "weak_topics": [],
            "strong_topics": [],
            "score_trends": [],
            "category_performance": []
        }

    total_interviews = len(sessions)
    average_score = sum(s.overall_score for s in sessions) / total_interviews

    # Query responses to evaluate category-level scores
    responses = db.query(
        Question.category,
        func.avg(InterviewResponse.technical_score).label("avg_tech"),
        func.avg(InterviewResponse.communication_score).label("avg_comm"),
        func.avg(InterviewResponse.confidence_score).label("avg_conf")
    ).join(
        InterviewResponse, Question.id == InterviewResponse.question_id
    ).join(
        InterviewSession, InterviewResponse.session_id == InterviewSession.id
    ).filter(
        InterviewSession.user_id == current_user.id
    ).group_by(Question.category).all()

    category_performance = []
    weak_topics = []
    strong_topics = []

    for r in responses:
        cat_name = r[0]
        # Average of the three dimensions for this category
        cat_avg = round((r[1] + r[2] + r[3]) / 3.0, 1)
        category_performance.append({
            "category": cat_name,
            "technical": round(r[1], 1),
            "communication": round(r[2], 1),
            "confidence": round(r[3], 1),
            "average": cat_avg
        })
        
        if cat_avg < 60.0:
            weak_topics.append(cat_name)
        elif cat_avg >= 75.0:
            strong_topics.append(cat_name)

    # Format historical trend chart data
    score_trends = []
    for idx, s in enumerate(sessions):
        score_trends.append({
            "index": idx + 1,
            "date": s.created_at.strftime("%Y-%m-%d"),
            "score": s.overall_score,
            "role": s.role
        })

    return {
        "total_interviews": total_interviews,
        "average_overall_score": round(average_score, 1),
        "weak_topics": weak_topics if weak_topics else ["None - Good baseline!"],
        "strong_topics": strong_topics if strong_topics else ["Keep practicing to build focus areas!"],
        "score_trends": score_trends,
        "category_performance": category_performance
    }

@router.get("/history", response_model=List[InterviewSessionResponse])
def get_interview_history(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Returns lists of all historical mock interview sessions.
    """
    return db.query(InterviewSession).filter(
        InterviewSession.user_id == current_user.id
    ).order_by(InterviewSession.created_at.desc()).all()

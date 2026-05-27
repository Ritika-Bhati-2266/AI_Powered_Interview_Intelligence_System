from fastapi import APIRouter
from app.api.endpoints import auth, question, interview, dashboard

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(question.router, prefix="/question", tags=["Questions Bank"])
api_router.include_router(interview.router, prefix="/interview", tags=["Mock Interview Session"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard Analytics"])

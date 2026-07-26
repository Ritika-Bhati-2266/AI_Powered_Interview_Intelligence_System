"""
Interview Engine Module
Core orchestration logic for the AI interview system.
Manages session state, question generation, answer evaluation,
difficulty adaptation, multi-round company structure, and final report generation.
"""

import json
import time
import random

from ai_service import (
    generate_question,
    evaluate_answer,
    detect_skill_gaps,
    generate_recommendations,
    generate_final_report_data,
    check_ollama_health,
)
from company_rounds import get_rounds_for_company
from aptitude_bank import get_aptitude_set

# ── Constants ──────────────────────────────────────────────────────────────────

# Question categories for each interview mode
HR_CATEGORIES = ["behavioral", "behavioral", "situational", "experience"]
TECHNICAL_CATEGORIES = ["technical", "technical", "project", "problem-solving"]

# Difficulty levels
DIFFICULTY_LEVELS = ["easy", "medium", "hard"]

# How many recent scores to consider for difficulty adjustment
DIFFICULTY_WINDOW = 3

# Score thresholds for difficulty adjustment
DIFFICULTY_UP_THRESHOLD = 7.0    # Avg score >= this -> increase difficulty
DIFFICULTY_DOWN_THRESHOLD = 4.0  # Avg score <= this -> decrease difficulty

# Default number of questions per interview session
DEFAULT_QUESTION_LIMIT = 8
MIN_QUESTIONS = 4
MAX_QUESTIONS = 20

# Resume phase: number of resume-specific questions to ask in Round 0
RESUME_PHASE_QUESTIONS = 3


def _experience_to_difficulty(experience: str) -> int:
    """
    Map candidate experience string to starting difficulty level.
    0 = easy, 1 = medium, 2 = hard
    """
    if not experience:
        return 0
    exp = experience.lower().strip()
    if exp in ("0-1", "0-1 years", "entry level", "0"):
        return 0
    if exp in ("1-2", "1-2 years", "junior", "1"):
        return 0
    if exp in ("2-4", "2-4 years", "mid-level", "mid", "2"):
        return 0
    if exp in ("4-7", "4-7 years", "senior", "4", "5", "6", "7"):
        return 1
    if exp in ("7-10", "7-10 years", "lead", "staff", "8", "9", "10"):
        return 1
    if exp in ("10+", "10+ years", "principal", "architect"):
        return 2
    try:
        years = float(experience)
        if years < 4:
            return 0
        if years < 7:
            return 1
        return 2
    except (ValueError, TypeError):
        return 0


# ── Session Management ────────────────────────────────────────────────────────

class InterviewSession:
    """
    Represents a single interview session with multi-round state tracking.

    Attributes:
        session_id: Unique identifier
        candidate_id: DB candidate ID
        candidate_name: Candidate's name
        candidate_role: Target role
        candidate_experience: Years of experience
        candidate_skills: List of skills
        resume_text: Full resume text
        mode: "hr" or "technical"
        status: "waiting", "in_progress", "completed"
        current_difficulty: Current difficulty level index (0=easy, 1=medium, 2=hard)
        current_round_index: 0-based index into the rounds list. -1 = resume phase, 0+ = company rounds
        rounds: List of round dicts from company_rounds (or resume-phase entry)
        round_question_count: Questions asked in the current round
        total_questions: Target total questions for this session
        questions: List of questions asked
        answers: List of answer evaluation dicts
        recent_scores: Rolling window of overall scores for difficulty adaptation
        start_time: Unix timestamp when interview started
        end_time: Unix timestamp when interview ended
        company: Company name for round structure
    """

    def __init__(self, session_id: str, candidate_id: int, candidate_name: str,
                 candidate_role: str, candidate_experience: str,
                 candidate_skills: list, resume_text: str, mode: str,
                 company: str = "General",
                 total_questions: int = DEFAULT_QUESTION_LIMIT):
        self.session_id = session_id
        self.candidate_id = candidate_id
        self.candidate_name = candidate_name
        self.candidate_role = candidate_role
        self.candidate_experience = candidate_experience
        self.candidate_skills = candidate_skills or []
        self.resume_text = resume_text or ""
        self.mode = mode
        self.company = company
        self.status = "waiting"
        self.current_difficulty = _experience_to_difficulty(candidate_experience)
        self.current_question_index = 0
        self.total_questions = max(MIN_QUESTIONS, min(total_questions, MAX_QUESTIONS))
        self.questions = []
        self.questions_meta = []
        self.answers = []
        self.recent_scores = []
        self.start_time = None
        self.end_time = None
        self.error = None

        # ── Multi-round state ──
        # Load company rounds
        raw_rounds = get_rounds_for_company(company)

        # We prepend a "Resume Phase" as round 0 (only if we have resume text)
        self.rounds = []
        if self.resume_text and self.resume_text.strip():
            # Resume phase: first 2-3 questions about the candidate's resume
            resume_questions = min(RESUME_PHASE_QUESTIONS, 3)
            # If first real round has fewer than 3 questions, combine resume into it
            if raw_rounds and raw_rounds[0].get("questions", 3) < 3:
                # Merge resume questions into Round 1's count
                round1 = dict(raw_rounds[0])
                round1["questions"] = round1.get("questions", 3) + resume_questions
                round1["focus"] = f"Resume Discussion + {round1.get('focus', 'Technical')}"
                round1["is_resume_phase"] = True
                self.rounds.append(round1)
                self.rounds.extend(raw_rounds[1:])
            else:
                resume_round = {
                    "name": "Resume Discussion",
                    "type": "technical" if mode == "technical" else "hr",
                    "questions": resume_questions,
                    "duration_min": 15,
                    "focus": "Your resume, skills, projects, and experience",
                    "is_resume_phase": True,
                }
                self.rounds.append(resume_round)
                self.rounds.extend(raw_rounds)
        else:
            self.rounds = raw_rounds

        # Round tracking
        self.current_round_index = 0
        self.round_question_count = 0
        self.is_resume_phase = bool(
            self.rounds and self.rounds[0].get("is_resume_phase", False)
        )

        # ── Aptitude round state ──
        self.aptitude_questions = []       # Pre-loaded MCQ question dicts
        self.aptitude_question_index = 0   # Current index into aptitude_questions
        self.aptitude_correct_count = 0    # Correct answers so far
        self.aptitude_total_count = 0      # Total aptitude questions answered

        # Recalculate total questions as sum of all rounds
        self.total_questions = sum(r.get("questions", 3) for r in self.rounds)

    def get_current_round(self) -> dict:
        """Return the current round dict, or empty dict if beyond last round."""
        if 0 <= self.current_round_index < len(self.rounds):
            return self.rounds[self.current_round_index]
        return {}

    def to_dict(self) -> dict:
        """Serialize session state to a dictionary for storage."""
        current_round = self.get_current_round()
        is_resume = self.is_resume_phase and self.current_round_index == 0

        return {
            "session_id": self.session_id,
            "candidate_id": self.candidate_id,
            "candidate_name": self.candidate_name,
            "candidate_role": self.candidate_role,
            "candidate_experience": self.candidate_experience,
            "candidate_skills": self.candidate_skills,
            "resume_text": self.resume_text[:500] if self.resume_text else "",
            "mode": self.mode,
            "company": self.company,
            "status": self.status,
            "current_difficulty": self.current_difficulty,
            "difficulty_label": DIFFICULTY_LEVELS[self.current_difficulty],
            "current_question_index": self.current_question_index,
            "total_questions": self.total_questions,
            # Round info
            "rounds": self.rounds,
            "current_round_index": self.current_round_index,
            "round_question_count": self.round_question_count,
            "is_resume_phase": is_resume,
            "current_round": current_round,
            "questions": self.questions,
            "questions_meta": self.questions_meta,
            "answers": self.answers,
            "recent_scores": self.recent_scores,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "error": self.error,
        }


# ── In-Memory Session Store ───────────────────────────────────────────────────

class SessionStore:
    """
    Simple in-memory store for active interview sessions.
    In production, this would be replaced with Redis or database storage.
    """

    def __init__(self):
        self._sessions = {}

    def create(self, session: InterviewSession):
        self._sessions[session.session_id] = session

    def get(self, session_id: str) -> InterviewSession:
        return self._sessions.get(session_id)

    def delete(self, session_id: str):
        self._sessions.pop(session_id, None)

    def list_by_candidate(self, candidate_id: int) -> list:
        return [
            s for s in self._sessions.values()
            if s.candidate_id == candidate_id
        ]

    def list_all(self) -> list:
        return list(self._sessions.values())


# Global session store instance
session_store = SessionStore()


# ── Core Interview Logic ───────────────────────────────────────────────────────

def start_interview(session_id: str, candidate_id: int, candidate_name: str,
                    candidate_role: str, candidate_experience: str,
                    candidate_skills: list, resume_text: str,
                    mode: str = "technical", total_questions: int = None,
                    company: str = "General") -> dict:
    """
    Initialize a new interview session with company-specific round structure.

    Returns:
        Dict with session state including the first question (if generated)
    """
    if total_questions is None:
        total_questions = DEFAULT_QUESTION_LIMIT

    session = InterviewSession(
        session_id=session_id,
        candidate_id=candidate_id,
        candidate_name=candidate_name,
        candidate_role=candidate_role,
        candidate_experience=candidate_experience,
        candidate_skills=candidate_skills,
        resume_text=resume_text,
        mode=mode,
        company=company,
        total_questions=total_questions,
    )

    session.status = "in_progress"
    session.start_time = time.time()

    session_store.create(session)

    # ── Pre-load aptitude questions if first round is aptitude ──
    current_round = session.get_current_round()
    if current_round.get("type") == "aptitude":
        q_count = current_round.get("questions", 10)
        # Distribute using company-specific ratios
        session.aptitude_questions = get_aptitude_set(
            num_quant=4, num_logical=4, num_verbal=2,
            company=session.company,
        )

    # Generate the first question
    result = _generate_next_question(session)
    if result.get("error"):
        session.error = result["error"]
        return {"error": result["error"]}

    current_round = session.get_current_round()

    return {
        "session_id": session.session_id,
        "status": session.status,
        "question": result.get("question", ""),
        "question_number": 1,
        "total_questions": session.total_questions,
        "difficulty": DIFFICULTY_LEVELS[session.current_difficulty],
        "mode": session.mode,
        "candidate_name": session.candidate_name,
        # Round info
        "rounds": session.rounds,
        "current_round_index": session.current_round_index,
        "round_question_count": session.round_question_count,
        "is_resume_phase": session.is_resume_phase and session.current_round_index == 0,
        "current_round": {
            "name": current_round.get("name", "Technical"),
            "type": current_round.get("type", session.mode),
            "focus": current_round.get("focus", ""),
            "questions": current_round.get("questions", 3),
        },
        "total_rounds": len(session.rounds),
        "is_aptitude": current_round.get("type") == "aptitude",
        "aptitude_total": len(session.aptitude_questions) if session.aptitude_questions else 0,
        "aptitude_score": 0,
        "aptitude_correct": 0,
    }


def submit_answer(session_id: str, answer: str) -> dict:
    """
    Process a candidate's answer, evaluate it, adapt difficulty,
    handle round transitions, and return the next question or completion.

    Args:
        session_id: Active session ID
        answer: Candidate's answer text

    Returns:
        Dict with evaluation results and next question (or completion)
    """
    session = session_store.get(session_id)
    if not session:
        return {"error": "Session not found. Please start a new interview."}

    if session.status == "completed":
        return {"error": "This interview session has already ended."}

    # Get the current question
    if session.current_question_index >= len(session.questions):
        return {"error": "No active question found. Please start a new interview."}

    current_question = session.questions[session.current_question_index]

    # Get current round info
    current_round = session.get_current_round()
    is_resume = session.is_resume_phase and session.current_round_index == 0

    # ── Aptitude Round Handling ───────────────────────────────────────────
    if current_round.get("type") == "aptitude":
        return _handle_aptitude_answer(session, answer, current_round, current_question)

    # Evaluate the answer
    evaluation = evaluate_answer(
        question=current_question,
        answer=answer,
        role=session.candidate_role,
        difficulty=DIFFICULTY_LEVELS[session.current_difficulty],
        skills=session.candidate_skills,
    )

    # Get question metadata
    question_meta = session.questions_meta[session.current_question_index] if session.questions_meta else {}
    category = question_meta.get('category', 'general')

    # Build the answer record
    answer_record = {
        "question": current_question,
        "answer": answer,
        "overall_score": evaluation.get("overall_score", 5),
        "technical_score": evaluation.get("technical_score", 5),
        "communication_score": evaluation.get("communication_score", 5),
        "confidence_score": evaluation.get("confidence_score", 5),
        "problem_solving_score": evaluation.get("problem_solving_score", 5),
        "time_management_score": evaluation.get("time_management_score", 5),
        "conceptual_clarity_score": evaluation.get("conceptual_clarity_score", 5),
        "feedback": evaluation.get("feedback", ""),
        "improved_answer": evaluation.get("improved_answer", ""),
        "ideal_answer": evaluation.get("ideal_answer", ""),
        "improvement_tip": evaluation.get("improvement_tip", ""),
        "score_explanation": evaluation.get("score_explanation", ""),
        "strengths": evaluation.get("strengths", []),
        "weaknesses": evaluation.get("weaknesses", []),
        "keywords_used": evaluation.get("keywords_used", []),
        "keywords_missed": evaluation.get("keywords_missed", []),
        "difficulty": DIFFICULTY_LEVELS[session.current_difficulty],
        "category": category,
        # Filler-word analysis (populated by ai_service.evaluate_answer)
        "filler_word_count": evaluation.get("filler_word_count", 0),
        "filler_words": evaluation.get("filler_words", {}),
        # Rewrite tracking
        "rewrite_used": False,
        "rewrite_text": "",
        "rewrite_scores": {},
        # Round tracking
        "round_name": current_round.get("name", "General"),
        "round_number": session.current_round_index + 1,
    }

    session.answers.append(answer_record)
    session.recent_scores.append(answer_record["overall_score"])
    session.round_question_count += 1

    # Adapt difficulty based on recent performance
    _adapt_difficulty(session)

    # Advance to next question
    session.current_question_index += 1

    # Check if current round is complete
    round_question_limit = current_round.get("questions", 3)
    round_complete = session.round_question_count >= round_question_limit
    is_last_round = session.current_round_index >= len(session.rounds) - 1
    is_complete = round_complete and is_last_round

    # Build response
    response = {
        "session_id": session.session_id,
        "evaluation": {
            "overall_score": answer_record["overall_score"],
            "technical_score": answer_record["technical_score"],
            "communication_score": answer_record["communication_score"],
            "confidence_score": answer_record["confidence_score"],
            "problem_solving_score": answer_record["problem_solving_score"],
            "time_management_score": answer_record["time_management_score"],
            "conceptual_clarity_score": answer_record["conceptual_clarity_score"],
            "feedback": answer_record["feedback"],
            "improved_answer": answer_record.get("improved_answer", ""),
            "ideal_answer": answer_record.get("ideal_answer", ""),
            "improvement_tip": answer_record.get("improvement_tip", ""),
            "score_explanation": answer_record.get("score_explanation", ""),
            "strengths": answer_record.get("strengths", []),
            "weaknesses": answer_record.get("weaknesses", []),
            "keywords_used": answer_record.get("keywords_used", []),
            "keywords_missed": answer_record.get("keywords_missed", []),
            "filler_word_count": answer_record.get("filler_word_count", 0),
            "filler_words": answer_record.get("filler_words", {}),
        },
        "progress": {
            "current": session.current_question_index,
            "total": session.total_questions,
        },
        "round_progress": {
            "current_round": session.current_round_index,
            "total_rounds": len(session.rounds),
            "round_question_count": session.round_question_count,
            "round_question_limit": round_question_limit,
            "round_complete": round_complete,
            "round_name": current_round.get("name", ""),
            "next_round_name": "",
        },
        "is_complete": is_complete,
        "current_round": {
            "name": current_round.get("name", "Technical"),
            "type": current_round.get("type", session.mode),
            "focus": current_round.get("focus", ""),
            "questions": round_question_limit,
        },
        "is_resume_phase": is_resume,
    }

    if is_complete:
        # End the interview
        session.status = "completed"
        session.end_time = time.time()
        response["completion"] = {
            "message": "🎉 All rounds complete! Generating your comprehensive report...",
            "report_url": f"/report/{session.session_id}",
        }
    elif round_complete and not is_last_round:
        # Round transition!
        session.current_round_index += 1
        session.round_question_count = 0
        session.is_resume_phase = False

        # Reset difficulty to experience-appropriate baseline for new round
        session.current_difficulty = _experience_to_difficulty(session.candidate_experience)
        session.recent_scores = []

        next_round = session.get_current_round()

        # ── Pre-load aptitude questions if transitioning to an aptitude round ──
        if next_round.get("type") == "aptitude":
            q_count = next_round.get("questions", 10)
            session.aptitude_questions = get_aptitude_set(
                num_quant=4, num_logical=4, num_verbal=2,
                company=session.company,
            )
            session.aptitude_question_index = 0
            session.aptitude_correct_count = 0
            session.aptitude_total_count = 0
        response["round_progress"]["next_round_name"] = next_round.get("name", "")
        response["round_transition"] = {
            "completed_round": current_round.get("name", ""),
            "next_round": next_round.get("name", ""),
            "next_round_focus": next_round.get("focus", ""),
            "message": f"✅ Round {session.current_round_index} ({current_round.get('name', '')}) Complete! "
                       f"Starting Round {session.current_round_index + 1}: {next_round.get('name', '')}",
        }
        response["current_round"] = {
            "name": next_round.get("name", "Technical"),
            "type": next_round.get("type", session.mode),
            "focus": next_round.get("focus", ""),
            "questions": next_round.get("questions", 3),
        }
        response["is_aptitude"] = (next_round.get("type") == "aptitude")

        # Generate next question for the new round
        next_q_result = _generate_next_question(session)
        if next_q_result.get("error"):
            response["next_question"] = None
            response["error"] = next_q_result["error"]
        else:
            response["next_question"] = next_q_result.get("question", "")
            response["difficulty"] = DIFFICULTY_LEVELS[session.current_difficulty]
    else:
        # Same round continues — generate next question
        next_q_result = _generate_next_question(session)
        if next_q_result.get("error"):
            response["next_question"] = None
            response["error"] = next_q_result["error"]
        else:
            response["next_question"] = next_q_result.get("question", "")
            response["difficulty"] = DIFFICULTY_LEVELS[session.current_difficulty]

    return response


def rewrite_answer(session_id: str, answer_index: int, rewritten_answer: str) -> dict:
    """
    Allow the candidate to rewrite a previous answer once.

    Args:
        session_id: Active session ID
        answer_index: Index into session.answers (0-based)
        rewritten_answer: The candidate's rewritten answer

    Returns:
        Dict with original evaluation, rewrite evaluation, improvement delta,
        and the updated answer record.
    """
    session = session_store.get(session_id)
    if not session:
        return {"error": "Session not found. Please start a new interview."}

    if not (0 <= answer_index < len(session.answers)):
        return {"error": "Invalid answer index."}

    record = session.answers[answer_index]

    if record.get("rewrite_used", False):
        return {"error": "This answer has already been rewritten. Only one rewrite is allowed per answer."}

    if not rewritten_answer or not rewritten_answer.strip():
        return {"error": "Rewritten answer cannot be empty."}

    question = record["question"]

    # Evaluate the rewritten answer using the same settings as the original
    rewrite_evaluation = evaluate_answer(
        question=question,
        answer=rewritten_answer,
        role=session.candidate_role,
        difficulty=record.get("difficulty", "medium"),
        skills=session.candidate_skills,
    )

    original_scores = {
        "overall_score": record.get("overall_score", 0),
        "technical_score": record.get("technical_score", 0),
        "communication_score": record.get("communication_score", 0),
        "confidence_score": record.get("confidence_score", 0),
        "problem_solving_score": record.get("problem_solving_score", 0),
        "time_management_score": record.get("time_management_score", 0),
        "conceptual_clarity_score": record.get("conceptual_clarity_score", 0),
    }

    rewrite_scores = {
        "overall_score": rewrite_evaluation.get("overall_score", 0),
        "technical_score": rewrite_evaluation.get("technical_score", 0),
        "communication_score": rewrite_evaluation.get("communication_score", 0),
        "confidence_score": rewrite_evaluation.get("confidence_score", 0),
        "problem_solving_score": rewrite_evaluation.get("problem_solving_score", 0),
        "time_management_score": rewrite_evaluation.get("time_management_score", 0),
        "conceptual_clarity_score": rewrite_evaluation.get("conceptual_clarity_score", 0),
    }

    improvement = {
        key: rewrite_scores[key] - original_scores[key]
        for key in original_scores
    }

    # Store rewrite on the answer record
    record["rewrite_used"] = True
    record["rewrite_text"] = rewritten_answer
    record["rewrite_scores"] = rewrite_scores
    record["rewrite_evaluation"] = rewrite_evaluation
    record["rewrite_improvement"] = improvement
    record["rewrite_filler_word_count"] = rewrite_evaluation.get("filler_word_count", 0)
    record["rewrite_filler_words"] = rewrite_evaluation.get("filler_words", {})

    # Promote the rewrite scores to become the "current" scores for reporting
    # but keep originals available via original_scores/rewrite_scores
    record["overall_score"] = rewrite_scores["overall_score"]
    record["technical_score"] = rewrite_scores["technical_score"]
    record["communication_score"] = rewrite_scores["communication_score"]
    record["confidence_score"] = rewrite_scores["confidence_score"]
    record["problem_solving_score"] = rewrite_scores["problem_solving_score"]
    record["time_management_score"] = rewrite_scores["time_management_score"]
    record["conceptual_clarity_score"] = rewrite_scores["conceptual_clarity_score"]
    record["feedback"] = rewrite_evaluation.get("feedback", record.get("feedback", ""))
    record["ideal_answer"] = rewrite_evaluation.get("ideal_answer", record.get("ideal_answer", ""))
    record["improvement_tip"] = rewrite_evaluation.get("improvement_tip", record.get("improvement_tip", ""))
    record["filler_word_count"] = rewrite_evaluation.get("filler_word_count", 0)
    record["filler_words"] = rewrite_evaluation.get("filler_words", {})

    # Update recent_scores rolling window to reflect the rewrite
    if session.recent_scores:
        # Replace the score corresponding to this answer if possible
        # answer_index maps directly to the order answers were appended
        if answer_index < len(session.recent_scores):
            session.recent_scores[answer_index] = rewrite_scores["overall_score"]

    return {
        "session_id": session_id,
        "answer_index": answer_index,
        "original_scores": original_scores,
        "rewrite_scores": rewrite_scores,
        "improvement": improvement,
        "rewrite_evaluation": rewrite_evaluation,
    }


def generate_report(session_id: str) -> dict:
    """
    Generate the final interview report with all scores, analysis,
    skill gaps, recommendations, and per-round breakdown.

    Args:
        session_id: Completed session ID

    Returns:
        Full report dict
    """
    session = session_store.get(session_id)
    if not session:
        return {"error": "Session not found."}

    candidate_info = {
        "name": session.candidate_name,
        "role": session.candidate_role,
        "experience": session.candidate_experience,
        "skills": session.candidate_skills,
        "mode": session.mode,
        "company": session.company,
    }

    session_data = {
        "session_id": session.session_id,
        "mode": session.mode,
        "company": session.company,
        "total_questions": session.total_questions,
        "completed_questions": len(session.answers),
        "rounds": [dict(r) for r in session.rounds],
        "start_time": session.start_time,
        "end_time": session.end_time,
        "duration": round((session.end_time or time.time()) - (session.start_time or time.time()), 1),
        # Aptitude data
        "aptitude_questions": session.aptitude_questions if hasattr(session, 'aptitude_questions') else [],
        "aptitude_correct_count": getattr(session, 'aptitude_correct_count', 0),
        "aptitude_total_count": getattr(session, 'aptitude_total_count', 0),
    }

    # ── Build aptitude-specific report section ──
    aptitude_data = None
    aptitude_answers = [a for a in session.answers if a.get("is_mcq")]
    if aptitude_answers:
        categories = {"quantitative": [], "logical_reasoning": [], "verbal": []}
        for a in aptitude_answers:
            cat = a.get("category", "unknown")
            if cat in categories:
                categories[cat].append(a)

        cat_breakdown = {}
        for cat, items in categories.items():
            if items:
                correct = sum(1 for i in items if i.get("is_correct"))
                cat_breakdown[cat.replace("_", " ").title()] = {
                    "correct": correct,
                    "total": len(items),
                    "score": round((correct / len(items)) * 100, 1),
                }

        aptitude_data = {
            "correct": session.aptitude_correct_count,
            "total": session.aptitude_total_count,
            "score": round((session.aptitude_correct_count / max(session.aptitude_total_count, 1)) * 100, 1),
            "score_out_of_10": round((session.aptitude_correct_count / max(session.aptitude_total_count, 1)) * 10, 1),
            "category_breakdown": cat_breakdown,
            "questions": [{
                "number": i + 1,
                "question": a.get("question", ""),
                "answer": a.get("answer", ""),
                "correct_answer": a.get("correct_answer", ""),
                "is_correct": a.get("is_correct", False),
                "category": a.get("category", ""),
                "explanation": a.get("explanation", ""),
            } for i, a in enumerate(aptitude_answers)],
        }

    # Detect skill gaps from the answers
    skill_gaps = detect_skill_gaps(
        skills=session.candidate_skills,
        questions_and_answers=session.answers,
        role=session.candidate_role,
    )

    # Calculate overall score for recommendations
    if session.answers:
        overall_score = sum(a.get("overall_score", 0) for a in session.answers) / len(session.answers)
    else:
        overall_score = 0

    # Generate recommendations
    recommendations = generate_recommendations(
        skill_gaps=skill_gaps,
        overall_score=int(overall_score),
        role=session.candidate_role,
    )

    # Generate the full report
    report = generate_final_report_data(
        candidate_info=candidate_info,
        session_data=session_data,
        answers=session.answers,
        skill_gaps=skill_gaps,
        recommendations=recommendations,
    )

    # Attach aptitude data
    if aptitude_data:
        report["aptitude_data"] = aptitude_data

    return report


def get_session_state(session_id: str) -> dict:
    """Get current session state for the UI."""
    session = session_store.get(session_id)
    if not session:
        return {"error": "Session not found"}

    current_round = session.get_current_round()

    return {
        "session_id": session.session_id,
        "candidate_name": session.candidate_name,
        "candidate_role": session.candidate_role,
        "mode": session.mode,
        "company": session.company,
        "status": session.status,
        "current_question": session.current_question_index,
        "total_questions": session.total_questions,
        "current_difficulty": DIFFICULTY_LEVELS[session.current_difficulty],
        "questions_asked": len(session.questions),
        "answers_given": len(session.answers),
        # Round info
        "rounds": [dict(r) for r in session.rounds],
        "current_round_index": session.current_round_index,
        "round_question_count": session.round_question_count,
        "current_round": {
            "name": current_round.get("name", ""),
            "type": current_round.get("type", ""),
            "focus": current_round.get("focus", ""),
            "questions": current_round.get("questions", 3),
        },
        "is_resume_phase": session.is_resume_phase and session.current_round_index == 0,
        "error": session.error,
    }


# ── Internal Helpers ──────────────────────────────────────────────────────────

def _generate_next_question(session: InterviewSession) -> dict:
    """
    Generate the next question for the session, considering round info,
    resume phase, difficulty, mode, and conversation context.
    For aptitude rounds, serves the next pre-loaded MCQ instead of calling Ollama.
    """
    current_round = session.get_current_round()

    # ── Aptitude round: serve from pre-loaded question bank ──
    if current_round.get("type") == "aptitude":
        # Defensive: auto-load if not pre-loaded at round transition
        if not session.aptitude_questions:
            q_count = current_round.get("questions", 10)
            session.aptitude_questions = get_aptitude_set(
                num_quant=4, num_logical=4, num_verbal=2,
                company=session.company,
            )
            session.aptitude_question_index = 0
            session.aptitude_correct_count = 0
            session.aptitude_total_count = 0

        idx = session.aptitude_question_index
        if idx >= len(session.aptitude_questions):
            return {"question": "", "category": "aptitude", "difficulty": "medium",
                    "round_info": {}, "is_resume_phase": False, "error": "No more aptitude questions"}

        q_data = session.aptitude_questions[idx]
        company_label = q_data.get("company_pattern_label", "")
        company_context_line = f"\n\n*[Context: {company_label}]" if company_label else ""
        question_text = (
            f"**[Aptitude - {q_data['category'].replace('_', ' ').title()}]**\n\n"
            f"{q_data['question']}{company_context_line}\n\n"
            f"A. {q_data['options'][0]}\n"
            f"B. {q_data['options'][1]}\n"
            f"C. {q_data['options'][2]}\n"
            f"D. {q_data['options'][3]}"
        )

        session.questions.append(question_text)
        session.questions_meta.append({
            "category": "aptitude",
            "difficulty": "medium",
            "round_index": session.current_round_index,
            "round_name": current_round.get("name", "Aptitude Test"),
            "is_resume_phase": False,
            "aptitude_index": idx,
            "company": session.company,
            "company_pattern_label": company_label,
        })

        return {"question": question_text, "category": "aptitude", "difficulty": "medium",
                "round_info": dict(current_round), "is_resume_phase": False,
                "company_pattern_label": company_label}

    difficulty = DIFFICULTY_LEVELS[session.current_difficulty]

    # Determine category based on mode and question index
    if session.mode == "hr":
        categories = HR_CATEGORIES
    else:
        categories = TECHNICAL_CATEGORIES

    category = categories[session.current_question_index % len(categories)]

    # Get current round info
    current_round = session.get_current_round()
    is_resume = session.is_resume_phase and session.current_round_index == 0

    round_info = {
        "name": current_round.get("name", "Technical"),
        "type": current_round.get("type", session.mode),
        "focus": current_round.get("focus", ""),
        "question_count": current_round.get("questions", 3),
    }

    # Build context from recent Q&A (for follow-up relevance)
    context_parts = []
    for qa in session.answers[-3:]:  # Last 3 answers for context
        context_parts.append(f"Q: {qa.get('question', '')}\nA: {qa.get('answer', '')}")
    context = "\n\n".join(context_parts)

    # Generate the question with round info, resume phase flag, and previous questions history
    question = generate_question(
        role=session.candidate_role,
        experience=session.candidate_experience,
        skills=session.candidate_skills,
        category=category,
        difficulty=difficulty,
        context=context,
        resume_text=session.resume_text,
        round_info=round_info,
        is_resume_phase=is_resume,
        company=session.company,
        previous_questions=session.questions,
    )

    if not question or question.startswith("[OLLAMA_") or question.startswith("[PARSE_"):
        # Fallback: use a pre-built question (respects round type)
        question = _fallback_question(session.candidate_role, round_info.get("type", category), difficulty)
        # Tag the fallback with company context
        company_label = ""
        if session.company and session.company.lower() != "general":
            from ai_service import get_company_hr_context
            try:
                ctx = get_company_hr_context(session.company)
                company_label = ctx["label"]
            except Exception:
                pass

    # Store question and metadata
    session.questions.append(question)
    session.questions_meta.append({
        "category": category,
        "difficulty": difficulty,
        "round_index": session.current_round_index,
        "round_name": current_round.get("name", ""),
        "is_resume_phase": is_resume,
        "company": session.company,
    })

    return {"question": question, "category": category, "difficulty": difficulty,
            "round_info": round_info, "is_resume_phase": is_resume}


def _adapt_difficulty(session: InterviewSession):
    """
    Adapt the question difficulty based on recent performance scores.
    Uses a sliding window of recent scores.
    Difficulty resets to easy at the start of each new round.
    """
    # Need enough data points
    if len(session.recent_scores) < DIFFICULTY_WINDOW:
        return

    # Use only the most recent scores
    recent = session.recent_scores[-DIFFICULTY_WINDOW:]
    avg_score = sum(recent) / len(recent)

    if avg_score >= DIFFICULTY_UP_THRESHOLD and session.current_difficulty < 2:
        # Candidate is doing well — increase difficulty
        session.current_difficulty = min(2, session.current_difficulty + 1)
    elif avg_score <= DIFFICULTY_DOWN_THRESHOLD and session.current_difficulty > 0:
        # Candidate is struggling — decrease difficulty
        session.current_difficulty = max(0, session.current_difficulty - 1)


def _fallback_question(role: str, category: str, difficulty: str) -> str:
    """
    Provide a sensible fallback question when AI generation fails.
    Respects round type (coding/technical/hr).
    """
    fallbacks = {
        "technical": [
            f"Can you walk me through your experience with technologies relevant to a {role} position?",
            f"How do you approach debugging a complex issue in your code?",
            f"Describe your experience with version control and collaboration workflows.",
            f"What's your preferred development setup and why?",
            f"How do you stay updated with the latest technologies in your field?",
        ],
        "coding": [
            f"Can you write a function to check if a string is a palindrome? Walk me through your approach.",
            f"How would you find the two numbers in an array that sum up to a target value?",
            f"Explain the time and space complexity of binary search. When would you use it?",
            f"Write pseudocode to reverse a linked list. What are the edge cases?",
        ],
        "behavioral": [
            f"Tell me about a challenging project you worked on and how you contributed to its success.",
            f"Describe a situation where you had to learn a new technology quickly. How did you approach it?",
            "How do you handle constructive criticism of your work?",
            "Tell me about a time you helped a teammate who was struggling.",
        ],
        "project": [
            f"Tell me about a project you're proud of. What was your specific contribution?",
            f"What was the most technically difficult problem you solved in a recent project?",
            f"How do you approach project planning and task estimation?",
        ],
        "situational": [
            "If you were given a project with a tight deadline and unclear requirements, how would you proceed?",
            "How would you handle a situation where you disagree with a technical decision made by your team?",
        ],
        "experience": [
            f"What attracted you to the {role} role and what experience makes you a good fit?",
            "What's one thing you would change about how your current/previous team works?",
        ],
        "problem-solving": [
            "Describe your approach to breaking down a large, complex problem into manageable pieces.",
            "How do you prioritize tasks when everything seems urgent?",
        ],
        "hr": [
            "Tell me about yourself and your career journey so far.",
            "What are your greatest strengths and areas for development?",
            "Where do you see yourself in 5 years?",
            "Why do you want to leave your current role?",
            "Describe a time you received difficult feedback. How did you handle it?",
        ],
    }

    cat_fallbacks = fallbacks.get(category, fallbacks["technical"])
    return random.choice(cat_fallbacks)


def _handle_aptitude_answer(session, answer, current_round, current_question) -> dict:
    """
    Handle an aptitude MCQ answer submission.
    No AI evaluation needed — deterministic correct/incorrect check.
    Returns a response dict in the same format as the regular submit_answer.
    """
    from aptitude_bank import format_aptitude_answer_record

    try:
        selected_option = int(answer.strip())
    except (ValueError, AttributeError):
        selected_option = -1

    # Get the aptitude question data
    q_idx = session.aptitude_question_index

    # Defensive: auto-load aptitude questions if missing
    if not session.aptitude_questions:
        from aptitude_bank import get_aptitude_set as _load_apt
        q_count = current_round.get("questions", 10)
        session.aptitude_questions = _load_apt(
            num_quant=4, num_logical=4, num_verbal=2,
            company=session.company,
        )
        session.aptitude_question_index = 0
        session.aptitude_correct_count = 0
        session.aptitude_total_count = 0
        q_idx = 0

    if q_idx >= len(session.aptitude_questions):
        return {"error": "Aptitude question index out of range."}

    q_data = session.aptitude_questions[q_idx]
    is_correct = selected_option == q_data["correct"]
    is_valid_option = 0 <= selected_option < len(q_data["options"])

    # Build answer record
    answer_record = format_aptitude_answer_record(q_data, selected_option)
    answer_record["round_name"] = current_round.get("name", "Aptitude Test")
    answer_record["round_number"] = session.current_round_index + 1
    answer_record["selected_option"] = selected_option
    answer_record["is_valid"] = is_valid_option

    session.answers.append(answer_record)
    session.aptitude_total_count += 1
    session.round_question_count += 1
    if is_correct:
        session.aptitude_correct_count += 1

    # Advance question index
    session.aptitude_question_index += 1
    session.current_question_index += 1

    # Check if round is complete
    round_question_limit = current_round.get("questions", 10)
    round_complete = session.round_question_count >= round_question_limit
    is_last_round = session.current_round_index >= len(session.rounds) - 1
    is_complete = round_complete and is_last_round

    # Score for this round
    aptitude_score = round((session.aptitude_correct_count / max(session.aptitude_total_count, 1)) * 10, 1)

    # Build response
    response = {
        "session_id": session.session_id,
        "is_aptitude": True,
        "evaluation": {
            "overall_score": answer_record["overall_score"],
            "selected_option": selected_option,
            "is_correct": is_correct,
            "correct_answer_index": q_data["correct"],
            "correct_answer": q_data["options"][q_data["correct"]],
            "explanation": q_data["explanation"],
            "feedback": "Correct!" if is_correct else f"Incorrect. The correct answer is: {q_data['options'][q_data['correct']]}",
        },
        "aptitude_progress": {
            "correct": session.aptitude_correct_count,
            "total": session.aptitude_total_count,
            "score": aptitude_score,
            "round_score": f"{session.aptitude_correct_count}/{session.aptitude_total_count}",
        },
        "progress": {
            "current": session.current_question_index,
            "total": session.total_questions,
        },
        "round_progress": {
            "current_round": session.current_round_index,
            "total_rounds": len(session.rounds),
            "round_question_count": session.round_question_count,
            "round_question_limit": round_question_limit,
            "round_complete": round_complete,
            "round_name": current_round.get("name", ""),
            "next_round_name": "",
        },
        "is_complete": is_complete,
        "current_round": {
            "name": current_round.get("name", "Aptitude Test"),
            "type": "aptitude",
            "focus": current_round.get("focus", ""),
            "questions": round_question_limit,
        },
        "is_resume_phase": False,
    }

    if is_complete:
        session.status = "completed"
        session.end_time = time.time()
        response["completion"] = {
            "message": "All rounds complete! Generating your comprehensive report...",
            "report_url": f"/report/{session.session_id}",
        }
    elif round_complete and not is_last_round:
        # Round transition
        session.current_round_index += 1
        session.round_question_count = 0

        # Reset difficulty to experience-appropriate baseline for new round
        session.current_difficulty = _experience_to_difficulty(session.candidate_experience)
        session.recent_scores = []

        next_round = session.get_current_round()
        response["round_progress"]["next_round_name"] = next_round.get("name", "")
        response["round_transition"] = {
            "completed_round": current_round.get("name", ""),
            "next_round": next_round.get("name", ""),
            "next_round_focus": next_round.get("focus", ""),
            "message": f"Round {current_round.get('name', 'Aptitude Test')} Complete! "
                       f"Starting: {next_round.get('name', '')}",
        }
        response["current_round"] = {
            "name": next_round.get("name", ""),
            "type": next_round.get("type", ""),
            "focus": next_round.get("focus", ""),
            "questions": next_round.get("questions", 3),
        }

        # Generate next question for new round
        next_q_result = _generate_next_question(session)
        if next_q_result.get("error"):
            response["error"] = next_q_result["error"]
        else:
            response["next_question"] = next_q_result.get("question", "")
            response["difficulty"] = DIFFICULTY_LEVELS[session.current_difficulty]
    else:
        # Same aptitude round — serve next question
        next_q_result = _generate_next_question(session)
        if next_q_result.get("error") or not next_q_result.get("question"):
            # No more aptitude questions — move to next round
            session.current_round_index += 1
            session.round_question_count = 0
            next_round = session.get_current_round()
            response["round_progress"]["round_complete"] = True
            response["round_transition"] = {
                "completed_round": current_round.get("name", "Aptitude Test"),
                "next_round": next_round.get("name", ""),
                "next_round_focus": next_round.get("focus", ""),
                "message": f"Aptitude round complete! Starting: {next_round.get('name', '')}",
            }
            response["current_round"] = {
                "name": next_round.get("name", ""),
                "type": next_round.get("type", ""),
                "focus": next_round.get("focus", ""),
                "questions": next_round.get("questions", 3),
            }
            next_q_result2 = _generate_next_question(session)
            if not next_q_result2.get("error"):
                response["next_question"] = next_q_result2.get("question", "")
                response["difficulty"] = DIFFICULTY_LEVELS[session.current_difficulty]
        else:
            response["next_question"] = next_q_result.get("question", "")
            response["difficulty"] = "medium"

    return response

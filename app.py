"""
AI Interview Intelligence System - Main Application
Flask server with SQLite database for the complete interview platform.
Routes: Registration, Interview, Dashboard, Report, Resume Upload
"""

import os
import sqlite3
import uuid
import json
import time
from datetime import datetime

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.utils import secure_filename

# Local modules
from resume_parser import parse_resume
from interview_engine import (
    start_interview,
    submit_answer,
    rewrite_answer,
    generate_report,
    get_session_state,
    session_store,
)
from ai_service import check_ollama_health
from stt_service import transcribe_audio

# ── Flask App Configuration ───────────────────────────────────────────────────

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()

# Upload configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
ALLOWED_EXTENSIONS = {"pdf", "docx"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max upload

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Database configuration
DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.db")


# ── Database Setup ────────────────────────────────────────────────────────────

def get_db():
    """Get a database connection with row factory for dict-like access."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """
    Initialize the SQLite database with all required tables.
    Creates tables if they don't exist.
    """
    conn = get_db()
    cursor = conn.cursor()

    # Candidates table: stores registered user profiles
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            role TEXT NOT NULL,
            experience TEXT DEFAULT '0',
            resume_filename TEXT,
            resume_text TEXT,
            skills TEXT DEFAULT '[]',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Interview sessions table: tracks each interview session
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            candidate_id INTEGER NOT NULL,
            mode TEXT NOT NULL CHECK(mode IN ('hr', 'technical')),
            status TEXT DEFAULT 'in_progress' CHECK(status IN ('waiting', 'in_progress', 'completed')),
            overall_score REAL DEFAULT 0,
            technical_score REAL DEFAULT 0,
            communication_score REAL DEFAULT 0,
            confidence_score REAL DEFAULT 0,
            total_questions INTEGER DEFAULT 0,
            completed_questions INTEGER DEFAULT 0,
            duration_seconds REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            FOREIGN KEY (candidate_id) REFERENCES candidates(id)
        )
    """)

    # Answers table: stores each Q&A pair with evaluation
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            category TEXT DEFAULT 'general',
            difficulty TEXT DEFAULT 'medium',
            overall_score INTEGER DEFAULT 5,
            technical_score INTEGER DEFAULT 5,
            communication_score INTEGER DEFAULT 5,
            confidence_score INTEGER DEFAULT 5,
            feedback TEXT DEFAULT '',
            improved_answer TEXT DEFAULT '',
            score_explanation TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
    """)

    # Skill gaps table: detected skill gaps per session
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS skill_gaps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            skill TEXT NOT NULL,
            level TEXT DEFAULT 'intermediate',
            gap_description TEXT DEFAULT '',
            recommendation TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
    """)

    # Recommendations table: learning recommendations per session
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            area TEXT NOT NULL,
            resource_type TEXT DEFAULT 'Learning Path',
            description TEXT DEFAULT '',
            priority TEXT DEFAULT 'medium',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
    """)

    conn.commit()

    # ── Safe column migrations ────────────────────────────────────────────
    _add_column_if_not_exists(cursor, "answers", "problem_solving_score", "INTEGER DEFAULT 5")
    _add_column_if_not_exists(cursor, "answers", "time_management_score", "INTEGER DEFAULT 5")
    _add_column_if_not_exists(cursor, "answers", "conceptual_clarity_score", "INTEGER DEFAULT 5")
    _add_column_if_not_exists(cursor, "answers", "strengths", "TEXT DEFAULT '[]'")
    _add_column_if_not_exists(cursor, "answers", "weaknesses", "TEXT DEFAULT '[]'")
    _add_column_if_not_exists(cursor, "answers", "ideal_answer", "TEXT DEFAULT ''")
    _add_column_if_not_exists(cursor, "answers", "improvement_tip", "TEXT DEFAULT ''")
    _add_column_if_not_exists(cursor, "answers", "keywords_used", "TEXT DEFAULT '[]'")
    _add_column_if_not_exists(cursor, "answers", "keywords_missed", "TEXT DEFAULT '[]'")
    _add_column_if_not_exists(cursor, "sessions", "problem_solving_score", "REAL DEFAULT 0")
    _add_column_if_not_exists(cursor, "sessions", "time_management_score", "REAL DEFAULT 0")
    _add_column_if_not_exists(cursor, "sessions", "conceptual_clarity_score", "REAL DEFAULT 0")
    _add_column_if_not_exists(cursor, "sessions", "readiness_score", "INTEGER DEFAULT 0")
    _add_column_if_not_exists(cursor, "sessions", "grade", "TEXT DEFAULT ''")
    _add_column_if_not_exists(cursor, "sessions", "star_rating", "INTEGER DEFAULT 0")

    # ── Multi-round migration ──────────────────────────────────────────
    _add_column_if_not_exists(cursor, "sessions", "rounds_data", "TEXT DEFAULT '[]'")
    _add_column_if_not_exists(cursor, "sessions", "current_round", "INTEGER DEFAULT 0")
    _add_column_if_not_exists(cursor, "sessions", "total_rounds", "INTEGER DEFAULT 1")
    _add_column_if_not_exists(cursor, "answers", "round_name", "TEXT DEFAULT ''")
    _add_column_if_not_exists(cursor, "answers", "round_number", "INTEGER DEFAULT 0")

    # ── Aptitude/MCQ migration ───────────────────────────────────────
    _add_column_if_not_exists(cursor, "answers", "is_mcq", "BOOLEAN DEFAULT 0")
    _add_column_if_not_exists(cursor, "answers", "selected_option", "INTEGER")
    _add_column_if_not_exists(cursor, "answers", "is_correct", "BOOLEAN")
    _add_column_if_not_exists(cursor, "answers", "correct_option", "INTEGER")
    _add_column_if_not_exists(cursor, "answers", "correct_answer", "TEXT DEFAULT ''")
    _add_column_if_not_exists(cursor, "answers", "explanation", "TEXT DEFAULT ''")

    conn.commit()
    conn.close()


def _add_column_if_not_exists(cursor, table: str, column: str, col_type: str):
    """Safely add a column to a table if it doesn't already exist."""
    try:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
    except Exception:
        pass


# ── Helper Functions ──────────────────────────────────────────────────────────

def allowed_file(filename: str) -> bool:
    """Check if uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_candidate_to_db(name: str, email: str, role: str, experience: str,
                         resume_filename: str = None, resume_text: str = "",
                         skills: list = None) -> int:
    """
    Insert or update a candidate record in the database.
    Returns the candidate ID.
    """
    conn = get_db()
    cursor = conn.cursor()
    skills_json = json.dumps(skills or [])

    # Check if candidate already exists by email
    existing = cursor.execute(
        "SELECT id FROM candidates WHERE email = ?", (email,)
    ).fetchone()

    if existing:
        # Update existing record
        cursor.execute("""
            UPDATE candidates
            SET name = ?, role = ?, experience = ?, resume_filename = ?,
                resume_text = ?, skills = ?
            WHERE id = ?
        """, (name, role, experience, resume_filename, resume_text, skills_json, existing["id"]))
        candidate_id = existing["id"]
    else:
        # Insert new candidate
        cursor.execute("""
            INSERT INTO candidates (name, email, role, experience, resume_filename, resume_text, skills)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, email, role, experience, resume_filename, resume_text, skills_json))
        candidate_id = cursor.lastrowid

    conn.commit()
    conn.close()
    return candidate_id


def save_session_to_db(session_data: dict):
    """Save or update interview session data to database."""
    conn = get_db()
    cursor = conn.cursor()

    # Upsert session record
    cursor.execute("""
        INSERT OR REPLACE INTO sessions
            (id, candidate_id, mode, status, overall_score, technical_score,
             communication_score, confidence_score, problem_solving_score,
             time_management_score, conceptual_clarity_score,
             readiness_score, grade, star_rating,
             total_questions, completed_questions, duration_seconds, completed_at,
             rounds_data, current_round, total_rounds)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        session_data.get("session_id"),
        session_data.get("candidate_id"),
        session_data.get("mode"),
        session_data.get("status"),
        session_data.get("overall_score", 0),
        session_data.get("technical_score", 0),
        session_data.get("communication_score", 0),
        session_data.get("confidence_score", 0),
        session_data.get("problem_solving_score", 0),
        session_data.get("time_management_score", 0),
        session_data.get("conceptual_clarity_score", 0),
        session_data.get("readiness_score", 0),
        session_data.get("grade", ""),
        session_data.get("star_rating", 0),
        session_data.get("total_questions", 0),
        session_data.get("completed_questions", 0),
        session_data.get("duration_seconds", 0),
        datetime.now().isoformat() if session_data.get("status") == "completed" else None,
        json.dumps(session_data.get("rounds", [])),
        session_data.get("current_round", 0),
        session_data.get("total_rounds", 1),
    ))

    conn.commit()
    conn.close()


def save_answers_to_db(session_id: str, answers: list):
    """Save all answers for a session to the database (with new score columns)."""
    if not answers:
        return

    conn = get_db()
    cursor = conn.cursor()

    for ans in answers:
        cursor.execute("""
            INSERT INTO answers
                (session_id, question, answer, category, difficulty,
                 overall_score, technical_score, communication_score,
                 confidence_score, problem_solving_score,
                 time_management_score, conceptual_clarity_score,
                 feedback, improved_answer, ideal_answer, improvement_tip,
                 score_explanation, strengths, weaknesses,
                 keywords_used, keywords_missed,
                 round_name, round_number,
                 is_mcq, selected_option, is_correct, correct_option, correct_answer, explanation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id,
            ans.get("question", ""),
            ans.get("answer", ""),
            ans.get("category", "general"),
            ans.get("difficulty", "medium"),
            ans.get("overall_score", 5),
            ans.get("technical_score", 5),
            ans.get("communication_score", 5),
            ans.get("confidence_score", 5),
            ans.get("problem_solving_score", 5),
            ans.get("time_management_score", 5),
            ans.get("conceptual_clarity_score", 5),
            ans.get("feedback", ""),
            ans.get("improved_answer", ""),
            ans.get("ideal_answer", ""),
            ans.get("improvement_tip", ""),
            ans.get("score_explanation", ""),
            json.dumps(ans.get("strengths", [])),
            json.dumps(ans.get("weaknesses", [])),
            json.dumps(ans.get("keywords_used", [])),
            json.dumps(ans.get("keywords_missed", [])),
            ans.get("round_name", ""),
            ans.get("round_number", 0),
            # MCQ fields
            1 if ans.get("is_mcq") else 0,
            ans.get("selected_option"),
            1 if ans.get("is_correct") else 0,
            ans.get("correct_option"),
            ans.get("correct_answer", ""),
            ans.get("explanation", ""),
        ))

    conn.commit()
    conn.close()


def save_skill_gaps_to_db(session_id: str, skill_gaps: list):
    """Save skill gaps to database."""
    if not skill_gaps:
        return

    conn = get_db()
    cursor = conn.cursor()

    for gap in skill_gaps:
        cursor.execute("""
            INSERT INTO skill_gaps (session_id, skill, level, gap_description, recommendation)
            VALUES (?, ?, ?, ?, ?)
        """, (
            session_id,
            gap.get("skill", ""),
            gap.get("level", "intermediate"),
            gap.get("gap", ""),
            gap.get("recommendation", ""),
        ))

    conn.commit()
    conn.close()


def get_candidate_history(candidate_id: int) -> dict:
    """Get all sessions and aggregate stats for a candidate."""
    conn = get_db()
    cursor = conn.cursor()

    # Get candidate info
    candidate = cursor.execute(
        "SELECT * FROM candidates WHERE id = ?", (candidate_id,)
    ).fetchone()

    if not candidate:
        conn.close()
        return None

    # Get all completed sessions with scores
    sessions = cursor.execute("""
        SELECT * FROM sessions
        WHERE candidate_id = ? AND status = 'completed'
        ORDER BY created_at DESC
    """, (candidate_id,)).fetchall()

    # Get all answers across all sessions
    session_ids = [s["id"] for s in sessions]
    all_answers = []
    if session_ids:
        placeholders = ",".join("?" * len(session_ids))
        all_answers = cursor.execute(f"""
            SELECT * FROM answers
            WHERE session_id IN ({placeholders})
            ORDER BY created_at DESC
        """, session_ids).fetchall()

    # Calculate aggregate stats
    total_sessions = len(sessions)
    total_answers = len(all_answers)

    avg_overall = 0
    avg_technical = 0
    avg_communication = 0
    avg_confidence = 0

    if all_answers:
        scores = [a["overall_score"] for a in all_answers if a["overall_score"]]
        tech_scores = [a["technical_score"] for a in all_answers if a["technical_score"]]
        comm_scores = [a["communication_score"] for a in all_answers if a["communication_score"]]
        conf_scores = [a["confidence_score"] for a in all_answers if a["confidence_score"]]

        if scores:
            avg_overall = round(sum(scores) / len(scores), 1)
        if tech_scores:
            avg_technical = round(sum(tech_scores) / len(tech_scores), 1)
        if comm_scores:
            avg_communication = round(sum(comm_scores) / len(comm_scores), 1)
        if conf_scores:
            avg_confidence = round(sum(conf_scores) / len(conf_scores), 1)

    conn.close()

    return {
        "candidate": dict(candidate) if candidate else None,
        "total_sessions": total_sessions,
        "total_answers": total_answers,
        "avg_overall": avg_overall,
        "avg_technical": avg_technical,
        "avg_communication": avg_communication,
        "avg_confidence": avg_confidence,
        "sessions": [dict(s) for s in sessions],
        "recent_answers": [dict(a) for a in all_answers[:20]],
    }


# ── Routes ────────────────────────────────────────────────────────────────────


@app.route("/")
def index():
    """Home/Registration page."""
    return render_template("index.html")


@app.route("/register", methods=["POST"])
def register():
    """
    Handle candidate registration form submission.
    Saves candidate info and optionally parses uploaded resume.
    """
    try:
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        role = request.form.get("role", "").strip()
        experience = request.form.get("experience", "0").strip()

        # Validate required fields
        if not all([name, email, role]):
            return jsonify({"error": "Name, email, and role are required."}), 400

        resume_text = ""
        skills = []
        resume_filename = None

        # Handle resume upload
        if "resume" in request.files:
            file = request.files["resume"]
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = str(int(time.time()))
                unique_filename = f"{timestamp}_{filename}"
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
                file.save(filepath)

                # Parse the resume
                parse_result = parse_resume(filepath)
                if parse_result["success"]:
                    resume_text = parse_result["text"]
                    skills = parse_result["skills"]
                    resume_filename = unique_filename

                    # Use parsed name if form name is generic
                    if parse_result.get("name") and name.lower() in ["", "candidate"]:
                        name = parse_result["name"]

        # Save candidate to database
        candidate_id = save_candidate_to_db(
            name=name,
            email=email,
            role=role,
            experience=experience,
            resume_filename=resume_filename,
            resume_text=resume_text,
            skills=skills,
        )

        # Store candidate info in session for interview flow
        session["candidate_id"] = candidate_id
        session["candidate_name"] = name
        session["candidate_email"] = email
        session["candidate_role"] = role
        session["candidate_experience"] = experience
        session["candidate_skills"] = skills
        session["candidate_company"] = request.form.get("company", "General")
        session["resume_text"] = resume_text[:5000]  # Truncate for session storage

        return jsonify({
            "success": True,
            "candidate_id": candidate_id,
            "name": name,
            "skills_found": len(skills),
            "skills": skills[:20],  # Top 20 skills for display
            "message": f"Registered successfully! {len(skills)} skills identified from resume."
        })

    except Exception as e:
        return jsonify({"error": f"Registration failed: {str(e)}"}), 500


@app.route("/interview")
def interview_page():
    """Interview chat interface page."""
    if not session.get("candidate_id"):
        return redirect(url_for("index"))

    mode = request.args.get("mode", "technical")
    return render_template("interview.html",
                           candidate_name=session.get("candidate_name", "Candidate"),
                           candidate_role=session.get("candidate_role", ""),
                           mode=mode)


@app.route("/api/start_interview", methods=["POST"])
def api_start_interview():
    """API endpoint to start a new interview session."""
    try:
        if not session.get("candidate_id"):
            return jsonify({"error": "Please register first."}), 401

        data = request.get_json() or {}
        mode = data.get("mode", "technical")
        total_questions = data.get("total_questions", None)  # None = auto from rounds

        # Get company from session or default
        company = session.get("candidate_company", "General")

        # Generate a unique session ID
        session_id = str(uuid.uuid4())[:8]

        result = start_interview(
            session_id=session_id,
            candidate_id=session["candidate_id"],
            candidate_name=session.get("candidate_name", "Candidate"),
            candidate_role=session.get("candidate_role", ""),
            candidate_experience=session.get("candidate_experience", "0"),
            candidate_skills=session.get("candidate_skills", []),
            resume_text=session.get("resume_text", ""),
            mode=mode,
            total_questions=total_questions,
            company=company,
        )

        if "error" in result:
            return jsonify(result), 500

        # Save session_id to Flask session
        session["current_session_id"] = session_id

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Start interview failed: {str(e)}"}), 500


@app.route("/api/submit_answer", methods=["POST"])
def api_submit_answer():
    """API endpoint to submit an answer and get evaluation + next question."""
    try:
        if not session.get("current_session_id"):
            return jsonify({"error": "No active interview session."}), 401

        data = request.get_json() or {}
        answer = data.get("answer", "").strip()

        if not answer:
            return jsonify({"error": "Answer cannot be empty."}), 400

        result = submit_answer(session["current_session_id"], answer)

        if "error" in result:
            return jsonify(result), 500

        # If interview is complete, save all data to database
        if result.get("is_complete"):
            _persist_session_to_db(session["current_session_id"])

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Submit answer failed: {str(e)}"}), 500


@app.route("/api/rewrite_answer", methods=["POST"])
def api_rewrite_answer():
    """
    API endpoint to submit a rewritten answer for re-evaluation.
    Input: {answer_index: int, rewritten_answer: str}
    Returns: original scores, rewrite scores, improvement delta, and updated evaluation.
    """
    try:
        if not session.get("current_session_id"):
            return jsonify({"error": "No active interview session."}), 401

        data = request.get_json() or {}
        answer_index = data.get("answer_index", -1)
        rewritten_answer = data.get("rewritten_answer", "").strip()

        if answer_index < 0:
            return jsonify({"error": "Invalid answer_index."}), 400
        if not rewritten_answer:
            return jsonify({"error": "Rewritten answer cannot be empty."}), 400

        result = rewrite_answer(session["current_session_id"], answer_index, rewritten_answer)

        if "error" in result:
            return jsonify(result), 500

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Rewrite failed: {str(e)}"}), 500


@app.route("/api/submit_aptitude_answer", methods=["POST"])
def api_submit_aptitude_answer():
    """
    API endpoint to submit an aptitude MCQ answer.
    Uses the same submit_answer engine (which detects aptitude round type).
    Input: {selected_option_index: int}
    Returns: deterministic correct/incorrect + next question
    """
    try:
        if not session.get("current_session_id"):
            return jsonify({"error": "No active interview session."}), 401

        data = request.get_json() or {}
        selected_option = data.get("selected_option_index", -1)

        try:
            selected_option = int(selected_option)
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid option selected."}), 400

        result = submit_answer(
            session["current_session_id"],
            str(selected_option)
        )

        if "error" in result:
            return jsonify(result), 500

        # If interview is complete, save all data to database
        if result.get("is_complete"):
            _persist_session_to_db(session["current_session_id"])

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Submit aptitude answer failed: {str(e)}"}), 500


@app.route("/api/session_state")
def api_session_state():
    """API endpoint to get current session state."""
    sid = session.get("current_session_id")
    if not sid:
        return jsonify({"error": "No active session"}), 401

    state = get_session_state(sid)
    if "error" in state:
        return jsonify(state), 404

    return jsonify(state)


@app.route("/api/ollama_status")
def api_ollama_status():
    """API endpoint to check Ollama connection status."""
    status = check_ollama_health()
    return jsonify(status)


@app.route("/api/transcribe", methods=["POST"])
def api_transcribe():
    """
    API endpoint to transcribe uploaded audio using local Whisper.
    Accepts multipart audio in any format supported by ffmpeg.
    Returns: {transcript, filler_words, filler_count, language}
    """
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided. Use multipart field 'audio'."}), 400

    file = request.files["audio"]
    if not file or not file.filename:
        return jsonify({"error": "Empty audio file."}), 400

    # Determine file extension from the uploaded filename or content type
    filename = secure_filename(file.filename) if file.filename else "audio.webm"
    ext = os.path.splitext(filename)[1].lower() or ".webm"

    try:
        audio_bytes = file.read()
    except Exception as e:
        return jsonify({"error": f"Could not read audio: {str(e)}"}), 400

    # Transcribe using local Whisper + filler detection
    result = transcribe_audio(audio_bytes, ext)

    if result.get("error") and not result.get("text"):
        return jsonify({
            "error": result["error"],
            "transcript": "",
            "filler_words": {},
            "filler_count": 0,
        }), 500

    return jsonify({
        "transcript": result.get("text", ""),
        "filler_words": result.get("filler_words", {}),
        "filler_count": result.get("filler_word_count", 0),
        "language": result.get("language", "en"),
    })


@app.route("/report/<session_id>")
def report_page(session_id: str):
    """Final interview report page."""
    report = generate_report(session_id)

    if "error" in report:
        return f"Report error: {report['error']}", 404

    # Ensure data is persisted
    _persist_session_to_db(session_id, report)

    return render_template("report.html", report=report)


@app.route("/api/report/<session_id>")
def api_report(session_id: str):
    """API endpoint to get report data as JSON."""
    report = generate_report(session_id)
    if "error" in report:
        return jsonify(report), 404
    return jsonify(report)


@app.route("/dashboard")
def dashboard_page():
    """Analytics dashboard page."""
    if not session.get("candidate_id"):
        return redirect(url_for("index"))

    candidate_id = session["candidate_id"]
    history = get_candidate_history(candidate_id)

    if not history:
        return render_template("dashboard.html", data=None)

    return render_template("dashboard.html", data=history)


@app.route("/api/dashboard/<int:candidate_id>")
def api_dashboard(candidate_id: int):
    """API endpoint to get dashboard data as JSON."""
    history = get_candidate_history(candidate_id)
    if not history:
        return jsonify({"error": "Candidate not found"}), 404
    return jsonify(history)


@app.route("/api/candidates")
def api_candidates():
    """List all candidates for debugging/admin."""
    conn = get_db()
    candidates = conn.execute(
        "SELECT id, name, email, role, experience, created_at FROM candidates ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return jsonify([dict(c) for c in candidates])


@app.route("/api/progress/<int:candidate_id>")
def api_progress(candidate_id: int):
    """Return score progress data for Chart.js dashboard charts."""
    conn = get_db()
    cursor = conn.cursor()
    sessions = cursor.execute("""
        SELECT id, created_at, overall_score, technical_score,
               communication_score, confidence_score, problem_solving_score,
               time_management_score, conceptual_clarity_score,
               readiness_score, grade, star_rating, mode
        FROM sessions
        WHERE candidate_id = ? AND status = 'completed'
        ORDER BY created_at ASC
    """, (candidate_id,)).fetchall()
    conn.close()

    labels = []
    datasets = {
        "overall": [], "technical": [], "communication": [],
        "confidence": [], "problem_solving": [], "time_management": [],
        "conceptual_clarity": [],
    }
    for s in sessions:
        d = dict(s)
        label = d.get("created_at", "")
        if label:
            label = label[:10]  # YYYY-MM-DD
        labels.append(label)
        datasets["overall"].append(d.get("overall_score", 0))
        datasets["technical"].append(d.get("technical_score", 0))
        datasets["communication"].append(d.get("communication_score", 0))
        datasets["confidence"].append(d.get("confidence_score", 0))
        datasets["problem_solving"].append(d.get("problem_solving_score", 0))
        datasets["time_management"].append(d.get("time_management_score", 0))
        datasets["conceptual_clarity"].append(d.get("conceptual_clarity_score", 0))

    return jsonify({
        "labels": labels,
        "datasets": datasets,
        "sessions": [dict(s) for s in sessions],
        "total_sessions": len(sessions),
    })


@app.route("/api/compare/<int:candidate_id>")
def api_compare(candidate_id: int):
    """Return comparison data across sessions for the dashboard."""
    conn = get_db()
    cursor = conn.cursor()

    # All completed sessions ordered by date
    sessions = cursor.execute("""
        SELECT id, created_at, overall_score, technical_score,
               communication_score, confidence_score, readiness_score,
               grade, star_rating, total_questions, completed_questions, mode
        FROM sessions
        WHERE candidate_id = ? AND status = 'completed'
        ORDER BY created_at DESC
    """, (candidate_id,)).fetchall()

    # Get candidate info
    candidate = cursor.execute(
        "SELECT name, role FROM candidates WHERE id = ?", (candidate_id,)
    ).fetchone()
    conn.close()

    if not sessions:
        return jsonify({"error": "No sessions found"}), 404

    session_list = [dict(s) for s in sessions]
    scores_only = [s.get("overall_score", 0) for s in session_list if s.get("overall_score")]

    # Best session
    best = max(session_list, key=lambda s: s.get("overall_score", 0)) if session_list else {}

    # Improvement calculation
    improvement = 0
    if len(scores_only) >= 2:
        improvement = round(scores_only[0] - scores_only[1], 1)  # last - second-to-last

    # Consistency (lower std dev = more consistent)
    consistency = 0
    if scores_only:
        avg = sum(scores_only) / len(scores_only)
        variance = sum((s - avg) ** 2 for s in scores_only) / len(scores_only)
        consistency = round(max(0, 10 - (variance ** 0.5) * 2), 1)

    # Percentile calculation (vs all candidates)
    all_scores = cursor.execute("""
        SELECT overall_score FROM sessions WHERE status = 'completed'
    """).fetchall()
    all_vals = [s["overall_score"] for s in all_scores if s["overall_score"]]
    percentile = 50
    if all_vals and scores_only:
        latest = scores_only[0]
        below = sum(1 for v in all_vals if v < latest)
        percentile = round((below / len(all_vals)) * 100)

    return jsonify({
        "sessions": session_list,
        "total_sessions": len(session_list),
        "best_session": {
            "id": best.get("id"),
            "score": best.get("overall_score", 0),
            "date": str(best.get("created_at", ""))[:10],
            "mode": best.get("mode", ""),
        },
        "improvement": improvement,
        "consistency": consistency,
        "percentile": percentile,
        "trend": "improving" if improvement > 0.5 else ("declining" if improvement < -0.5 else "stable"),
    })


# ── Internal Helpers ──────────────────────────────────────────────────────────

def _persist_session_to_db(session_id: str, report: dict = None):
    """Save session, answers, skill gaps, and recommendations to the database."""
    try:
        if report is None:
            report = generate_report(session_id)

        if "error" in report:
            return

        # Save session record
        session_data = {
            "session_id": session_id,
            "candidate_id": session.get("candidate_id"),
            "mode": report.get("session_data", {}).get("mode", "technical"),
            "status": "completed",
            "overall_score": report.get("overall_score", 0),
            "technical_score": report.get("technical_score", 0),
            "communication_score": report.get("communication_score", 0),
            "confidence_score": report.get("confidence_score", 0),
            "problem_solving_score": report.get("problem_solving_score", 0),
            "time_management_score": report.get("time_management_score", 0),
            "conceptual_clarity_score": report.get("conceptual_clarity_score", 0),
            "readiness_score": report.get("readiness_score", 0),
            "grade": report.get("grade", ""),
            "star_rating": report.get("star_rating", 0),
            "total_questions": report.get("total_questions", 0),
            "completed_questions": len(report.get("answers", [])),
            "duration_seconds": report.get("session_data", {}).get("duration", 0),
            # Round data
            "rounds": report.get("session_data", {}).get("rounds", []),
            "current_round": len(report.get("session_data", {}).get("rounds", [])),
            "total_rounds": len(report.get("session_data", {}).get("rounds", [])),
        }
        save_session_to_db(session_data)

        # Save answers
        save_answers_to_db(session_id, report.get("answers", []))

        # Save skill gaps
        save_skill_gaps_to_db(session_id, report.get("skill_gaps", []))

        # Save recommendations
        conn = get_db()
        cursor = conn.cursor()
        for rec in report.get("recommendations", []):
            cursor.execute("""
                INSERT INTO recommendations (session_id, area, resource_type, description, priority)
                VALUES (?, ?, ?, ?, ?)
            """, (
                session_id,
                rec.get("area", ""),
                rec.get("resource_type", "Learning Path"),
                rec.get("description", ""),
                rec.get("priority", "medium"),
            ))
        conn.commit()
        conn.close()

    except Exception as e:
        print(f"Warning: Failed to persist session data: {e}")


# ── Application Entry Point ───────────────────────────────────────────────────

if __name__ == "__main__":
    # Initialize database on startup
    init_db()
    print("=" * 60)
    print("  AI Interview Intelligence System")
    print("  Database initialized: database.db")
    print("=" * 60)
    print()
    print("  Server: http://127.0.0.1:5050")
    print("  Register: http://127.0.0.1:5050/")
    print()
    print("  Make sure Ollama is running:")
    print("  $ ollama serve")
    print(f"  $ ollama pull llama3.2:latest")
    print()
    app.run(host="127.0.0.1", port=5050, debug=True, use_reloader=False)

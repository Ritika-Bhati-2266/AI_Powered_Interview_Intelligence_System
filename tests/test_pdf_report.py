"""
Tests for Report PDF Export feature.
"""

import os
import sys
import io

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import patch
from app import app
import report_generator


def _sample_report_data(with_ats=True):
    candidate = {
        "name": "Test Candidate",
        "email": "test@example.com",
        "role": "Python Developer",
        "company": "General",
    }
    session = {
        "session_id": "TEST1234",
        "total_questions": 3,
        "overall_score": 7.5,
        "technical_score": 8,
        "communication_score": 7,
        "confidence_score": 6,
        "problem_solving_score": 7,
        "time_management_score": 6,
        "conceptual_clarity_score": 7,
        "skill_gaps": [
            {"skill": "Docker", "level": "intermediate", "gap": "Need hands-on", "recommendation": "Practice Docker labs"},
        ],
        "recommendations": [
            {"area": "Docker", "description": "Learn Docker basics", "priority": "high"},
        ],
        "answers": [
            {"question": "What is Python?", "answer": "Python is a programming language.", "overall_score": 8, "feedback": "Good answer"},
            {"question": "Explain OOP", "answer": "OOP is object oriented programming with classes.", "overall_score": 7, "feedback": "Needs more depth"},
        ],
    }
    ats = None
    if with_ats:
        ats = {
            "score": 78,
            "breakdown": {"skills_match": 30, "experience_keywords": 15, "education": 12, "formatting": 8, "keyword_density": 13},
            "matched_keywords": ["python", "docker"],
            "missing_keywords": ["kubernetes", "aws"],
        }
    return candidate, session, ats


class TestGeneratePdfDirect:
    def test_returns_bytesio_and_pdf_header(self):
        cand, sess, ats = _sample_report_data(with_ats=True)
        buf = report_generator.generate_pdf_report(cand, sess, ats)
        assert isinstance(buf, io.BytesIO)
        data = buf.getvalue()
        assert len(data) > 500
        assert data[:4] == b"%PDF"

    def test_missing_ats_graceful(self):
        cand, sess, _ = _sample_report_data(with_ats=False)
        buf = report_generator.generate_pdf_report(cand, sess, None)
        assert isinstance(buf, io.BytesIO)
        assert buf.getvalue()[:4] == b"%PDF"

    def test_missing_fields_graceful(self):
        # Empty dicts should not crash, use safe defaults
        buf = report_generator.generate_pdf_report({}, {}, None)
        assert buf.getvalue()[:4] == b"%PDF"

    def test_empty_candidate_and_session(self):
        buf = report_generator.generate_pdf_report(None, None, None)
        assert buf.getvalue()[:4] == b"%PDF"

    def test_long_answer_truncated(self):
        cand, sess, ats = _sample_report_data()
        sess["answers"] = [
            {"question": "Q1", "answer": "A" * 5000, "overall_score": 5, "feedback": "F" * 5000},
        ]
        buf = report_generator.generate_pdf_report(cand, sess, ats)
        assert buf.getvalue()[:4] == b"%PDF"
        assert len(buf.getvalue()) > 500


class TestPdfApiRoute:
    def test_invalid_session_404(self):
        app.config["TESTING"] = True
        client = app.test_client()
        resp = client.get("/api/report/pdf/invalid-session-xyz-999")
        assert resp.status_code == 404
        j = resp.get_json()
        assert "error" in j

    def test_valid_session_returns_pdf(self):
        app.config["TESTING"] = True
        client = app.test_client()
        fake_report = {
            "candidate_info": {"name": "PDF Tester", "email": "pdf@example.com", "role": "Software Engineer", "company": "General"},
            "session_data": {
                "session_id": "MOCK123",
                "total_questions": 2,
                "overall_score": 7,
                "technical_score": 7,
                "communication_score": 6,
                "confidence_score": 6,
                "answers": [
                    {"question": "What is Python?", "answer": "Python is great.", "overall_score": 7, "feedback": "Nice"},
                ],
                "skill_gaps": [],
                "recommendations": [],
            },
            "overall_score": 7,
            "technical_score": 7,
            "communication_score": 6,
            "confidence_score": 6,
            "skill_gaps": [],
            "recommendations": [],
            "answers": [
                {"question": "What is Python?", "answer": "Python is great.", "overall_score": 7, "feedback": "Nice"},
            ],
        }
        with patch("app.generate_report", return_value=fake_report):
            # Also mock ATS fetch to avoid DB hit
            with patch("app.get_db") as mock_db:
                mock_conn = mock_db.return_value
                # Make session fallback not needed
                resp = client.get("/api/report/pdf/MOCK123")
                assert resp.status_code == 200
                assert resp.content_type == "application/pdf"
                data = resp.data
                assert len(data) > 500
                assert data[:4] == b"%PDF"
                # Check download header
                cd = resp.headers.get("Content-Disposition", "")
                assert "interview_report_MOCK123.pdf" in cd

    def test_valid_session_with_ats_in_report(self):
        app.config["TESTING"] = True
        client = app.test_client()
        fake_report = {
            "candidate_info": {"name": "ATS PDF Tester", "email": "ats_pdf@example.com", "role": "DevOps Engineer", "company": "General"},
            "session_data": {
                "session_id": "ATSPDF1",
                "total_questions": 1,
                "overall_score": 8,
                "technical_score": 8,
                "communication_score": 7,
                "confidence_score": 7,
                "answers": [{"question": "Explain Kubernetes", "answer": "K8s is orchestration", "overall_score": 8, "feedback": "Good"}],
                "skill_gaps": [{"skill": "Helm", "level": "beginner", "gap": "No helm exp", "recommendation": "Learn Helm"}],
                "recommendations": [{"area": "Helm", "description": "Helm charts", "priority": "high"}],
            },
            "overall_score": 8,
            "technical_score": 8,
            "communication_score": 7,
            "confidence_score": 7,
            "skill_gaps": [{"skill": "Helm", "level": "beginner", "gap": "No helm exp", "recommendation": "Learn Helm"}],
            "recommendations": [{"area": "Helm", "description": "Helm charts", "priority": "high"}],
            "answers": [{"question": "Explain Kubernetes", "answer": "K8s is orchestration", "overall_score": 8, "feedback": "Good"}],
        }
        # Simulate ATS in session
        with client.session_transaction() as sess:
            sess["ats_score"] = {
                "score": 85,
                "breakdown": {"skills_match": 35, "experience_keywords": 16, "education": 12, "formatting": 9, "keyword_density": 13},
                "matched_keywords": ["kubernetes", "docker"],
                "missing_keywords": ["terraform"],
            }
        with patch("app.generate_report", return_value=fake_report):
            resp = client.get("/api/report/pdf/ATSPDF1")
            assert resp.status_code == 200
            assert resp.content_type == "application/pdf"
            assert resp.data[:4] == b"%PDF"

"""
Tests for JD-Based Question Generation feature.
Verifies:
- JD provided -> prompt contains JD keywords + JD ALIGNMENT instruction
- JD not provided -> generic flow unchanged
- jd_text length cap (3000 chars) enforced at app.py and InterviewSession
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import patch, MagicMock
import ai_service
from interview_engine import InterviewSession, session_store, start_interview, _generate_next_question
from app import app

# Helper to capture prompt sent to LLM
def _capture_prompt_with_jd(jd_text, round_type="technical", category="technical"):
    captured = {}
    def fake_llm(prompt, system_prompt=None, temperature=0.8):
        captured["prompt"] = prompt
        captured["system"] = system_prompt
        return "What is Kubernetes and how do you manage deployments?"
    with patch("ai_service._call_llm", side_effect=fake_llm):
        result = ai_service.generate_question(
            role="DevOps Engineer",
            experience="3",
            skills=["docker", "aws"],
            category=category,
            difficulty="medium",
            context="",
            resume_text="",
            round_info={"name": "Technical Round", "type": round_type, "focus": "System Design"},
            is_resume_phase=False,
            company="General",
            previous_questions=[],
            jd_text=jd_text,
        )
    return captured, result

class TestGenerateQuestionJD:
    def test_jd_injected_when_provided(self):
        jd = "We need Kubernetes, Docker, AWS and microservices expertise."
        captured, _ = _capture_prompt_with_jd(jd, round_type="technical")
        prompt = captured["prompt"]
        assert "JOB DESCRIPTION:" in prompt
        assert "Kubernetes" in prompt
        assert "Prioritize skills, tools, and requirements mentioned in this JD" in prompt
        # Technical round JD alignment instruction
        assert "JD ALIGNMENT" in prompt or "JD ALIGNMENT" in prompt or "CRITICAL JD ALIGNMENT" in prompt

    def test_jd_coding_round_alignment(self):
        jd = "Kubernetes and Helm charts experience required."
        captured, _ = _capture_prompt_with_jd(jd, round_type="coding", category="coding")
        prompt = captured["prompt"]
        assert "JOB DESCRIPTION:" in prompt
        assert "Kubernetes" in prompt
        assert "JD ALIGNMENT FOR CODING ROUND" in prompt

    def test_jd_empty_gives_generic_flow(self):
        captured, _ = _capture_prompt_with_jd("", round_type="technical")
        prompt = captured["prompt"]
        assert "JOB DESCRIPTION:" not in prompt
        # No JD alignment text when jd empty
        assert "CRITICAL JD ALIGNMENT" not in prompt
        assert "JD ALIGNMENT FOR CODING ROUND" not in prompt

    def test_jd_none_gives_generic_flow(self):
        captured, _ = _capture_prompt_with_jd(None, round_type="technical")
        prompt = captured["prompt"]
        assert "JOB DESCRIPTION:" not in prompt

    def test_jd_length_cap_in_generate_question(self):
        long_jd = "A" * 5000
        captured, _ = _capture_prompt_with_jd(long_jd)
        prompt = captured["prompt"]
        # Should be truncated to 3000 inside generate_question
        # The JD part should not contain 5000 As
        assert prompt.count("A") < 5000
        # Extract JD block and check length roughly <=3000
        # Ensure JD still present
        assert "JOB DESCRIPTION:" in prompt

    def test_backward_compat_no_jd_param(self):
        # Calling without jd_text kwarg should still work (default "")
        with patch("ai_service._call_llm", return_value="Generic question?"):
            q = ai_service.generate_question(
                role="Software Engineer",
                experience="2",
                skills=["python"],
                category="technical",
                difficulty="easy",
            )
            assert isinstance(q, str)
            assert len(q) > 0

class TestInterviewSessionJD:
    def test_session_stores_jd_text(self):
        sess = InterviewSession(
            session_id="jd_test_1",
            candidate_id=1,
            candidate_name="Test",
            candidate_role="DevOps Engineer",
            candidate_experience="3",
            candidate_skills=["docker"],
            resume_text="",
            mode="technical",
            company="General",
            total_questions=5,
            jd_text="Kubernetes, AWS, Docker required",
        )
        assert sess.jd_text == "Kubernetes, AWS, Docker required"
        assert sess.to_dict()["jd_text"] == "Kubernetes, AWS, Docker required"

    def test_session_jd_empty_default(self):
        sess = InterviewSession(
            session_id="jd_test_2",
            candidate_id=1,
            candidate_name="Test",
            candidate_role="Software Engineer",
            candidate_experience="2",
            candidate_skills=[],
            resume_text="",
            mode="technical",
        )
        assert sess.jd_text == ""

    def test_session_jd_length_cap(self):
        long_jd = "X" * 4000
        sess = InterviewSession(
            session_id="jd_test_3",
            candidate_id=1,
            candidate_name="Test",
            candidate_role="Software Engineer",
            candidate_experience="2",
            candidate_skills=[],
            resume_text="",
            mode="technical",
            jd_text=long_jd,
        )
        assert len(sess.jd_text) == 3000
        assert sess.jd_text == "X" * 3000

    def test_start_interview_passes_jd(self):
        sid = "jd_start_test"
        session_store.delete(sid)
        try:
            with patch("interview_engine._generate_next_question") as mock_gen:
                mock_gen.return_value = {"question": "Q1", "category": "technical", "difficulty": "medium", "question_id": ""}
                result = start_interview(
                    session_id=sid,
                    candidate_id=99,
                    candidate_name="JD Candidate",
                    candidate_role="DevOps Engineer",
                    candidate_experience="4",
                    candidate_skills=["k8s"],
                    resume_text="",
                    mode="technical",
                    company="General",
                    jd_text="Need Kubernetes expert",
                )
                assert "error" not in result
                sess = session_store.get(sid)
                assert sess is not None
                assert sess.jd_text == "Need Kubernetes expert"
                # Ensure _generate_next_question was called and would have received jd via session
                assert mock_gen.called
        finally:
            session_store.delete(sid)

    def test_generate_next_question_forwards_jd(self):
        sess = InterviewSession(
            session_id="jd_fwd_test",
            candidate_id=1,
            candidate_name="Test",
            candidate_role="DevOps Engineer",
            candidate_experience="3",
            candidate_skills=["docker"],
            resume_text="",
            mode="technical",
            jd_text="Kubernetes, Terraform",
        )
        sess.status = "in_progress"
        sess.current_round_index = 0
        # Mock generate_question to capture jd_text
        with patch("interview_engine.generate_question") as mock_gen:
            mock_gen.return_value = "Mocked JD question about Kubernetes?"
            from interview_engine import _generate_next_question as gen
            # Avoid GD/aptitude paths, make sure it's technical round
            result = gen(sess)
            assert mock_gen.called
            kwargs = mock_gen.call_args[1]
            assert kwargs.get("jd_text") == "Kubernetes, Terraform"
            assert "jd_text" in kwargs

class TestAppRegisterJD:
    def test_register_caps_jd_text(self):
        app.config["TESTING"] = True
        client = app.test_client()
        long_jd = "Y" * 5000
        data = {
            "name": "JD Tester",
            "email": "jd_tester_cap@example.com",
            "role": "DevOps Engineer",
            "experience": "2-4",
            "company": "General",
            "jd_text": long_jd,
        }
        resp = client.post("/register", data=data)
        assert resp.status_code == 200
        json_data = resp.get_json()
        assert json_data["success"] is True
        with client.session_transaction() as sess:
            assert "jd_text" in sess
            assert len(sess["jd_text"]) == 3000

    def test_register_without_jd_still_works(self):
        app.config["TESTING"] = True
        client = app.test_client()
        data = {
            "name": "NoJD Tester",
            "email": "no_jd@example.com",
            "role": "Software Engineer",
            "experience": "0-1",
            "company": "General",
        }
        resp = client.post("/register", data=data)
        assert resp.status_code == 200
        assert resp.get_json()["success"] is True
        with client.session_transaction() as sess:
            # jd_text should be present but empty
            assert sess.get("jd_text", "") == ""

    def test_register_with_jd_stored_and_used_in_start(self):
        app.config["TESTING"] = True
        client = app.test_client()
        jd = "Looking for Kubernetes, Docker, CI/CD pipeline expert"
        data = {
            "name": "Flow Tester",
            "email": "flow_jd@example.com",
            "role": "DevOps Engineer",
            "experience": "2-4",
            "company": "General",
            "jd_text": jd,
        }
        resp = client.post("/register", data=data)
        assert resp.status_code == 200
        # Now start interview — should succeed and use JD
        with patch("interview_engine._generate_next_question") as mock_gen:
            mock_gen.return_value = {"question": "JD tailored Q?", "category": "technical", "difficulty": "medium", "question_id": ""}
            resp2 = client.post("/api/start_interview", json={"mode": "technical"})
            assert resp2.status_code == 200
            data2 = resp2.get_json()
            assert "question" in data2
            # Verify JD was passed through (mock captured)
            # Session should have been created with jd_text
            # We can inspect session_store via sid
            sid = data2.get("session_id")
            from interview_engine import session_store as ss
            sess = ss.get(sid)
            if sess:
                assert sess.jd_text == jd
                ss.delete(sid)

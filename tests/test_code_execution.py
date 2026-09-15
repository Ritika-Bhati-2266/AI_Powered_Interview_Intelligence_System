"""
Tests for Live Code Execution — POST /api/run_code with mocked Judge0
"""

import os
import sys
import json
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Ensure Judge0 key is set for tests
os.environ["JUDGE0_API_KEY"] = "test_rapidapi_key_123"

from app import app
from coding_questions_bank import FALLBACK_CODING_QUESTIONS, get_question_by_id


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


class TestCodingBankTestCases:
    def test_all_questions_have_test_cases(self):
        for diff, lst in FALLBACK_CODING_QUESTIONS.items():
            for q in lst:
                assert "test_cases" in q, f"Missing test_cases for {q.get('id')}"
                assert isinstance(q["test_cases"], list)
                assert len(q["test_cases"]) > 0
                for tc in q["test_cases"]:
                    assert "input" in tc
                    assert "expected_output" in tc

    def test_all_questions_have_id(self):
        for diff, lst in FALLBACK_CODING_QUESTIONS.items():
            for q in lst:
                assert "id" in q and q["id"], f"Missing id for question: {q.get('question')[:30]}"

    def test_get_question_by_id(self):
        q = get_question_by_id("easy_1")
        assert q is not None
        assert q["id"] == "easy_1"
        assert get_question_by_id("nonexistent_xyz") is None


class TestRunCodeEndpoint:
    def test_empty_code_rejected(self, client):
        resp = client.post("/api/run_code", json={"code": "", "language": "python"})
        assert resp.status_code == 400
        assert "empty" in resp.get_json()["error"].lower()

    def test_unsupported_language(self, client):
        resp = client.post("/api/run_code", json={"code": "print(1)", "language": "ruby"})
        assert resp.status_code == 400
        assert "unsupported" in resp.get_json()["error"].lower()

    def test_no_api_key_graceful(self, client):
        # Temporarily clear key
        with patch.dict(os.environ, {"JUDGE0_API_KEY": ""}):
            resp = client.post("/api/run_code", json={"code": "print('hi')", "language": "python", "question_id": "easy_1"})
            assert resp.status_code == 503
            data = resp.get_json()
            assert "execution service unavailable" in data["error"].lower()

    @patch("app.requests.post")
    def test_run_python_all_pass(self, mock_post, client):
        # Mock Judge0 to return stdout matching expected_output for easy_1: "true", "false"
        # easy_1 test_cases: racecar->true, hello->false
        def side_effect(url, json=None, headers=None, timeout=None):
            stdin = json.get("stdin", "")
            m = MagicMock()
            # Map stdin to expected
            if "racecar" in stdin:
                m.json.return_value = {"stdout": "true\n", "stderr": "", "compile_output": "", "status": {"description": "Accepted"}}
            elif "hello" in stdin:
                m.json.return_value = {"stdout": "false\n", "stderr": "", "compile_output": "", "status": {"description": "Accepted"}}
            elif "Panama" in stdin:
                m.json.return_value = {"stdout": "true\n", "stderr": "", "compile_output": "", "status": {"description": "Accepted"}}
            else:
                m.json.return_value = {"stdout": "true", "stderr": "", "compile_output": "", "status": {"description": "Accepted"}}
            m.raise_for_status.return_value = None
            return m
        mock_post.side_effect = side_effect

        resp = client.post("/api/run_code", json={"code": "print('true')", "language": "python", "question_id": "easy_1"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["passed"] == 3
        assert data["total"] == 3
        assert len(data["details"]) == 3
        for d in data["details"]:
            assert d["passed"] is True
            assert "input" in d and "expected" in d and "actual" in d

    @patch("app.requests.post")
    def test_run_partial_pass(self, mock_post, client):
        # medium_1: two-sum — 3 test cases, 2 pass, 1 fails
        call_count = {"n": 0}
        def side_effect(url, json=None, headers=None, timeout=None):
            m = MagicMock()
            # First two calls pass, third fails
            call_count["n"] += 1
            if call_count["n"] <= 2:
                m.json.return_value = {"stdout": json.get("stdin", ""), "stderr": "", "compile_output": "", "status": {"description": "Accepted"}}
                # Actually return expected to pass — we mock to equal expected
                # For medium_1: expected are "0 1", "1 2", "-1 -1"
                exp_map = ["0 1", "1 2", "-1 -1"]
                m.json.return_value = {"stdout": exp_map[call_count["n"]-1], "stderr": "", "compile_output": "", "status": {"description": "Accepted"}}
            else:
                m.json.return_value = {"stdout": "wrong", "stderr": "", "compile_output": "", "status": {"description": "Accepted"}}
            m.raise_for_status.return_value = None
            return m
        mock_post.side_effect = side_effect

        resp = client.post("/api/run_code", json={"code": "print('0 1')", "language": "python", "question_id": "medium_1"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["passed"] == 2
        assert data["total"] == 3
        assert data["details"][0]["passed"] is True
        assert data["details"][2]["passed"] is False

    @patch("app.requests.post")
    def test_javascript_language_id(self, mock_post, client):
        # Verify javascript=63 is used
        m = MagicMock()
        m.json.return_value = {"stdout": "hello", "stderr": "", "compile_output": "", "status": {"description": "Accepted"}}
        m.raise_for_status.return_value = None
        mock_post.return_value = m
        # easy_1 has 3 cases, so 3 calls
        resp = client.post("/api/run_code", json={"code": "console.log('hi')", "language": "javascript", "question_id": "easy_1"})
        assert resp.status_code == 200
        # Check that language_id 63 was sent in at least one call
        first_call_payload = mock_post.call_args_list[0][1]["json"]
        assert first_call_payload["language_id"] == 63
        # Also test alias "js"
        mock_post.reset_mock()
        resp = client.post("/api/run_code", json={"code": "console.log('hi')", "language": "js", "question_id": "easy_1"})
        assert resp.status_code == 200
        assert mock_post.call_args_list[0][1]["json"]["language_id"] == 63

    @patch("app.requests.post")
    def test_judge0_timeout_fallback(self, mock_post, client):
        import requests as req
        mock_post.side_effect = req.exceptions.Timeout("timeout")
        resp = client.post("/api/run_code", json={"code": "print(1)", "language": "python", "question_id": "easy_1"})
        assert resp.status_code == 503
        data = resp.get_json()
        assert "execution service unavailable" in data["error"].lower()
        assert "timeout" in data["details"].lower()

    @patch("app.requests.post")
    def test_judge0_request_exception_fallback(self, mock_post, client):
        import requests as req
        mock_post.side_effect = req.exceptions.ConnectionError("conn fail")
        resp = client.post("/api/run_code", json={"code": "print(1)", "language": "python", "question_id": "easy_1"})
        assert resp.status_code == 503
        assert "execution service unavailable" in resp.get_json()["error"].lower()

    @patch("app.requests.post")
    def test_run_without_question_id_single_execution(self, mock_post, client):
        # No question_id -> server creates single test case with empty input
        m = MagicMock()
        m.json.return_value = {"stdout": "hello", "stderr": "", "compile_output": "", "status": {"description": "Accepted"}}
        m.raise_for_status.return_value = None
        mock_post.return_value = m
        resp = client.post("/api/run_code", json={"code": "print('hello')", "language": "python"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["total"] == 1
        assert data["passed"] == 1  # Accepted with no expected => pass

    @patch("app.requests.post")
    def test_compile_error_shown(self, mock_post, client):
        m = MagicMock()
        m.json.return_value = {"stdout": "", "stderr": "", "compile_output": "SyntaxError: invalid syntax", "status": {"description": "Compilation Error"}}
        m.raise_for_status.return_value = None
        mock_post.return_value = m
        resp = client.post("/api/run_code", json={"code": "print(", "language": "python", "question_id": "easy_1"})
        assert resp.status_code == 200
        data = resp.get_json()
        # All should fail when compile error
        assert data["passed"] == 0
        assert "SyntaxError" in data["details"][0]["stderr"] or "SyntaxError" in data["details"][0]["actual"]


class TestEvaluateWithCodeExecution:
    def test_evaluate_injects_code_result(self):
        from ai_service import evaluate_answer
        # Mock Groq call to avoid network
        with patch("ai_service._call_llm") as mock_llm:
            mock_llm.return_value = json.dumps({
                "overall_score": 9,
                "technical_score": 9,
                "communication_score": 8,
                "confidence_score": 8,
                "problem_solving_score": 9,
                "time_management_score": 8,
                "conceptual_clarity_score": 8,
                "strengths": ["Clean code"],
                "weaknesses": [],
                "ideal_answer": "ideal",
                "feedback": "Great!",
                "improvement_tip": "Keep it up",
                "keywords_used": ["loop"],
                "keywords_missed": []
            })
            result = evaluate_answer(
                question="Write a function to check palindrome",
                answer="def is_palindrome(s): return s==s[::-1]",
                role="Software Engineer",
                difficulty="easy",
                skills=["python"],
                code_execution_result={"passed": 3, "total": 3, "details": [{"input":"racecar","expected":"true","actual":"true","passed":True}]}
            )
            assert result["overall_score"] == 9
            # Verify prompt included execution note
            called_prompt = mock_llm.call_args[0][0]
            assert "3/3 test cases" in called_prompt or "passed 3/3" in called_prompt.lower()

    def test_submit_answer_with_code_execution(self):
        from interview_engine import InterviewSession, session_store, submit_answer
        sid = "test_code_exec_sid"
        session_store.delete(sid)
        sess = InterviewSession(sid, 1, "Coder", "Software Engineer", "2", ["python"], "", "coding", "General", 5)
        sess.status = "in_progress"
        sess.questions = ["Write a function to check whether a given string is a palindrome."]
        sess.questions_meta = [{"category": "strings", "difficulty": "easy", "question_id": "easy_1"}]
        sess.current_question_index = 0
        session_store.create(sess)
        try:
            with patch("interview_engine.evaluate_answer") as mock_eval:
                mock_eval.return_value = {
                    "overall_score": 8, "technical_score": 8, "communication_score": 7,
                    "confidence_score": 7, "problem_solving_score": 8, "time_management_score": 7,
                    "conceptual_clarity_score": 7, "feedback": "ok", "ideal_answer": "", "improvement_tip": "",
                    "strengths": [], "weaknesses": [], "keywords_used": [], "keywords_missed": [],
                    "filler_word_count": 0, "filler_words": {}
                }
                result = submit_answer(sid, "def is_palindrome(s): return s==s[::-1]", code_execution_result={"passed": 3, "total": 3, "details": []})
                assert mock_eval.called
                # Check that code_execution_result was forwarded
                kwargs = mock_eval.call_args[1] if mock_eval.call_args[1] else {}
                assert "code_execution_result" in kwargs
                assert kwargs["code_execution_result"]["passed"] == 3
                assert result["evaluation"]["overall_score"] == 8
        finally:
            session_store.delete(sid)

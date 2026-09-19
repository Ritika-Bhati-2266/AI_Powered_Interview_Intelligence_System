"""Tests for Piston error categorization (Syntax/TLE/MLE)"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import patch, MagicMock
from app import app

def _piston_run(stdout="", stderr="", code=0, signal=None, compile_stderr="", compile_code=0, compile_output=""):
    return {
        "run": {"stdout": stdout, "stderr": stderr, "code": code, "signal": signal, "output": stdout or stderr},
        "compile": {"stdout": "", "stderr": compile_stderr, "code": compile_code, "output": compile_output or compile_stderr},
        "language": "python", "version": "3.10.0"
    }

class TestPistonCategorization:
    def setup_method(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    @patch("app.requests.post")
    def test_syntax_error_compile(self, mock_post):
        m = MagicMock()
        m.json.return_value = _piston_run(stdout="", stderr="", code=None, compile_stderr="SyntaxError: invalid syntax", compile_code=1)
        m.raise_for_status.return_value = None
        mock_post.return_value = m
        resp = self.client.post("/api/run_code", json={"code": "print(", "language": "python", "question_id": "easy_1"})
        assert resp.status_code == 200
        assert resp.get_json()["details"][0]["status"] == "Syntax Error"

    @patch("app.requests.post")
    def test_syntax_error_runtime(self, mock_post):
        m = MagicMock()
        m.json.return_value = _piston_run(stdout="", stderr="SyntaxError: unexpected EOF", code=1, compile_stderr="", compile_code=0)
        m.raise_for_status.return_value = None
        mock_post.return_value = m
        resp = self.client.post("/api/run_code", json={"code": "x = ", "language": "python", "question_id": "easy_1"})
        assert resp.get_json()["details"][0]["status"] == "Syntax Error"

    @patch("app.requests.post")
    def test_tle_via_sigkill(self, mock_post):
        m = MagicMock()
        m.json.return_value = _piston_run(stdout="", stderr="killed", code=137, signal="SIGKILL", compile_code=0)
        m.raise_for_status.return_value = None
        mock_post.return_value = m
        resp = self.client.post("/api/run_code", json={"code": "while True: pass", "language": "python", "question_id": "easy_1"})
        # 3 test cases for easy_1, all should be TLE
        assert resp.get_json()["details"][0]["status"] == "Time Limit Exceeded"

    @patch("app.requests.post")
    def test_mle(self, mock_post):
        m = MagicMock()
        m.json.return_value = _piston_run(stdout="", stderr="MemoryError", code=1, compile_code=0)
        m.raise_for_status.return_value = None
        mock_post.return_value = m
        resp = self.client.post("/api/run_code", json={"code": "a=[1]*10**9", "language": "python", "question_id": "easy_1"})
        assert resp.get_json()["details"][0]["status"] == "Memory Limit Exceeded"

    @patch("app.requests.post")
    def test_runtime_error_generic(self, mock_post):
        m = MagicMock()
        m.json.return_value = _piston_run(stdout="", stderr="NameError: name 'x' is not defined", code=1, compile_code=0)
        m.raise_for_status.return_value = None
        mock_post.return_value = m
        resp = self.client.post("/api/run_code", json={"code": "print(x)", "language": "python", "question_id": "easy_1"})
        assert resp.get_json()["details"][0]["status"] == "Runtime Error"

    @patch("app.requests.post")
    def test_accepted_still(self, mock_post):
        m = MagicMock()
        m.json.return_value = _piston_run(stdout="hello", stderr="", code=0, compile_code=0)
        m.raise_for_status.return_value = None
        mock_post.return_value = m
        resp = self.client.post("/api/run_code", json={"code": "print('hello')", "language": "python"})
        # single execution (no question_id)
        assert resp.get_json()["details"][0]["status"] == "Accepted"

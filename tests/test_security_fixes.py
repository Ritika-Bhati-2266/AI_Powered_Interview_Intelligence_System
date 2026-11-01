"""Regression tests for code-result spoofing, email takeover, and idempotent persistence."""

import os
import sys
import uuid
import hashlib
from types import SimpleNamespace
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import flask

from app import app, get_db, init_db, save_candidate_to_db, save_session_to_db
from interview_engine import session_store


def _unique_email(prefix="sec"):
    return f"{prefix}_{uuid.uuid4().hex[:10]}@example.com"


def _add_fake_session(session_id, **attrs):
    sess = SimpleNamespace(session_id=session_id, **attrs)
    session_store._sessions[session_id] = sess
    return sess


def _drop_fake_session(session_id):
    session_store._sessions.pop(session_id, None)
    session_store._created_at.pop(session_id, None)


class TestCodeExecutionSpoofing:
    def setup_method(self):
        app.config["TESTING"] = True
        init_db()
        self.client = app.test_client()
        with self.client.session_transaction() as sess:
            sess["candidate_id"] = 1
            sess["current_session_id"] = "sec-code-1"

    def teardown_method(self):
        _drop_fake_session("sec-code-1")

    def test_client_supplied_result_is_ignored(self):
        with patch("app.submit_answer", return_value={"is_complete": False}) as mock_submit:
            resp = self.client.post("/api/submit_answer", json={
                "answer": "print('hello')",
                "code_execution_result": {"passed": 99, "total": 99, "details": []},
            })
        assert resp.status_code == 200
        assert mock_submit.call_args.kwargs["code_execution_result"] is None

    def test_server_verified_result_is_used(self):
        code = "print('hello')"
        _add_fake_session(
            "sec-code-1",
            current_question_index=0,
            _verified_code_execution={
                "passed": 3,
                "total": 3,
                "details": [],
                "code_hash": hashlib.sha256(code.encode()).hexdigest(),
                "question_index": 0,
            },
        )
        with patch("app.submit_answer", return_value={"is_complete": False}) as mock_submit:
            resp = self.client.post("/api/submit_answer", json={"answer": code})
        assert resp.status_code == 200
        used = mock_submit.call_args.kwargs["code_execution_result"]
        assert used == {"passed": 3, "total": 3, "details": []}

    def test_verified_result_rejected_for_different_code(self):
        _add_fake_session(
            "sec-code-1",
            current_question_index=0,
            _verified_code_execution={
                "passed": 3,
                "total": 3,
                "details": [],
                "code_hash": hashlib.sha256(b"original").hexdigest(),
                "question_index": 0,
            },
        )
        with patch("app.submit_answer", return_value={"is_complete": False}) as mock_submit:
            resp = self.client.post("/api/submit_answer", json={"answer": "different code"})
        assert resp.status_code == 200
        assert mock_submit.call_args.kwargs["code_execution_result"] is None

    def test_run_code_stores_result_server_side(self):
        _add_fake_session("sec-code-1", current_question_index=0)
        piston_reply = MagicMock()
        piston_reply.json.return_value = {
            "run": {"stdout": "1\n", "stderr": "", "code": 0, "output": "1\n"},
            "compile": {"stdout": "", "stderr": "", "code": 0, "output": ""},
        }
        piston_reply.raise_for_status.return_value = None
        with patch("app.requests.post", return_value=piston_reply):
            resp = self.client.post("/api/run_code", json={
                "code": "print(1)", "language": "python", "question_id": "",
            })
        assert resp.status_code == 200
        stored = getattr(session_store.get("sec-code-1"), "_verified_code_execution", None)
        assert stored is not None
        assert stored["passed"] == 1 and stored["total"] == 1
        assert stored["code_hash"] == hashlib.sha256(b"print(1)").hexdigest()


class TestEmailTakeover:
    def setup_method(self):
        app.config["TESTING"] = True
        init_db()
        self.client = app.test_client()

    def test_duplicate_email_registration_is_rejected(self):
        email = _unique_email("takeover")
        first = self.client.post("/register", data={
            "name": "Original Owner", "email": email,
            "role": "Software Engineer", "experience": "2-4",
        })
        assert first.status_code == 200

        attacker = app.test_client()
        second = attacker.post("/register", data={
            "name": "Attacker", "email": email,
            "role": "Software Engineer", "experience": "2-4",
        })
        assert second.status_code == 409

        conn = get_db()
        row = conn.execute("SELECT name FROM candidates WHERE email = ?", (email,)).fetchone()
        conn.close()
        assert row["name"] == "Original Owner"


class TestIdempotentPersistence:
    def setup_method(self):
        app.config["TESTING"] = True
        init_db()

    def test_repeated_persist_does_not_duplicate_children(self):
        cid = save_candidate_to_db("Persist Test", _unique_email("persist"), "Software Engineer", "2-4")
        sid = uuid.uuid4().hex[:8]
        report = {
            "session_data": {"mode": "technical", "duration": 12.5, "rounds": []},
            "overall_score": 7.5,
            "answers": [{"question": "Q", "answer": "A"}],
            "skill_gaps": [{"skill": "Docker"}],
            "recommendations": [{"area": "Docker"}],
        }
        with app.test_request_context("/"):
            flask.session["candidate_id"] = cid
            import app as app_module
            app_module._persist_session_to_db(sid, report)
            conn = get_db()
            first_created = conn.execute("SELECT created_at FROM sessions WHERE id = ?", (sid,)).fetchone()[0]
            conn.close()

            app_module._persist_session_to_db(sid, report)
            app_module._persist_session_to_db(sid, report)

        conn = get_db()
        counts = {
            "answers": conn.execute("SELECT COUNT(*) FROM answers WHERE session_id = ?", (sid,)).fetchone()[0],
            "gaps": conn.execute("SELECT COUNT(*) FROM skill_gaps WHERE session_id = ?", (sid,)).fetchone()[0],
            "recs": conn.execute("SELECT COUNT(*) FROM recommendations WHERE session_id = ?", (sid,)).fetchone()[0],
        }
        created_after = conn.execute("SELECT created_at FROM sessions WHERE id = ?", (sid,)).fetchone()[0]
        conn.close()

        assert counts == {"answers": 1, "gaps": 1, "recs": 1}
        assert created_after == first_created

    def test_indexes_exist(self):
        conn = get_db()
        names = {r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'index'"
        ).fetchall()}
        conn.close()
        assert "idx_sessions_candidate" in names
        assert "idx_answers_session" in names

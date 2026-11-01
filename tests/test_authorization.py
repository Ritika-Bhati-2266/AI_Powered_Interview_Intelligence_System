"""Regression tests for access control (IDOR), PII exposure, and admin XSS."""

import os
import sys
import uuid
import base64

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import patch

from app import app, get_db, init_db


def _make_candidate(name="Auth Test", email=None, role="Software Engineer"):
    email = email or f"auth_{uuid.uuid4().hex[:10]}@example.com"
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO candidates (name, email, role, experience) VALUES (?,?,?,?)",
        (name, email, role, "2-4"),
    )
    candidate_id = cur.lastrowid
    conn.commit()
    conn.close()
    return candidate_id


def _make_session(candidate_id, status="completed", score=7.0):
    session_id = uuid.uuid4().hex[:8]
    conn = get_db()
    conn.execute(
        "INSERT INTO sessions (id, candidate_id, mode, status, overall_score) VALUES (?,?,?,?,?)",
        (session_id, candidate_id, "technical", status, score),
    )
    conn.commit()
    conn.close()
    return session_id


class TestAccessControl:
    def setup_method(self):
        app.config["TESTING"] = True
        init_db()
        os.environ.pop("ADMIN_USER", None)
        os.environ.pop("ADMIN_PASSWORD", None)
        self.client = app.test_client()

    def test_candidates_endpoint_requires_admin(self):
        assert self.client.get("/api/candidates").status_code == 403

    def test_candidates_endpoint_allows_admin(self):
        cred = base64.b64encode(b"admin:secret123").decode()
        with patch.dict(os.environ, {"ADMIN_USER": "admin", "ADMIN_PASSWORD": "secret123"}):
            resp = self.client.get(
                "/api/candidates", headers={"Authorization": f"Basic {cred}"}
            )
        assert resp.status_code == 200
        assert isinstance(resp.get_json(), list)

    def test_dashboard_blocks_other_candidate(self):
        owner = _make_candidate()
        other = _make_candidate()
        with self.client.session_transaction() as sess:
            sess["candidate_id"] = other
        with patch("app.get_candidate_history", return_value={"ok": True}):
            assert self.client.get(f"/api/dashboard/{owner}").status_code == 403
            assert self.client.get(f"/api/dashboard/{other}").status_code == 200

    def test_progress_blocks_anonymous(self):
        owner = _make_candidate()
        assert self.client.get(f"/api/progress/{owner}").status_code == 403

    def test_report_blocks_anonymous(self):
        owner = _make_candidate()
        sid = _make_session(owner)
        assert self.client.get(f"/api/report/{sid}").status_code == 403
        assert self.client.get(f"/report/{sid}").status_code == 302

    def test_report_allows_owner(self):
        owner = _make_candidate()
        sid = _make_session(owner)
        with self.client.session_transaction() as sess:
            sess["candidate_id"] = owner
        with patch("app.generate_report", return_value={"session_data": {}, "answers": []}):
            assert self.client.get(f"/api/report/{sid}").status_code == 200

    def test_report_blocks_different_candidate(self):
        owner = _make_candidate()
        other = _make_candidate()
        sid = _make_session(owner)
        with self.client.session_transaction() as sess:
            sess["candidate_id"] = other
        with patch("app.generate_report", return_value={"session_data": {}, "answers": []}):
            assert self.client.get(f"/api/report/{sid}").status_code == 403

    def test_compare_works_for_owner_and_closes_connection(self):
        owner = _make_candidate()
        _make_session(owner, score=8.0)
        with self.client.session_transaction() as sess:
            sess["candidate_id"] = owner
        resp = self.client.get(f"/api/compare/{owner}")
        assert resp.status_code == 200
        assert "percentile" in resp.get_json()

    def test_compare_blocks_other_candidate(self):
        owner = _make_candidate()
        other = _make_candidate()
        with self.client.session_transaction() as sess:
            sess["candidate_id"] = other
        assert self.client.get(f"/api/compare/{owner}").status_code == 403


class TestAdminXssEscaping:
    def setup_method(self):
        app.config["TESTING"] = True
        init_db()
        os.environ.pop("ADMIN_USER", None)
        os.environ.pop("ADMIN_PASSWORD", None)
        self.client = app.test_client()

    def test_candidate_name_is_html_escaped(self):
        _make_candidate(name='<script>alert("xss")</script>')
        resp = self.client.get("/admin")
        assert resp.status_code == 200
        body = resp.data.decode("utf-8", "ignore")
        assert "<script>alert(\"xss\")</script>" not in body
        assert "&lt;script&gt;" in body

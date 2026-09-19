"""Tests for Admin Panel (/admin)"""

import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import base64
from unittest.mock import patch
from app import app, get_db, init_db

class TestAdminPanel:
    def setup_method(self):
        app.config["TESTING"] = True
        self.client = app.test_client()
        init_db()

    def test_admin_open_without_env(self):
        # No ADMIN_USER set -> should allow 200
        with patch.dict(os.environ, {}, clear=False):
            # Ensure ADMIN_USER not set
            os.environ.pop("ADMIN_USER", None)
            os.environ.pop("ADMIN_PASSWORD", None)
            resp = self.client.get("/admin")
            assert resp.status_code == 200
            assert b"Admin Panel" in resp.data
            assert b"Candidates" in resp.data

    def test_admin_requires_auth_when_configured(self):
        env = {"ADMIN_USER": "admin", "ADMIN_PASSWORD": "secret123"}
        with patch.dict(os.environ, env):
            resp = self.client.get("/admin")
            assert resp.status_code == 401
            assert "WWW-Authenticate" in resp.headers
            # Correct credentials
            cred = base64.b64encode(b"admin:secret123").decode()
            resp2 = self.client.get("/admin", headers={"Authorization": f"Basic {cred}"})
            assert resp2.status_code == 200
            assert b"Admin Panel" in resp2.data
            # Wrong password
            bad = base64.b64encode(b"admin:wrong").decode()
            resp3 = self.client.get("/admin", headers={"Authorization": f"Basic {bad}"})
            assert resp3.status_code == 401

    def test_admin_lists_candidates_and_sessions(self):
        # Register a candidate first
        data = {"name": "Admin Test", "email": "admin_test_list@example.com", "role": "Software Engineer", "experience": "2-4", "company": "General"}
        resp = self.client.post("/register", data=data)
        assert resp.status_code == 200
        # Now admin should list it
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("ADMIN_USER", None)
            resp2 = self.client.get("/admin")
            assert resp2.status_code == 200
            assert b"admin_test_list@example.com" in resp2.data

    def test_admin_delete_session(self):
        # Create a session via direct DB insert
        conn = get_db()
        cur = conn.cursor()
        # Ensure candidate exists
        cur.execute("INSERT OR IGNORE INTO candidates (name, email, role, experience) VALUES (?,?,?,?)", ("Del Candidate", "del_sess@example.com", "Software Engineer", "2-4"))
        conn.commit()
        cand = conn.execute("SELECT id FROM candidates WHERE email = ?", ("del_sess@example.com",)).fetchone()
        cid = cand["id"]
        sid = "DELTEST1"
        cur.execute("INSERT OR REPLACE INTO sessions (id, candidate_id, mode, status, overall_score, total_questions) VALUES (?,?,?,?,?,?)", (sid, cid, "technical", "completed", 7, 5))
        conn.commit()
        conn.close()
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("ADMIN_USER", None)
            # Ensure exists
            resp = self.client.get("/admin")
            assert sid.encode() in resp.data
            # Delete
            del_resp = self.client.post(f"/admin/delete/{sid}", follow_redirects=True)
            assert del_resp.status_code == 200
            # Verify gone
            conn2 = get_db()
            row = conn2.execute("SELECT id FROM sessions WHERE id = ?", (sid,)).fetchone()
            conn2.close()
            assert row is None

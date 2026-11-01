"""
Tests for Group Discussion (GD) round in interview_engine.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from interview_engine import start_interview, submit_answer, session_store


class TestGDRound:
    """Test the GD round functionality."""

    def setup_method(self):
        """Clean up any leftover sessions."""
        for sid in list(session_store._sessions.keys()):
            session_store.delete(sid)

    def _make_session(self, session_id="gdtest_session", company="TCS", practice_round="gd"):
        """Start a GD interview session."""
        return start_interview(
            session_id=session_id,
            candidate_id=1,
            candidate_name="Rahul",
            candidate_role="SDE",
            candidate_experience="0-1",
            candidate_skills=["Python"],
            resume_text="B.Tech CS.",
            mode="technical",
            company=company,
            practice_round=practice_round,
        )

    def test_gd_round_starts_with_topic_and_personas(self):
        """GD round should start with a topic and 3 personas."""
        r = self._make_session()
        assert r.get("is_gd") is True, f"Expected is_gd=True, got {r.get('is_gd')}"
        assert r.get("gd_topic"), "GD topic should not be empty"
        assert len(r.get("gd_personas", [])) == 3, f"Expected 3 personas, got {len(r.get('gd_personas', []))}"
        assert r.get("question"), "GD intro question should not be empty"
        assert "Group Discussion" in r.get("question", "")

    def test_gd_only_allowed_companies(self):
        """GD should only be available for TCS, Infosys, Wipro (or explicit practice_round=gd)."""
        # Explicit practice_round=gd should work for any company
        r = self._make_session(company="Google", practice_round="gd")
        assert r.get("is_gd") is True

    def test_gd_candidate_turns_generate_ai_responses(self):
        """Each candidate turn should generate 2 AI persona responses."""
        r = self._make_session()
        assert r.get("is_gd") is True

        # Submit 4 candidate turns
        for i in range(4):
            res = submit_answer(r["session_id"], f"My view on turn {i + 1}.")
            if i < 3:
                assert res.get("gd_complete") is False, f"Turn {i+1} should not complete GD"
                # After each non-final turn, there should be 2 AI next_turns
                assert len(res.get("next_turns", [])) == 2, f"Expected 2 AI turns, got {len(res.get('next_turns', []))}"

    def test_gd_completes_after_max_turns(self):
        """GD should complete after gd_max_candidate_turns (4) candidate turns."""
        r = self._make_session()
        final_res = None
        for i in range(4):
            final_res = submit_answer(r["session_id"], f"Turn {i + 1} answer.")
        assert final_res.get("gd_complete") is True, "GD should be complete after 4 turns"
        assert final_res.get("gd_scores") is not None, "GD scores should be calculated"
        scores = final_res.get("gd_scores", {})
        for key in ("initiative", "listening", "clarity", "collaboration", "balance"):
            assert key in scores, f"GD score missing key: {key}"
            assert 1 <= scores[key] <= 10, f"GD score {key} out of range: {scores[key]}"

    def test_gd_transcript_contains_candidate_and_ai_turns(self):
        """GD transcript should include both candidate and AI turns."""
        r = self._make_session()
        submit_answer(r["session_id"], "I believe AI should assist teachers.")
        s = session_store.get(r["session_id"])
        transcript = s.gd_transcript
        speakers = [t.get("speaker") for t in transcript]
        assert "candidate" in speakers, "Transcript should contain candidate turns"
        assert "ai" in speakers, "Transcript should contain AI turns"

    def test_gd_scores_have_feedback(self):
        """GD evaluation should include feedback and dominance label."""
        r = self._make_session()
        for i in range(4):
            res = submit_answer(r["session_id"], f"Turn {i + 1}.")
        scores = res.get("gd_scores", {})
        assert "feedback" in scores, "GD scores should include feedback"
        assert "dominance_label" in scores, "GD scores should include dominance label"

    def test_gd_round_transitions_to_next_round(self):
        """After GD completes, session should transition to next round (not session complete)."""
        r = self._make_session(company="TCS", practice_round="full")
        # TCS: GD -> Aptitude -> Coding -> Technical -> HR
        # After GD completes, should NOT be session complete
        for i in range(4):
            res = submit_answer(r["session_id"], f"GD turn {i + 1}.")
        assert res.get("gd_complete") is True
        # is_complete should be False since there are more rounds (aptitude next)
        # Note: next_question generation may call Groq (external), so we only check gd_complete
        assert res.get("is_complete") is False or res.get("is_complete") is None

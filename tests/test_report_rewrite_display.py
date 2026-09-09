"""
Regression test: the report's "Answer Optimizations" section must display the
real ORIGINAL score, the REWRITTEN score, and a correct non-zero delta.

Bug: rewrite_answer() computed original_scores but never stored them on the
answer record (they were only returned in the API response). It then overwrote
the record's top-level score fields with the rewrite scores. As a result,
generate_final_report_data() could not reconstruct the original score, so the
report showed original == rewritten and Metric Delta = 0.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ai_service
from ai_service import generate_final_report_data
from interview_engine import rewrite_answer, InterviewSession, session_store


class TestReportRewriteDisplay:
    """Report "Answer Optimizations" section uses correct original/rewrite/delta."""

    ORIGINAL = {
        "overall_score": 2, "technical_score": 2, "communication_score": 2,
        "confidence_score": 3, "problem_solving_score": 2,
        "time_management_score": 3, "conceptual_clarity_score": 2,
    }

    def setup_method(self):
        """Deterministic environment: no real LLM calls."""
        ai_service._call_llm = lambda *a, **k: "[GROQ_ERROR] offline (test)"
        self.session_id = "test_report_rewrite_display"
        session_store.delete(self.session_id)

        session = InterviewSession(
            session_id=self.session_id,
            candidate_id=1,
            candidate_name="Test User",
            candidate_role="Software Engineer",
            candidate_experience="3",
            candidate_skills=["python", "javascript"],
            resume_text="",
            mode="technical",
            company="General",
            total_questions=5,
        )
        session.status = "completed"
        session.questions = ["Q1", "Q2"]
        session.questions_meta = [{"category": "technical"}, {"category": "technical"}]
        session.answers = [
            {
                "question": "Explain how a hash map works.",
                "answer": "idk",
                "overall_score": 2,
                "technical_score": 2,
                "communication_score": 2,
                "confidence_score": 3,
                "problem_solving_score": 2,
                "time_management_score": 3,
                "conceptual_clarity_score": 2,
                "feedback": "Too brief.",
                "ideal_answer": "A complete answer would describe hashing and collision handling.",
                "improvement_tip": "Add detail.",
                "filler_word_count": 0,
                "filler_words": {},
                "rewrite_used": False,
                "rewrite_text": "",
                "rewrite_scores": {},
                "round_name": "Technical",
                "round_number": 1,
            }
        ]
        session.recent_scores = [2]
        session_store.create(session)

    def teardown_method(self):
        session_store.delete(self.session_id)

    def _build_report(self, answers):
        candidate_info = {
            "name": "Test User", "role": "Software Engineer",
            "experience": "3", "skills": ["python"], "mode": "technical",
            "company": "General",
        }
        session_data = {
            "session_id": self.session_id, "mode": "technical",
            "company": "General", "total_questions": len(answers),
            "completed_questions": len(answers), "rounds": [],
            "start_time": 0, "end_time": 1, "duration": 1,
        }
        return generate_final_report_data(
            candidate_info=candidate_info,
            session_data=session_data,
            answers=answers,
            skill_gaps=[],
            recommendations=[],
        )

    def test_report_shows_original_rewrite_and_nonzero_delta(self):
        """A low-scoring answer rewritten with a stronger answer must show both
        score sets and a positive delta in the report."""
        rewritten = (
            "A hash map is a data structure that stores key-value pairs using a hash "
            "function to compute an index into an array of buckets, achieving O(1) "
            "average lookup, insertion, and deletion. For example, Python dicts and "
            "Java HashMap handle collisions with chaining or open addressing, and the "
            "load factor governs when the table resizes. I would also consider "
            "worst-case O(n) behaviour and memory overhead when choosing a hash map."
        )

        result = rewrite_answer(self.session_id, 0, rewritten)
        assert "error" not in result

        record = session_store.get(self.session_id).answers[0]

        # Original scores must be preserved on the record (the core bug)
        assert "original_scores" in record, "original_scores must be stored on the record"
        for key, val in self.ORIGINAL.items():
            assert record["original_scores"][key] == val, f"{key} not preserved"

        # Rewritten scores must be higher
        assert record["rewrite_scores"]["overall_score"] > self.ORIGINAL["overall_score"]

        report = self._build_report(session_store.get(self.session_id).answers)

        assert report["has_rewrites"] is True
        rw = report["rewrites"][0]

        # Original displayed score must be the true original (not the rewrite score)
        assert rw["original_scores"]["overall_score"] == self.ORIGINAL["overall_score"]
        # Rewritten displayed score must be the rewrite score
        assert rw["rewritten_scores"]["overall_score"] == record["rewrite_scores"]["overall_score"]
        assert rw["rewritten_scores"]["overall_score"] > rw["original_scores"]["overall_score"]
        # Delta must be non-zero and equal to rewritten - original
        assert rw["improvement"]["overall_score"] > 0
        assert rw["improvement"]["overall_score"] == (
            rw["rewritten_scores"]["overall_score"] - rw["original_scores"]["overall_score"]
        )


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])

"""
Tests for one-rewrite-per-answer workflow in interview_engine.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from interview_engine import rewrite_answer, InterviewSession, session_store


class TestRewriteFlow:
    """Test the rewrite functionality."""

    def setup_method(self):
        """Create a mock session with answers for testing."""
        # Use a test session ID
        self.session_id = "test_rewrite_session"
        session_store.delete(self.session_id)

        # Create a minimal session object for testing
        from interview_engine import session_store as ss
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
            total_questions=5
        )
        session.status = "in_progress"
        session.current_question_index = 2  # 2 questions already asked
        session.questions = ["Q1", "Q2"]
        session.questions_meta = [{"category": "technical"}, {"category": "technical"}]

        # Add two mock answers
        session.answers = [
            {
                "question": "What is Python?",
                "answer": "Python is a programming language.",
                "overall_score": 4,
                "technical_score": 3,
                "communication_score": 4,
                "confidence_score": 4,
                "problem_solving_score": 3,
                "time_management_score": 5,
                "conceptual_clarity_score": 4,
                "feedback": "Basic but correct.",
                "ideal_answer": "Python is a high-level, interpreted language...",
                "improvement_tip": "Add more detail.",
                "filler_word_count": 0,
                "filler_words": {},
                "rewrite_used": False,
                "rewrite_text": "",
                "rewrite_scores": {},
                "round_name": "Technical",
                "round_number": 1,
            },
            {
                "question": "Explain decorators.",
                "answer": "Decorators modify functions.",
                "overall_score": 5,
                "technical_score": 5,
                "communication_score": 5,
                "confidence_score": 5,
                "problem_solving_score": 4,
                "time_management_score": 5,
                "conceptual_clarity_score": 5,
                "feedback": "Good overview.",
                "ideal_answer": "Decorators are functions that wrap other functions...",
                "improvement_tip": "Give an example.",
                "filler_word_count": 0,
                "filler_words": {},
                "rewrite_used": False,
                "rewrite_text": "",
                "rewrite_scores": {},
                "round_name": "Technical",
                "round_number": 1,
            }
        ]
        session.recent_scores = [4, 5]

        session_store.create(session)

    def teardown_method(self):
        """Clean up test session."""
        session_store.delete(self.session_id)

    def test_rewrite_improves_scores(self):
        """Rewriting an answer should produce new scores."""
        rewritten = (
            "Decorators are functions that take another function and extend its "
            "behavior without explicitly modifying it. For example, @property "
            "turns a method into an attribute, and @staticmethod marks a method "
            "that doesn't use self or cls."
        )

        result = rewrite_answer(self.session_id, 1, rewritten)

        assert "error" not in result
        assert result["answer_index"] == 1
        assert "original_scores" in result
        assert "rewrite_scores" in result
        assert "improvement" in result
        assert "rewrite_evaluation" in result

    def test_rewrite_cannot_be_used_twice(self):
        """Only one rewrite per answer is allowed."""
        rewritten = "A better explanation of decorators with examples."

        result1 = rewrite_answer(self.session_id, 0, rewritten)
        assert "error" not in result1

        result2 = rewrite_answer(self.session_id, 0, "Another attempt.")
        assert "error" in result2
        assert "already been rewritten" in result2["error"]

    def test_rewrite_invalid_index(self):
        """Invalid answer index should return error."""
        result = rewrite_answer(self.session_id, 99, "Some answer.")
        assert "error" in result
        assert "Invalid answer index" in result["error"]

    def test_rewrite_empty_answer(self):
        """Empty rewritten answer should return error."""
        result = rewrite_answer(self.session_id, 0, "")
        assert "error" in result
        assert "empty" in result["error"]

    def test_rewrite_updates_session_answer_record(self):
        """The session's answer record should be updated with rewrite scores."""
        rewritten = (
            "Decorators allow adding functionality to existing functions. "
            "Common examples include @property, @classmethod, @staticmethod."
        )

        rewrite_answer(self.session_id, 1, rewritten)

        session = session_store.get(self.session_id)
        record = session.answers[1]

        assert record["rewrite_used"] is True
        assert record["rewrite_text"] == rewritten
        assert "rewrite_scores" in record
        assert record["overall_score"] == record["rewrite_scores"]["overall_score"]
        assert record["rewrite_filler_word_count"] >= 0
        assert "rewrite_filler_words" in record

    def test_improvement_delta_calculated(self):
        """Improvement delta should be calculated for all score dimensions."""
        rewritten = "Decorators wrap functions to extend behavior. Example: @property."

        result = rewrite_answer(self.session_id, 1, rewritten)

        assert "improvement" in result
        imp = result["improvement"]
        expected_keys = [
            "overall_score", "technical_score", "communication_score",
            "confidence_score", "problem_solving_score",
            "time_management_score", "conceptual_clarity_score"
        ]
        for key in expected_keys:
            assert key in imp
            assert isinstance(imp[key], int)


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])

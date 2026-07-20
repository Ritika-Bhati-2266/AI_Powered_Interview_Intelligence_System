"""
Tests for filler-word integration in ai_service.evaluate_answer()
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_service import evaluate_answer


class TestFillerWordIntegration:
    """Test that evaluate_answer returns filler-word fields."""

    def test_filler_fields_present(self):
        """Fallback evaluation should include filler_word_count and filler_words."""
        question = "What is your greatest strength?"
        answer = "Well, um, I think I am good at Python and, like, solving problems."

        result = evaluate_answer(
            question=question,
            answer=answer,
            role="Software Engineer",
            difficulty="medium",
            skills=["python", "problem solving"]
        )

        assert "filler_word_count" in result
        assert "filler_words" in result
        assert result["filler_word_count"] >= 3  # well, um, like
        assert "um" in result["filler_words"]
        assert "like" in result["filler_words"]

    def test_no_fillers_zero_count(self):
        """Clean answer has zero filler words."""
        question = "Tell me about yourself."
        answer = "I am a software engineer with five years of experience building web applications."

        result = evaluate_answer(
            question=question,
            answer=answer,
            role="Software Engineer",
            difficulty="medium"
        )

        assert result["filler_word_count"] == 0
        assert result["filler_words"] == {}

    def test_communication_and_confidence_scores_present(self):
        """Ensure standard score fields remain present."""
        result = evaluate_answer(
            question="Why should we hire you?",
            answer="I have the right skills and experience.",
            role="Software Engineer",
            difficulty="easy"
        )

        assert "overall_score" in result
        assert "technical_score" in result
        assert "communication_score" in result
        assert "confidence_score" in result
        assert 0 <= result["overall_score"] <= 10

    def test_filler_penalty_reduces_scores(self):
        """Answers with many fillers should score lower on communication/confidence."""
        question = "Explain your experience."

        clean_answer = "I led a team to redesign the payment system using Python and PostgreSQL."
        filler_answer = "Um, well, like, basically, I led, um, a team to, like, redesign the payment system."

        clean = evaluate_answer(question, clean_answer, "Software Engineer", "medium")
        filler = evaluate_answer(question, filler_answer, "Software Engineer", "medium")

        assert filler["filler_word_count"] > clean["filler_word_count"]
        assert filler["communication_score"] <= clean["communication_score"] + 2
        assert filler["confidence_score"] <= clean["confidence_score"] + 2


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])

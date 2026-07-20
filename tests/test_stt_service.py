"""
Tests for stt_service.py
"""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stt_service import detect_filler_words, FILLER_WORDS


class TestFillerWordDetection:
    """Test filler word detection logic."""

    def test_empty_text(self):
        """Empty text returns zero fillers."""
        result = detect_filler_words("")
        assert result["filler_words"] == {}
        assert result["total_count"] == 0

    def test_no_fillers(self):
        """Clean text returns zero fillers."""
        text = "I have experience with Python and JavaScript."
        result = detect_filler_words(text)
        assert result["filler_words"] == {}
        assert result["total_count"] == 0

    def test_single_filler(self):
        """Detects single filler word."""
        text = "I um have experience with Python."
        result = detect_filler_words(text)
        assert "um" in result["filler_words"]
        assert result["filler_words"]["um"] == 1
        assert result["total_count"] == 1

    def test_multiple_fillers(self):
        """Detects multiple different filler words."""
        text = "I um like actually have experience."
        result = detect_filler_words(text)
        assert result["filler_words"]["um"] == 1
        assert result["filler_words"]["like"] == 1
        assert result["filler_words"]["actually"] == 1
        assert result["total_count"] == 3

    def test_repeated_filler(self):
        """Counts repeated filler words."""
        text = "Um um um I think so."
        result = detect_filler_words(text)
        assert result["filler_words"]["um"] == 3
        assert result["total_count"] == 4  # "so" is also a filler word

    def test_case_insensitive(self):
        """Detection is case insensitive."""
        text = "UM Like ACTUALLY"
        result = detect_filler_words(text)
        assert result["filler_words"]["um"] == 1
        assert result["filler_words"]["like"] == 1
        assert result["filler_words"]["actually"] == 1

    def test_phrase_fillers(self):
        """Detects multi-word filler phrases."""
        text = "You know I mean basically it works."
        result = detect_filler_words(text)
        assert result["filler_words"]["you know"] == 1
        assert result["filler_words"]["i mean"] == 1
        assert result["filler_words"]["basically"] == 1

    def test_filler_at_boundaries(self):
        """Detects fillers at start/end of text."""
        text = "um hello world uh"
        result = detect_filler_words(text)
        assert result["filler_words"]["um"] == 1
        assert result["filler_words"]["uh"] == 1

    def test_no_partial_matches(self):
        """Does not match partial words."""
        text = "I am actually working."
        result = detect_filler_words(text)
        # "actually" should match, "am" should not match "um"
        assert "actually" in result["filler_words"]
        assert "um" not in result["filler_words"]

    def test_all_defined_fillers_recognized(self):
        """All filler words in FILLER_WORDS have patterns."""
        # Just verify the constant is defined and non-empty
        assert len(FILLER_WORDS) > 0
        assert "um" in FILLER_WORDS
        assert "like" in FILLER_WORDS
        assert "you know" in FILLER_WORDS


class TestTranscriptionIntegration:
    """Integration-style tests for transcribe_audio (requires Whisper model)."""

    @pytest.mark.skipif(
        os.environ.get("WHISPER_TEST") != "1",
        reason="Set WHISPER_TEST=1 to run actual transcription tests"
    )
    def test_transcribe_simple_wav(self):
        """Test transcription with a generated silent WAV."""
        # Generate a small silent WAV programmatically
        import wave
        import io

        sample_rate = 16000
        duration = 0.5  # seconds
        n_frames = int(sample_rate * duration)

        buf = io.BytesIO()
        with wave.open(buf, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(sample_rate)
            wf.writeframes(b'\x00' * (n_frames * 2))  # silence

        wav_bytes = buf.getvalue()

        # Import here to avoid loading model in non-integration tests
        from stt_service import transcribe_audio

        result = transcribe_audio(wav_bytes, ".wav")
        assert "text" in result
        assert "filler_words" in result
        assert "filler_word_count" in result
        assert "language" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

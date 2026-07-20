"""
Speech-to-Text Service using OpenAI Whisper (local)
Provides audio transcription and filler-word detection.
"""

import os
import tempfile
import warnings
from typing import Dict, Any, Optional

# Suppress Whisper warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# Lazy-loaded model
_whisper_model = None
_model_name = os.environ.get("WHISPER_MODEL", "base")


def _get_model():
    """Load Whisper model on first use."""
    global _whisper_model
    if _whisper_model is None:
        try:
            import whisper
            _whisper_model = whisper.load_model(_model_name)
        except Exception as e:
            raise RuntimeError(
                f"Failed to load Whisper model '{_model_name}': {e}. "
                f"Ensure ffmpeg is installed and in PATH."
            )
    return _whisper_model


def _convert_to_wav(input_bytes: bytes, input_ext: str = ".webm") -> str:
    """
    Convert audio bytes to a temporary 16kHz mono WAV file.
    Returns path to the WAV file.
    """
    import ffmpeg

    # Write input to temp file
    with tempfile.NamedTemporaryFile(suffix=input_ext, delete=False) as f_in:
        f_in.write(input_bytes)
        in_path = f_in.name

    out_path = in_path.replace(input_ext, ".wav")

    try:
        # Convert to 16kHz mono WAV using ffmpeg
        (
            ffmpeg
            .input(in_path)
            .output(out_path, acodec='pcm_s16le', ac=1, ar=16000)
            .overwrite_output()
            .run(quiet=True, capture_stdout=True, capture_stderr=True)
        )
    except Exception as e:
        # Clean up input file on failure
        try:
            os.unlink(in_path)
        except Exception:
            pass
        raise RuntimeError(f"Audio conversion failed: {e}. Ensure ffmpeg is installed.")

    # Clean up input file
    try:
        os.unlink(in_path)
    except Exception:
        pass

    return out_path


def transcribe_audio(audio_bytes: bytes, file_ext: str = ".webm") -> Dict[str, Any]:
    """
    Transcribe audio bytes to text using Whisper and detect filler words.

    Args:
        audio_bytes: Raw audio file bytes
        file_ext: Original file extension (.webm, .mp3, .wav, .m4a, etc.)

    Returns:
        Dict with keys:
            - text: Transcribed text (str)
            - filler_words: Dict of filler word -> count
            - filler_word_count: Total filler word count (int)
            - language: Detected language code (str)
    """
    if not audio_bytes or len(audio_bytes) < 100:
        return {
            "text": "",
            "filler_words": {},
            "filler_word_count": 0,
            "language": "en",
            "error": "Audio too short or empty"
        }

    wav_path = None
    try:
        # Convert to WAV if needed
        if file_ext.lower() != ".wav":
            wav_path = _convert_to_wav(audio_bytes, file_ext)
            transcribe_path = wav_path
        else:
            # Write WAV directly to temp file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                f.write(audio_bytes)
                transcribe_path = f.name

        # Transcribe with Whisper
        model = _get_model()
        result = model.transcribe(
            transcribe_path,
            fp16=False,  # Use fp32 for CPU compatibility
            language="en",
            task="transcribe"
        )

        text = result.get("text", "").strip()
        language = result.get("language", "en")

        # Detect filler words
        filler_info = detect_filler_words(text)

        return {
            "text": text,
            "filler_words": filler_info["filler_words"],
            "filler_word_count": filler_info["total_count"],
            "language": language
        }

    except Exception as e:
        return {
            "text": "",
            "filler_words": {},
            "filler_word_count": 0,
            "language": "en",
            "error": str(e)
        }
    finally:
        # Cleanup temp WAV file
        if wav_path:
            try:
                os.unlink(wav_path)
            except Exception:
                pass
        if file_ext.lower() == ".wav":
            try:
                os.unlink(transcribe_path)
            except Exception:
                pass


# ── Filler Word Detection ───────────────────────────────────────────────────

FILLER_WORDS = [
    "um", "uh", "er", "ah", "hmm",
    "like", "you know", "i mean", "actually",
    "basically", "literally", "so", "well",
    "right", "okay", "ok", "sort of", "kind of",
    "i guess", "i suppose", "maybe", "just"
]

# Compile regex patterns for word-boundary matching
import re
_FILLER_PATTERNS = {}
for fw in FILLER_WORDS:
    # Escape special regex chars, match whole words
    pattern = r'\b' + re.escape(fw) + r'\b'
    _FILLER_PATTERNS[fw] = re.compile(pattern, re.IGNORECASE)


def detect_filler_words(text: str) -> Dict[str, Any]:
    """
    Detect common filler words in text.

    Returns:
        Dict with:
            - filler_words: Dict mapping filler word -> count
            - total_count: Sum of all filler word occurrences
    """
    if not text:
        return {"filler_words": {}, "total_count": 0}

    text_lower = text.lower()
    found = {}
    total = 0

    for word, pattern in _FILLER_PATTERNS.items():
        matches = pattern.findall(text_lower)
        if matches:
            count = len(matches)
            found[word] = count
            total += count

    return {
        "filler_words": found,
        "total_count": total
    }


# ── Public API ──────────────────────────────────────────────────────────────

def get_whisper_model_name() -> str:
    """Return the currently configured Whisper model name."""
    return _model_name


def preload_model() -> bool:
    """Preload the Whisper model (useful at app startup)."""
    try:
        _get_model()
        return True
    except Exception:
        return False

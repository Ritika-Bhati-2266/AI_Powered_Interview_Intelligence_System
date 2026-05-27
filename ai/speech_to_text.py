import os
import logging

logger = logging.getLogger(__name__)

# Global whisper model cache
_whisper_model = None

def get_whisper_model():
    """
    Loads and caches the Whisper model locally on CPU.
    Uses 'tiny' which is highly lightweight (~70MB) and fast on CPU.
    """
    global _whisper_model
    if _whisper_model is not None:
        return _whisper_model
    
    try:
        import whisper
        logger.info("Initializing local Whisper 'tiny' model...")
        _whisper_model = whisper.load_model("tiny")
        logger.info("Whisper model loaded successfully.")
        return _whisper_model
    except Exception as e:
        logger.error(f"Error loading local Whisper model: {e}")
        return None

def transcribe_audio(audio_path: str) -> str:
    """
    Transcribes the WAV/audio file located at audio_path.
    Includes a fallback in case Whisper is unavailable.
    """
    if not os.path.exists(audio_path):
        logger.error(f"Audio file not found: {audio_path}")
        return "Audio recording error. No file was received."
        
    model = get_whisper_model()
    if model is None:
        logger.warning("Whisper is unavailable. Using mock transcription fallback.")
        return "This is a local fallback transcript because the local Whisper model is still downloading. In a fully installed setup, your spoken words are transcribed locally."
        
    try:
        logger.info(f"Transcribing audio file: {audio_path}")
        result = model.transcribe(audio_path, fp16=False)
        transcript = result.get("text", "").strip()
        logger.info("Transcription completed.")
        return transcript
    except Exception as e:
        logger.error(f"Error during audio transcription: {e}")
        return "Transcription error occurred. Please try speaking again."

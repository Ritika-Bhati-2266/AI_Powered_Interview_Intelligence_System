import os
import json
import logging
from typing import Dict, Any, Optional

try:
    from vosk import Model, KaldiRecognizer
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False

logger = logging.getLogger("speech-engine-stt")

class VoskTranscriber:
    def __init__(self, model_path: str, sample_rate: int = 16000):
        """
        Initializes the Vosk Speech-to-Text transcriber.
        Requires a local Vosk model to be loaded.
        """
        self.model_path = model_path
        self.sample_rate = sample_rate
        self.model: Optional[Any] = None
        self.recognizer: Optional[Any] = None
        self._is_ready = False

        self._initialize_model()

    def _initialize_model(self):
        if not VOSK_AVAILABLE:
            logger.warning("Vosk package not installed. Running in mock/simulation mode.")
            return

        if not os.path.exists(self.model_path):
            logger.warning(
                f"Vosk model weights not found at: '{self.model_path}'. "
                "Speech recognition will operate in mock/simulation mode. "
                "To resolve, run 'models/download_weights.py' to download model weights."
            )
            return

        try:
            logger.info(f"Loading local offline Vosk model from: '{self.model_path}'...")
            self.model = Model(self.model_path)
            self.recognizer = KaldiRecognizer(self.model, self.sample_rate)
            self.recognizer.SetWords(True)  # Enable word level timestamps
            self._is_ready = True
            logger.info("Vosk offline model successfully loaded!")
        except Exception as e:
            logger.error(f"Failed to load Vosk model: {e}")

    def accept_wave_chunk(self, chunk: bytes) -> Dict[str, Any]:
        """
        Ingests a byte buffer of raw 16kHz 16-bit Mono PCM audio.
        Returns:
            Dict containing transcription text, timestamps, and confidence indicator.
        """
        if not self._is_ready or not self.recognizer:
            return self._simulate_transcription(chunk)

        try:
            # Process audio chunk
            if self.recognizer.AcceptWaveform(chunk):
                # Sentence completed (silence detected)
                res_str = self.recognizer.Result()
                res_dict = json.loads(res_str)
                
                # Extract words with timestamps
                words = res_dict.get("result", [])
                text = res_dict.get("text", "")
                
                if text:
                    logger.info(f"Final STT Transcript: '{text}'")
                    return {
                        "is_final": True,
                        "text": text,
                        "words": [
                            {
                                "word": w.get("word"),
                                "start": w.get("start"),
                                "end": w.get("end"),
                                "conf": w.get("conf")
                            } for w in words
                        ]
                    }
            else:
                # Partial transcription mid-sentence
                res_str = self.recognizer.PartialResult()
                res_dict = json.loads(res_str)
                partial_text = res_dict.get("partial", "")
                
                if partial_text:
                    return {
                        "is_final": False,
                        "text": partial_text,
                        "words": []
                    }
                    
        except Exception as e:
            logger.error(f"Error decoding wave chunk: {e}")
            return {"error": str(e), "is_final": False, "text": "", "words": []}

        return {"is_final": False, "text": "", "words": []}

    def _simulate_transcription(self, chunk: bytes) -> Dict[str, Any]:
        """
        Fallback simulation logic producing mock transcripts based on ingestion.
        Allows immediate out-of-the-box local pipeline evaluation without model file downloads.
        """
        # Very simple chunk analysis to simulate speech (e.g. if length of audio exceeds 50KB, yield text)
        chunk_len = len(chunk)
        if chunk_len == 0:
            return {"is_final": False, "text": "", "words": []}

        # Return a simulated result occasionally
        import random
        if random.random() < 0.05:
            words_pool = ["hello", "my", "name", "is", "alex", "i", "have", "five", "years", "of", "experience", "building", "systems", "with", "python", "and", "fastapi"]
            selected_words = random.sample(words_pool, random.randint(2, 6))
            
            simulated_words = []
            current_time = 0.0
            for w in selected_words:
                simulated_words.append({
                    "word": w,
                    "start": round(current_time, 2),
                    "end": round(current_time + 0.4, 2),
                    "conf": 0.98
                })
                current_time += 0.5

            return {
                "is_final": True,
                "text": " ".join(selected_words),
                "words": simulated_words
            }
        
        return {"is_final": False, "text": "", "words": []}

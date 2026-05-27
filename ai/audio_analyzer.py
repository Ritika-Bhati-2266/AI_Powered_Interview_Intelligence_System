import os
import logging
import numpy as np

logger = logging.getLogger(__name__)

def analyze_audio_metrics(audio_path: str, transcript: str) -> dict:
    """
    Extracts speech tempo, pause durations, hesitations, and RMS vocal energy.
    """
    metrics = {
        "duration_seconds": 12.0,
        "speaking_speed_wpm": 125.0,
        "pause_count": 1,
        "silence_duration": 2.0,
        "hesitation_rate": 0.16,
        "vocal_energy_rms": 0.04,
        "status": "fallback"
    }

    if not os.path.exists(audio_path):
        return metrics

    try:
        import librosa
        
        y, sr = librosa.load(audio_path, sr=None)
        if len(y) == 0:
            return metrics
            
        duration = librosa.get_duration(y=y, sr=sr)
        rms = librosa.feature.rms(y=y)
        avg_rms = float(np.mean(rms))
        
        # Split non-silent speech segments
        non_silent_intervals = librosa.effects.split(y, top_db=25)
        non_silent_duration = 0.0
        for interval in non_silent_intervals:
            start_sec = interval[0] / sr
            end_sec = interval[1] / sr
            non_silent_duration += (end_sec - start_sec)
            
        silence_duration = max(0.0, duration - non_silent_duration)
        
        pause_count = 0
        if len(non_silent_intervals) > 1:
            for i in range(len(non_silent_intervals) - 1):
                gap = (non_silent_intervals[i+1][0] - non_silent_intervals[i][1]) / sr
                if gap > 1.2:
                    pause_count += 1
                    
        hesitation_rate = silence_duration / duration if duration > 0 else 0.0
        
        word_count = len(transcript.split()) if transcript else 0
        speaking_speed_wpm = (word_count / duration) * 60.0 if duration > 0 else 120.0
        
        return {
            "duration_seconds": round(duration, 2),
            "speaking_speed_wpm": round(speaking_speed_wpm, 1),
            "pause_count": pause_count,
            "silence_duration": round(silence_duration, 2),
            "hesitation_rate": round(hesitation_rate, 2),
            "vocal_energy_rms": round(avg_rms, 4),
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error executing librosa audio analysis: {e}")
        try:
            import soundfile as sf
            info = sf.info(audio_path)
            metrics["duration_seconds"] = round(info.duration, 2)
            word_count = len(transcript.split()) if transcript else 0
            if info.duration > 0:
                metrics["speaking_speed_wpm"] = round((word_count / info.duration) * 60.0, 1)
        except Exception:
            pass
        return metrics

import os
import logging
import numpy as np

logger = logging.getLogger(__name__)

def analyze_audio_metrics(audio_path: str, transcript: str) -> dict:
    """
    Analyzes physical speaking properties of a WAV file using librosa.
    Returns WPM (Words Per Minute), pause count, total silence duration,
    hesitation index, and average vocal energy.
    """
    # Default return structure (used as fallback)
    metrics = {
        "duration_seconds": 15.0,
        "speaking_speed_wpm": 120.0,
        "pause_count": 2,
        "silence_duration": 3.0,
        "hesitation_rate": 0.20,
        "vocal_energy_rms": 0.05,
        "status": "fallback"
    }

    if not os.path.exists(audio_path):
        logger.warning(f"Audio file not found for signal analysis: {audio_path}")
        return metrics

    try:
        import librosa
        import soundfile as sf
        
        logger.info(f"Loading audio file for librosa analysis: {audio_path}")
        y, sr = librosa.load(audio_path, sr=None)
        
        if len(y) == 0:
            logger.warning("Empty audio file received.")
            return metrics
            
        duration = librosa.get_duration(y=y, sr=sr)
        
        # Calculate RMS energy (Vocal confidence/volume presence)
        rms = librosa.feature.rms(y=y)
        avg_rms = float(np.mean(rms))
        
        # Detect non-silent intervals (threshold of top_db=25 is standard for speech)
        # Anything below 25 dB from peak is treated as silence
        non_silent_intervals = librosa.effects.split(y, top_db=25)
        
        non_silent_duration = 0.0
        for interval in non_silent_intervals:
            start_sec = interval[0] / sr
            end_sec = interval[1] / sr
            non_silent_duration += (end_sec - start_sec)
            
        silence_duration = max(0.0, duration - non_silent_duration)
        
        # Identify pauses (periods of silence between speech segments longer than 1.5 seconds)
        pause_count = 0
        if len(non_silent_intervals) > 1:
            for i in range(len(non_silent_intervals) - 1):
                # Gap between end of current segment and start of next segment
                gap = (non_silent_intervals[i+1][0] - non_silent_intervals[i][1]) / sr
                if gap > 1.2:  # Pause threshold in seconds
                    pause_count += 1
                    
        # Hesitation index (Ratio of silence to total duration)
        hesitation_rate = silence_duration / duration if duration > 0 else 0.0
        
        # Calculate WPM based on transcription length
        word_count = len(transcript.split()) if transcript else 0
        if duration > 0:
            # Word counts over full duration
            speaking_speed_wpm = (word_count / duration) * 60.0
        else:
            speaking_speed_wpm = 120.0
            
        # Normalize speed (ideal speech tempo is 110 - 150 WPM)
        speaking_speed_wpm = round(speaking_speed_wpm, 1)
        
        logger.info(f"Audio analysis complete. Duration: {duration:.2f}s, WPM: {speaking_speed_wpm}, Pauses: {pause_count}")
        
        return {
            "duration_seconds": round(duration, 2),
            "speaking_speed_wpm": speaking_speed_wpm,
            "pause_count": pause_count,
            "silence_duration": round(silence_duration, 2),
            "hesitation_rate": round(hesitation_rate, 2),
            "vocal_energy_rms": round(avg_rms, 4),
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error executing librosa audio analysis: {e}. Returning mock feedback.")
        # Attempt to estimate duration from file size if soundfile fails
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

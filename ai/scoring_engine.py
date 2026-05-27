import logging

logger = logging.getLogger(__name__)

def compute_scores(
    similarity_score: float,
    keyword_score: float,
    filler_density: float,
    filler_count: int,
    wpm: float,
    pause_count: int,
    hesitation_rate: float,
    vocal_rms: float,
    transcript_word_count: int,
    ideal_word_count: int
) -> dict:
    """
    Computes unified scoring across Technical, Communication, Confidence, and Overall dimensions.
    """
    # 1. Technical Score (50% Semantic Sim + 40% Keyword Match + 10% Completeness)
    completeness = min(1.0, (transcript_word_count / (ideal_word_count * 0.7))) if ideal_word_count > 0 else 1.0
    raw_tech = (similarity_score * 50) + (keyword_score * 40) + (completeness * 10)
    technical_score = round(max(10.0, min(100.0, raw_tech)), 1)
    
    # 2. Communication Score (Base 100. Penalize filler density, out-of-bound WPM, and pauses)
    comm_score = 100.0
    if filler_density > 0.02:
        comm_score -= min(30.0, (filler_density - 0.02) * 400.0)
    
    if wpm < 100:
        comm_score -= min(20.0, (100 - wpm) * 0.4)
    elif wpm > 160:
        comm_score -= min(20.0, (wpm - 160) * 0.4)
        
    if pause_count > 3:
        comm_score -= min(15.0, (pause_count - 3) * 3)
        
    communication_score = round(max(15.0, comm_score), 1)
    
    # 3. Confidence Score (Calculated from hesitation rate, volume energy, and low pauses)
    # Ideal RMS is around 0.05. Normalize RMS.
    norm_rms = min(1.0, vocal_rms / 0.05) if vocal_rms > 0 else 0.5
    hesitation_penalty = hesitation_rate * 50.0
    
    raw_confidence = (norm_rms * 40) + (max(0.0, 60.0 - hesitation_penalty))
    confidence_score = round(max(10.0, min(100.0, raw_confidence)), 1)
    
    # 4. Overall Rating
    overall_score = round((technical_score + communication_score + confidence_score) / 3.0, 1)
    
    return {
        "technical": technical_score,
        "communication": communication_score,
        "confidence": confidence_score,
        "overall": overall_score
    }

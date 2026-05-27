import logging

logger = logging.getLogger(__name__)

def generate_feedback(
    similarity_score: float,
    keyword_results: dict,
    filler_results: dict,
    audio_results: dict,
    scores: dict
) -> dict:
    """
    Synthesizes numerical evaluations into structural bullet review suggestions.
    """
    strengths = []
    weaknesses = []
    suggestions = []
    recommended_topics = []

    # Technical reviews
    if similarity_score >= 0.7:
        strengths.append("Exceptional coverage of technical concepts with accurate context matching.")
    elif similarity_score >= 0.5:
        strengths.append("Satisfactory conceptual coverage matching ideal reference standards.")
    else:
        weaknesses.append("Significant technical depth gaps flagged. Answer lacked foundational focus.")
        suggestions.append("Structure technical concepts chronologically: define, state operations, then list trade-offs.")

    # Keyword review
    matched_kws = keyword_results.get("matched", [])
    missing_kws = keyword_results.get("missing", [])
    if len(matched_kws) >= 3:
        strengths.append(f"Successfully integrated key terminology: {', '.join(matched_kws[:3])}.")
    if missing_kws:
        weaknesses.append(f"Omitted crucial operational terminology: {', '.join(missing_kws[:3])}.")
        suggestions.append(f"Try to explicitly detail terms like {', '.join(missing_kws[:2])} to show domain precision.")

    # Articulation speed review
    wpm = audio_results.get("speaking_speed_wpm", 120.0)
    if wpm >= 110 and wpm <= 150:
        strengths.append(f"Engaging speaking tempo of {wpm} WPM making your response easy to follow.")
    elif wpm < 100:
        weaknesses.append(f"Slow articulation pacing ({wpm} WPM), which can cause the interviewer to lose focus.")
        suggestions.append("Slightly increase your reading and speaking pace. Aim to articulate ~130 Words Per Minute.")
    else:
        weaknesses.append(f"Rapid speaking pace ({wpm} WPM), which can make complex ideas difficult to track.")
        suggestions.append("Consciously slow down your transitions. Take short breaths between separate technical stages.")

    # Fillers review
    filler_count = filler_results.get("count", 0)
    if filler_count > 3:
        weaknesses.append(f"Frequent verbal filler words ({filler_count} instances) interrupted delivery fluidness.")
        suggestions.append("When thinking of the next point, pause silently instead of vocalizing fillers like 'like' or 'uh'.")
    else:
        strengths.append("Crisp speech delivery containing minimal verbal fillers.")

    # Attention & hesitation warnings
    hesitation = audio_results.get("hesitation_rate", 0.0)
    if hesitation > 0.25:
        weaknesses.append("High hesitation intervals or long silent gaps logged.")
        suggestions.append("Practice formulating mock structures using a standard outline (Problem, Approach, Solution) to reduce search gaps.")

    if missing_kws:
        recommended_topics.append("Deep dive into the operational mechanics of the target question.")
        recommended_topics.append("Review standard terminology card references for this technical category.")
    else:
        recommended_topics.append("Proceed to advanced problem-solving challenges in this domain.")

    return {
        "strengths": strengths,
        "weaknesses": weaknesses,
        "suggestions": suggestions,
        "recommended_topics": recommended_topics
    }

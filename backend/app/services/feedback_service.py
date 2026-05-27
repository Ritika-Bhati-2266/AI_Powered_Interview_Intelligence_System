import logging
from app.services.nlp_service import compute_semantic_similarity, analyze_keywords, count_filler_words
from app.services.audio_service import analyze_audio_metrics

logger = logging.getLogger(__name__)

def evaluate_response(
    question_text: str,
    ideal_answer: str,
    keywords: str,
    transcript: str,
    audio_path: str,
    eye_contact_score: float,
    attention_score: float,
    smile_score: float
) -> dict:
    """
    Evaluates a candidate's answer using local AI and audio diagnostics.
    Combines NLP scores, Librosa metrics, and client-side CV parameters.
    Generates technical, communication, confidence, and overall ratings with diagnostic text.
    """
    logger.info("Executing unified response evaluation...")
    
    # 1. NLP Processing
    similarity_score = compute_semantic_similarity(transcript, ideal_answer)
    kw_result = analyze_keywords(transcript, keywords)
    filler_result = count_filler_words(transcript)
    
    # 2. Audio Processing
    audio_result = analyze_audio_metrics(audio_path, transcript)
    
    # --- 3. Compute Component Scores ---
    
    # A. Technical Score (Weight: 50% Semantic Sim + 40% Keywords + 10% Length Completeness)
    transcript_len = len(transcript.split()) if transcript else 0
    ideal_len = len(ideal_answer.split())
    # Completeness capped at 100%
    completeness = min(1.0, (transcript_len / (ideal_len * 0.7))) if ideal_len > 0 else 1.0
    
    raw_tech = (similarity_score * 50) + (kw_result["score"] * 40) + (completeness * 10)
    # Ensure realistic range
    technical_score = round(max(10.0, min(100.0, raw_tech)), 1)
    
    # B. Communication Score (Base 100. Penalize filler density, out-of-bound WPM, and pauses)
    comm_score = 100.0
    
    # Penalize filler words (e.g. density > 5% drops score)
    filler_density = filler_result["density"]
    if filler_density > 0.02:
        # Deduct up to 30 points
        comm_score -= min(30.0, (filler_density - 0.02) * 400.0)
        
    # Penalize speech speed (ideal WPM is 110 - 150)
    wpm = audio_result["speaking_speed_wpm"]
    if wpm < 100:
        # Too slow: deduct up to 20 points
        comm_score -= min(20.0, (100 - wpm) * 0.4)
    elif wpm > 160:
        # Too fast: deduct up to 20 points
        comm_score -= min(20.0, (wpm - 160) * 0.4)
        
    # Penalize structural hesitations / pauses
    pause_cnt = audio_result["pause_count"]
    if pause_cnt > 3:
        comm_score -= min(15.0, (pause_cnt - 3) * 3)
        
    communication_score = round(max(15.0, comm_score), 1)
    
    # C. Confidence Score (Weight: 35% Eye Contact + 35% Focus/Attention + 30% Vocal Presence)
    # Vocal Presence is based on low hesitation rate and standard volume energy
    hesitation_penalty = audio_result["hesitation_rate"] * 50.0  # High hesitation cuts score
    vocal_presence = max(0.0, 100.0 - hesitation_penalty)
    
    raw_confidence = (eye_contact_score * 35) + (attention_score * 35) + (vocal_presence * 0.3)
    confidence_score = round(max(10.0, min(100.0, raw_confidence)), 1)
    
    # D. Overall Score (Average of the three cores)
    overall_score = round((technical_score + communication_score + confidence_score) / 3.0, 1)
    
    # --- 4. Synthesize Qualitative Feedback ---
    strengths = []
    weaknesses = []
    suggestions = []
    recommended_topics = []
    
    # Evaluate Strengths/Weaknesses from Tech
    if similarity_score >= 0.7:
        strengths.append("Excellent conceptual coverage, demonstrating a strong theoretical understanding of the topic.")
    elif similarity_score >= 0.5:
        strengths.append("Covered the core ideas of the question satisfactorily.")
    else:
        weaknesses.append("Struggled to cover the fundamental concepts of the question. Answer lacked core technical depth.")
        suggestions.append("Structure technical concepts chronologically: state the definition first, explain operations, then cover pros/cons.")

    if len(kw_result["matched"]) >= 3:
        strengths.append(f"Successfully integrated essential industry keywords: {', '.join(kw_result['matched'][:3])}.")
    if kw_result["missing"]:
        weaknesses.append(f"Omitted crucial terminology, such as: {', '.join(kw_result['missing'][:3])}.")
        suggestions.append(f"Make sure to explicitly mention key terms like {', '.join(kw_result['missing'][:2])} to signal technical precision.")
        
    # Evaluate Speech Metrics
    if wpm >= 110 and wpm <= 150:
        strengths.append(f"Paced the response at an optimal speaking speed of {wpm} WPM, making the articulation highly digestible.")
    elif wpm < 90:
        weaknesses.append("Speaking pace was notably slow, which can cause the interviewer's attention to wander.")
        suggestions.append("Try to increase your speaking tempo slightly. Practice reading technical text aloud with a timer to target ~130 WPM.")
    else:
        weaknesses.append("Speaking pace was very rapid, which can make complex technical steps hard to follow.")
        suggestions.append("Consciously slow down your pacing, especially when transitioning between separate ideas. Take short deep breaths.")

    if filler_result["count"] > 3:
        weaknesses.append(f"Utilized a high frequency of filler phrases ({filler_result['count']} counts detected).")
        suggestions.append("When searching for the next word, replace vocal fillers like 'uh' or 'like' with silent pauses. Silence sounds much more professional.")
    else:
        strengths.append("Kept the delivery extremely crisp with minimal filler words.")

    # Evaluate CV metrics
    if eye_contact_score >= 80:
        strengths.append("Maintained exceptional, direct eye contact with the camera, establishing a highly confident presence.")
    elif eye_contact_score < 60:
        weaknesses.append("Frequent gaze drift detected. Looking away often can convey hesitation or uncertainty.")
        suggestions.append("Position your camera directly at eye level and make a conscious effort to look at the lens rather than secondary screens.")
        
    if attention_score < 70:
        weaknesses.append("Frequent head movements or focus distraction flagged.")
        suggestions.append("Maintain a stable posture and keep your head centered relative to the screen to project attentiveness.")

    # Recommendation mapping based on missing keywords or categories
    # Provide simple standard topic recommendations
    if kw_result["missing"]:
        recommended_topics.append("Deep dive into the operational mechanics of the target question.")
        recommended_topics.append("Review standard terminology card references for this technical category.")
    else:
        recommended_topics.append("Proceed to advanced problem-solving challenges in this domain.")
        
    # Compile text
    feedback_text = (
        f"### Technical Evaluation\n"
        f"Your technical response achieved a score of **{technical_score}%**. "
        f"You matched **{len(kw_result['matched'])} out of {len(kw_result['matched'])+len(kw_result['missing'])}** primary concepts. "
        f"{'You covered the ideal answer robustly.' if similarity_score > 0.6 else 'There is a noticeable gap between your response and the ideal benchmark answer.'}\n\n"
        
        f"### Communication & Vocal Delivery\n"
        f"Your speaking cadence logged **{wpm} Words Per Minute** with **{pause_cnt} long pauses**. "
        f"We flagged **{filler_result['count']} verbal filler words** in your response. "
        f"A communication grade of **{communication_score}%** was awarded based on articulation fluidity.\n\n"
        
        f"### Visual Presentation & Confidence\n"
        f"Visual tracking registered an average eye-contact score of **{eye_contact_score}%** and attention consistency of **{attention_score}%**. "
        f"Vocal energy dynamics and focus stability calculated a **{confidence_score}%** confidence coefficient.\n\n"
        
        f"### Strengths\n" + "".join([f"- {s}\n" for s in strengths]) + "\n"
        f"### Areas for Improvement\n" + "".join([f"- {w}\n" for w in weaknesses]) + "\n"
        f"### Actionable Recommendations\n" + "".join([f"- {su}\n" for su in suggestions])
    )

    return {
        "similarity_score": round(similarity_score * 100, 1),
        "technical_score": technical_score,
        "communication_score": communication_score,
        "confidence_score": confidence_score,
        "overall_score": overall_score,
        "feedback": feedback_text,
        "audio_metrics": audio_result,
        "nlp_metrics": {
            "filler_count": filler_result["count"],
            "matched_keywords": kw_result["matched"],
            "missing_keywords": kw_result["missing"]
        }
    }

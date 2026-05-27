import logging
import re
import numpy as np

logger = logging.getLogger(__name__)

# Global model caches
_nlp_spacy = None
_sentence_model = None

FILLER_WORDS = [
    r"\bumm?\b", r"\buhh?\b", r"\blike\b", r"\bactually\b", 
    r"\bbasically\b", r"\byou know\b", r"\bliterally\b", r"\bi mean\b"
]

def get_spacy_model():
    """
    Loads and caches spaCy en_core_web_sm model with auto-download fallback.
    """
    global _nlp_spacy
    if _nlp_spacy is not None:
        return _nlp_spacy
    
    try:
        import spacy
        try:
            _nlp_spacy = spacy.load("en_core_web_sm")
        except IOError:
            logger.warning("spaCy model 'en_core_web_sm' not found. Downloading...")
            from spacy.cli import download
            download("en_core_web_sm")
            _nlp_spacy = spacy.load("en_core_web_sm")
        return _nlp_spacy
    except Exception as e:
        logger.error(f"Failed to load spaCy model: {e}")
        return None

def get_sentence_model():
    """
    Loads and caches SentenceTransformers model locally.
    Uses 'all-MiniLM-L6-v2' (~90MB).
    """
    global _sentence_model
    if _sentence_model is not None:
        return _sentence_model
    
    try:
        from sentence_transformers import SentenceTransformer
        logger.info("Initializing local SentenceTransformer 'all-MiniLM-L6-v2'...")
        _sentence_model = SentenceTransformer("all-MiniLM-L6-v2")
        return _sentence_model
    except Exception as e:
        logger.error(f"Error loading SentenceTransformer: {e}")
        return None

def compute_semantic_similarity(user_text: str, ideal_text: str) -> float:
    """
    Calculates cosine similarity between user response and ideal response.
    """
    if not user_text or not ideal_text:
        return 0.0

    model = get_sentence_model()
    if model is None:
        return float(calculate_fallback_similarity(user_text, ideal_text))

    try:
        embeddings = model.encode([user_text, ideal_text])
        vec_user = embeddings[0]
        vec_ideal = embeddings[1]
        
        dot_product = np.dot(vec_user, vec_ideal)
        norm_user = np.linalg.norm(vec_user)
        norm_ideal = np.linalg.norm(vec_ideal)
        
        if norm_user == 0 or norm_ideal == 0:
            return 0.0
            
        similarity = dot_product / (norm_user * norm_ideal)
        normalized_sim = (similarity + 1) / 2.0 if similarity >= -1 else 0.0
        return float(round(normalized_sim, 3))
    except Exception as e:
        logger.error(f"Error calculating similarity: {e}")
        return float(calculate_fallback_similarity(user_text, ideal_text))

def analyze_keywords(user_text: str, keyword_string: str) -> dict:
    """
    Checks matching status against question key concepts.
    """
    if not keyword_string:
        return {"matched": [], "missing": [], "score": 1.0}
        
    required_keywords = [k.strip().lower() for k in keyword_string.split(",") if k.strip()]
    if not required_keywords:
        return {"matched": [], "missing": [], "score": 1.0}
        
    nlp = get_spacy_model()
    user_clean = user_text.lower()
    
    if nlp is not None:
        try:
            doc = nlp(user_clean)
            lemmas = {token.lemma_ for token in doc}
            
            matched = []
            missing = []
            
            for keyword in required_keywords:
                if " " in keyword:
                    if keyword in user_clean:
                        matched.append(keyword)
                    else:
                        missing.append(keyword)
                else:
                    kw_doc = nlp(keyword)
                    kw_lemma = kw_doc[0].lemma_ if len(kw_doc) > 0 else keyword
                    if keyword in user_clean or kw_lemma in lemmas or keyword in lemmas:
                        matched.append(keyword)
                    else:
                        missing.append(keyword)
        except Exception as e:
            logger.error(f"spaCy keyword processing failed: {e}")
            matched, missing = run_simple_keyword_check(user_clean, required_keywords)
    else:
        matched, missing = run_simple_keyword_check(user_clean, required_keywords)
        
    score = len(matched) / len(required_keywords) if required_keywords else 1.0
    return {
        "matched": matched,
        "missing": missing,
        "score": round(score, 2)
    }

def count_filler_words(text: str) -> dict:
    """
    Counts verbal filler frequencies.
    """
    if not text:
        return {"count": 0, "density": 0.0, "details": {}}
        
    clean_text = text.lower()
    total_words = len(clean_text.split())
    
    count = 0
    details = {}
    
    for pattern in FILLER_WORDS:
        matches = re.findall(pattern, clean_text)
        if matches:
            kw = matches[0]
            details[kw] = len(matches)
            count += len(matches)
            
    density = count / total_words if total_words > 0 else 0.0
    return {
        "count": count,
        "density": round(density, 3),
        "details": details
    }

def run_simple_keyword_check(text: str, required_keywords: list) -> tuple:
    matched = []
    missing = []
    for keyword in required_keywords:
        pattern = r"\b" + re.escape(keyword) + r"\b"
        if re.search(pattern, text):
            matched.append(keyword)
        else:
            missing.append(keyword)
    return matched, missing

def calculate_fallback_similarity(text_a: str, text_b: str) -> float:
    words_a = set(re.findall(r"\w+", text_a.lower()))
    words_b = set(re.findall(r"\w+", text_b.lower()))
    if not words_a or not words_b:
        return 0.0
    intersection = words_a.intersection(words_b)
    union = words_a.union(words_b)
    return len(intersection) / len(union)

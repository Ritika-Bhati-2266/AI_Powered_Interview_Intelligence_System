"""
AI Service Module
Handles all communication with LLM providers (Groq cloud API or local Ollama).
Provides prompt templates for question generation, evaluation, and reporting.
"""

import json
import os
import requests
import time
import re

from stt_service import detect_filler_words

# ── Provider selection ──────────────────────────────────────────────────────────
# Groq (cloud) is preferred when GROQ_API_KEY is set; otherwise falls back to Ollama (local).
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"

# Ollama fallback (local dev)
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2:latest")
OLLAMA_ENDPOINT = f"{OLLAMA_BASE_URL}/api/generate"

MAX_RETRIES = 2
RETRY_DELAY = 1  # seconds
REQUEST_TIMEOUT = 120  # seconds (generation can be slow on CPU, cold-start delay)


def _call_groq(prompt: str, system_prompt: str = None, temperature: float = 0.7) -> str:
    """Send a prompt to Groq's OpenAI-compatible API and return the text response."""
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 4096,
    }

    for attempt in range(MAX_RETRIES + 1):
        try:
            resp = requests.post(GROQ_ENDPOINT, json=payload, headers=headers, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()

        except requests.exceptions.ConnectionError:
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
                continue
            return "[OLLAMA_CONNECTION_ERROR] Cannot connect to Groq API. Check your internet connection."
        except requests.exceptions.Timeout:
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
                continue
            return "[OLLAMA_TIMEOUT] Groq API request timed out."
        except requests.exceptions.RequestException as e:
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
                continue
            # Try to extract a meaningful error from the response body
            try:
                detail = e.response.json().get("error", {}).get("message", str(e))
            except Exception:
                detail = str(e)
            return f"[OLLAMA_ERROR] Groq API error: {detail}"
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            return f"[PARSE_ERROR] Could not parse Groq response: {str(e)}"


def _call_ollama(prompt: str, system_prompt: str = None, temperature: float = 0.7) -> str:
    """
    Send a prompt to Ollama and return the raw text response.
    Handles connection errors, timeouts, and malformed responses.
    """
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "temperature": temperature,
        "num_predict": 2048,
    }
    if system_prompt:
        payload["system"] = system_prompt

    for attempt in range(MAX_RETRIES + 1):
        try:
            resp = requests.post(OLLAMA_ENDPOINT, json=payload, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            return data.get("response", "").strip()

        except requests.exceptions.ConnectionError:
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
                continue
            return "[OLLAMA_CONNECTION_ERROR] Cannot connect to Ollama. Ensure it's running (ollama serve)."
        except requests.exceptions.Timeout:
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
                continue
            return "[OLLAMA_TIMEOUT] The model took too long to respond. Try a smaller model."
        except requests.exceptions.RequestException as e:
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
                continue
            return f"[OLLAMA_ERROR] {str(e)}"
        except (json.JSONDecodeError, KeyError) as e:
            return f"[PARSE_ERROR] Could not parse Ollama response: {str(e)}"


def _call_llm(prompt: str, system_prompt: str = None, temperature: float = 0.7) -> str:
    """
    Route a prompt to the available LLM provider.
    Uses Groq (cloud) when GROQ_API_KEY is set, otherwise falls back to Ollama (local).
    """
    if GROQ_API_KEY:
        return _call_groq(prompt, system_prompt, temperature)
    return _call_ollama(prompt, system_prompt, temperature)


def _extract_json(text: str):
    """
    Extract JSON from model output, handling markdown-wrapped json blocks
    and partial/trailing text.
    """
    # Try to find a JSON block between ```json and ``` markers
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', text)
    if json_match:
        text = json_match.group(1).strip()

    # Try to find the first { ... } or [ ... ] block
    for delim in ('{', '['):
        start = text.find(delim)
        if start == -1:
            continue
        # Find the matching closing bracket
        depth = 0
        end = -1
        in_string = False
        escape = False
        for i in range(start, len(text)):
            ch = text[i]
            if escape:
                escape = False
                continue
            if ch == '\\':
                escape = True
                continue
            if ch == '"':
                in_string = not in_string
                continue
            if in_string:
                continue
            if ch == '{' or ch == '[':
                depth += 1
            elif ch == '}' or ch == ']':
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        if end > 0:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                pass

    # Last resort: try to parse the whole thing
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


# ── Company-Specific HR/Behavioral Style Patterns ───────────────────────────

COMPANY_HR_STYLE = {
    "google": {
        "label": "Google Googleyness",
        "principles": [
            "Handling Ambiguity",
            "Collaboration Across Teams",
            "Using Data to Make Decisions",
            "Changing Your Mind Based on Evidence",
            "Working Without Clear Direction",
            "Intellectual Humility",
            "Comfort with Being Wrong",
        ],
        "style_note": (
            "Google's Googleyness/behavioral rounds are known for asking about: "
            "how you handle ambiguity, working without clear direction, collaborating "
            "across teams, changing your mind based on data, and intellectual humility. "
            "Questions often explore ethical reasoning and comfort with being wrong."
        ),
    },
    "amazon": {
        "label": "Amazon Leadership Principles",
        "principles": [
            "Customer Obsession",
            "Ownership",
            "Invent and Simplify",
            "Are Right, A Lot",
            "Learn and Be Curious",
            "Hire and Develop the Best",
            "Insist on the Highest Standards",
            "Think Big",
            "Bias for Action",
            "Frugality",
            "Earn Trust",
            "Dive Deep",
            "Have Backbone; Disagree and Commit",
            "Deliver Results",
            "Strive to be Earth's Best Employer",
            "Success and Scale Bring Broad Responsibility",
        ],
        "style_note": (
            "Amazon behavioral rounds are defined by the 16 Leadership Principles. "
            "EVERY behavioral question MUST assess one specific Leadership Principle. "
            "Interviewers expect STAR-format (Situation, Task, Action, Result) answers "
            "with specific, quantified examples."
        ),
    },
    "microsoft": {
        "label": "Microsoft Growth Mindset",
        "principles": [
            "Growth Mindset",
            "Learning from Failure",
            "Inclusive Collaboration",
            "Customer Obsession (Microsoft version)",
            "Making a Difference",
        ],
        "style_note": (
            "Microsoft's 'As Appropriate' (AA) rounds focus on growth mindset: "
            "'tell me about a time you failed and what you learned'. Questions explore "
            "collaboration, inclusive behavior, how you handle feedback, and your approach "
            "to learning new technologies."
        ),
    },
    "meta": {
        "label": "Meta Behavioral",
        "principles": [
            "Direct Communication",
            "Moving Fast",
            "Conflict Resolution",
            "Long-Term Impact",
            "Being Bold",
        ],
        "style_note": (
            "Meta behavioral rounds feature direct conflict-handling questions: "
            "'tell me about a time you disagreed with a decision', 'how do you handle "
            "a fast-paced environment', and questions about pushing back respectfully. "
            "Meta values speed, directness, and impact-driven thinking."
        ),
    },
    "apple": {
        "label": "Apple Team Fit",
        "principles": [
            "Attention to Detail",
            "Design Thinking",
            "Cross-Functional Collaboration",
            "Ownership and Accountability",
        ],
        "style_note": (
            "Apple behavioral/team-fit rounds focus on attention to detail, design thinking, "
            "cross-functional collaboration, and accountability. Questions explore your "
            "work ethic, pride in craftsmanship, and how you handle high expectations."
        ),
    },
    "flipkart": {
        "label": "Flipkart Culture Fit",
        "principles": [
            "Ownership and Bias for Action",
            "Customer First",
            "Frugality",
            "Data-Driven Decisions",
        ],
        "style_note": (
            "Flipkart HR rounds explore culture fit around ownership, customer-first mindset, "
            "frugality, and data-driven decision making. Questions focus on e-commerce context "
            "and fast-paced startup-style work."
        ),
    },
    "tcs": {
        "label": "TCS HR",
        "principles": [
            "Communication Skills",
            "Willingness to Relocate",
            "Flexibility",
            "Teamwork",
        ],
        "style_note": (
            "TCS HR rounds ask simpler, standard questions: willingness to relocate, "
            "why TCS, strengths/weaknesses, career goals, ability to work in teams. "
            "Focus is on communication clarity and basic professionalism."
        ),
    },
    "infosys": {
        "label": "Infosys HR",
        "principles": [
            "Communication Skills",
            "Motivation and Goals",
            "Teamwork",
            "Background and Experience",
        ],
        "style_note": (
            "Infosys HR rounds focus on communication, career motivation, background, "
            "and teamwork. Questions are standard but assess clarity of thought and "
            "professional communication."
        ),
    },
    "wipro": {
        "label": "Wipro HR",
        "principles": [
            "Communication Skills",
            "Culture Fit",
            "Motivation",
        ],
        "style_note": (
            "Wipro HR rounds assess communication, culture fit, and motivation. "
            "Expect standard questions about strengths, weaknesses, career aspirations, "
            "and why you want to join Wipro."
        ),
    },
    "hcl": {
        "label": "HCL HR",
        "principles": [
            "Communication",
            "Background and Experience",
            "Teamwork",
        ],
        "style_note": (
            "HCL HR rounds ask about communication skills, background, experience, "
            "and teamwork. Standard HR questions with emphasis on basic professionalism."
        ),
    },
    "general": {
        "label": "General HR",
        "principles": [
            "Teamwork",
            "Leadership",
            "Problem-Solving",
            "Communication",
        ],
        "style_note": (
            "Standard behavioral interview questions assessing soft skills, teamwork, "
            "leadership, and problem-solving ability using the STAR format."
        ),
    },
}

# Companies with specifically documented strong HR/behavioral patterns
HR_PATTERN_COMPANIES = {"google", "amazon", "microsoft", "meta", "apple", "flipkart"}

# Companies with simpler/standard HR patterns
SIMPLE_HR_COMPANIES = {"tcs", "infosys", "wipro", "hcl"}


def get_company_hr_context(company: str) -> dict:
    """Get the HR/behavioral style context for a given company."""
    company_lower = company.lower().strip()
    style = COMPANY_HR_STYLE.get(company_lower, COMPANY_HR_STYLE["general"])
    return {
        "label": style["label"],
        "principles": style["principles"],
        "style_note": style["style_note"],
    }


def _get_company_coding_prompt(company: str) -> str:
    """Get company-specific coding round style context for prompts."""
    from coding_questions_bank import get_coding_style_context
    return get_coding_style_context(company)


def _get_company_coding_label(company: str) -> str:
    """Get the short display label for a company's coding style."""
    from coding_questions_bank import get_coding_style_label
    return get_coding_style_label(company)


# ── Prompt Templates ───────────────────────────────────────────────────────────

QUESTION_GENERATION_SYSTEM = """You are a professional interviewer at a top technology company.
You must generate thoughtful, relevant interview questions that test real-world knowledge.
Your questions should be specific, clear, and appropriate for the candidate's experience level.

IMPORTANT: When the question is for a specific company (e.g., Google, Amazon, Microsoft, Meta),
match the AUTHENTIC interview style that company is actually known for — not generic questions.
Use the company-specific style guidance provided in the prompt below."""


def generate_question(role: str, experience: str, skills: list, category: str,
                      difficulty: str, context: str = "", resume_text: str = "",
                      round_info: dict = None, is_resume_phase: bool = False,
                      company: str = "General", previous_questions: list = None) -> str:
    """
    Generate an interview question based on candidate profile.
    
    Args:
        role: Job role (e.g., "Python Developer")
        experience: Years of experience
        skills: List of skills extracted from resume
        category: "technical", "behavioral", or "project"
        difficulty: "easy", "medium", "hard"
        context: Previous Q&A context for follow-ups
        resume_text: Extracted resume content
        previous_questions: List of questions previously asked in this session
    
    Returns:
        Question string
    """
    skills_str = ", ".join(skills) if skills else "general programming"
    company_lower = company.lower().strip() if company else "general"
    newline = chr(10)

    context_part = (
        f'Previous Interview Context (generate a relevant follow-up question based on this):{newline}{context[:1500]}'
        if context else 'This is the start of the interview - generate a good opening question.'
    )

    # Anti-repetition section from previous session questions
    prev_q_part = ""
    if previous_questions:
        recent_qs = [q.strip() for q in previous_questions[-5:] if q and isinstance(q, str) and q.strip()]
        if recent_qs:
            formatted_qs = "\n".join([f"- {q}" for q in recent_qs])
            prev_q_part = (
                f"PREVIOUSLY ASKED QUESTIONS IN THIS SESSION (DO NOT REPEAT THESE TOPICS):\n"
                f"{formatted_qs}\n\n"
                f"CRITICAL TOPIC VARIETY RULE:\n"
                f"Do NOT ask about any technology, database, framework, project, or concept already covered in the questions above. "
                f"(For example, if caching, Redis, Express.js, or system architecture was already asked, pick a COMPLETELY DIFFERENT skill or project from the candidate's resume/skills list)."
            )

    resume_part = (
        f'Resume Context:{newline}{resume_text[:4000]}'
        if resume_text else ''
    )

    # Build round-specific instruction
    round_focus = ""
    round_type_instruction = ""
    company_round_style = ""
    if round_info:
        round_focus = round_info.get("focus", "")
        rtype = round_info.get("type", category)

        # Company-specific coding style
        if rtype == "coding":
            coding_style = _get_company_coding_prompt(company_lower)
            round_type_instruction = (
                "This is a CODING round. Ask a problem-solving question that requires "
                "writing code, discussing algorithms, data structures, time/space complexity, "
                "and edge cases. "
                "CRITICAL: Output ONLY a short question (1-2 sentences) that asks the candidate "
                "to design, explain, or implement something. Do NOT write actual code, class "
                "definitions, pseudocode, or any part of the solution yourself. You are the "
                "interviewer asking the question, not the candidate answering it. If you need "
                "to reference code, describe it in words (e.g., 'implement a function that...') "
                "rather than writing it out."
            )
            if coding_style:
                company_round_style = (
                    f"COMPANY-SPECIFIC CODING STYLE:\n{coding_style}\n\n"
                    f"Generate a coding question in this company's authentic style. "
                    f"Do NOT preface the question with any description or label — output ONLY the question."
                )
                round_type_instruction = f"{round_type_instruction}\n\n{company_round_style}"

        elif rtype == "technical":
            round_type_instruction = "This is a TECHNICAL round. Ask about system design, architecture, best practices, or deep technical concepts relevant to the role."

        elif rtype == "hr":
            hr_context = get_company_hr_context(company_lower)
            style_note = hr_context["style_note"]
            principles = hr_context["principles"]

            # For Amazon, explicitly require Leadership Principle mapping
            if company_lower == "amazon":
                principles_str = "\n".join([f"- {p}" for p in principles])
                company_round_style = (
                    "CRITICAL - This interview is for AMAZON. You MUST follow these rules:\n"
                    "1. Focus on ONE of Amazon's 16 Leadership Principles in the question.\n"
                    "2. Ask a direct behavioral question evaluating how the candidate demonstrates this principle. Do NOT append parenthetical tags or internal notes.\n"
                    f"3. The 16 Leadership Principles are:\n{principles_str}\n"
                    "4. Pick a DIFFERENT principle than previously used in this session.\n"
                    "5. Expect STAR-format (Situation, Task, Action, Result) answers."
                )
            elif company_lower in HR_PATTERN_COMPANIES:
                principles_str = "\n".join([f"- {p}" for p in principles])
                company_round_style = (
                    f"COMPANY-SPECIFIC HR STYLE - {hr_context['label']}:\n"
                    f"{style_note}\n"
                    f"Key focus areas:\n{principles_str}\n"
                    f"Generate a question matching this company's authentic behavioral style. "
                    f"Do NOT preface the question with any description or label — output ONLY the question."
                )
            elif company_lower in SIMPLE_HR_COMPANIES:
                company_round_style = (
                    f"COMPANY CONTEXT: This is an interview for {company}. "
                    f"{style_note}\n"
                    f"Ask standard HR questions with emphasis on clear communication "
                    f"and basic professionalism."
                )
            else:
                company_round_style = (
                    "Use standard behavioral interview format (STAR method). "
                    "Ask about soft skills, teamwork, leadership, and career goals."
                )

            round_type_instruction = f"This is a BEHAVIORAL/HR round.\n\n{company_round_style}"
        else:
            round_type_instruction = f"Ask a {rtype} question appropriate for this round."

    # Resume-phase and general resume context instruction
    resume_instruction = ""
    if is_resume_phase and resume_text:
        resume_instruction = (
            f"CRITICAL - RESUME DISCUSSION ROUND:\n"
            f"1. You MUST pull a specific, concrete project, technology, tool, or past experience mentioned in the candidate's resume.\n"
            f"2. TARGET ROLE ALIGNMENT: The candidate's target role is '{role}'. You MUST frame the question around how that resume project or skill connects to a '{role}' role.\n"
            f"   - For example: If candidate targets 'Data Scientist' but resume mentions a web dev project, do NOT ask frontend/CSS questions. Reframe around data engineering, ML algorithms, performance metrics, or data pipelines for that project.\n"
            f"   - For example: If candidate targets 'DevOps Engineer', reframe their backend/project experience around deployment, CI/CD, scalability, or monitoring.\n"
            f"3. Keep the question conversational, concise (1-2 sentences), and tailored to {experience} years of experience."
        )
    elif resume_text:
        resume_instruction = (
            f"RESUME CONTEXT INTEGRATION:\n"
            f"Where relevant, pull specific details from the candidate's resume below, but ALWAYS frame the question to evaluate core competencies needed for their target role '{role}'."
        )
    elif round_info and round_info.get("focus"):
        resume_instruction = (
            f"ROUND FOCUS: This round covers '{round_info.get('name', '')}' with focus on: "
            f"{round_focus}. Tailor the question accordingly to the target role '{role}'."
        )

    # Company-specific tag for the question itself
    company_tag = f"\nCompany: {company}" if company and company_lower != "general" else ""

    prompt = f"""Generate a single {difficulty} interview question for a {role} candidate with {experience} years of experience.{company_tag}

Candidate's Target Role: {role}
Candidate's Skills: {skills_str}
Question Category: {category}

{context_part}

{prev_q_part}

{resume_part}

{round_type_instruction}

{resume_instruction}

DIFFICULTY ENFORCEMENT (hard constraints based on difficulty='{difficulty}'):
{'HARD CONSTRAINT - Difficulty is EASY:' if difficulty == 'easy' else
 'HARD CONSTRAINT - Difficulty is MEDIUM:' if difficulty == 'medium' else
 'HARD CONSTRAINT - Difficulty is HARD:'}
{'Do NOT ask about system design, scalability, distributed systems, architecture, or advanced algorithms (DP, graph algorithms, NP-complete). Focus on: basic data structures (arrays, strings, linked lists), core language features, fundamental concepts. The question should be answerable by someone with 0-2 years experience. Keep it straightforward and specific.' if difficulty == 'easy' else
 'You MAY ask about intermediate concepts: design patterns, common algorithms, basic system design. Avoid expert-level or specialized niche topics. The question should suit someone with 2-6 years experience.' if difficulty == 'medium' else
 'You MAY ask about advanced topics: system design, distributed systems, complex algorithms, trade-off analysis. The question should challenge someone with 6+ years experience.'}

CRITICAL RULES:
- Return ONLY the raw question text. No labels, no prefixes (like 'Question:', 'Q:', 'Based on your resume...', 'Here is my question:', 'Sure, here is...'), and no quotes.
- NEVER preface the question with a descriptive sentence like "Here is a ... question tailored to ...", "Here is a ... question for ...", or "For a ... candidate with ... years of experience:". Return JUST the question itself, nothing before it.
- Keep the question CONCISE: 1-2 sentences maximum. Do NOT write long multi-part scenarios or paragraphs.
- Keep it highly conversational and direct, like an interviewer asking a candidate in person.
- Ensure high TOPIC VARIETY: Do NOT repeat topics or technologies from previous questions in this session.
- The question MUST be relevant to the candidate's target role '{role}' and their stated experience level ({experience} years).
- NEVER leak any instructions, system tags, metadata, or parenthetical explanations (e.g., do NOT append '(This maps to...)', '(This relates to...)', '[Context: ...]', or any other annotations) in the response.
- Output ONLY a question. Do NOT write any code, class definitions, pseudocode, or partial solution in your response. You are the interviewer asking — the candidate will provide the code."""

    response = _call_llm(prompt, QUESTION_GENERATION_SYSTEM, temperature=0.8)

    # Clean up common prefixes and leaked headers/notes
    response = re.sub(r'^(Question[:\s]*|Q[:\s]*|"|\')', '', response).strip()
    response = re.sub(r'["\']$', '', response).strip()
    
    # Strip parenthetical annotations or tags models leak (e.g. "(This maps to Amazon Leadership Principle: Ownership)")
    response = re.sub(r'\s*[\(\[][^\]\)]*?(?:maps to|relates to|principle|leadership|company|context|role|experience|difficulty|category|question|amazon|google|meta|microsoft)[^\]\)]*?[\)\]]', '', response, flags=re.IGNORECASE).strip()
    
    # Strip common conversational introductory filler phrases that leak system instructions
    # Also strips "Here is a ... question tailored to ..." type preambles the model sometimes emits
    response = re.sub(r'^(Based on your resume,?\s*|Looking at your resume,?\s*|In your resume,?\s*|Let\'s discuss your resume:?\s*|Could you tell me,?\s*|Sure,?\s*|Here is an? .+? question[^.]*?:?\s*|For an? .+? candidate with .+? years? of experience:?\s*)', '', response, flags=re.IGNORECASE).strip()
    
    # Ensure the first letter is capitalized
    if response:
        response = response[0].upper() + response[1:]
    
    if not response or response.startswith("[OLLAMA_"):
        # Fallback questions if Ollama is unavailable
        return _get_fallback_question(role, category, difficulty, company)
    
    # Safety check: if response contains code (class/def/enum/struct/etc.) or is too
    # long (>50 words for a 1-2 sentence question), fall back to a proper question.
    word_count = len(response.split())
    has_code_block = bool(re.search(r'\b(class|def |void |int |struct |enum |function\s*\w+\s*\()', response))
    if has_code_block or word_count > 50:
        fallback = _get_fallback_question(role, category, difficulty, company)
        return fallback
    
    return response


def evaluate_answer(question: str, answer: str, role: str, difficulty: str,
                    skills: list = None) -> dict:
    """
    Evaluate a candidate's answer with detailed multi-dimension scoring.
    
    Returns enhanced dict with 7 score dimensions, strengths/weaknesses,
    ideal answer, keywords analysis, and improvement tips.
    """
    skills_str = ", ".join(skills) if skills else "general"

    # Get role-specific scoring rubric
    rubric = get_role_rubric(role)
    focus_areas = ", ".join(rubric.get("focus_areas", []))
    scoring_guidance = rubric.get("scoring_guidance", "")

    system_prompt = """You are an expert interview evaluator. Evaluate answers fairly and constructively.
You must provide specific, actionable feedback and a realistic improved answer.
Be encouraging but honest about areas for improvement.
Return ONLY valid JSON — no markdown, no extra text."""

    # Detect filler words in the answer
    filler_data = detect_filler_words(answer)

    rubric_section = f"""
Role-Specific Scoring Guidance:
Target Role: {role}
Key Focus Areas for This Role: {focus_areas}
Scoring Emphasis: {scoring_guidance}

When scoring, prioritize the focus areas above based on the target role's requirements.
"""
    
    prompt = f"""Evaluate this interview answer thoroughly.

Role: {role}
Difficulty Level: {difficulty}
Skills Required: {skills_str}
{rubric_section}
Question: {question}

Question: {question}

Candidate's Answer: {answer}

Score each dimension from 0-10:

1. TECHNICAL_ACCURACY - Is the answer technically correct? Deep understanding shown?
2. COMMUNICATION_SKILL - Well-structured, clear, concise?
3. CONFIDENCE_LEVEL - Definite statements, no hedging/filler words?
4. PROBLEM_SOLVING - Systematic approach, considers edge cases, trade-offs discussed?
5. TIME_MANAGEMENT - Concise enough? Hits key points efficiently?
6. CONCEPTUAL_CLARITY - Explains concepts clearly, uses analogies or examples?
7. OVERALL_SCORE - Weighted combination of all dimensions

Also:
- STRENGTHS: List 1-3 things done well (specific, evidence-based)
- WEAKNESSES: List 1-3 things missing or wrong (specific, actionable)
- IDEAL_ANSWER: A complete model answer showing the best possible response
- FEEDBACK: 2-3 sentence constructive feedback
- IMPROVEMENT_TIP: One specific actionable tip for next time
- KEYWORDS_USED: Keywords/concepts the candidate mentioned
- KEYWORDS_MISSED: Important keywords/concepts that were omitted

Return as JSON ONLY with this exact structure:
{{
    "overall_score": <int 0-10>,
    "technical_score": <int 0-10>,
    "communication_score": <int 0-10>,
    "confidence_score": <int 0-10>,
    "problem_solving_score": <int 0-10>,
    "time_management_score": <int 0-10>,
    "conceptual_clarity_score": <int 0-10>,
    "strengths": ["strength1", "strength2"],
    "weaknesses": ["weakness1", "weakness2"],
    "ideal_answer": "A complete model answer...",
    "feedback": "2-3 sentence constructive feedback",
    "improvement_tip": "One specific actionable tip",
    "keywords_used": ["keyword1", "keyword2"],
    "keywords_missed": ["missing1", "missing2"]
}}"""

    # Inject filler-word context into the evaluation prompt
    if filler_data["total_count"] > 0:
        filler_note = f"""
Filler Word Override:
The candidate's answer contains {filler_data['total_count']} filler word(s):
{filler_data['filler_words']}

When scoring COMMUNICATION_SKILL and CONFIDENCE_LEVEL, factor in the filler word count:
- 0-2 filler words: small impact
- 3-5 filler words: moderate impact (-1 to -2 points)
- 6+ filler words: significant impact (-2 to -3 points)

Also include 'filler_word_count': {filler_data['total_count']} in the response.
"""
        prompt += f"\n\n{filler_note}"

    response = _call_llm(prompt, system_prompt, temperature=0.3)
    
    if response.startswith("[OLLAMA_"):
        return _get_fallback_evaluation(answer)
    
    result = _extract_json(response)
    if result and isinstance(result, dict) and result.get('overall_score') is not None:
        # Ensure all score fields exist with defaults
        score_keys = [
            'overall_score', 'technical_score', 'communication_score',
            'confidence_score', 'problem_solving_score',
            'time_management_score', 'conceptual_clarity_score'
        ]
        for key in score_keys:
            if key not in result:
                result[key] = result.get('overall_score', 5)
            result[key] = max(0, min(10, int(round(result[key]))))
        
        # Ensure list fields exist
        for list_key in ['strengths', 'weaknesses', 'keywords_used', 'keywords_missed']:
            if list_key not in result or not isinstance(result[list_key], list):
                result[list_key] = []
        
        # Ensure text fields exist
        for text_key in ['ideal_answer', 'feedback', 'improvement_tip']:
            if text_key not in result:
                result[text_key] = ''
        
        # Backward compatibility
        result.setdefault('improved_answer', result.get('ideal_answer', ''))
        result.setdefault('score_explanation', result.get('feedback', ''))

        # Filler-word data (computed locally for accuracy)
        result['filler_word_count'] = filler_data['total_count']
        result['filler_words'] = filler_data['filler_words']

        return result
    
    # If JSON parsing failed, extract scores manually
    return _extract_scores_fallback(response, answer)


def detect_skill_gaps(skills: list, questions_and_answers: list, role: str) -> list:
    """
    Analyze interview performance to detect skill gaps.
    
    Args:
        skills: Skills listed on resume
        questions_and_answers: List of dicts with 'question', 'answer', 'score', 'category'
        role: Job role
    
    Returns:
        List of dicts: {skill, level, gap, recommendation}
    """
    if not questions_and_answers:
        return []

    qa_context = "\n".join([
        f"Q: {qa.get('question', '')}\nA: {qa.get('answer', '')}\nScore: {qa.get('score', 'N/A')}/10"
        for qa in questions_and_answers[-5:]  # Last 5 Q&A
    ])

    skills_str = ", ".join(skills) if skills else "Not specified"

    system_prompt = "You are a career coach who identifies skill gaps and provides actionable learning recommendations."

    prompt = f"""Analyze this candidate's interview performance and identify skill gaps.

Role: {role}
Skills on Resume: {skills_str}

Recent Interview Performance:
{qa_context[:2000]}

Identify 2-4 skill gaps that the candidate should work on. For each gap provide:
1. The specific skill
2. Current proficiency level (beginner/intermediate/advanced)
3. Why it's a gap (specific evidence from the interview)
4. A concrete learning recommendation (specific topics, resources, or practice methods)

Return as JSON ONLY with this structure:
{{
    "skill_gaps": [
        {{
            "skill": "<skill name>",
            "level": "beginner|intermediate|advanced",
            "gap": "<description of the gap>",
            "recommendation": "<actionable learning recommendation>"
        }}
    ]
}}"""

    response = _call_llm(prompt, system_prompt, temperature=0.4)
    
    result = _extract_json(response)
    if result and isinstance(result, dict) and 'skill_gaps' in result:
        return result['skill_gaps']
    
    # Fallback
    return [
        {
            "skill": "General Knowledge",
            "level": "intermediate",
            "gap": "Further depth needed in core concepts",
            "recommendation": "Review fundamentals and practice with real-world projects"
        }
    ]


def generate_recommendations(skill_gaps: list, overall_score: int, role: str) -> list:
    """
    Generate learning recommendations based on skill gaps and performance.
    
    Returns:
        List of dicts: {area, resource_type, description, priority}
    """
    if not skill_gaps:
        return [{
            "area": "Continue Building",
            "resource_type": "Practice",
            "description": "Keep practicing with mock interviews and real-world projects",
            "priority": "medium"
        }]
    
    recommendations = []
    for gap in skill_gaps:
        recommendations.append({
            "area": gap.get('skill', 'General'),
            "resource_type": "Learning Path",
            "description": gap.get('recommendation', f"Study {gap.get('skill', 'this topic')} in depth"),
            "priority": "high" if gap.get('level') == 'beginner' else "medium"
        })
    
    return recommendations


def generate_final_report_data(candidate_info: dict, session_data: dict,
                                answers: list, skill_gaps: list,
                                recommendations: list) -> dict:
    """
    Generate a comprehensive final report with all score dimensions,
    improvement roadmap, and motivational feedback.
    """
    total_questions = len(answers)
    if total_questions == 0:
        return {"error": "No answers to generate report from"}

    # Calculate all aggregate scores from individual answers
    score_fields = [
        'overall_score', 'technical_score', 'communication_score',
        'confidence_score', 'problem_solving_score',
        'time_management_score', 'conceptual_clarity_score'
    ]
    avg_scores = {}
    for field in score_fields:
        vals = [a.get(field, 0) or 0 for a in answers]
        avg_scores[field] = round(sum(vals) / len(vals), 1) if vals else 0

    # Score distribution
    score_ranges = {"excellent (8-10)": 0, "good (6-7)": 0, "average (4-5)": 0, "needs improvement (0-3)": 0}
    for a in answers:
        s = a.get('overall_score', 0)
        if s >= 8: score_ranges["excellent (8-10)"] += 1
        elif s >= 6: score_ranges["good (6-7)"] += 1
        elif s >= 4: score_ranges["average (4-5)"] += 1
        else: score_ranges["needs improvement (0-3)"] += 1

    # Prepare answer details with all new fields
    answer_details = []
    for i, a in enumerate(answers, 1):
        answer_details.append({
            "number": i,
            "question": a.get('question', ''),
            "answer": a.get('answer', ''),
            "category": a.get('category', 'general'),
            "difficulty": a.get('difficulty', 'medium'),
            "overall_score": a.get('overall_score', 0),
            "technical_score": a.get('technical_score', 0),
            "communication_score": a.get('communication_score', 0),
            "confidence_score": a.get('confidence_score', 0),
            "problem_solving_score": a.get('problem_solving_score', 0),
            "time_management_score": a.get('time_management_score', 0),
            "conceptual_clarity_score": a.get('conceptual_clarity_score', 0),
            "feedback": a.get('feedback', ''),
            "improved_answer": a.get('improved_answer', ''),
            "ideal_answer": a.get('ideal_answer', ''),
            "improvement_tip": a.get('improvement_tip', ''),
            "strengths": a.get('strengths', []),
            "weaknesses": a.get('weaknesses', []),
            "keywords_used": a.get('keywords_used', []),
            "keywords_missed": a.get('keywords_missed', []),
        })

    # Generate summary via AI
    system_prompt = "You are an interview coach writing a personalized final performance summary."
    prompt = f"""Write a brief, personalized final interview summary (2-3 sentences) for this candidate:
Role: {candidate_info.get('role', 'N/A')}
Name: {candidate_info.get('name', 'Candidate')}
Avg Score: {avg_scores['overall_score']}/10
Questions: {total_questions}
Weakest Area: {min(avg_scores, key=avg_scores.get) if avg_scores else 'N/A'}

The tone should be professional, encouraging, and constructive — like a real interview feedback session."""

    summary_text = _call_llm(prompt, system_prompt, temperature=0.7)
    if summary_text.startswith("[OLLAMA_"):
        summary_text = "Thank you for completing the interview. Review the detailed scores and recommendations below to identify areas for improvement."

    # Determine weakest areas for improvement roadmap
    weak_areas = sorted(
        [(k, v) for k, v in avg_scores.items() if v < 7],
        key=lambda x: x[1]
    )
    
    # Generate improvement roadmap
    improvement_roadmap = generate_improvement_roadmap(
        weak_areas=weak_areas,
        role=candidate_info.get('role', 'Software Engineer'),
    )

    # Calculate grade and readiness
    overall = avg_scores['overall_score']
    grade = _calculate_grade(overall)
    readiness = _calculate_readiness(avg_scores)
    
    # Motivational message
    motivational = _get_motivational_message(
        overall, candidate_info.get('role', 'Software Engineer'),
        weak_areas[:2] if weak_areas else []
    )

    # Star rating (1-5)
    star_rating = max(1, min(5, round(overall / 2)))

    # ── Rewrite data ──
    rewritten_answers = [a for a in answers if a.get("rewrite_used")]
    rewrite_count = len(rewritten_answers)
    has_rewrites = rewrite_count > 0
    rewrites = []
    total_improvement = 0
    for ra in rewritten_answers:
        orig = ra.get("original_scores") or {k: ra.get(k, 0) for k in ["overall_score", "technical_score", "communication_score", "confidence_score", "problem_solving_score", "time_management_score", "conceptual_clarity_score"]}
        rewrite_scores = ra.get("rewrite_scores", {})
        imp = {}
        for key in ["overall_score", "technical_score", "communication_score", "confidence_score", "problem_solving_score", "time_management_score", "conceptual_clarity_score"]:
            old_val = orig.get(key, 0)
            new_val = rewrite_scores.get(key, old_val)
            imp[key] = new_val - old_val
        total_improvement += imp.get("overall_score", 0)
        rewrites.append({
            "question": ra.get("question", ""),
            "original_answer": ra.get("answer", ""),
            "rewritten_answer": ra.get("rewrite_text", ""),
            "original_scores": orig,
            "rewritten_scores": rewrite_scores,
            "improvement": imp,
        })
    avg_rewrite_improvement = round(total_improvement / max(rewrite_count, 1), 1)

    # ── Filler word stats for report ──
    filler_word_stats = None
    filler_answers = [a for a in answers if a.get("filler_word_count", 0) > 0]
    if filler_answers:
        total_filler_count = sum(a.get("filler_word_count", 0) for a in filler_answers)
        max_count = max(a.get("filler_word_count", 0) for a in filler_answers) if filler_answers else 0
        filler_breakdown = {}
        for a in filler_answers:
            fw = a.get("filler_words", {})
            for word, count in fw.items():
                filler_breakdown[word] = filler_breakdown.get(word, 0) + count
        filler_word_stats = {
            "total": total_filler_count,
            "max_count": max_count,
            "breakdown": filler_breakdown,
            "by_question": [
                {
                    "number": i + 1,
                    "question": a.get("question", ""),
                    "count": a.get("filler_word_count", 0),
                }
                for i, a in enumerate(answers) if a.get("filler_word_count", 0) > 0
            ],
        }

    return {
        "candidate_info": candidate_info,
        "session_data": session_data,
        "summary": summary_text,
        "grade": grade,
        "star_rating": star_rating,
        "readiness_score": readiness,
        "motivational": motivational,
        # All score dimensions
        "overall_score": avg_scores['overall_score'],
        "technical_score": avg_scores['technical_score'],
        "communication_score": avg_scores['communication_score'],
        "confidence_score": avg_scores['confidence_score'],
        "problem_solving_score": avg_scores['problem_solving_score'],
        "time_management_score": avg_scores['time_management_score'],
        "conceptual_clarity_score": avg_scores['conceptual_clarity_score'],
        # Additional data
        "total_questions": total_questions,
        "score_distribution": score_ranges,
        "weak_areas": [{"area": k, "score": v} for k, v in weak_areas],
        "skill_gaps": skill_gaps,
        "recommendations": recommendations,
        "improvement_roadmap": improvement_roadmap,
        "answers": answer_details,
        # Rewrite data for report
        "has_rewrites": has_rewrites,
        "rewrite_count": rewrite_count,
        "rewrites": rewrites,
        "avg_rewrite_improvement": avg_rewrite_improvement,
        # Filler word stats for report
        "filler_word_stats": filler_word_stats,
    }


def _calculate_grade(score: float) -> str:
    """Convert numeric score to letter grade."""
    if score >= 9: return "A+"
    elif score >= 8: return "A"
    elif score >= 7: return "B+"
    elif score >= 6: return "B"
    elif score >= 5: return "C"
    else: return "F"


def _calculate_readiness(avg_scores: dict) -> int:
    """
    Calculate interview readiness percentage based on all score dimensions.
    Returns 0-100.
    """
    weights = {
        'overall_score': 0.25, 'technical_score': 0.25,
        'communication_score': 0.15, 'confidence_score': 0.10,
        'problem_solving_score': 0.10, 'conceptual_clarity_score': 0.15,
    }
    weighted = 0
    total_weight = 0
    for key, weight in weights.items():
        val = avg_scores.get(key, 5)
        weighted += val * weight
        total_weight += weight
    
    if total_weight == 0:
        return 50
    return min(100, max(0, int((weighted / total_weight) * 10)))


def _get_motivational_message(score: float, role: str, weak_areas: list) -> str:
    """Generate motivational feedback based on overall score."""
    weak_str = ", ".join([w[0].replace('_', ' ').title() for w in weak_areas[:2]]) if weak_areas else "general knowledge"
    company = "top tech companies" if score > 5 else "entry-level positions"
    
    if score >= 9:
        return f"Exceptional! You're interview-ready for top companies. Focus on staying updated with latest trends."
    elif score >= 7:
        return f"Good performance! Focus on {weak_str} to crack interviews at {company}."
    elif score >= 5:
        return f"Keep practicing! You need more work on {weak_str}. Consistent daily practice will show results."
    else:
        return f"Don't give up! Start with the fundamentals of {weak_str} and practice daily. Every expert was once a beginner."


# ── Improvement Roadmap ──────────────────────────────────────────────────────

def generate_improvement_roadmap(weak_areas: list, role: str = "Software Engineer") -> dict:
    """
    Generate a structured 30-day improvement plan based on weak areas.
    
    Args:
        weak_areas: List of (area_name, score) tuples, sorted worst-first
        role: Target job role
    
    Returns:
        dict with weekly plans and learning resources
    """
    area_names = [a[0].replace('_', ' ').title() for a in weak_areas[:4]]
    # Pad to 4 areas
    while len(area_names) < 4:
        area_names.append("General Knowledge")
    
    roadmap = {
        "week_1": {
            "focus": area_names[0] if len(area_names) > 0 else "Fundamentals",
            "goal": f"Master the basics of {area_names[0] if len(area_names) > 0 else 'core concepts'}",
            "daily_plan": [
                "Study core concepts for 45 minutes",
                f"Practice 3-5 problems related to {area_names[0] if len(area_names) > 0 else 'core skills'}",
                "Review and note down key learnings",
            ],
        },
        "week_2": {
            "focus": area_names[1] if len(area_names) > 1 else "Application",
            "goal": f"Build practical skills in {area_names[1] if len(area_names) > 1 else 'real-world scenarios'}",
            "daily_plan": [
                f"Deep dive into {area_names[1] if len(area_names) > 1 else 'applied concepts'}",
                "Build a small project incorporating both areas",
                "Get feedback on your approach",
            ],
        },
        "week_3": {
            "focus": "Mock Interviews & Company Prep",
            "goal": f"Practice for {role} interviews with timed mock sessions",
            "daily_plan": [
                "1 full mock interview (self or with partner)",
                "Review and analyze your performance",
                f"Study {role}-specific interview patterns",
                "Practice answering in 2 minutes or less",
            ],
        },
        "week_4": {
            "focus": "Revision & Mastery",
            "goal": "Consolidate all learning and identify remaining gaps",
            "daily_plan": [
                "Review all weak areas from weeks 1-2",
                "Full-length mock interview simulation",
                "Track improvement against baseline scores",
                "Create a cheat sheet of key concepts",
            ],
        },
    }
    
    # Generate learning resources based on weak areas
    resources = []
    for area_name, _ in weak_areas[:3]:
        area_key = area_name.replace(' ', '_').lower()
        area_resources = LEARNING_RESOURCES.get(area_key, LEARNING_RESOURCES.get('general', []))
        resources.extend(area_resources[:2])  # Top 2 per area
    
    if not resources:
        resources = LEARNING_RESOURCES.get('general', [])
    
    return {
        "roadmap": roadmap,
        "weak_areas_ranked": [a[0] for a in weak_areas],
        "learning_resources": resources[:6],  # Top 6 overall
        "overall_advice": f"Focus 60%% of your time on {area_names[0] if area_names else 'weak areas'}, 30%% on practice, and 10%% on revision. Consistency matters more than intensity."
    }


# ── Hardcoded Learning Resources ─────────────────────────────────────────────

LEARNING_RESOURCES = {
    "technical_score": [
        {"title": "Cracking the Coding Interview", "type": "Book", "description": "189 programming questions with solutions", "url": "https://www.crackingthecodinginterview.com/"},
        {"title": "LeetCode Top 100", "type": "Practice", "description": "Solve 100 most common interview problems", "url": "https://leetcode.com/problemset/top-100-liked-questions/"},
        {"title": "Abdul Bari Algorithms", "type": "Video", "description": "YouTube: Master algorithm fundamentals", "url": "https://youtube.com/playlist?list=PLDN4rrl48XKpZkf03iYFl-O29szjTr3_O"},
        {"title": "NeetCode DSA Course", "type": "Course", "description": "Structured DSA learning path", "url": "https://neetcode.io/"},
        {"title": "GeeksforGeeks", "type": "Reference", "description": "Comprehensive algorithm explanations", "url": "https://www.geeksforgeeks.org/"},
    ],
    "problem_solving_score": [
        {"title": "Grooking Algorithms", "type": "Book", "description": "Visual guide to algorithms and problem-solving", "url": "https://www.manning.com/books/grokking-algorithms"},
        {"title": "System Design Primer", "type": "Guide", "description": "Learn to design large-scale systems", "url": "https://github.com/donnemartin/system-design-primer"},
        {"title": "Daily Coding Problem", "type": "Practice", "description": "Get a new problem every day", "url": "https://www.dailycodingproblem.com/"},
        {"title": "CodeSignal Arcade", "type": "Practice", "description": "Gamified problem-solving practice", "url": "https://codesignal.com/"},
    ],
    "communication_score": [
        {"title": "STAR Method Guide", "type": "Guide", "description": "Structure behavioral answers effectively", "url": "https://www.themuse.com/advice/star-interview-method"},
        {"title": "Interview Warmup by Google", "type": "Tool", "description": "Practice answering common questions", "url": "https://interviewwarmup.withgoogle.com/"},
        {"title": "Write Speak Code", "type": "Workshop", "description": "Improve technical communication", "url": "https://www.writespeakcode.com/"},
    ],
    "confidence_score": [
        {"title": "Toastmasters", "type": "Community", "description": "Practice public speaking in a supportive group", "url": "https://www.toastmasters.org/"},
        {"title": "Avoid Filler Words Guide", "type": "Article", "description": "Eliminate um, uh, like from your speech", "url": "https://virtualspeech.com/blog/how-to-stop-saying-um-uh-like"},
        {"title": "Mirror Practice", "type": "Exercise", "description": "Practice answers in front of a mirror for 10 min/day", "url": ""},
    ],
    "conceptual_clarity_score": [
        {"title": "MIT OpenCourseWare", "type": "Course", "description": "Free CS courses from MIT", "url": "https://ocw.mit.edu/"},
        {"title": "CS50 by Harvard", "type": "Course", "description": "Excellent computer science fundamentals", "url": "https://cs50.harvard.edu/"},
        {"title": "Khan Academy CS", "type": "Course", "description": "Learn programming fundamentals visually", "url": "https://www.khanacademy.org/computing/computer-science"},
    ],
    "time_management_score": [
        {"title": "Pomodoro Technique", "type": "Method", "description": "25-min focused work intervals", "url": "https://todoist.com/productivity-methods/pomodoro-technique"},
        {"title": "Interview Time Boxing", "type": "Guide", "description": "Practice answering within time limits", "url": ""},
    ],
    "general": [
        {"title": "Pramp", "type": "Platform", "description": "Free mock interviews with peers", "url": "https://www.pramp.com/"},
        {"title": "InterviewBit", "type": "Platform", "description": "Structured interview preparation", "url": "https://www.interviewbit.com/"},
        {"title": "HackerRank", "type": "Practice", "description": "Code practice for interviews", "url": "https://www.hackerrank.com/"},
        {"title": "ByteByteGo", "type": "Video", "description": "System design explained visually", "url": "https://www.youtube.com/@ByteByteGo"},
    ],
}


def calculate_readiness_score(all_sessions: list) -> dict:
    """
    Calculate interview readiness based on all completed sessions.
    
    Args:
        all_sessions: List of session dicts with scores
    
    Returns:
        dict with readiness percentage, consistency score, and improvement trend
    """
    if not all_sessions:
        return {
            "readiness_percent": 0,
            "consistency_score": 0,
            "improvement_trend": "neutral",
            "total_sessions": 0,
            "message": "Complete at least one interview to get your readiness score."
        }
    
    # Average overall score across sessions
    scores = [s.get('overall_score', 0) for s in all_sessions if s.get('overall_score')]
    if not scores:
        return {"readiness_percent": 0, "consistency_score": 0, "improvement_trend": "neutral", "total_sessions": len(all_sessions)}
    
    avg_score = sum(scores) / len(scores)
    
    # Consistency: lower std dev = more consistent
    variance = sum((s - avg_score) ** 2 for s in scores) / len(scores)
    std_dev = variance ** 0.5
    consistency = max(0, 10 - std_dev * 2)  # 0-10 scale, inverted
    
    # Improvement trend: compare first 3 vs last 3 if enough sessions
    trend = "neutral"
    if len(scores) >= 4:
        first_half = sum(scores[:len(scores)//2]) / (len(scores)//2)
        second_half = sum(scores[-(len(scores)//2):]) / (len(scores)//2)
        if second_half > first_half + 0.5:
            trend = "improving"
        elif first_half > second_half + 0.5:
            trend = "declining"
    
    # Readiness percent (0-100)
    readiness = min(100, int((avg_score / 10) * 80 + consistency * 2))
    
    return {
        "readiness_percent": readiness,
        "consistency_score": round(consistency, 1),
        "improvement_trend": trend,
        "total_sessions": len(all_sessions),
        "avg_score": round(avg_score, 1),
        "sessions_completed": len(scores),
        "message": f"You're {readiness}% interview ready based on {len(scores)} completed sessions."
    }


# ── Fallback Methods (when Ollama is unavailable) ──────────────────────────────

def _get_fallback_question(role: str, category: str, difficulty: str, company: str = "General") -> str:
    """Provide sensible fallback questions when Ollama is offline.
    Uses company-specific questions when applicable."""
    company_lower = company.lower().strip() if company else "general"
    import random

    # ── Company-specific behavioral questions for known patterns ──
    if category in ("behavioral", "hr"):
        if company_lower == "amazon":
            amazon_questions = [
                "Tell me about a time you went above and beyond for a customer or end-user. How did you handle their needs and what was the outcome?",
                "Describe a situation where you had to take full ownership of a project outside your core responsibilities. What steps did you take?",
                "Tell me about a complex process or system you simplified. What was the impact of that simplification?",
                "Give an example of a tough decision you had to make with incomplete data. How did you arrive at your decision?"
            ]
            return random.choice(amazon_questions)
        elif company_lower == "google":
            return (
                "Tell me about a time when you had to work on a project with ambiguous "
                "requirements and unclear direction. How did you approach it and what was the result?"
            )
        elif company_lower == "microsoft":
            return (
                "Tell me about a time you failed at a task and what specific lessons you learned from it. "
                "How did this experience change your overall technical approach?"
            )
        elif company_lower == "meta":
            return (
                "Tell me about a time you disagreed with a team member's technical decision. "
                "How did you handle the disagreement and what was the resolution?"
            )

    # ── Standard fallback questions for all other cases ──
    questions = {
        "technical": {
            "easy": [
                f"What programming languages and frameworks are you most comfortable with for {role} roles?",
                f"Can you explain the difference between a list and a dictionary in Python?",
                f"What version control systems have you used and how do you handle merge conflicts?",
            ],
            "medium": [
                f"Describe the architecture of a web application you've built. How did you handle data flow?",
                f"Explain how you would debug a performance issue in a production application.",
                f"What's your approach to writing unit tests? Can you give an example of a test you'd write for an API endpoint?",
            ],
            "hard": [
                f"Design a system that handles 1 million concurrent users. Walk me through your architecture decisions.",
                f"Explain the CAP theorem and how you would make trade-offs in a distributed payment system.",
                f"How would you implement a real-time notification system that scales horizontally?",
            ],
        },
        "behavioral": {
            "easy": [
                f"Tell me about yourself and why you're interested in this {role} position.",
                f"What do you consider your greatest professional strength?",
                f"Why do you want to work in this field?",
            ],
            "medium": [
                f"Tell me about a time you had a conflict with a teammate. How did you resolve it?",
                f"Describe a project that failed. What did you learn from it?",
                f"How do you handle tight deadlines and competing priorities?",
            ],
            "hard": [
                f"Tell me about a time you had to lead a team through a difficult technical decision.",
                f"Describe a situation where you disagreed with your manager. How did you handle it?",
                f"Have you ever had to deliver bad news to a stakeholder? How did you approach it?",
            ],
        },
        "hr": {
            "easy": [
                f"Tell me about yourself and why you're interested in this {role} position.",
                f"What do you consider your greatest professional strength?",
                f"Why do you want to work in this field?",
            ],
            "medium": [
                f"Tell me about a time you had a conflict with a teammate. How did you resolve it?",
                f"Describe a project that failed. What did you learn from it?",
                f"How do you handle tight deadlines and competing priorities?",
            ],
            "hard": [
                f"Tell me about a time you had to lead a team through a difficult technical decision.",
                f"Describe a situation where you disagreed with your manager. How did you handle it?",
                f"Have you ever had to deliver bad news to a stakeholder? How did you approach it?",
            ],
        },
        "coding": {
            "easy": [
                f"Can you write a function to check if a string is a palindrome? Walk me through your approach.",
                f"How would you find the two numbers in an array that sum up to a target value?",
                f"Write a function to reverse a linked list. What are the edge cases?",
            ],
            "medium": [
                f"Write a function to find the longest substring without repeating characters.",
                f"Design a function to check if a binary tree is balanced.",
                f"Implement a function to find if there are two numbers in an array that sum to a target.",
            ],
            "hard": [
                f"Design an LRU cache with O(1) get and put operations.",
                f"Implement a function to serialize and deserialize a binary tree.",
                f"Design a system to find the shortest path between two nodes in a weighted graph.",
            ],
        },
        "project": {
            "easy": [
                f"Can you walk me through your most recent project and your specific role in it?",
                f"What technologies did you use in your last project and why did you choose them?",
            ],
            "medium": [
                f"What was the most challenging bug you encountered in a recent project and how did you solve it?",
                f"How did you ensure code quality in your last project?",
            ],
            "hard": [
                f"If you could redesign your last project from scratch, what would you do differently?",
                f"How did you handle scalability or performance concerns in your most complex project?",
            ],
        },
        "situational": [
            "If you were given a project with a tight deadline and unclear requirements, how would you proceed?",
            "How would you handle a situation where you disagree with a technical decision made by your team?",
        ],
        "experience": [
            f"What attracted you to the {role} role and what experience makes you a good fit?",
            "What's one thing you would change about how your current/previous team works?",
        ],
        "problem-solving": [
            "Describe your approach to breaking down a large, complex problem into manageable pieces.",
            "How do you prioritize tasks when everything seems urgent?",
        ],
    }

    cat_questions = questions.get(category, questions["technical"])
    if isinstance(cat_questions, list):
        return random.choice(cat_questions)
    diff_questions = cat_questions.get(difficulty, cat_questions.get("medium", cat_questions["easy"]))
    return random.choice(diff_questions)


def _get_fallback_evaluation(answer: str) -> dict:
    """Enhanced rule-based fallback with all score dimensions."""
    answer_lower = answer.lower()
    answer_len = len(answer.split())
    
    # Use shared filler-word detector for consistency with evaluate_answer()
    filler_data = detect_filler_words(answer)
    filler_count = filler_data["total_count"]
    filler_map = filler_data["filler_words"]

    # Hedging phrase detection (separate from filler words)
    hedging_words = ['i think', 'maybe', 'perhaps', 'kind of', 'sort of', 'i guess', 'probably']
    hedging_count = sum(1 for w in hedging_words if w in answer_lower)
    
    # Example/structure indicators
    has_examples = any(w in answer_lower for w in ['for example', 'for instance', 'such as', 'specifically'])
    has_structure = any(w in answer_lower for w in ['first', 'second', 'finally', 'in summary', 'approach'])
    has_technical_terms = any(w in answer_lower for w in ['algorithm', 'complexity', 'architecture', 'design', 'system', 'function', 'class', 'api', 'database'])
    
    # Determine base scores from heuristics
    if answer_len < 5:
        base = {
            "overall_score": 2, "technical_score": 2, "communication_score": 2,
            "confidence_score": 3, "problem_solving_score": 2,
            "time_management_score": 3, "conceptual_clarity_score": 2,
            "feedback": "Your answer was too brief. Elaborate with specific examples and technical details.",
            "ideal_answer": "A strong answer would include: 1) Direct response to the question, 2) Specific examples from experience, 3) Technical details showing depth, 4) Clear structure with key takeaways.",
            "improvement_tip": "Aim for at least 3-4 sentences per answer. Use the STAR method: Situation, Task, Action, Result.",
            "score_explanation": "Very short answers lack depth and evidence of knowledge.",
            "strengths": ["Concise"],
            "weaknesses": ["Too brief - needs elaboration", "No specific examples or technical depth"],
            "keywords_used": [], "keywords_missed": [],
            "filler_word_count": filler_count, "filler_words": filler_map,
        }
    elif answer_len < 20:
        base_score = 5
        base = {
            "overall_score": base_score, "technical_score": base_score,
            "communication_score": base_score, "confidence_score": base_score,
            "problem_solving_score": base_score - 1,
            "time_management_score": base_score, "conceptual_clarity_score": base_score - 1,
            "feedback": "Good effort! Expand with more specific technical details and concrete examples from your experience.",
            "ideal_answer": "To improve: 1) Start with a clear thesis statement, 2) Provide 1-2 specific examples, 3) Explain your thought process, 4) Summarize the key takeaway.",
            "improvement_tip": "Use the 'claim-evidence-impact' framework: state your point, back it with evidence, explain the impact.",
            "score_explanation": "Reasonable answer but needs more depth and structure.",
            "strengths": ["On the right track", "Shows basic understanding"],
            "weaknesses": ["Needs more specific examples", "Could be better structured"],
            "keywords_used": [], "keywords_missed": [],
            "filler_word_count": filler_count, "filler_words": filler_map,
        }
    else:
        # Adjust based on quality indicators
        quality_bonus = 0
        if has_examples: quality_bonus += 1
        if has_structure: quality_bonus += 1
        if has_technical_terms: quality_bonus += 1
        
        confidence_penalty = min(2, hedging_count + filler_count)
        
        base_score = min(10, 7 + quality_bonus - confidence_penalty // 2)
        base = {
            "overall_score": base_score, "technical_score": min(10, base_score + (1 if has_technical_terms else 0)),
            "communication_score": min(10, base_score + (1 if has_structure else -1)),
            "confidence_score": max(0, 7 - confidence_penalty),
            "problem_solving_score": min(10, base_score + (1 if has_structure else 0)),
            "time_management_score": min(10, base_score),
            "conceptual_clarity_score": min(10, base_score + (1 if has_technical_terms else -1)),
            "feedback": "Solid answer with good detail. Consider structuring your response more clearly with a definite beginning, middle, and end.",
            "ideal_answer": "Your answer was good. An excellent answer would add: 1) A clear opening statement, 2) Specific metrics or outcomes, 3) Consideration of trade-offs or alternatives, 4) A concise summary.",
            "improvement_tip": "Practice the '10-second rule': spend the first 10 seconds organizing your thoughts before speaking.",
            "score_explanation": "Good length and effort but can be optimized for clarity and impact.",
            "strengths": [],
            "weaknesses": [],
            "keywords_used": [], "keywords_missed": [],
        }
        if quality_bonus >= 2:
            base["strengths"] = ["Good use of examples", "Clear structure", "Technical depth shown"]
        else:
            base["weaknesses"] = ["Could use more concrete examples", "Structure could be clearer"]
        base["filler_word_count"] = filler_count
        base["filler_words"] = filler_map

    # Detect keywords present
    common_keywords = {
        'algorithm', 'data structure', 'complexity', 'performance', 'scalable', 'design pattern',
        'rest', 'api', 'database', 'sql', 'nosql', 'cache', 'load balancing', 'microservices',
        'testing', 'deployment', 'ci/cd', 'version control', 'git', 'agile', 'scrum',
        'optimization', 'security', 'authentication', 'authorization', 'middleware',
        'frontend', 'backend', 'full stack', 'cloud', 'docker', 'kubernetes',
    }
    used = [kw for kw in common_keywords if kw in answer_lower]
    base["keywords_used"] = used[:5]
    
    return base


def _extract_scores_fallback(response: str, original_answer: str) -> dict:
    """
    Last-resort fallback: try to find any numbers in the response
    that look like scores, or just return a default.
    """
    numbers = re.findall(r'\b([0-9]|10)\b', response)
    scores = [int(n) for n in numbers if 0 <= int(n) <= 10]

    base = _get_fallback_evaluation(original_answer)
    
    # Map extracted numbers to score fields in order
    score_keys = [
        'overall_score', 'technical_score', 'communication_score',
        'confidence_score', 'problem_solving_score',
        'time_management_score', 'conceptual_clarity_score'
    ]
    for i, key in enumerate(score_keys):
        if i < len(scores):
            base[key] = scores[i]
    
    base['feedback'] = response[:500] if response and not response.startswith('[') else base['feedback']
    base['score_explanation'] = base['feedback'][:200] if base['feedback'] else ''
    
    return base


# ── Role-Specific Scoring Rubrics ────────────────────────────────────────────

ROLE_SCORING_RUBRICS = {
    "Software Engineer": {
        "display_name": "Software Engineering (SWE)",
        "focus_areas": ["System Design & Architecture", "Algorithms & Data Structures", "Code Quality & Best Practices", "Testing & Debugging"],
        "dimension_weights": {
            "technical_score": 0.30,
            "communication_score": 0.15,
            "confidence_score": 0.10,
            "problem_solving_score": 0.25,
            "time_management_score": 0.10,
            "conceptual_clarity_score": 0.10
        },
        "scoring_guidance": "Emphasize: system design reasoning, algorithmic thinking, scalability discussion, code quality comprehension, testing methodology. A strong SWE answer shows depth in architecture decisions and trade-off analysis."
    },
    "Product Manager": {
        "display_name": "Product Management (PM)",
        "focus_areas": ["Product Strategy & Roadmap", "User Empathy & Research", "Metrics & Data-Driven Decisions", "Stakeholder Management"],
        "dimension_weights": {
            "technical_score": 0.15,
            "communication_score": 0.25,
            "confidence_score": 0.15,
            "problem_solving_score": 0.20,
            "time_management_score": 0.15,
            "conceptual_clarity_score": 0.10
        },
        "scoring_guidance": "Emphasize: product vision, prioritization frameworks (RICE/ICE), cross-functional collaboration, user research methods, A/B testing interpretation, stakeholder communication. Strong PM answers show structured thinking about user needs and business impact."
    },
    "Data Scientist": {
        "display_name": "Data Science (DS)",
        "focus_areas": ["Statistical Methods & ML", "Data Pipeline & Cleaning", "Experimentation & A/B Testing", "Model Evaluation & Interpretation"],
        "dimension_weights": {
            "technical_score": 0.30,
            "communication_score": 0.15,
            "confidence_score": 0.10,
            "problem_solving_score": 0.20,
            "time_management_score": 0.10,
            "conceptual_clarity_score": 0.15
        },
        "scoring_guidance": "Emphasize: statistical reasoning, ML algorithm understanding, data quality assessment, feature engineering, experiment design, model evaluation metrics. Strong DS answers show understanding of bias-variance tradeoff, cross-validation, and practical deployment considerations."
    },
    "QA Engineer": {
        "display_name": "Quality Assurance (QA)",
        "focus_areas": ["Test Strategy & Coverage", "Automation Frameworks", "Bug Lifecycle & Root Cause", "CI/CD Integration"],
        "dimension_weights": {
            "technical_score": 0.25,
            "communication_score": 0.20,
            "confidence_score": 0.10,
            "problem_solving_score": 0.25,
            "time_management_score": 0.10,
            "conceptual_clarity_score": 0.10
        },
        "scoring_guidance": "Emphasize: test coverage strategy, automated vs manual testing, regression testing, edge case exploration, CI/CD pipeline testing, bug prioritization. Strong QA answers show systematic approach to finding and preventing defects."
    },
    "DevOps Engineer": {
        "display_name": "DevOps / SRE",
        "focus_areas": ["Infrastructure as Code", "Monitoring & Observability", "Deployment & Release Management", "Incident Response & Reliability"],
        "dimension_weights": {
            "technical_score": 0.30,
            "communication_score": 0.15,
            "confidence_score": 0.10,
            "problem_solving_score": 0.20,
            "time_management_score": 0.15,
            "conceptual_clarity_score": 0.10
        },
        "scoring_guidance": "Emphasize: infrastructure automation (Terraform/Ansible/K8s), monitoring stack (Prometheus/Grafana/Datadog), deployment strategies (blue-green/canary), incident management, SLO/SLI/SLA, reliability engineering. Strong DevOps answers show depth in operational excellence and system resilience."
    },
    "Data Analyst": {
        "display_name": "Data Analytics",
        "focus_areas": ["SQL & Data Querying", "Dashboard Design", "Statistical Analysis", "Data Storytelling"],
        "dimension_weights": {
            "technical_score": 0.20,
            "communication_score": 0.25,
            "confidence_score": 0.10,
            "problem_solving_score": 0.20,
            "time_management_score": 0.15,
            "conceptual_clarity_score": 0.10
        },
        "scoring_guidance": "Emphasize: SQL proficiency, data visualization best practices, analytical thinking, business metric interpretation, dashboard usability. Strong Data Analyst answers show ability to translate data into actionable insights."
    },
    "Full Stack Developer": {
        "display_name": "Full Stack Development",
        "focus_areas": ["Frontend & Backend Architecture", "API Design & Integration", "Database Design", "Performance & Scalability"],
        "dimension_weights": {
            "technical_score": 0.25,
            "communication_score": 0.15,
            "confidence_score": 0.10,
            "problem_solving_score": 0.25,
            "time_management_score": 0.15,
            "conceptual_clarity_score": 0.10
        },
        "scoring_guidance": "Emphasize: end-to-end architecture understanding, API design principles (REST/GraphQL), database optimization (SQL/NoSQL), caching strategies, deployment considerations. Strong Full Stack answers show balanced understanding of both frontend and backend ecosystems."
    },
    "Machine Learning Engineer": {
        "display_name": "MLE / AI Engineering",
        "focus_areas": ["ML Pipeline & Training", "Model Deployment & Serving", "Feature Engineering", "MLOps & Monitoring"],
        "dimension_weights": {
            "technical_score": 0.30,
            "communication_score": 0.10,
            "confidence_score": 0.10,
            "problem_solving_score": 0.25,
            "time_management_score": 0.10,
            "conceptual_clarity_score": 0.15
        },
        "scoring_guidance": "Emphasize: ML system design, training infrastructure, model serving (batch/realtime), feature stores, data leakage prevention, experiment tracking, MLOps tooling. Strong MLE answers show practical understanding of production ML systems."
    },
}

def get_role_rubric(role: str) -> dict:
    """Get the scoring rubric for a specific role."""
    normalized = role.lower().strip()
    
    # Map common variations
    role_map = {
        "swe": "Software Engineer",
        "software engineer": "Software Engineer",
        "backend": "Software Engineer",
        "frontend": "Full Stack Developer",
        "fullstack": "Full Stack Developer",
        "pm": "Product Manager",
        "product manager": "Product Manager",
        "data": "Data Scientist",
        "data scientist": "Data Scientist",
        "ml": "Machine Learning Engineer",
        "ml engineer": "Machine Learning Engineer",
        "qa": "QA Engineer",
        "devops": "DevOps Engineer",
        "sre": "DevOps Engineer",
    }
    
    for pattern, canonical in role_map.items():
        if pattern in normalized:
            return ROLE_SCORING_RUBRICS.get(canonical, ROLE_SCORING_RUBRICS["Software Engineer"])
    
    return ROLE_SCORING_RUBRICS.get(role, ROLE_SCORING_RUBRICS["Software Engineer"])


def check_ollama_health() -> dict:
    """
    Check LLM provider health.
    Returns dict with status and available models.
    When GROQ_API_KEY is set, validates the key by listing Groq models.
    Otherwise falls back to checking local Ollama.
    """
    if GROQ_API_KEY:
        try:
            headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
            resp = requests.get("https://api.groq.com/openai/v1/models", headers=headers, timeout=10)
            if resp.status_code == 200:
                models = [m["id"] for m in resp.json().get("data", [])]
                our_model = GROQ_MODEL in models
                return {
                    "status": "connected",
                    "provider": "groq",
                    "model_available": our_model,
                    "model_name": GROQ_MODEL,
                    "available_models": models[:20],
                    "message": f"Groq connected. Model '{GROQ_MODEL}' {'✓ available' if our_model else '✗ NOT found in Groq catalog. GROQ_MODEL=' + GROQ_MODEL}"
                }
            detail = ""
            try:
                detail = resp.json().get("error", {}).get("message", "")
            except Exception:
                detail = resp.text[:200]
            return {"status": "error", "provider": "groq", "message": f"Groq returned {resp.status_code}: {detail}"}
        except requests.exceptions.ConnectionError:
            return {"status": "disconnected", "provider": "groq", "message": "Cannot connect to Groq API."}
        except Exception as e:
            return {"status": "error", "provider": "groq", "message": f"Groq check failed: {str(e)}"}

    # Fallback: Ollama local check
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if resp.status_code == 200:
            models = [m['name'] for m in resp.json().get('models', [])]
            our_model = OLLAMA_MODEL in models
            return {
                "status": "connected",
                "provider": "ollama",
                "model_available": our_model,
                "model_name": OLLAMA_MODEL,
                "available_models": models,
                "message": f"Ollama is running. Model '{OLLAMA_MODEL}' {'✓ available' if our_model else '✗ NOT found. Run: ollama pull ' + OLLAMA_MODEL}"
            }
        return {"status": "error", "provider": "ollama", "message": f"Ollama returned status {resp.status_code}"}
    except requests.exceptions.ConnectionError:
        return {
            "status": "disconnected",
            "provider": "ollama",
            "model_available": False,
            "message": "Cannot connect to Ollama. Install: https://ollama.com, then run: ollama serve"
        }

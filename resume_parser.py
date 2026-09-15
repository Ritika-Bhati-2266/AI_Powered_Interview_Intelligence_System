"""
Resume Parser Module
Extracts text content from PDF and DOCX resume files.
Uses PyPDF2 for PDFs and python-docx for DOCX files.
Provides basic skill extraction from text content.
"""

import re
import os


def extract_text_from_pdf(filepath: str) -> str:
    """
    Extract text content from a PDF file.
    
    Args:
        filepath: Absolute or relative path to PDF file
    
    Returns:
        Extracted text as a single string
    
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file is not a valid PDF
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Resume file not found: {filepath}")

    try:
        from PyPDF2 import PdfReader
    except ImportError:
        raise ImportError("PyPDF2 is required. Install with: pip install PyPDF2")

    try:
        reader = PdfReader(filepath)
        text_parts = []

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

        full_text = "\n".join(text_parts)

        if not full_text.strip():
            # Some PDFs have extractable text issues
            raise ValueError("PDF appears to be a scanned image or has no extractable text")

        return full_text.strip()

    except Exception as e:
        if isinstance(e, (FileNotFoundError, ValueError, ImportError)):
            raise
        raise ValueError(f"Failed to parse PDF: {str(e)}")


def extract_text_from_docx(filepath: str) -> str:
    """
    Extract text content from a DOCX file.
    
    Args:
        filepath: Absolute or relative path to DOCX file
    
    Returns:
        Extracted text as a single string
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Resume file not found: {filepath}")

    try:
        from docx import Document
    except ImportError:
        raise ImportError("python-docx is required. Install with: pip install python-docx")

    try:
        doc = Document(filepath)
        text_parts = []

        # Extract text from paragraphs
        for para in doc.paragraphs:
            if para.text.strip():
                text_parts.append(para.text)

        # Also extract text from tables
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text.strip():
                        text_parts.append(cell.text)

        return "\n".join(text_parts).strip()

    except Exception as e:
        raise ValueError(f"Failed to parse DOCX: {str(e)}")


def extract_text(filepath: str) -> str:
    """
    Extract text from a resume file (auto-detect format by extension).
    
    Args:
        filepath: Path to resume (PDF or DOCX)
    
    Returns:
        Extracted plain text
    """
    ext = os.path.splitext(filepath)[1].lower()

    if ext == '.pdf':
        return extract_text_from_pdf(filepath)
    elif ext == '.docx':
        return extract_text_from_docx(filepath)
    else:
        raise ValueError(f"Unsupported file format: {ext}. Please upload a PDF or DOCX file.")


def extract_skills(text: str) -> list:
    """
    Extract technical skills from resume text using keyword matching.
    Detects programming languages, frameworks, tools, and technologies.
    
    Args:
        text: Plain text extracted from resume
    
    Returns:
        Sorted list of identified skills (lowercase, deduplicated)
    """
    if not text:
        return []

    text_lower = text.lower()

    # Comprehensive skill keyword list organized by category
    skill_keywords = {
        # Programming Languages
        "python", "javascript", "typescript", "java", "c++", "c#", "ruby", "go", "golang",
        "rust", "swift", "kotlin", "scala", "php", "perl", "r", "matlab", "dart", "lua",
        "bash", "shell", "sql", "graphql", "html", "css", "sass", "less", "julia",
        "c", "objective-c", "elixir", "haskell", "clojure", "solidity",

        # Frontend Frameworks
        "react", "angular", "vue", "vue.js", "svelte", "next.js", "nuxt", "gatsby",
        "jquery", "bootstrap", "tailwind", "material-ui", "chakra-ui", "redux",
        "webpack", "vite", "parcel", "electron", "react native", "flutter",

        # Backend Frameworks
        "django", "flask", "fastapi", "spring", "spring boot", "ruby on rails",
        "express", "node.js", "laravel", "asp.net", "gin", "echo", "fiber",
        "ktor", "actix", "rocket",

        # Databases
        "postgresql", "postgres", "mysql", "mongodb", "redis", "sqlite",
        "oracle", "sql server", "mariadb", "cassandra", "dynamodb", "firebase",
        "elasticsearch", "neo4j", "couchdb", "influxdb", "supabase",

        # Cloud & DevOps
        "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "k8s",
        "jenkins", "github actions", "gitlab ci", "circleci", "terraform",
        "ansible", "puppet", "chef", "helm", "argocd", "prometheus", "grafana",
        "nginx", "apache", "cloudflare", "heroku", "vercel", "netlify",

        # Data Science & ML
        "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy",
        "jupyter", "spark", "hadoop", "airflow", "mlflow", "dvc",
        "opencv", "nltk", "hugging face", "langchain", "llama", "ollama",
        "machine learning", "deep learning", "nlp", "computer vision",
        "data science", "data analysis", "statistics",

        # Tools & Platforms
        "git", "github", "gitlab", "bitbucket", "jira", "confluence",
        "figma", "sketch", "photoshop", "trello", "asana", "notion",
        "slack", "discord", "postman", "insomnia", "swagger",
        "linux", "unix", "macos", "windows", "vim", "vscode", "intellij",
        "yarn", "npm", "pnpm", "pip", "maven", "gradle",

        # Testing
        "jest", "mocha", "chai", "pytest", "cypress", "selenium",
        "playwright", "junit", "unittest", "rspec", "testng",

        # Concepts
        "rest api", "restful", "microservices", "api", "graphql",
        "ci/cd", "agile", "scrum", "tdd", "devops", "serverless",
        "event-driven", "message queue", "rabbitmq", "kafka",
        "unit testing", "integration testing", "e2e testing",
    }

    found_skills = set()
    skill_pattern_lower = {s.lower() for s in skill_keywords}

    # Check each skill keyword
    for skill in skill_pattern_lower:
        # Use word boundary matching to avoid false positives
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.add(skill)

    # Also extract capitalized proper nouns that appear with high frequency
    # (company names, specific technologies not in our list)
    words = text_lower.split()

    return sorted(found_skills)


# Role -> common expected skills for ATS fallback when JD not provided
ROLE_COMMON_SKILLS = {
    "python developer": ["python", "django", "flask", "fastapi", "sql", "git", "rest api", "docker"],
    "full stack developer": ["javascript", "react", "node.js", "express", "mongodb", "sql", "html", "css", "git"],
    "frontend developer": ["javascript", "typescript", "react", "angular", "vue", "html", "css", "tailwind"],
    "backend developer": ["python", "java", "node.js", "express", "sql", "mongodb", "rest api", "docker"],
    "data scientist": ["python", "machine learning", "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "sql"],
    "machine learning engineer": ["python", "tensorflow", "pytorch", "machine learning", "deep learning", "scikit-learn", "mlflow"],
    "devops engineer": ["docker", "kubernetes", "aws", "jenkins", "terraform", "linux", "ci/cd", "ansible"],
    "software engineer": ["python", "java", "javascript", "sql", "git", "rest api", "docker", "agile"],
    "react developer": ["react", "javascript", "typescript", "redux", "html", "css", "node.js", "git"],
    "node.js developer": ["node.js", "javascript", "express", "mongodb", "sql", "rest api", "docker", "git"],
    "java developer": ["java", "spring", "spring boot", "sql", "hibernate", "maven", "git", "rest api"],
    "cloud engineer": ["aws", "azure", "gcp", "docker", "kubernetes", "terraform", "linux", "jenkins"],
    "product manager": ["agile", "scrum", "jira", "confluence", "roadmap", "analytics", "api", "sql"],
    "data analyst": ["sql", "python", "pandas", "excel", "tableau", "statistics", "data analysis", "power bi"],
    "qa engineer": ["selenium", "pytest", "junit", "testng", "cypress", "postman", "agile", "sql"],
}

_STOPWORDS = {
    "the", "and", "for", "with", "you", "are", "have", "this", "that", "will", "from", "your",
    "our", "their", "about", "which", "when", "what", "where", "experience", "years", "year",
    "must", "should", "required", "requirements", "responsibilities", "looking", "candidate",
    "role", "position", "company", "team", "work", "working", "ability", "knowledge", "skill",
    "skills", "strong", "good", "excellent", "plus", "including", "using", "within", "across",
}


def _extract_jd_terms(jd_text: str) -> list:
    """Extract important keyword terms from JD (skip stopwords, length>2)."""
    if not jd_text:
        return []
    # Lowercase and extract words (alphanumeric + . + - + #)
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9\.\-\+#]*", jd_text.lower())
    terms = []
    seen = set()
    for w in words:
        w = w.strip(".-")
        if len(w) < 3 or w in _STOPWORDS:
            continue
        # Filter pure numbers
        if re.match(r"^\d+$", w):
            continue
        if w not in seen:
            seen.add(w)
            terms.append(w)
    return terms


def calculate_ats_score(resume_text: str, jd_text: str = "", role: str = "", extracted_skills: list = None) -> dict:
    """
    Calculate ATS-style match score for resume.
    Returns dict: {
        "score": int (0-100),
        "breakdown": {
            "skills_match": int (0-40),
            "experience_keywords": int (0-20),
            "education": int (0-15),
            "formatting": int (0-10),
            "keyword_density": int (0-15)
        },
        "missing_keywords": list[str],
        "matched_keywords": list[str]
    }
    """
    try:
        resume_text = resume_text or ""
        jd_text = jd_text or ""
        role = role or ""
        extracted_skills = extracted_skills or []
        if extracted_skills is None:
            extracted_skills = extract_skills(resume_text)
        # Normalize
        resume_lower = resume_text.lower()
        jd_lower = jd_text.lower()
        extracted_lower = set(s.lower() for s in extracted_skills)

        # ── Skills match (40) ──
        skills_match = 0
        matched_keywords = []
        missing_keywords = []
        if jd_lower.strip():
            # JD-based: extract required skills by scanning JD against skill_keywords
            # Reuse skill_keywords from extract_skills scope — rebuild minimal set
            # Approach: JD terms that are also known skills
            jd_terms = _extract_jd_terms(jd_text)
            # Required skills are JD terms that appear in our skill universe
            # Build quick skill universe
            skill_universe = set(
                s.lower() for s in [
                    "python","javascript","typescript","java","c++","c#","ruby","go","golang","rust","swift","kotlin","scala","php",
                    "react","angular","vue","next.js","django","flask","fastapi","spring","express","node.js","postgresql","mysql","mongodb","redis",
                    "aws","azure","gcp","docker","kubernetes","jenkins","terraform","ansible","helm","prometheus","grafana","nginx",
                    "tensorflow","pytorch","keras","scikit-learn","pandas","numpy","spark","hadoop","git","github","jira","figma",
                    "jest","pytest","selenium","cypress","rest api","microservices","ci/cd","agile","kafka","rabbitmq"
                ]
            )
            required_skills = set()
            for term in jd_terms:
                if term in skill_universe:
                    required_skills.add(term)
                # Also check multi-word? For simplicity, also scan JD lower for exact skill phrase
            # Also directly scan JD for skill universe via regex (covers "react native" etc)
            for sk in skill_universe:
                if re.search(r'\b' + re.escape(sk) + r'\b', jd_lower):
                    required_skills.add(sk)
            if required_skills:
                matched = extracted_lower.intersection(required_skills)
                missing = required_skills - extracted_lower
                matched_keywords = sorted(matched)[:8]
                missing_keywords = sorted(missing)[:8]
                ratio = len(matched) / len(required_skills) if required_skills else 0
                skills_match = int(round(ratio * 40))
            else:
                # No skill-like terms in JD — fallback to generic JD term overlap for skills_match
                jd_terms_set = set(jd_terms[:20])
                if jd_terms_set:
                    overlap = sum(1 for t in jd_terms_set if t in resume_lower)
                    ratio = overlap / len(jd_terms_set) if jd_terms_set else 0
                    skills_match = int(round(ratio * 40))
                    # For missing/matched, use JD terms
                    matched_keywords = [t for t in jd_terms[:8] if t in resume_lower][:8]
                    missing_keywords = [t for t in jd_terms[:8] if t not in resume_lower][:8]
                else:
                    skills_match = 20  # neutral
        else:
            # Role-based fallback
            role_key = role.lower().strip()
            role_skills = ROLE_COMMON_SKILLS.get(role_key)
            if not role_skills:
                # Try partial match
                for k, v in ROLE_COMMON_SKILLS.items():
                    if k in role_key or role_key in k:
                        role_skills = v
                        break
            if not role_skills:
                role_skills = ROLE_COMMON_SKILLS.get("software engineer", [])
            role_set = set(s.lower() for s in role_skills)
            matched = extracted_lower.intersection(role_set)
            missing = role_set - extracted_lower
            matched_keywords = sorted(matched)[:8]
            # If no extracted skills at all, missing will be full role set
            missing_keywords = sorted(missing)[:8]
            ratio = len(matched) / len(role_set) if role_set else 0
            skills_match = int(round(ratio * 40))
            # If resume empty, ensure 0
            if not resume_text.strip():
                skills_match = 0

        skills_match = max(0, min(40, skills_match))

        # ── Experience keywords (20) ──
        exp_keywords = ["led", "managed", "developed", "implemented", "built", "designed", "created", "delivered", "achieved", "improved", "optimized", "launched", "mentored"]
        exp_score = 0
        if resume_text.strip():
            found_exp = sum(1 for kw in exp_keywords if re.search(r'\b' + re.escape(kw) + r'\b', resume_lower))
            # Cap at 4 keywords * 3 pts =12
            exp_score += min(found_exp * 3, 12)
            # Quantified achievements: numbers with % or numbers + years/months
            has_percent = bool(re.search(r'\d+%', resume_text))
            has_number = bool(re.search(r'\b\d+[\+]?\s*(years?|months?|projects?|users?|clients?)\b', resume_lower))
            has_years_phrase = "years of experience" in resume_lower or "year of experience" in resume_lower
            if has_percent:
                exp_score += 4
            if has_number:
                exp_score += 2
            if has_years_phrase:
                exp_score += 2
            exp_score = min(20, exp_score)
        experience_keywords = max(0, min(20, exp_score))

        # ── Education (15) ──
        edu_score = 0
        if resume_text.strip():
            degree_pattern = r'\b(b\.?tech|b\.?e\.?|m\.?tech|m\.?e\.?|bachelor|master|b\.?sc|m\.?sc|mba|ph\.?d|doctorate|degree|university|college|institute)\b'
            if re.search(degree_pattern, resume_lower):
                edu_score += 8
            field_pattern = r'\b(computer science|information technology|electronics|mechanical|civil|engineering|data science|artificial intelligence|commerce|business)\b'
            if re.search(field_pattern, resume_lower):
                edu_score += 7
        education = max(0, min(15, edu_score))

        # ── Formatting (10) ──
        fmt_score = 0
        if not resume_text.strip():
            formatting = 0
        else:
            length = len(resume_text)
            if 300 <= length <= 8000:
                fmt_score += 4
            elif 200 <= length < 300 or 8000 < length <= 12000:
                fmt_score += 2
            # Sections present
            sections = ["education", "experience", "skills", "projects", "summary", "objective"]
            found_sections = sum(1 for sec in sections if re.search(r'\b' + re.escape(sec) + r'\b', resume_lower))
            fmt_score += min(found_sections, 4)  # up to 4
            # Excessive special characters
            special_count = len(re.findall(r'[^\w\s.,;:\-\(\)\/]', resume_text))
            ratio_special = special_count / max(length, 1)
            if ratio_special < 0.15:
                fmt_score += 2
            formatting = max(0, min(10, fmt_score))
            # Ensure variable name consistency
            formatting = fmt_score
        formatting = max(0, min(10, formatting if 'formatting' in locals() else fmt_score))

        # ── Keyword density (15) ──
        keyword_density = 0
        if jd_lower.strip():
            jd_terms = _extract_jd_terms(jd_text)
            # Use top 20 distinct JD terms
            distinct = []
            seen = set()
            for t in jd_terms:
                if t not in seen:
                    seen.add(t)
                    distinct.append(t)
                if len(distinct) >= 20:
                    break
            if distinct:
                found = sum(1 for t in distinct if re.search(r'\b' + re.escape(t) + r'\b', resume_lower))
                ratio = found / len(distinct) if distinct else 0
                keyword_density = int(round(ratio * 15))
                # If no resume, 0
                if not resume_text.strip():
                    keyword_density = 0
            else:
                keyword_density = 0
            # Override missing/matched if still empty and JD present — use JD terms
            if not matched_keywords and not missing_keywords and distinct:
                matched_keywords = [t for t in distinct[:8] if re.search(r'\b' + re.escape(t) + r'\b', resume_lower)][:8]
                missing_keywords = [t for t in distinct[:8] if not re.search(r'\b' + re.escape(t) + r'\b', resume_lower)][:8]
        else:
            # JD empty — fallback: density based on role keywords overlap (already counted in skills_match partially, but give partial)
            # Use role skills density
            role_key = role.lower().strip()
            role_skills = ROLE_COMMON_SKILLS.get(role_key)
            if not role_skills:
                for k, v in ROLE_COMMON_SKILLS.items():
                    if k in role_key or role_key in k:
                        role_skills = v
                        break
            if not role_skills:
                role_skills = ROLE_COMMON_SKILLS.get("software engineer", [])
            # Count how many role skills appear as substrings
            if role_skills and resume_text.strip():
                found = sum(1 for sk in role_skills if re.search(r'\b' + re.escape(sk.lower()) + r'\b', resume_lower))
                ratio = found / len(role_skills) if role_skills else 0
                keyword_density = int(round(ratio * 15))
            else:
                keyword_density = 0

        keyword_density = max(0, min(15, keyword_density))

        total = skills_match + experience_keywords + education + formatting + keyword_density
        total = max(0, min(100, total))
        # Empty resume -> ensure low score
        if not resume_text.strip():
            total = min(total, 10)
            # Force breakdown to minimal if empty
            if total > 10:
                total = 5

        breakdown = {
            "skills_match": skills_match,
            "experience_keywords": experience_keywords,
            "education": education,
            "formatting": formatting,
            "keyword_density": keyword_density,
        }

        return {
            "score": int(total),
            "breakdown": breakdown,
            "missing_keywords": missing_keywords[:8],
            "matched_keywords": matched_keywords[:8],
        }
    except Exception:
        # Graceful fallback — never crash
        return {
            "score": 0,
            "breakdown": {
                "skills_match": 0,
                "experience_keywords": 0,
                "education": 0,
                "formatting": 0,
                "keyword_density": 0,
            },
            "missing_keywords": [],
            "matched_keywords": [],
        }


def extract_name(text: str) -> str:
    """
    Attempt to extract candidate name from resume text.
    Looks for patterns like "Name" at the top of the document.
    
    Args:
        text: Plain text from resume
    
    Returns:
        Extracted name or empty string
    """
    if not text:
        return ""

    lines = text.strip().split('\n')
    
    # Usually the first non-empty line is the name
    for line in lines[:10]:
        line = line.strip()
        if line and len(line) < 40 and not re.match(r'^[\d\s@#$%^&*()]+$', line):
            # Skip obvious non-name lines
            if not any(word in line.lower() for word in
                       ['resume', 'cv', 'curriculum', 'vitae', 'email', '@', 'phone',
                        'linkedin', 'github', 'address', 'summary', 'profile']):
                # Check it looks like a name (2-4 words, mostly alpha)
                words = line.split()
                if 1 < len(words) <= 4 and all(w.rstrip('.').isalpha() for w in words if w):
                    # Reject lines where every word is a section heading word
                    section_words = {
                        'skills', 'experience', 'education', 'projects', 'summary',
                        'profile', 'certifications', 'publications', 'patents',
                        'awards', 'honors', 'languages', 'interests', 'volunteering',
                        'references', 'leadership', 'technical', 'professional',
                        'work', 'additional', 'information', 'objective',
                        'qualifications', 'achievements', 'activities', 'research',
                        'training', 'employment', 'history', 'background', 'contact',
                        'details', 'personal', 'expertise', 'competencies',
                        'capabilities', 'highlights', 'accomplishments', 'career',
                        'affiliations', 'community', 'internships', 'courses',
                        'extracurricular', 'data', 'related', 'tools', 'platforms',
                        'frameworks', 'libraries', 'databases', 'operating', 'systems',
                        'methodologies', 'concepts', 'core', 'relevant', 'key',
                        'strengths', 'portfolio', 'seminars', 'workshops',
                    }
                    cleaned = [w.rstrip('.').lower() for w in words if w]
                    if all(w in section_words for w in cleaned):
                        continue
                    return line.strip()

    return ""


def extract_email(text: str) -> str:
    """Extract email address from text."""
    match = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', text)
    return match.group(0) if match else ""


def parse_resume(filepath: str) -> dict:
    """
    Complete resume parsing: extract text, detect format, identify skills,
    and return structured information.
    
    Args:
        filepath: Path to resume file
    
    Returns:
        Dict with keys: text, skills, name, email, format, success, error
    """
    result = {
        "text": "",
        "skills": [],
        "name": "",
        "email": "",
        "format": "",
        "success": False,
        "error": None,
    }

    try:
        # Detect format
        ext = os.path.splitext(filepath)[1].lower()
        if ext == '.pdf':
            result["format"] = "pdf"
            result["text"] = extract_text_from_pdf(filepath)
        elif ext == '.docx':
            result["format"] = "docx"
            result["text"] = extract_text_from_docx(filepath)
        else:
            result["error"] = f"Unsupported format: {ext}"
            return result

        # Extract information
        result["skills"] = extract_skills(result["text"])
        result["name"] = extract_name(result["text"])
        result["email"] = extract_email(result["text"])
        result["success"] = True

    except FileNotFoundError as e:
        result["error"] = str(e)
    except ValueError as e:
        result["error"] = str(e)
    except ImportError as e:
        result["error"] = str(e)
    except Exception as e:
        result["error"] = f"Unexpected error parsing resume: {str(e)}"

    return result

import httpx
import logging
import json
from typing import Dict, Any, List

from src.config import ai_config
from src.question_gen.rules import generate_fallback_questions

logger = logging.getLogger("ai-engine-generator")

class QuestionGenerator:
    def __init__(self):
        self.ollama_url = f"{ai_config.OLLAMA_BASE_URL}/api/generate"
        self.model = ai_config.OLLAMA_MODEL

    async def generate_questions(self, resume_data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Generates interview questions based on candidate resume data.
        Attempts to use local Ollama LLM, falling back to heuristic templates if unavailable.
        """
        logger.info("Initializing interview question generation...")
        
        # Build prompt for local LLM
        prompt = self._build_prompt(resume_data)
        
        # Try local Ollama
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                logger.info(f"Connecting to Ollama at {self.ollama_url} using model '{self.model}'...")
                response = await client.post(
                    self.ollama_url,
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "format": "json",
                        "stream": False
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    response_text = result.get("response", "")
                    parsed_questions = json.loads(response_text)
                    logger.info("Successfully generated structured questions via local Ollama LLM.")
                    return self._normalize_llm_output(parsed_questions)
                else:
                    logger.warning(f"Ollama returned status code {response.status_code}. Falling back to rule-based templates.")
                    
        except httpx.ConnectError:
            logger.warning("Ollama service offline. Seamlessly falling back to local rule-based questions.")
        except Exception as e:
            logger.warning(f"Error during Ollama question generation: {e}. Falling back to rule-based questions.")
            
        # Fallback to pure rule-based system
        return generate_fallback_questions(resume_data)

    def _build_prompt(self, resume_data: Dict[str, Any]) -> str:
        """Construct the prompt instructing the LLM to output clean JSON matching our schema."""
        candidate_name = resume_data.get("candidate_name", "Candidate")
        skills = resume_data.get("skills", [])
        experience_years = resume_data.get("experience_years", 2)
        projects = resume_data.get("projects", [])
        
        prompt_text = f"""
        You are an expert interviewer. Analyze this candidate's resume summary and generate exactly:
        - 3 HR (behavioral) questions
        - 5 Technical questions based on their core skills
        - 3 Follow-up questions based on their highlighted projects
        
        Candidate Profile:
        - Name: {candidate_name}
        - Experience: {experience_years} years
        - Technical Skills: {', '.join(skills)}
        - Key Projects: {json.dumps(projects)}
        
        Return ONLY a JSON object with the following schema:
        {{
            "hr": [
                {{
                    "id": "hr-1",
                    "question": "question text",
                    "focus": "focus area",
                    "difficulty": "Medium"
                }}
            ],
            "technical": [
                {{
                    "id": "tech-1",
                    "question": "question text",
                    "focus": "skill/focus area",
                    "difficulty": "Hard/Medium"
                }}
            ],
            "follow_up": [
                {{
                    "id": "follow-1",
                    "question": "question text",
                    "focus": "project/topic",
                    "difficulty": "Medium"
                }}
            ]
        }}
        """
        return prompt_text

    def _normalize_llm_output(self, raw_json: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Ensures all standard categories exist in LLM response."""
        normalized = {
            "hr": raw_json.get("hr", []),
            "technical": raw_json.get("technical", []),
            "follow_up": raw_json.get("follow_up", [])
        }
        return normalized

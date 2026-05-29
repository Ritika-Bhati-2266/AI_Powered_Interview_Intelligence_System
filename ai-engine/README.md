# AI Evaluation & Question Generation Engine

This module handles:
1. Candidate technical & behavioral profiling.
2. Personalized interview question generation.
3. Scoring, evaluation, and grading of candidate feedback.

## Features
- **Local Heuristics Generator**: Built-in template matching mapping candidate skills, seniority levels, and projects to comprehensive technical and behavioral questions.
- **Ollama Integration**: Automated semantic generation via local Ollama LLMs (e.g., `llama3`, `mistral`, `phi3`) returning structured JSON output.
- **Transparent Fallback**: Seamless, high-performance rule execution in case the Ollama service is unreachable.

## Setup & Running
Install dependencies:
```bash
pip install -r requirements.txt
```

Run manual generation tests by calling `QuestionGenerator().generate_questions(resume_data)`.

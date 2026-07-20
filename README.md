# AI Interview Intelligence System

A full-stack AI Interview Coach that runs locally with Flask, SQLite, Ollama (LLM), and
OpenAI Whisper (speech-to-text). Candidates register, upload a resume, choose a role
and company, answer role-specific questions (text or voice), receive instant multi-dimension
feedback, and may rewrite each answer once for a re-score.

## Features

- **Candidate registration** with resume parsing (PDF/DOCX) and skill extraction
- **Multi-round interviews** tailored to companies (Amazon, Google, Microsoft, Meta, etc.)
- **Role-specific questions** for SWE, PM, DS, QA, DevOps, and more
- **Local LLM** (Ollama) for question generation and answer evaluation
- **Local speech-to-text** (Whisper) — record or upload audio, transcript is auto-filled
- **Filler-word detection** (`um`, `uh`, `like`, `you know`, etc.) with score impact
- **One rewrite per answer** — see feedback, rewrite, get a second evaluation
- **Persistent history** in SQLite — sessions, answers, skill gaps, recommendations
- **Dashboard** with progress charts, skill radar, and per-session comparison

## Requirements

- Python 3.10+
- Ollama running locally (`ollama serve`)
- `ffmpeg` on PATH (required by Whisper)

### Install ffmpeg on Windows

```bash
# Using winget (recommended)
winget install Gyan.FFmpeg

# Or download from https://www.gyan.dev/ffmpeg/builds/ and add bin/ to PATH
ffmpeg -version  # verify
```

### Install Ollama model

```bash
ollama serve               # in one terminal
ollama pull llama3.2:latest   # or llama3.1, llama3.2
```

### Install Python dependencies

```bash
cd ai-interview-system
python -m pip install -r requirements.txt
```

Whisper downloads the `base` model on first transcription (~140 MB). Override with
the environment variable `WHISPER_MODEL=tiny|base|small|medium|large`.

## Run

```bash
python app.py
# Server: http://127.0.0.1:5050
```

## Run tests

```bash
python -m pytest tests/ -v
```

## Project layout

```
ai-interview-system/
├── app.py                 # Flask routes
├── ai_service.py          # Ollama LLM prompts + role rubrics
├── interview_engine.py    # Session state, rounds, evaluation
├── stt_service.py         # Whisper STT + filler-word detection
├── resume_parser.py       # PDF/DOCX resume parsing
├── company_rounds.py      # Per-company round structures
├── coding_questions_bank.py
├── aptitude_bank.py       # Aptitude MCQ bank
├── templates/             # HTML pages
├── static/                # CSS/JS
└── tests/                 # pytest suite
```

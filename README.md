# AI Interview Intelligence System

A full-stack AI Interview Coach that runs locally with Flask, SQLite, Groq cloud API or Ollama (LLM),
and OpenAI Whisper (speech-to-text). Candidates register, upload a resume, choose a role
and company, answer role-specific questions (text or voice), receive instant multi-dimension
feedback, and may rewrite each answer once for a re-score.

## Features

- **Candidate registration** with resume parsing (PDF/DOCX) and skill extraction
- **Multi-round interviews** tailored to companies (Amazon, Google, Microsoft, Meta, etc.)
- **Role-specific questions** for SWE, PM, DS, QA, DevOps, and more
- **LLM** (Groq cloud API or local Ollama) for question generation and answer evaluation
- **Local speech-to-text** (Whisper) — record or upload audio, transcript is auto-filled
- **Filler-word detection** (`um`, `uh`, `like`, `you know`, etc.) with score impact
- **One rewrite per answer** — see feedback, rewrite, get a second evaluation
- **Persistent history** in SQLite — sessions, answers, skill gaps, recommendations
- **Dashboard** with progress charts, skill radar, and per-session comparison

## Requirements

- Python 3.10+
- `ffmpeg` on PATH (required by Whisper)
- **Either** a Groq API key (cloud, recommended for deployment),
  **or** Ollama running locally (`ollama serve`) for local-only use

### Install ffmpeg on Windows

```bash
# Using winget (recommended)
winget install Gyan.FFmpeg

# Or download from https://www.gyan.dev/ffmpeg/builds/ and add bin/ to PATH
ffmpeg -version  # verify
```

### Set up LLM provider

**Option A — Groq (cloud, preferred for Render deployment):**

1. Get a free API key from https://console.groq.com/keys
2. Copy `.env.example` to `.env` and set your key:
   ```
   GROQ_API_KEY=gsk_your_key_here
   ```

**Option B — Ollama (local, easy for development):**

```bash
ollama serve               # in one terminal
ollama pull llama3.2:latest
```

### Install Python dependencies

```bash
cd ai-interview-system
python -m pip install -r requirements.txt
```

Whisper downloads the `base` model on first transcription (~140 MB). Override with
the environment variable `WHISPER_MODEL=tiny|base|small|medium|large`.

## Environment Variables

Create a `.env` file (copy from `.env.example`) with these optional overrides:

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | — | Groq API key (set this on Render; omit for local Ollama) |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Groq model ID |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL (fallback when no `GROQ_API_KEY`) |
| `OLLAMA_MODEL` | `llama3.2:latest` | Ollama model name |
| `WHISPER_MODEL` | `base` | Whisper model size: `tiny`, `base`, `small`, `medium`, `large` |
| `SECRET_KEY` | random | Flask session secret (set a fixed value on Render to persist sessions across restarts) |

## Deploy to Render

This app requires **ffmpeg** at the system level (the Python package `ffmpeg-python` is
only a wrapper — it does not bundle the binary). Render's default Python runtime does
**not** include ffmpeg, so you need a `render.yaml` with a pre-build command or a Dockerfile.

**Important:** On Render you **must** set `GROQ_API_KEY` in the environment variables
(Groq is a cloud API that works from any server). Ollama only runs locally and will
not be accessible from Render.

### Option A — render.yaml (Blueprint)

```yaml
services:
  - type: web
    name: ai-interview-system
    env: python
    buildCommand: |
      apt-get update && apt-get install -y ffmpeg
      pip install -r requirements.txt
    startCommand: gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 300
    envVars:
      - key: GROQ_API_KEY
        sync: false          # Enter manually in Render dashboard (never committed)
      - key: GROQ_MODEL
        value: llama-3.3-70b-versatile
      - key: WHISPER_MODEL
        value: tiny
      - key: SECRET_KEY
        sync: false
      - key: PYTHON_VERSION
        value: 3.11.9
```

### Option B — Dockerfile

```dockerfile
FROM python:3.11-slim
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 300
```

Set `GROQ_API_KEY` in Render's dashboard (Environment Variables → Add Secret File or
manual entry). Use `WHISPER_MODEL=tiny` to reduce cold-start download time.
Persistent storage (SQLite) will reset on each deploy — mount a Render Disk
or switch to PostgreSQL for production.

## Run

```bash
# Local dev with Ollama (no API key needed):
python app.py

# Or with Groq (set .env first):
# GROQ_API_KEY=gsk_... python app.py

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
├── ai_service.py          # LLM (Groq / Ollama) prompts + role rubrics
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

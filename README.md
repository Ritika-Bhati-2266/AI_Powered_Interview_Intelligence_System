# AI Interview Intelligence System

A production-ready, modular, and 100% offline-compatible AI Interview System. This project structures interactive video and audio ingestion, real-time speech transcription, and local AI evaluation to simulate professional recruitment loops without requiring external paid APIs.

---

## System Architecture

```
AI Interview Intelligence System/
├── backend/                # FastAPI Backend Service (Orchestration & Event Bus)
├── frontend/               # Next.js 14 Web UI (TypeScript + Tailwind CSS)
├── ai-engine/              # Question Generator Engine (Rule-based & Ollama LLM support)
├── cv-engine/              # Computer Vision Engine (Emotion & Posture extraction)
├── speech-engine/          # Speech Processing Engine (Offline Vosk STT)
└── models/                 # Model registry and offline weights downloader
```

### Key Architectural Flows
1. **Resume Processing**: The user uploads a resume PDF. The `backend` calls the local PyMuPDF extractor to parse skills, projects, and career milestones.
2. **Contextual Questioning**: The `ai-engine` consumes the resume JSON, targeting key technologies to generate **HR**, **Technical**, and **Follow-up** questions. It connects dynamically to a local **Ollama** daemon (defaults to `llama3`) or executes highly optimized fallback templates if offline.
3. **Real-time Evaluation**: The user joins an interactive interview space. Microphone audio downsampled to 16kHz is streamed down a **FastAPI WebSocket** (`/ws/interview`). The `speech-engine` pipes these chunks into **Vosk** to stream live text transcripts and word-level timestamps.
4. **Behavioral Telemetry**: Frontend WebRTC streams or calculations for emotion/posture feed into the `cv-engine` via WebSocket channels. The backend **Event Bus** orchestrates state updates and publishes insights reactively.

---

## Local Setup Instructions

### 1. Requirements
- Python 3.10+
- Node.js 18+
- Ollama (Optional, for advanced LLM question variations)

### 2. Install & Start Backend
From the root directory:
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```
The server will boot on `http://localhost:8000`. You can query the health endpoint at `http://localhost:8000/health`.

### 3. Fetch Offline Speech Models
In another terminal, download the local Vosk STT small model (~40MB) to enable full offline transcription:
```bash
cd models
python download_weights.py
```

### 4. Install & Start Frontend
From the root directory:
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:3000` in your web browser.

---

## Key Scaffolding Modules

### 1. Async Event Bus (`backend/app/core/event_bus.py`)
Provides reactive publish/subscribe handling for real-time video/audio telemetry and transcriptions, ensuring decoupled processing.

### 2. Session Manager (`backend/app/services/session_manager.py`)
Thread-safe session tracking. Manages candidate details, question buffers, WebSocket registries, and aggregated session performance indicators.

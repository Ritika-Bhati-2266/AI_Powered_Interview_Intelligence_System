# Speech Processing Engine

This engine handles high-fidelity offline speech-to-text processing, text-to-speech feedback, and voice prosody metrics.

## Features
- **Offline Transcription**: Powered by **Vosk** Kaldi engines. Processes 16kHz mono PCM chunks locally.
- **Word-Level Timing**: Emits word arrays matching spoken bounds for live highlighting and pacing reviews.
- **Filler Word Spotting**: Highlights hesitation patterns like "um", "ah", "like", and pacing features.

## Setup
Install dependencies:
```bash
pip install -r requirements.txt
```
To run full offline features, place Vosk weights under `models/vosk_models/vosk-model-small-en-us-0.15`.

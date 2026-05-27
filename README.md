<<<<<<< HEAD
# AI Interview Intelligence System (Local Multimodal DS Pro)

Aegis AI is an advanced, multimodal, and locally run AI Mock Interview Platform built on standard consumer hardware. It evaluates user speech and articulation using open-source, offline AI engines without any paid API dependencies.

---

## 🛠️ Tech Stack & Local AI Pipeline

1. **Frontend**: [Streamlit](https://streamlit.io/) with custom dark futuristic CSS styling.
2. **Speech-to-Text**: [Whisper Tiny](https://github.com/openai/whisper) loads locally on CPU to transcribe recorded audio waveforms.
3. **Audio Analytics**: [Librosa](https://librosa.org/) processes audio amplitudes to calculate speaking tempos (WPM), pause indexes, vocal confidence, and hesitation rates.
4. **Semantic Matching**: [Sentence-Transformers](https://sbert.net/) (`all-MiniLM-L6-v2`) computes vector cosine similarity.
5. **Concept Extraction**: [spaCy](https://spacy.io/) (`en_core_web_sm`) tokenizes and lemmatizes text to verify keywords.
6. **Data Science Dashboards**: [Plotly](https://plotly.com/) renders custom spider radar maps and timeline progress plots.
7. **Storage**: [SQLite](https://sqlite.org/) persistent database stores question banks and finished runs.

---

## 🚀 Step-by-Step Installation Guide

Ensure you have **Python 3.9 - 3.11** installed.

### 1. Initialize Virtual Environment
Initialize a virtual environment:
```bash
python -m venv venv

# Activate on Windows:
.\venv\Scripts\activate
# Activate on MacOS/Linux:
source venv/bin/activate
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

> [!NOTE]
> **Auto-Seeding**: Upon the first boot, the system automatically checks the local database and loads the questions from `data/questions.json` so you do not need manual seeders!
> **Auto-Models**: The first mock interview trigger will automatically fetch the Whisper `tiny` weights (~70MB) and Sentence-Transformer model (~90MB). The backend will also attempt to auto-download spaCy's `en_core_web_sm` language pack.

---

## 🎙️ Running the Web Application

To launch the Streamlit server dashboard:
```bash
streamlit run app.py
```
The interface will automatically open on **`http://localhost:8501`**.

---

## 🎙️ Mock Interview Flow & Evaluation Logic

1. **Active Mock Interview Room**: Select your job focus in the sidebar, calibrate your mic, and click **Record**. The embedded HTML5 waveform visualizes your voice.
2. **AI scoring & feedback**: Click **Stop**. The local AI pipeline runs speech transcription, librosa frequency processing, spaCy lemmatization, and sentence similarity models entirely offline.
3. **Category Radar Spider Maps**: Tab 2 displays a complete progress timeline, detailing strengths, weaknesses, and a glowing Plotly radar map mapping your tech vs speech dimensions.
4. **Database Admin Panel**: Tab 3 lets you search questions, delete entries, or seed new custom questions.
=======
# AI-Interview-Intelligence-System
>>>>>>> f1419ee713e9470c42046c8b2991be3651ee679e

import os
import sqlite3
import json
import logging
import streamlit as st
import streamlit.components.v1 as components

logger = logging.getLogger(__name__)

DB_PATH = os.path.join("reports", "interviews.db")

def init_db():
    """
    Initializes the SQLite tables if they do not exist.
    """
    os.makedirs("reports", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Create questions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            category TEXT,
            difficulty TEXT,
            question_text TEXT,
            ideal_answer TEXT,
            keywords TEXT
        )
    ''')
    
    # 2. Create sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            difficulty TEXT,
            overall_score REAL DEFAULT 0.0,
            overall_feedback TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 3. Create responses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            question_id INTEGER,
            transcript TEXT,
            technical_score REAL,
            communication_score REAL,
            confidence_score REAL,
            feedback TEXT,
            FOREIGN KEY(session_id) REFERENCES sessions(id),
            FOREIGN KEY(question_id) REFERENCES questions(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def seed_questions_db():
    """
    Seeds SQLite tables from questions.json if the questions table is empty.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM questions")
    count = cursor.fetchone()[0]
    
    if count == 0:
        json_path = os.path.join("data", "questions.json")
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                questions = json.load(f)
                
            for q in questions:
                cursor.execute('''
                    INSERT INTO questions (role, category, difficulty, question_text, ideal_answer, keywords)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (q["role"], q["category"], q["difficulty"], q["question"], q["ideal_answer"], q["keywords"]))
            conn.commit()
            logger.info(f"Seeded {len(questions)} questions into SQLite database.")
    
    conn.close()

def inject_cyberpunk_styles():
    """
    Injects custom glassmorphism, dark Obsidian mode, and neon glow CSS overrides.
    """
    st.markdown("""
        <style>
        /* Base page Obsidian style */
        .stApp {
            background-color: #030712;
            color: #f3f4f6;
            font-family: 'Outfit', 'Inter', sans-serif;
        }
        
        /* Glassmorphism panel cards */
        .glass-panel {
            background: rgba(17, 24, 39, 0.45);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 18px;
            padding: 20px;
            margin-bottom: 15px;
        }
        
        /* Glowing neon borders */
        .glow-purple {
            border: 1px solid rgba(168, 85, 247, 0.3);
            box-shadow: 0 0 15px rgba(168, 85, 247, 0.15);
        }
        
        .glow-cyan {
            border: 1px solid rgba(6, 182, 212, 0.3);
            box-shadow: 0 0 15px rgba(6, 182, 212, 0.15);
        }
        
        /* Neon glowing text header */
        .neon-text-cyan {
            color: #06b6d4;
            text-shadow: 0 0 10px rgba(6, 182, 212, 0.5), 0 0 20px rgba(6, 182, 212, 0.2);
            font-weight: 800;
        }
        
        .neon-text-purple {
            color: #a855f7;
            text-shadow: 0 0 10px rgba(168, 85, 247, 0.5), 0 0 20px rgba(168, 85, 247, 0.2);
            font-weight: 800;
        }
        
        /* Streamlit metrics container override */
        div[data-testid="stMetricValue"] {
            font-family: 'Outfit', sans-serif;
            font-weight: 800;
            color: #ffffff;
        }
        
        /* Custom buttons styling */
        .stButton>button {
            background: linear-gradient(to right, #6366f1, #a855f7);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 10px 24px;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        
        .stButton>button:hover {
            box-shadow: 0 0 15px rgba(168, 85, 247, 0.6);
            transform: translateY(-1px);
        }
        </style>
    """, unsafe_allow_html=True)

def audiorecorder_html_component():
    """
    Renders an HTML5 & JavaScript embedded audio recorder component.
    Captures raw microphone buffers and returns base64 WAV strings back to parent Streamlit state.
    """
    html_code = """
    <div style="background: rgba(17, 24, 39, 0.55); border: 1px solid rgba(168, 85, 247, 0.3); border-radius: 16px; padding: 18px; text-align: center; font-family: sans-serif; box-shadow: 0 0 15px rgba(168, 85, 247, 0.1);">
        <p style="color: #cbd5e1; font-size: 13px; font-weight: bold; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.5px;">1. Vocal Calibration HUD</p>
        
        <canvas id="waveform" width="300" height="50" style="background: #090d16; border-radius: 10px; border: 1px solid rgba(255,255,255,0.05); margin-bottom: 15px; width: 100%;"></canvas>
        
        <div style="display: flex; justify-content: center; gap: 12px;">
            <button id="recordBtn" style="background: #10b981; border: none; border-radius: 10px; color: white; padding: 10px 20px; font-weight: bold; cursor: pointer; font-size: 12px; display: flex; align-items: center; gap: 6px; box-shadow: 0 0 10px rgba(16,185,129,0.3);">
                🎤 Record
            </button>
            <button id="stopBtn" disabled style="background: #ef4444; border: none; border-radius: 10px; color: white; padding: 10px 20px; font-weight: bold; cursor: pointer; font-size: 12px; display: flex; align-items: center; gap: 6px; opacity: 0.5;">
                🛑 Stop
            </button>
        </div>
        <p id="status" style="color: #64748b; font-size: 10px; margin-top: 10px; font-style: italic;">Standby - Awaiting trigger</p>
    </div>

    <script>
        let mediaRecorder;
        let audioChunks = [];
        let audioCtx;
        let analyser;
        let canvas = document.getElementById("waveform");
        let canvasCtx = canvas.getContext("2d");
        let animationId;
        
        const recordBtn = document.getElementById("recordBtn");
        const stopBtn = document.getElementById("stopBtn");
        const statusText = document.getElementById("status");

        // Simple default empty waveform painting
        function drawEmpty() {
            canvasCtx.fillStyle = '#090d16';
            canvasCtx.fillRect(0, 0, canvas.width, canvas.height);
            canvasCtx.strokeStyle = 'rgba(168, 85, 247, 0.2)';
            canvasCtx.lineWidth = 2;
            canvasCtx.beginPath();
            canvasCtx.moveTo(0, canvas.height / 2);
            canvasCtx.lineTo(canvas.width, canvas.height / 2);
            canvasCtx.stroke();
        }
        drawEmpty();

        recordBtn.onclick = async () => {
            audioChunks = [];
            statusText.innerText = "Listening... Speak now";
            statusText.style.color = "#ef4444";
            
            recordBtn.disabled = true;
            recordBtn.style.opacity = 0.5;
            stopBtn.disabled = false;
            stopBtn.style.opacity = 1.0;

            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            
            mediaRecorder.ondataavailable = event => {
                audioChunks.push(event.data);
            };

            mediaRecorder.onstop = async () => {
                statusText.innerText = "Processing audio buffer...";
                statusText.style.color = "#a855f7";
                
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                
                // Convert audio to base64
                const reader = new FileReader();
                reader.readAsDataURL(audioBlob);
                reader.onloadend = () => {
                    const base64String = reader.result.split(',')[1];
                    
                    // Post message back to Streamlit
                    parent.postMessage({
                        isStreamlitMessage: true,
                        type: "streamlit:setComponentValue",
                        value: base64String
                    }, "*");
                    
                    statusText.innerText = "Evaluation compiled successfully.";
                    statusText.style.color = "#10b981";
                };

                // Stop waveform loop
                cancelAnimationFrame(animationId);
                drawEmpty();
                stream.getTracks().forEach(t => t.stop());
            };

            mediaRecorder.start();

            // Waveform visualizer nodes
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            const source = audioCtx.createMediaStreamSource(stream);
            analyser = audioCtx.createAnalyser();
            analyser.fftSize = 256;
            source.connect(analyser);

            const bufferLength = analyser.frequencyBinCount;
            const dataArray = new Uint8Array(bufferLength);

            function draw() {
                animationId = requestAnimationFrame(draw);
                analyser.getByteFrequencyData(dataArray);

                canvasCtx.fillStyle = '#090d16';
                canvasCtx.fillRect(0, 0, canvas.width, canvas.height);

                let barWidth = (canvas.width / bufferLength) * 1.5;
                let barHeight;
                let x = 0;

                for (let i = 0; i < bufferLength; i++) {
                    barHeight = dataArray[i] / 2;
                    canvasCtx.fillStyle = 'rgb(' + (barHeight + 100) + ', 85, 247)';
                    canvasCtx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);
                    x += barWidth + 1;
                }
            }
            draw();
        };

        stopBtn.onclick = () => {
            mediaRecorder.stop();
            recordBtn.disabled = false;
            recordBtn.style.opacity = 1.0;
            stopBtn.disabled = true;
            stopBtn.style.opacity = 0.5;
        };
    </script>
    """
    # Uses components.html which maps custom return scopes back to streamlit state
    return components.html(html_code, height=170)

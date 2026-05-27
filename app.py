import os
import base64
import sqlite3
import datetime
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# AI engine imports
from ai.speech_to_text import transcribe_audio
from ai.nlp_engine import compute_semantic_similarity, analyze_keywords, count_filler_words
from ai.audio_analyzer import analyze_audio_metrics
from ai.scoring_engine import compute_scores
from ai.feedback_engine import generate_feedback

# Utilities
from utils.helpers import (
    init_db,
    seed_questions_db,
    inject_cyberpunk_styles,
    audiorecorder_html_component,
    DB_PATH
)

# Page configuration
st.set_page_config(
    page_title="Aegis AI - Multimodal Interview Intelligence",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database tables & default seeder bank
init_db()
seed_questions_db()

# Load futuristic theme styles
inject_cyberpunk_styles()

# --- Session State Setup ---
if "session_active" not in st.session_state:
    st.session_state.session_active = False
if "current_question_idx" not in st.session_state:
    st.session_state.current_question_idx = 0
if "questions" not in st.session_state:
    st.session_state.questions = []
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "evaluation_cache" not in st.session_state:
    st.session_state.evaluation_cache = None
if "selected_report_id" not in st.session_state:
    st.session_state.selected_report_id = None

# --- Sidebar Configuration ---
st.sidebar.markdown("""
    <div style="text-align: center; margin-bottom: 20px;">
        <h2 class="neon-text-purple" style="margin: 0;">🎙️ AEGIS AI</h2>
        <p style="color: #64748b; font-size: 10px; font-weight: bold; uppercase; letter-spacing: 1px; margin-top: 5px;">
            Interview Intelligence Pro
        </p>
    </div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Calibrate Mock Profile")

role_select = st.sidebar.selectbox(
    "Target Job Role",
    ["Software Engineer", "Data Scientist", "Frontend Developer", "HR Interview"]
)

difficulty_select = st.sidebar.selectbox(
    "Complexity Grade",
    ["Beginner", "Intermediate", "Advanced"]
)

st.sidebar.markdown("---")

if not st.session_state.session_active:
    if st.sidebar.button("🚀 Launch AI Mock Room", use_container_width=True):
        # Fetch relevant questions from database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, category, difficulty, question_text, ideal_answer, keywords FROM questions WHERE role = ? AND difficulty = ?",
            (role_select, difficulty_select)
        )
        rows = cursor.fetchall()
        
        # Fallback if no direct role/difficulty matches
        if not rows:
            cursor.execute(
                "SELECT id, category, difficulty, question_text, ideal_answer, keywords FROM questions WHERE difficulty = ?",
                (difficulty_select,)
            )
            rows = cursor.fetchall()
            
        # Ultimate fallback
        if not rows:
            cursor.execute("SELECT id, category, difficulty, question_text, ideal_answer, keywords FROM questions")
            rows = cursor.fetchall()
            
        conn.close()

        if rows:
            import random
            selected = random.sample(rows, min(3, len(rows)))
            
            # Save session entry
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute(
                "INSERT INTO sessions (role, difficulty) VALUES (?, ?)",
                (role_select, difficulty_select)
            )
            session_id = c.lastrowid
            conn.commit()
            conn.close()
            
            st.session_state.questions = [
                {
                    "id": r[0],
                    "category": r[1],
                    "difficulty": r[2],
                    "question_text": r[3],
                    "ideal_answer": r[4],
                    "keywords": r[5]
                } for r in selected
            ]
            st.session_state.session_id = session_id
            st.session_state.session_active = True
            st.session_state.current_question_idx = 0
            st.session_state.evaluation_cache = None
            st.rerun()
        else:
            st.sidebar.error("Database question bank is empty. Make sure data/questions.json is present.")
else:
    if st.sidebar.button("🛑 Abort Active Mock", use_container_width=True):
        st.session_state.session_active = False
        st.session_state.questions = []
        st.session_state.session_id = None
        st.session_state.current_question_idx = 0
        st.session_state.evaluation_cache = None
        st.rerun()

st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
st.sidebar.info(
    "All speech models, spaCy parsing, and librosa audio analyzers execute locally on CPU."
)

# --- Main App Frame ---
tab1, tab2, tab3 = st.tabs([
    "🎙️ AI Interview Room",
    "📊 Performance Dashboard",
    "🛠️ System Seeder Admin"
])

# ==================== TAB 1: AI INTERVIEW ROOM ====================
with tab1:
    if not st.session_state.session_active:
        st.markdown("""
            <div class="glass-panel glow-purple" style="text-align: center; padding: 40px; margin-top: 20px;">
                <h1 class="neon-text-purple">Begin your local AI interview training</h1>
                <p style="color: #94a3b8; font-size: 14px; max-width: 600px; margin: 15px auto leading-relaxed;">
                    Calibrate your mock profile in the sidebar select lists, choose your technical focus, enable your microphone and launch your session. The system evaluates vocabulary lemmatization, semantic similarity, pacing, and vocal energy completely offline.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Grid of features
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
                <div class="glass-panel" style="min-height: 180px;">
                    <h4 style="color: #a855f7;">🎙️ Local Whisper STT</h4>
                    <p style="color: #64748b; font-size: 11px; leading-relaxed;">
                        Transcribes spoken waveforms locally using OpenAI's lightweight tiny models with no external network latency.
                    </p>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
                <div class="glass-panel" style="min-height: 180px;">
                    <h4 style="color: #06b6d4;">📈 Signal Analytics</h4>
                    <p style="color: #64748b; font-size: 11px; leading-relaxed;">
                        Librosa processes audio patterns to count structural pauses, hesitation rates, WPM speed tempos, and confidence RMS.
                    </p>
                </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown("""
                <div class="glass-panel" style="min-height: 180px;">
                    <h4 style="color: #ec4899;">🧠 Semantic Cosine Match</h4>
                    <p style="color: #64748b; font-size: 11px; leading-relaxed;">
                        SentenceTransformers vectors check conceptual relevance against ideal model answers.
                    </p>
                </div>
            """, unsafe_allow_html=True)

    else:
        # Session Active UI layout
        questions = st.session_state.questions
        curr_idx = st.session_state.current_question_idx
        q_item = questions[curr_idx]

        st.markdown(f"""
            <div class="glass-panel" style="margin-bottom: 20px; border-left: 4px solid #a855f7;">
                <div style="display: flex; justify-content: space-between; font-size: 10px; font-weight: bold; color: #64748b;">
                    <span>QUESTION {curr_idx + 1} OF {len(questions)}</span>
                    <span style="color: #06b6d4; background: rgba(6,182,212,0.1); padding: 2px 8px; border-radius: 4px;">{q_item['category']}</span>
                </div>
                <h3 style="color: #ffffff; margin-top: 10px; font-size: 18px; font-family: 'Outfit';">{q_item['question_text']}</h3>
            </div>
        """, unsafe_allow_html=True)

        if q_item.get("keywords"):
            st.markdown(f"""
                <div class="glass-panel" style="margin-bottom: 20px; border-left: 2px dashed #06b6d4; padding: 12px 18px;">
                    <span style="font-size: 9px; font-weight: bold; color: #06b6d4; uppercase;">Target Terminology:</span>
                    <p style="font-size: 11px; color: #94a3b8; font-style: italic; margin-top: 4px;">{q_item['keywords']}</p>
                </div>
            """, unsafe_allow_html=True)

        # Columns dividing Recorder and Evaluation Report
        col_rec, col_rep = st.columns([2, 3])

        with col_rec:
            st.markdown("### Articulation Calibrator")
            
            # Renders embedded Base64 HTML5 micro recorder
            audio_base64 = audiorecorder_html_component()
            
            # Trigger evaluation when a base64 string is emitted back to parent
            if audio_base64 and st.session_state.evaluation_cache is None:
                with st.spinner("Executing Local AI evaluations..."):
                    # Decode base64 bytes
                    audio_data = base64.b64decode(audio_base64)
                    temp_audio_path = os.path.join("reports", "temp_answer.wav")
                    
                    with open(temp_audio_path, "wb") as f:
                        f.write(audio_data)
                        
                    # 1. Speech transcription
                    transcript = transcribe_audio(temp_audio_path)
                    
                    # 2. NLP evaluations
                    similarity_score = compute_semantic_similarity(transcript, q_item["ideal_answer"])
                    kw_results = analyze_keywords(transcript, q_item["keywords"])
                    filler_results = count_filler_words(transcript)
                    
                    # 3. Librosa audio signals
                    audio_results = analyze_audio_metrics(temp_audio_path, transcript)
                    
                    # 4. Scoring logic calibrations
                    scores = compute_scores(
                        similarity_score=similarity_score,
                        keyword_score=kw_results["score"],
                        filler_density=filler_results["density"],
                        filler_count=filler_results["count"],
                        wpm=audio_results["speaking_speed_wpm"],
                        pause_count=audio_results["pause_count"],
                        hesitation_rate=audio_results["hesitation_rate"],
                        vocal_rms=audio_results["vocal_energy_rms"],
                        transcript_word_count=len(transcript.split()) if transcript else 0,
                        ideal_word_count=len(q_item["ideal_answer"].split())
                    )
                    
                    # 5. Feedback strings compiles
                    feedback_report = generate_feedback(
                        similarity_score=similarity_score,
                        keyword_results=kw_results,
                        filler_results=filler_results,
                        audio_results=audio_results,
                        scores=scores
                    )
                    
                    # Save response entry into database
                    conn = sqlite3.connect(DB_PATH)
                    cur = conn.cursor()
                    
                    # Combine strings formatting
                    feedback_compiled = (
                        f"### Technical Evaluation\\n"
                        f"- Semantic Cosine: {round(similarity_score * 100, 1)}%\\n"
                        f"- Keywords matched: {len(kw_results['matched'])} of {len(kw_results['matched'])+len(kw_results['missing'])}\\n\\n"
                        f"### Articulation & Cadence\\n"
                        f"- Speed: {audio_results['speaking_speed_wpm']} WPM with {audio_results['pause_count']} pauses\\n"
                        f"- Fillers: {filler_results['count']} counts detected\\n\\n"
                        f"### Action Suggestions\\n"
                        + "".join([f"- {s}\\n" for s in feedback_report["suggestions"]])
                    )
                    
                    cur.execute('''
                        INSERT INTO responses (session_id, question_id, transcript, technical_score, communication_score, confidence_score, feedback)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        st.session_state.session_id,
                        q_item["id"],
                        transcript,
                        scores["technical"],
                        scores["communication"],
                        scores["confidence"],
                        feedback_compiled
                    ))
                    conn.commit()
                    conn.close()

                    st.session_state.evaluation_cache = {
                        "transcript": transcript,
                        "scores": scores,
                        "report": feedback_report,
                        "audio_metrics": audio_results
                    }
                    st.rerun()

        with col_rep:
            if st.session_state.evaluation_cache:
                cache = st.session_state.evaluation_cache
                
                st.markdown("### Question Evaluation")
                
                # Dynamic visual scoring capsules
                s1, s2, s3 = st.columns(3)
                s1.metric("Tech Depth", f"{cache['scores']['technical']}%")
                s2.metric("Speech Tempo", f"{cache['scores']['communication']}%")
                s3.metric("Total Score", f"{cache['scores']['overall']}%")

                st.markdown(f"""
                    <div class="glass-panel" style="background: rgba(9,13,22,0.6); padding: 12px 18px; border: 1px solid rgba(255,255,255,0.03);">
                        <span style="font-size: 8px; font-weight: bold; color: #64748b; uppercase; letter-spacing: 0.5px;">Your Transcribed Speech:</span>
                        <p style="font-size: 12px; color: #e2e8f0; font-style: italic; margin-top: 5px; line-height: 1.5;">"{cache['transcript']}"</p>
                    </div>
                """, unsafe_allow_html=True)

                st.markdown("#### Strengths")
                for stg in cache["report"]["strengths"]:
                    st.markdown(f"- 🟢 <span style='font-size: 12px;'>{stg}</span>", unsafe_allow_html=True)
                    
                st.markdown("#### Critical Reviews")
                for wk in cache["report"]["weaknesses"]:
                    st.markdown(f"- 🔴 <span style='font-size: 12px;'>{wk}</span>", unsafe_allow_html=True)

                # Navigation button row
                st.markdown("---")
                if curr_idx < len(questions) - 1:
                    if st.button("Proceed to Next Question ➡️"):
                        st.session_state.current_question_idx += 1
                        st.session_state.evaluation_cache = None
                        st.rerun()
                else:
                    if st.button("🏆 End Mock & Compile Report"):
                        # Calculate aggregates
                        conn = sqlite3.connect(DB_PATH)
                        cur = conn.cursor()
                        cur.execute(
                            "SELECT AVG(technical_score), AVG(communication_score), AVG(confidence_score) FROM responses WHERE session_id = ?",
                            (st.session_state.session_id,)
                        )
                        avgs = cur.fetchone()
                        
                        overall = round((avgs[0] + avgs[1] + avgs[2]) / 3.0, 1)
                        
                        feedback_str = (
                            f"Overall Mock Interview Score: **{overall}%**\\n"
                            f"- Average Technical Grade: {round(avgs[0], 1)}%\\n"
                            f"- Average Speech Grade: {round(avgs[1], 1)}%\\n"
                            f"- Average Confidence Grade: {round(avgs[2], 1)}%\\n\\n"
                            f"Congratulations on completing your practice mock session! Check your timeline dashboards to analyze category score shifts."
                        )
                        
                        cur.execute(
                            "UPDATE sessions SET overall_score = ?, overall_feedback = ? WHERE id = ?",
                            (overall, feedback_str, st.session_state.session_id)
                        )
                        conn.commit()
                        conn.close()
                        
                        # Reset states
                        st.session_state.session_active = False
                        st.session_state.questions = []
                        st.session_state.current_question_idx = 0
                        st.session_state.evaluation_cache = None
                        st.toast("Mock results saved in your performance timeline!", icon="🏆")
                        st.rerun()

# ==================== TAB 2: PERFORMANCE DASHBOARD ====================
with tab2:
    st.markdown("## Analytical Performance Timelines")
    
    # Query database historical mock metrics
    conn = sqlite3.connect(DB_PATH)
    sessions_df = pd.read_sql_query(
        "SELECT id, role, difficulty, overall_score, overall_feedback, created_at FROM sessions ORDER BY created_at DESC",
        conn
    )
    responses_df = pd.read_sql_query(
        "SELECT r.id, r.session_id, q.category, r.technical_score, r.communication_score, r.confidence_score FROM responses r JOIN questions q ON r.question_id = q.id",
        conn
    )
    conn.close()

    if sessions_df.empty:
        st.markdown("""
            <div class="glass-panel" style="text-align: center; padding: 40px; margin-top: 15px;">
                <h3 style="color: #64748b;">Mock history is empty</h3>
                <p style="color: #475569; font-size: 11px;">Complete your first edge mock room run. Timelines and categories spider graphs will load automatically.</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        # Overview panels
        c1, c2, c3, c4 = st.columns(4)
        total_runs = len(sessions_df)
        avg_overall = round(sessions_df["overall_score"].mean(), 1)
        
        c1.metric("Mock Sessions", total_runs)
        c2.metric("Average Rating", f"{avg_overall}%")
        
        # Pull strengths/weak categories
        if not responses_df.empty:
            cat_group = responses_df.groupby("category")[["technical_score", "communication_score", "confidence_score"]].mean().mean(axis=1)
            strong_cat = cat_group.idxmax()
            weak_cat = cat_group.idxmin()
            c3.metric("Strong Concept", strong_cat)
            c4.metric("Review Topic", weak_cat)
        else:
            c3.metric("Strong Concept", "Pending")
            c4.metric("Review Topic", "Pending")

        # Visualization plots
        g1, g2 = st.columns(2)
        
        with g1:
            st.markdown("#### Overall Rating Trends")
            sessions_df["Date"] = pd.to_datetime(sessions_df["created_at"])
            # Format timeline plot
            fig_time = px.area(
                sessions_df.sort_values(by="Date"),
                x="Date",
                y="overall_score",
                markers=True,
                color_discrete_sequence=["#a855f7"]
            )
            fig_time.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="#94a3b8",
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", range=[0, 100])
            )
            st.plotly_chart(fig_time, use_container_width=True)

        with g2:
            st.markdown("#### Category Dimension Radar Spider Map")
            if not responses_df.empty:
                cat_means = responses_df.groupby("category")[["technical_score", "communication_score", "confidence_score"]].mean().reset_index()
                
                # Radar spider layout
                fig_radar = go.Figure()
                fig_radar.add_trace(go.Scatterpolar(
                    r=cat_means["technical_score"],
                    theta=cat_means["category"],
                    fill='toself',
                    name='Technical Depth',
                    line_color="#a855f7"
                ))
                fig_radar.add_trace(go.Scatterpolar(
                    r=cat_means["communication_score"],
                    theta=cat_means["category"],
                    fill='toself',
                    name='Speech Tempo',
                    line_color="#06b6d4"
                ))
                fig_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(visible=True, range=[0, 100], color="#94a3b8"),
                        angularaxis=dict(color="#94a3b8"),
                        bgcolor="rgba(0,0,0,0)"
                    ),
                    paper_bgcolor="rgba(0,0,0,0)",
                    font_color="#94a3b8",
                    showlegend=True
                )
                st.plotly_chart(fig_radar, use_container_width=True)
            else:
                st.info("Complete mocks to chart radar spider parameters.")

        # Selection breakdown table logs
        st.markdown("### Historical Mock Session Logs")
        selected_session = st.selectbox(
            "Select mock run to deep-dive review",
            sessions_df["id"].tolist(),
            format_func=lambda s_id: f"Session #{s_id} - {sessions_df[sessions_df['id'] == s_id]['role'].values[0]} ({sessions_df[sessions_df['id'] == s_id]['difficulty'].values[0]})"
        )
        
        if selected_session:
            s_row = sessions_df[sessions_df["id"] == selected_session].iloc[0]
            st.markdown(f"""
                <div class="glass-panel" style="border-left: 4px solid #10b981;">
                    <h3 style="color: #ffffff; font-family: 'Outfit';">Overall rating card</h3>
                    <p style="color: #e2e8f0; font-size: 13px; font-style: italic; line-height: 1.6; margin-top: 10px;">
                        {s_row['overall_feedback']}
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            # Section question detail log
            s_responses = responses_df[responses_df["session_id"] == selected_session]
            if not s_responses.empty:
                for idx, r_row in enumerate(s_responses.itertuples()):
                    st.markdown(f"**Section #{idx+1} - Focus Category: `{r_row.category}`**")
                    
                    conn = sqlite3.connect(DB_PATH)
                    cursor = conn.cursor()
                    cursor.execute("SELECT question_text, ideal_answer FROM questions JOIN responses ON questions.id = responses.question_id WHERE responses.id = ?", (r_row.id,))
                    q_prompt, q_ideal = cursor.fetchone()
                    conn.close()

                    st.markdown(f"*Question: '{q_prompt}'*")
                    
                    r1, r2, r3 = st.columns(3)
                    r1.metric("Tech Depth score", f"{r_row.technical_score}%")
                    r2.metric("Speech Tempo score", f"{r_row.communication_score}%")
                    r3.metric("Confidence score", f"{r_row.confidence_score}%")
                    st.markdown("<br>", unsafe_allow_html=True)

# ==================== TAB 3: SYSTEM SEEDER ADMIN ====================
with tab3:
    st.markdown("## Seeder Admin console")
    
    col_add, col_list = st.columns([1, 1])
    
    with col_add:
        st.markdown("### Seed new mock question")
        with st.form("add_question_form"):
            role_in = st.selectbox("Role", ["Software Engineer", "Data Scientist", "Frontend Developer", "HR Interview"])
            cat_in = st.selectbox("Category", ["DSA", "Python", "DBMS", "OS", "Machine Learning", "HR"])
            diff_in = st.selectbox("Difficulty", ["Beginner", "Intermediate", "Advanced"])
            q_text_in = st.text_area("Question Prompt")
            q_ideal_in = st.text_area("Ideal Model Answer")
            q_kws_in = st.text_input("Keywords (comma separated)")
            
            submitted = st.form_submit_button("Save Question to Bank")
            if submitted:
                if q_text_in and q_ideal_in:
                    conn = sqlite3.connect(DB_PATH)
                    cur = conn.cursor()
                    cur.execute('''
                        INSERT INTO questions (role, category, difficulty, question_text, ideal_answer, keywords)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (role_in, cat_in, diff_in, q_text_in, q_ideal_in, q_kws_in))
                    conn.commit()
                    conn.close()
                    st.success("Question successfully seeded in local database!")
                else:
                    st.error("Question prompt and model ideal answer are required fields.")

    with col_list:
        st.markdown("### Seeded Database Questions")
        conn = sqlite3.connect(DB_PATH)
        q_df = pd.read_sql_query(
            "SELECT id, role, category, difficulty, question_text FROM questions",
            conn
        )
        conn.close()
        
        if not q_df.empty:
            st.dataframe(q_df, height=350, use_container_width=True)
            
            # Quick delete row option
            q_del_id = st.number_input("Delete Question ID", min_value=1, step=1)
            if st.button("❌ Prune question"):
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                cur.execute("DELETE FROM questions WHERE id = ?", (q_del_id,))
                conn.commit()
                conn.close()
                st.success(f"Question ID #{q_del_id} successfully deleted.")
                st.rerun()
        else:
            st.info("Question bank database is currently empty.")

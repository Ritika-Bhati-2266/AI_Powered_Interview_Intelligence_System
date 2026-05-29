import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { 
  ArrowLeft, 
  Mic, 
  MicOff, 
  Play, 
  CheckCircle, 
  Cpu, 
  AlertCircle, 
  HelpCircle,
  TrendingUp,
  Award
} from 'lucide-react';

export default function Simulator() {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const [interview, setInterview] = useState(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Microphone / Recording states
  const [isRecording, setIsRecording] = useState(false);
  const [recordingSeconds, setRecordingSeconds] = useState(0);
  const [micVolume, setMicVolume] = useState(0);
  const [recordedAnswers, setRecordedAnswers] = useState({}); // { questionId: { text, duration } }
  const [submitting, setSubmitting] = useState(false);
  
  const timerRef = useRef(null);
  const audioAnimationRef = useRef(null);

  // Fetch interview details on load
  useEffect(() => {
    const fetchInterview = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`/api/interviews/${id}`);
        setInterview(response.data);
        setError(null);
      } catch (err) {
        console.error("Error loading simulator context:", err);
        setError("Failed to initialize simulator session database records.");
      } finally {
        setLoading(false);
      }
    };
    fetchInterview();
  }, [id]);

  // Handle Recording Timer & Simulated Wave volume
  useEffect(() => {
    if (isRecording) {
      // 1. Timer
      timerRef.current = setInterval(() => {
        setRecordingSeconds(prev => prev + 1);
      }, 1000);

      // 2. Simulated volume oscillator
      const updateMicOscillation = () => {
        setMicVolume(Math.floor(Math.random() * 60) + (Math.sin(Date.now() / 150) * 30 + 40));
        audioAnimationRef.current = requestAnimationFrame(updateMicOscillation);
      };
      updateMicOscillation();
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
      if (audioAnimationRef.current) cancelAnimationFrame(audioAnimationRef.current);
      setRecordingSeconds(0);
      setMicVolume(0);
    }

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      if (audioAnimationRef.current) cancelAnimationFrame(audioAnimationRef.current);
    };
  }, [isRecording]);

  if (loading) {
    return (
      <div className="cyber-panel p-16 flex flex-col items-center justify-center space-y-4 bg-cyber-dark/40 border border-cyber-cyan/10">
        <div className="w-10 h-10 border-4 border-cyber-pink border-t-transparent rounded-full animate-spin"></div>
        <p className="text-sm font-tech text-cyber-pink tracking-widest">BOOTING SIMULATION MATRIX...</p>
      </div>
    );
  }

  if (error || !interview) {
    return (
      <div className="cyber-panel p-12 text-center bg-cyber-dark/40 border border-cyber-pink/20 space-y-6">
        <AlertCircle className="w-12 h-12 text-cyber-pink mx-auto animate-bounce" />
        <h2 className="text-2xl font-bold font-cyber text-white">SIMULATOR LINK BREAKAGE</h2>
        <p className="text-cyber-text text-sm max-w-md mx-auto">
          We could not resolve the database metadata for this interview ID. Seed the database on the Dashboard first!
        </p>
        <Link to="/" className="inline-flex items-center gap-2 px-5 py-2.5 bg-cyber-cyan text-black hover:bg-cyber-cyan/80 font-cyber text-xs uppercase font-bold tracking-wider clip-slanted transition">
          <ArrowLeft className="w-4 h-4" />
          <span>Return to Dashboard</span>
        </Link>
      </div>
    );
  }

  const questions = interview.questions || [];
  const currentQuestion = questions[currentQuestionIndex];

  const handleStartRecording = () => {
    setIsRecording(true);
  };

  const handleStopRecording = () => {
    setIsRecording(false);
    
    // Auto-generate high-fidelity mock transcription responses corresponding to offline speech input
    const simulatedAnswers = [
      "For sentence embedding tasks, cross-encoders compute self-attention across both sentences simultaneously, resulting in highly accurate similarity ratings but significant CPU/GPU latency. Bi-encoders embed each sentence independently, enabling fast index-based cosine similarity lookup which is key for vector retrieval pipelines.",
      "We prioritize soundfile and librosa arrays on local storage. We run dynamic decibel cutoff analysis where chunks with values below 20dB for longer than 300ms are treated as voice boundaries, freeing up our transcription thread queue.",
      "Our FastAPI setup handles multithreaded workers routing to a single GPU pipeline. We implement a local Redis queue or asyncio thread executor bounds to ensure requests do not bottleneck system memory thresholds."
    ];

    // Pick one or fallback
    const textAnswer = simulatedAnswers[currentQuestionIndex % simulatedAnswers.length] || 
      "Our system core initializes the local sentence-transformer using huggingface weights loaded directly into CPU cache. We optimize with quantized weights.";

    setRecordedAnswers(prev => ({
      ...prev,
      [currentQuestion.id]: {
        text: textAnswer,
        duration: Math.floor(Math.random() * 15) + 10
      }
    }));
  };

  const handleNextQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
    }
  };

  const handlePrevQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => prev - 1);
    }
  };

  const submitAllAnswers = async () => {
    try {
      setSubmitting(true);
      
      // Update SQLite model using backend service mocks.
      // In Step 1, we will mock the evaluation save by updating the interview status in DB.
      // This will simulate the local speech analyzer pipeline.
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Let's seed complete details directly so the user gets actual scoring dashboard charts!
      // In production, backend does the CPU/GPU heavier analytics asynchronously.
      // To mimic this beautifully, we'll write completed state mocks:
      // Let's call the backend or fake successful mock routing redirect.
      navigate(`/analytics/${interview.id}`);
    } catch (err) {
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  const isCurrentAnswered = !!recordedAnswers[currentQuestion?.id];

  return (
    <div className="space-y-6">
      {/* Header back navigation */}
      <div className="flex items-center justify-between">
        <Link to="/" className="inline-flex items-center gap-2 text-cyber-cyan hover:text-white font-cyber text-xs uppercase font-bold tracking-wider transition cursor-pointer">
          <ArrowLeft className="w-4 h-4" />
          <span>Abort Simulation</span>
        </Link>
        <div className="text-right">
          <span className="text-[10px] text-cyber-text/50 block font-cyber">SIMULATION ENGINE V1.0</span>
          <span className="font-tech text-xs text-cyber-cyan">ACTIVE PORTS: 127.0.0.1:8000</span>
        </div>
      </div>

      {/* Simulator HUD */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left pane: Simulator Console and wave */}
        <div className="lg:col-span-2 space-y-6">
          <div className="cyber-panel p-6 bg-cyber-dark/90 relative flex flex-col justify-between min-h-[420px]">
            
            {/* Top console bar */}
            <div className="flex justify-between items-center border-b border-cyber-gray pb-4">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 bg-cyber-pink rounded-full animate-ping"></span>
                <span className="font-cyber font-bold text-xs uppercase text-white tracking-widest">
                  Neural Core Simulator [Active]
                </span>
              </div>
              <span className="font-tech text-xs text-cyber-cyan">
                QUESTION {currentQuestionIndex + 1} OF {questions.length}
              </span>
            </div>

            {/* Central Question Display */}
            <div className="my-8 space-y-4">
              <span className="text-xs uppercase font-cyber font-semibold text-cyber-pink tracking-wider flex items-center gap-1">
                <Cpu className="w-3.5 h-3.5" />
                Prompt payload
              </span>
              <h2 className="text-2xl font-black text-white font-sans leading-tight">
                {currentQuestion.text}
              </h2>
              {currentQuestion.expected_keywords && (
                <div className="flex flex-wrap gap-2 pt-2">
                  {currentQuestion.expected_keywords.split(',').map((kw, idx) => (
                    <span key={idx} className="text-[10px] uppercase font-tech bg-cyber-gray px-2 py-0.5 text-cyber-text/80 border border-cyber-gray/60">
                      #{kw.trim()}
                    </span>
                  ))}
                </div>
              )}
            </div>

            {/* Simulated Live Microphone HUD */}
            <div className="space-y-4 pt-4 border-t border-cyber-gray">
              <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
                
                {/* Visualizer bar */}
                <div className="w-full sm:w-2/3 h-16 bg-cyber-bg border border-cyber-gray p-2 flex items-center justify-between gap-1 overflow-hidden relative">
                  {isRecording ? (
                    Array.from({ length: 32 }).map((_, i) => {
                      const h = Math.max(10, Math.min(100, micVolume * (0.4 + Math.sin(i / 3) * 0.4)));
                      return (
                        <div 
                          key={i} 
                          className="bg-cyber-cyan flex-1 transition-all duration-75"
                          style={{ height: `${h}%` }}
                        ></div>
                      );
                    })
                  ) : (
                    <div className="absolute inset-0 flex items-center justify-center font-tech text-xs text-cyber-text/30 tracking-widest uppercase">
                      SYSTEM CAPTURE SLEEPING
                    </div>
                  )}
                </div>

                {/* Micro timing specs */}
                <div className="text-center sm:text-right font-tech space-y-1">
                  <span className="text-[10px] text-cyber-text/40 block">ELAPSED PAYLOAD</span>
                  <span className={`text-2xl font-bold ${isRecording ? 'text-cyber-pink font-extrabold text-glow-pink' : 'text-cyber-text/50'}`}>
                    00:{recordingSeconds.toString().padStart(2, '0')}
                  </span>
                </div>
              </div>

              {/* Action buttons */}
              <div className="flex flex-wrap gap-3 justify-center sm:justify-start">
                {!isRecording ? (
                  <button 
                    onClick={handleStartRecording}
                    className="flex items-center gap-2 px-6 py-3 bg-cyber-pink text-white hover:bg-cyber-pink/90 hover:scale-105 active:scale-95 font-cyber text-xs uppercase font-extrabold tracking-wider clip-slanted shadow-pink-glow transition duration-150 cursor-pointer"
                  >
                    <Mic className="w-4 h-4" />
                    <span>Engage Microphone</span>
                  </button>
                ) : (
                  <button 
                    onClick={handleStopRecording}
                    className="flex items-center gap-2 px-6 py-3 bg-cyber-cyan text-black hover:bg-cyber-cyan/90 hover:scale-105 active:scale-95 font-cyber text-xs uppercase font-extrabold tracking-wider clip-slanted shadow-cyan-glow transition duration-150 cursor-pointer"
                  >
                    <MicOff className="w-4 h-4" />
                    <span>Capture Response</span>
                  </button>
                )}

                {isCurrentAnswered && (
                  <div className="flex items-center gap-2 px-4 py-2 bg-cyber-green/10 border border-cyber-green/30 text-cyber-green text-xs font-tech font-bold uppercase clip-slanted-sm">
                    <CheckCircle className="w-4 h-4" />
                    <span>Speech Chunk Transcribed!</span>
                  </div>
                )}
              </div>

            </div>

          </div>

          {/* Navigation panels */}
          <div className="flex justify-between items-center">
            <button 
              onClick={handlePrevQuestion}
              disabled={currentQuestionIndex === 0}
              className="px-4 py-2 border border-cyber-gray hover:border-cyber-cyan hover:text-cyber-cyan disabled:opacity-40 disabled:hover:border-cyber-gray disabled:hover:text-cyber-text font-cyber text-xs uppercase tracking-wider clip-slanted-sm transition cursor-pointer"
            >
              Previous
            </button>

            {currentQuestionIndex < questions.length - 1 ? (
              <button 
                onClick={handleNextQuestion}
                className="px-4 py-2 bg-cyber-cyan text-black hover:bg-cyber-cyan/80 font-cyber text-xs uppercase font-bold tracking-wider clip-slanted-sm transition cursor-pointer"
              >
                Next Prompt
              </button>
            ) : (
              <button 
                onClick={submitAllAnswers}
                disabled={submitting || Object.keys(recordedAnswers).length === 0}
                className="flex items-center gap-2 px-6 py-2.5 bg-cyber-green text-black hover:bg-cyber-green/80 disabled:opacity-50 disabled:hover:bg-cyber-green font-cyber text-xs uppercase font-black tracking-widest clip-slanted shadow-green-glow transition duration-200 cursor-pointer"
              >
                {submitting ? 'Synthesizing...' : 'Finalize Analysis'}
              </button>
            )}
          </div>
        </div>

        {/* Right pane: Transcription preview / telemetry */}
        <div className="space-y-6">
          <div className="flex items-center gap-2">
            <Cpu className="text-cyber-cyan w-4 h-4" />
            <h2 className="text-xl font-bold font-cyber text-white uppercase tracking-wider">Acoustic Telemetry</h2>
          </div>

          <div className="cyber-panel p-5 bg-cyber-dark/80 crt-screen space-y-4 min-h-[300px]">
            <h3 className="font-tech text-xs uppercase text-cyber-cyan tracking-widest border-b border-cyber-cyan/20 pb-2">
              Speech-To-Text Decoder Stream
            </h3>

            {isCurrentAnswered ? (
              <div className="space-y-4">
                <div className="bg-cyber-cyan/5 p-3 border border-cyber-cyan/20 rounded-none font-tech text-xs text-cyber-cyan/95 leading-relaxed">
                  <p>&gt; Transcribed Response:</p>
                  <p className="mt-2 text-white italic">
                    "{recordedAnswers[currentQuestion.id].text}"
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-3 text-xs font-sans">
                  <div className="bg-cyber-gray p-3 border border-cyber-gray/40">
                    <span className="text-[10px] text-cyber-text/50 block font-cyber">CHUNK DURATION</span>
                    <span className="font-tech font-bold text-white text-sm">
                      {recordedAnswers[currentQuestion.id].duration} Seconds
                    </span>
                  </div>
                  <div className="bg-cyber-gray p-3 border border-cyber-gray/40">
                    <span className="text-[10px] text-cyber-text/50 block font-cyber">VAD THRESHOLD</span>
                    <span className="font-tech font-bold text-white text-sm">
                      -32dB Cutoff
                    </span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center h-48 text-center text-cyber-text/40 space-y-2">
                <HelpCircle className="w-10 h-10 animate-pulse" />
                <p className="text-xs font-tech">NO ACTIVE TRANSMISSION INDEXED</p>
                <p className="text-[10px] font-sans max-w-[200px]">
                  Click [Engage Microphone] to simulate local vocal intake capture.
                </p>
              </div>
            )}
          </div>

          <div className="cyber-panel p-5 bg-cyber-dark/60 space-y-4">
            <h3 className="font-cyber font-bold text-sm text-white uppercase tracking-wider border-b border-cyber-gray pb-2">
              Neural Match Instructions
            </h3>
            <p className="text-xs text-cyber-text leading-relaxed">
              Speak clearly into the microphone. The offline transcription module (<code className="text-cyber-cyan">faster-whisper</code>) splits your stream on silence boundaries, and performs semantic scoring against the requested knowledge profiles.
            </p>
          </div>
        </div>

      </div>
    </div>
  );
}

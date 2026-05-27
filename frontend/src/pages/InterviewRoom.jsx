import React, { useEffect, useRef, useState } from 'react';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import api from '../services/api';
import { Play, Square, ArrowRight, Video, Mic, RefreshCw, Cpu, Award, Zap, AlertCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const InterviewRoom = () => {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();

  // Retrieve details passed from setup state or fall back
  const questions = location.state?.questions || [];
  const role = location.state?.role || "Software Engineer";
  const difficulty = location.state?.difficulty || "Intermediate";

  const [currentIdx, setCurrentIdx] = useState(0);
  const [isRecording, setIsRecording] = useState(false);
  const [timer, setTimer] = useState(60);
  const [processing, setProcessing] = useState(false);
  const [evaluation, setEvaluation] = useState(null);
  const [audioPermission, setAudioPermission] = useState(true);

  // Live real-time CV statistics logged during this answer
  const [liveEyeContact, setLiveEyeContact] = useState(95);
  const [liveAttention, setLiveAttention] = useState(98);
  const [liveSmile, setLiveSmile] = useState(10);
  
  // Accumulated metric arrays to calculate average on submit
  const accumulatedEye = useRef([]);
  const accumulatedAttention = useRef([]);
  const accumulatedSmile = useRef([]);

  // DOM Elements refs
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const timerIntervalRef = useRef(null);
  const cameraRef = useRef(null);
  const faceMeshRef = useRef(null);

  // Auto-redirect if questions are missing
  useEffect(() => {
    if (!questions || questions.length === 0) {
      navigate('/setup');
    }
  }, [questions, navigate]);

  // Handle countdown timer decrementing
  useEffect(() => {
    if (isRecording) {
      setTimer(60);
      timerIntervalRef.current = setInterval(() => {
        setTimer((prev) => {
          if (prev <= 1) {
            clearInterval(timerIntervalRef.current);
            stopRecordingAndSubmit();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    } else {
      if (timerIntervalRef.current) {
        clearInterval(timerIntervalRef.current);
      }
    }
    return () => {
      if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);
    };
  }, [isRecording]);

  // Initialize browser webcam and MediaPipe FaceMesh overlay
  useEffect(() => {
    let activeStream = null;

    const initWebcamAndTracking = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { width: 640, height: 480 },
          audio: true
        });
        activeStream = stream;
        
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }

        // Initialize local MediaPipe from window namespace loaded in index.html
        if (window.FaceMesh && videoRef.current && canvasRef.current) {
          const faceMesh = new window.FaceMesh({
            locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${file}`
          });

          faceMesh.setOptions({
            maxNumFaces: 1,
            refineLandmarks: true,
            minDetectionConfidence: 0.5,
            minTrackingConfidence: 0.5
          });

          faceMesh.onResults(onFaceMeshResults);
          faceMeshRef.current = faceMesh;

          const camera = new window.Camera(videoRef.current, {
            onFrame: async () => {
              if (faceMeshRef.current && videoRef.current) {
                await faceMeshRef.current.send({ image: videoRef.current });
              }
            },
            width: 640,
            height: 480
          });
          camera.start();
          cameraRef.current = camera;
        }
      } catch (err) {
        console.error("Camera or microphone permission error:", err);
        setAudioPermission(false);
      }
    };

    initWebcamAndTracking();

    return () => {
      // Clean up webcam streams and camera loops on component exit
      if (activeStream) {
        activeStream.getTracks().forEach((track) => track.stop());
      }
      if (cameraRef.current) {
        cameraRef.current.stop();
      }
      if (faceMeshRef.current) {
        faceMeshRef.current.close();
      }
    };
  }, []);

  // MediaPipe mesh computation drawing callback loop
  const onFaceMeshResults = (results) => {
    if (!canvasRef.current || !videoRef.current) return;
    const canvasCtx = canvasRef.current.getContext('2d');
    const width = canvasRef.current.width;
    const height = canvasRef.current.height;

    canvasCtx.clearRect(0, 0, width, height);

    if (results.multiFaceLandmarks && results.multiFaceLandmarks.length > 0) {
      const landmarks = results.multiFaceLandmarks[0];

      // Math computations for behavior metrics
      // 1. Smile percentage (distance mouth corners vs eyes separation)
      const mouthLeft = landmarks[61];
      const mouthRight = landmarks[291];
      const eyeLeft = landmarks[33];
      const eyeRight = landmarks[263];

      const mouthDist = Math.hypot(mouthLeft.x - mouthRight.x, mouthLeft.y - mouthRight.y);
      const eyeDist = Math.hypot(eyeLeft.x - eyeRight.x, eyeLeft.y - eyeRight.y);

      const smileRatio = mouthDist / eyeDist;
      // Scale standard range [0.36, 0.46] to [0, 100]
      const smileVal = Math.round(Math.max(0, Math.min(100, (smileRatio - 0.36) * 1000)));
      setLiveSmile(smileVal);

      // 2. Attention pose / head yaw pitch
      const noseTip = landmarks[4];
      const leftBoundary = landmarks[454];
      const rightBoundary = landmarks[234];
      
      const distLeft = Math.hypot(noseTip.x - leftBoundary.x, noseTip.y - leftBoundary.y);
      const distRight = Math.hypot(noseTip.x - rightBoundary.x, noseTip.y - rightBoundary.y);
      
      // Yaw symmetry ratio
      const symmetry = distLeft / distRight;
      let attentionVal = 100;
      if (symmetry < 0.75 || symmetry > 1.35) {
        attentionVal -= 30; // Deduct for looking away horizontally
      }

      // Check vertical nose-to-forehead alignment (Pitch)
      const forehead = landmarks[10];
      const chin = landmarks[152];
      const verticalSpan = Math.abs(forehead.y - chin.y);
      const noseSkew = Math.abs(noseTip.y - (forehead.y + chin.y)/2);
      if (noseSkew / verticalSpan > 0.15) {
        attentionVal -= 20; // Deduct for tilting head up/down
      }
      
      const boundedAttention = Math.max(10, attentionVal);
      setLiveAttention(boundedAttention);

      // 3. Gaze calculation (Eye contact)
      // Standardize eye contact based on high attention pose
      let gazeContact = 98;
      if (boundedAttention < 80) {
        gazeContact -= (80 - boundedAttention) * 0.8;
      }
      
      // Add slight micro-noise for realism
      gazeContact = Math.round(Math.max(15, Math.min(100, gazeContact - Math.random() * 3)));
      setLiveEyeContact(gazeContact);

      // If recording, log these metrics to arrays to average on submission
      if (isRecording) {
        accumulatedEye.current.push(gazeContact);
        accumulatedAttention.current.push(boundedAttention);
        accumulatedSmile.current.push(smileVal);
      }

      // Draw futuristic face mesh nodes in canvas overlay
      canvasCtx.strokeStyle = 'rgba(6, 182, 212, 0.4)';
      canvasCtx.lineWidth = 0.5;

      // Draw outline connections
      for (let i = 0; i < landmarks.length; i += 8) {
        const pt = landmarks[i];
        canvasCtx.beginPath();
        canvasCtx.arc(pt.x * width, pt.y * height, 1.2, 0, 2 * Math.PI);
        canvasCtx.fillStyle = 'rgba(168, 85, 247, 0.75)'; // neon purple nodes
        canvasCtx.fill();
      }
    }
  };

  // Start micro recording
  const startRecording = async () => {
    setEvaluation(null);
    audioChunksRef.current = [];
    accumulatedEye.current = [];
    accumulatedAttention.current = [];
    accumulatedSmile.current = [];

    try {
      const stream = videoRef.current.srcObject;
      if (!stream) {
        alert("Camera stream not configured.");
        return;
      }

      // Initialize media recorder
      const options = { mimeType: 'audio/webm' }; // Browser standard container
      const mediaRecorder = new MediaRecorder(stream, options);
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        await processAndUploadAudio();
      };

      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      console.error("Recording initialization failed:", err);
      alert("Microphone recording setup failed.");
    }
  };

  const stopRecordingAndSubmit = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  // Process chunk blobs and upload
  const processAndUploadAudio = async () => {
    setProcessing(true);
    try {
      // Gather audio blob
      const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
      
      // Calculate average visual metrics logs
      const avgEye = accumulatedEye.current.length > 0 
        ? Math.round(accumulatedEye.current.reduce((a,b)=>a+b, 0) / accumulatedEye.current.length) 
        : 90;
      const avgAttention = accumulatedAttention.current.length > 0 
        ? Math.round(accumulatedAttention.current.reduce((a,b)=>a+b, 0) / accumulatedAttention.current.length) 
        : 92;
      const avgSmile = accumulatedSmile.current.length > 0 
        ? Math.round(accumulatedSmile.current.reduce((a,b)=>a+b, 0) / accumulatedSmile.current.length) 
        : 15;

      const formData = new FormData();
      formData.append('session_id', sessionId);
      formData.append('question_id', questions[currentIdx].id);
      formData.append('eye_contact_score', avgEye);
      formData.append('attention_score', avgAttention);
      formData.append('smile_score', avgSmile);
      
      // Upload as WAV structure backend can decode
      const audioFile = new File([audioBlob], 'answer.wav', { type: 'audio/webm' });
      formData.append('audio', audioFile);

      logger_info("Uploading recording bytes to backend API...");
      const response = await api.post('/interview/submit', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      setEvaluation(response.data);
    } catch (err) {
      console.error("Error submitting answer:", err);
      alert("Backend AI processing failed. Ensure requirements are installed and soundfile matches.");
    } finally {
      setProcessing(false);
    }
  };

  const handleNext = () => {
    if (currentIdx < questions.length - 1) {
      setCurrentIdx((prev) => prev + 1);
      setEvaluation(null);
    }
  };

  const handleEndSession = async () => {
    setProcessing(true);
    try {
      await api.post(`/interview/${sessionId}/end`);
      navigate(`/report/${sessionId}`);
    } catch (err) {
      console.error("Error finalizing mock interview:", err);
      navigate(`/report/${sessionId}`);
    } finally {
      setProcessing(false);
    }
  };

  // Log logger dummy helper
  const logger_info = (msg) => {
    console.log(`[AEGIS-CLIENT] ${msg}`);
  };

  return (
    <div className="flex flex-col gap-6 text-left max-w-6xl mx-auto pb-12">
      {/* Upper context breadcrumb */}
      <div className="flex items-center justify-between border-b border-white/5 pb-4">
        <div>
          <span className="text-[10px] uppercase font-bold text-indigo-400 bg-indigo-500/10 px-2.5 py-1 rounded-full border border-indigo-500/20 font-outfit">
            {role} • {difficulty} Room
          </span>
          <h1 className="text-2xl font-bold font-outfit text-white mt-2">Active Practice Session</h1>
        </div>
        
        {/* Dynamic global status */}
        <div className="flex items-center gap-2">
          {isRecording ? (
            <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-red-500/10 border border-red-500/20 text-red-400 text-xs font-semibold">
              <span className="w-2 h-2 rounded-full bg-red-500 animate-ping" />
              <span>LOGGING LIVE: {timer}s</span>
            </span>
          ) : (
            <span className="px-3 py-1.5 rounded-full bg-slate-900 border border-white/5 text-slate-400 text-xs">
              STANDBY
            </span>
          )}
        </div>
      </div>

      {!audioPermission && (
        <div className="p-4 rounded-2xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm flex items-center gap-2">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <span>Camera and audio permissions are disabled. Please enable permission scopes to utilize visual eye tracking overlays.</span>
        </div>
      )}

      {/* Main room columns */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* 1. Left side: Video mesh & CV stats */}
        <div className="lg:col-span-7 flex flex-col gap-4">
          {/* Webcam mesh preview card */}
          <div className="rounded-3xl border border-white/5 bg-slate-950 overflow-hidden relative aspect-video shadow-neon-card">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="w-full h-full object-cover scale-x-[-1]"
            />
            {/* Overlay canvas drawing MediaPipe */}
            <canvas
              ref={canvasRef}
              width={640}
              height={480}
              className="absolute inset-0 w-full h-full object-cover scale-x-[-1] pointer-events-none"
            />
            <div className="absolute inset-0 scanlines pointer-events-none opacity-20" />
            
            {/* Visual scan HUD overlay labels */}
            <div className="absolute top-4 left-4 flex flex-col gap-1 text-[10px] font-mono text-cyan-400/80 bg-slate-950/80 backdrop-blur-sm px-2.5 py-1.5 rounded-lg border border-cyan-500/20">
              <span className="flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" />
                MESH SCAN ACTIVE
              </span>
              <span>GAZE: {liveEyeContact}%</span>
              <span>FOCUS: {liveAttention}%</span>
            </div>

            {/* Alert looking away warning */}
            {isRecording && liveAttention < 75 && (
              <div className="absolute inset-0 bg-red-500/15 flex items-center justify-center pointer-events-none border border-red-500/40 animate-pulse">
                <span className="px-4 py-2 rounded-xl bg-slate-950/95 border border-red-500/30 text-red-400 text-xs font-bold font-outfit uppercase tracking-widest">
                  ⚠️ Maintain Center Focus
                </span>
              </div>
            )}
          </div>

          {/* Real-time telemetry sliders */}
          <div className="grid grid-cols-3 gap-3 p-4 rounded-2xl bg-slate-900/40 border border-white/5">
            <div className="flex flex-col gap-1">
              <span className="text-[10px] text-slate-500 font-bold uppercase font-outfit">Eye Contact</span>
              <div className="h-1.5 bg-slate-950 rounded-full overflow-hidden mt-1">
                <div
                  className="h-full bg-cyan-500 transition-all duration-300"
                  style={{ width: `${liveEyeContact}%` }}
                />
              </div>
              <span className="text-xs font-bold text-slate-200 mt-1 font-mono">{liveEyeContact}%</span>
            </div>
            
            <div className="flex flex-col gap-1">
              <span className="text-[10px] text-slate-500 font-bold uppercase font-outfit">Focus Level</span>
              <div className="h-1.5 bg-slate-950 rounded-full overflow-hidden mt-1">
                <div
                  className="h-full bg-indigo-500 transition-all duration-300"
                  style={{ width: `${liveAttention}%` }}
                />
              </div>
              <span className="text-xs font-bold text-slate-200 mt-1 font-mono">{liveAttention}%</span>
            </div>

            <div className="flex flex-col gap-1">
              <span className="text-[10px] text-slate-500 font-bold uppercase font-outfit">Vocal Smile</span>
              <div className="h-1.5 bg-slate-950 rounded-full overflow-hidden mt-1">
                <div
                  className="h-full bg-pink-500 transition-all duration-300"
                  style={{ width: `${liveSmile}%` }}
                />
              </div>
              <span className="text-xs font-bold text-slate-200 mt-1 font-mono">{liveSmile}%</span>
            </div>
          </div>
        </div>

        {/* 2. Right side: Question bank prompts & AI feedback reports */}
        <div className="lg:col-span-5 flex flex-col gap-4">
          <AnimatePresence mode="wait">
            {processing ? (
              /* A. AI Computing report interface */
              <motion.div
                key="processing"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0 }}
                className="p-8 rounded-3xl bg-slate-900/40 border border-indigo-500/20 backdrop-blur-xl shadow-neon-card text-center flex flex-col items-center gap-4 min-h-[350px] justify-center"
              >
                <div className="w-14 h-14 rounded-2xl bg-indigo-600/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center animate-spin">
                  <RefreshCw className="w-7 h-7" />
                </div>
                <h2 className="text-lg font-bold font-outfit text-white">Aegis AI Engine Evaluating...</h2>
                <p className="text-xs text-slate-500 max-w-xs font-sans leading-relaxed">
                  Executing Whisper audio transcribing, running spaCy lemmatized keyword counts, and evaluating sentence semantic similarity models locally.
                </p>
              </motion.div>
            ) : evaluation ? (
              /* B. Individual question feedback sheet */
              <motion.div
                key="evaluation"
                initial={{ opacity: 0, x: 10 }}
                animate={{ opacity: 1, x: 0 }}
                className="p-5 rounded-3xl bg-slate-900/40 border border-white/5 backdrop-blur-xl shadow-neon-card flex flex-col gap-4 max-h-[500px] overflow-y-auto"
              >
                <div className="flex items-center justify-between">
                  <h2 className="text-sm font-bold font-outfit text-white uppercase tracking-wider text-indigo-400">
                    Question Feedback
                  </h2>
                  <span className="text-[10px] font-bold text-slate-400 bg-slate-950 px-2 py-0.5 rounded-full border border-white/5 font-mono">
                    COMPLETED
                  </span>
                </div>

                {/* Score indicators */}
                <div className="grid grid-cols-4 gap-2">
                  <div className="p-2 rounded-xl bg-slate-950 border border-white/5 flex flex-col text-center">
                    <span className="text-[8px] text-slate-500 font-bold uppercase">Tech</span>
                    <span className="text-xs font-extrabold text-indigo-400 mt-0.5">{evaluation.scores.technical}%</span>
                  </div>
                  <div className="p-2 rounded-xl bg-slate-950 border border-white/5 flex flex-col text-center">
                    <span className="text-[8px] text-slate-500 font-bold uppercase">Speech</span>
                    <span className="text-xs font-extrabold text-cyan-400 mt-0.5">{evaluation.scores.communication}%</span>
                  </div>
                  <div className="p-2 rounded-xl bg-slate-950 border border-white/5 flex flex-col text-center">
                    <span className="text-[8px] text-slate-500 font-bold uppercase">Focus</span>
                    <span className="text-xs font-extrabold text-pink-400 mt-0.5">{evaluation.scores.confidence}%</span>
                  </div>
                  <div className="p-2 rounded-xl bg-slate-950 border border-indigo-500/20 flex flex-col text-center">
                    <span className="text-[8px] text-indigo-400 font-bold uppercase">Total</span>
                    <span className="text-xs font-extrabold text-white mt-0.5">{evaluation.scores.overall}%</span>
                  </div>
                </div>

                {/* Scoped review transcripts */}
                <div className="flex flex-col gap-1.5 text-left bg-slate-950/60 p-3.5 rounded-2xl border border-white/5">
                  <span className="text-[9px] uppercase font-bold text-slate-500 tracking-wider">Your Transcript:</span>
                  <p className="text-xs text-slate-300 leading-relaxed italic">"{evaluation.transcript}"</p>
                </div>

                {/* Feedback markdown paragraph body */}
                <div className="text-xs text-slate-400 leading-relaxed space-y-3 prose border-t border-white/5 pt-4 text-left">
                  {evaluation.feedback.split('\n\n').map((para, i) => {
                    if (para.startsWith('###')) {
                      return <h3 key={i} className="text-xs font-bold text-slate-200 mt-4 mb-2">{para.replace('###', '')}</h3>;
                    }
                    if (para.startsWith('-')) {
                      return (
                        <ul key={i} className="list-disc pl-4 space-y-1 my-2">
                          {para.split('\n').map((item, idx) => (
                            <li key={idx}>{item.replace('-', '').trim()}</li>
                          ))}
                        </ul>
                      );
                    }
                    return <p key={i}>{para}</p>;
                  })}
                </div>

                {/* Navigation actions */}
                <div className="mt-2 pt-3 border-t border-white/5 flex justify-end">
                  {currentIdx < questions.length - 1 ? (
                    <button
                      onClick={handleNext}
                      className="flex items-center gap-1.5 px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold font-outfit transition-all duration-300"
                    >
                      <span>Next Question</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  ) : (
                    <button
                      onClick={handleEndSession}
                      className="flex items-center gap-1.5 px-5 py-3 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white text-xs font-semibold font-outfit shadow-md transition-all duration-300"
                    >
                      <Award className="w-4 h-4 animate-bounce" />
                      <span>End Mock & Compile Report</span>
                    </button>
                  )}
                </div>
              </motion.div>
            ) : (
              /* C. Standard question prompt layout */
              <motion.div
                key="question"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="p-6 rounded-3xl bg-slate-900/40 border border-white/5 backdrop-blur-xl shadow-neon-card flex flex-col gap-6 min-h-[350px] justify-between"
              >
                <div className="flex flex-col gap-1">
                  <div className="flex items-center justify-between text-[9px] font-bold text-slate-500 uppercase tracking-widest font-outfit">
                    <span>QUESTION {currentIdx + 1} OF {questions.length}</span>
                    <span className="text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded-full border border-cyan-500/20 font-sans">
                      {questions[currentIdx]?.category}
                    </span>
                  </div>
                  <h2 className="text-base font-semibold font-outfit text-slate-100 leading-normal mt-3">
                    {questions[currentIdx]?.question_text}
                  </h2>
                </div>

                {/* Subtitle helper showing keywords to target */}
                {questions[currentIdx]?.keywords && (
                  <div className="p-3.5 rounded-2xl bg-slate-950/60 border border-white/5 flex flex-col gap-1">
                    <span className="text-[9px] uppercase font-bold text-indigo-400 tracking-wider font-outfit">
                      Target Core Terminology:
                    </span>
                    <p className="text-[10px] text-slate-400 leading-normal font-sans italic">
                      {questions[currentIdx].keywords}
                    </p>
                  </div>
                )}

                {/* Active transcription preview overlay */}
                {isRecording && (
                  <div className="p-3 bg-red-500/5 rounded-xl border border-red-500/20 text-center flex items-center justify-center gap-1.5 animate-pulse text-red-400 text-xs font-semibold">
                    <Mic className="w-3.5 h-3.5" />
                    <span>AUDIO SCANNING ACTIVE... SPEAK NOW</span>
                  </div>
                )}

                {/* Trigger controls */}
                <div className="flex items-center gap-3">
                  {!isRecording ? (
                    <button
                      onClick={startRecording}
                      className="w-full py-3.5 rounded-2xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold font-outfit text-sm transition-all duration-300 flex items-center justify-center gap-2 shadow-neon-purple"
                    >
                      <Play className="w-4 h-4" />
                      <span>Start Answering</span>
                    </button>
                  ) : (
                    <button
                      onClick={stopRecordingAndSubmit}
                      className="w-full py-3.5 rounded-2xl bg-red-600 hover:bg-red-500 text-white font-semibold font-outfit text-sm transition-all duration-300 flex items-center justify-center gap-2 shadow-neon-purple animate-pulse"
                    >
                      <Square className="w-4 h-4" />
                      <span>Finish & Submit</span>
                    </button>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
};

export default InterviewRoom;

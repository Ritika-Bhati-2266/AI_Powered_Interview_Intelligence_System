import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import { 
  ArrowLeft, 
  Award, 
  Cpu, 
  Layers, 
  Terminal, 
  Clock, 
  MessageSquare,
  AlertCircle,
  TrendingUp,
  Brain,
  ThumbsUp
} from 'lucide-react';

export default function Analytics() {
  const { id } = useParams();
  const [interview, setInterview] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchInterviewDetails = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`/api/interviews/${id}`);
        setInterview(response.data);
        setError(null);
      } catch (err) {
        console.error("Failed to load interview analytics:", err);
        setError("Could not resolve analytics parameters. Seeding may be incomplete.");
      } finally {
        setLoading(false);
      }
    };
    fetchInterviewDetails();
  }, [id]);

  if (loading) {
    return (
      <div className="cyber-panel p-16 flex flex-col items-center justify-center space-y-4 bg-cyber-dark/40 border border-cyber-cyan/10">
        <div className="w-10 h-10 border-4 border-cyber-cyan border-t-transparent rounded-full animate-spin"></div>
        <p className="text-sm font-tech text-cyber-cyan tracking-widest">LOADING NEURAL MODEL DATA...</p>
      </div>
    );
  }

  if (error || !interview) {
    return (
      <div className="cyber-panel p-12 text-center bg-cyber-dark/40 border border-cyber-pink/20 space-y-6">
        <AlertCircle className="w-12 h-12 text-cyber-pink mx-auto animate-bounce" />
        <h2 className="text-2xl font-bold font-cyber text-white">ANALYTICS BREAKAGE</h2>
        <p className="text-cyber-text text-sm max-w-md mx-auto">
          {error || "Could not retrieve completed telemetry datasets."}
        </p>
        <Link to="/" className="inline-flex items-center gap-2 px-5 py-2.5 bg-cyber-cyan text-black hover:bg-cyber-cyan/80 font-cyber text-xs uppercase font-bold tracking-wider clip-slanted transition">
          <ArrowLeft className="w-4 h-4" />
          <span>Return to Dashboard</span>
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Back button and telemetry header */}
      <div className="flex items-center justify-between">
        <Link to="/" className="inline-flex items-center gap-2 text-cyber-cyan hover:text-white font-cyber text-xs uppercase font-bold tracking-wider transition cursor-pointer">
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Grid Dashboard</span>
        </Link>
        <span className="font-tech text-xs text-cyber-pink">COMPLETED COGNITIVE ASSAY</span>
      </div>

      {/* Main HUD Scoring panel */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        
        {/* Metric Core Left */}
        <div className="cyber-panel p-6 bg-cyber-dark/95 flex flex-col justify-between items-center text-center relative overflow-hidden h-full min-h-[280px]">
          <div className="absolute top-2 left-2 text-[10px] text-cyber-text/30 font-tech">NODE_COGNITIVE_GRADE</div>
          
          <div className="my-auto space-y-4">
            <Award className="w-16 h-16 text-cyber-cyan mx-auto drop-shadow-[0_0_15px_rgba(0,243,255,0.4)] animate-pulse" />
            <div>
              <h3 className="text-sm font-cyber uppercase tracking-wider text-cyber-text font-bold">Overall Performance</h3>
              <p className="text-5xl font-black text-white font-cyber tracking-tighter mt-1 text-glow-cyan">
                {interview.performance_score}%
              </p>
            </div>
          </div>
          
          <div className="w-full bg-cyber-bg p-3 border border-cyber-gray text-xs font-tech text-cyber-cyan flex justify-between">
            <span>ASSAY RATING:</span>
            <span className="font-bold">EXCELLENT</span>
          </div>
        </div>

        {/* Synthesis Right Block */}
        <div className="lg:col-span-3 cyber-panel p-6 bg-cyber-dark/65 flex flex-col justify-between space-y-4">
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-cyber-pink font-cyber font-bold tracking-wider text-xs">
              <Brain className="w-4 h-4 animate-pulse" />
              <span>COGNITIVE BRAIN SYNAPSE SUMMARY</span>
            </div>
            <h2 className="text-2xl font-black text-white font-cyber uppercase tracking-tight">
              {interview.title}
            </h2>
            <div className="text-xs text-cyber-text flex items-center gap-3">
              <span>CREATED: {new Date(interview.created_at).toLocaleString()}</span>
              <span>•</span>
              <span className="text-cyber-green">STATUS: PIPELINE ANALYZED</span>
            </div>
          </div>

          <div className="bg-cyber-bg p-4 border border-cyber-gray font-sans text-sm text-white/90 leading-relaxed border-l-4 border-l-cyber-cyan">
            {interview.overall_feedback || "No neural summary registered."}
          </div>
        </div>

      </div>

      {/* Answer evaluation segment */}
      <div className="space-y-6">
        <div className="flex items-center gap-2">
          <Layers className="text-cyber-cyan w-4 h-4" />
          <h2 className="text-xl font-bold font-cyber text-white uppercase tracking-wider">Acoustic & Semantic breakdown</h2>
        </div>

        <div className="space-y-6">
          {interview.questions.map((q, idx) => (
            <div key={q.id} className="cyber-panel p-6 bg-cyber-dark/50 space-y-4 relative border-l-4 border-l-cyber-pink">
              
              {/* Question header */}
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 border-b border-cyber-gray pb-3">
                <div className="flex items-center gap-2 font-cyber font-bold text-sm text-white">
                  <span className="text-cyber-pink">#{idx + 1}</span>
                  <h3>Prompt Question</h3>
                </div>
                {q.answer && (
                  <div className="flex items-center gap-4 text-xs font-tech">
                    <span className="text-cyber-text">Audio Duration: <strong className="text-white">{q.answer.audio_duration}s</strong></span>
                    <span className="text-cyber-text">Sentiment: <strong className="text-cyber-cyan capitalize">{q.answer.sentiment}</strong></span>
                  </div>
                )}
              </div>

              {/* Question text */}
              <p className="text-md font-bold text-white font-sans">
                "{q.text}"
              </p>

              {/* Answer block */}
              {q.answer ? (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-2">
                  
                  {/* Left Column: Transcribed Text */}
                  <div className="md:col-span-2 space-y-3">
                    <span className="text-[10px] uppercase font-cyber text-cyber-text/50 block">LOCAL STT TRANSCRIPTION</span>
                    <div className="bg-cyber-bg/90 p-4 border border-cyber-gray text-xs font-tech text-white leading-relaxed whitespace-pre-wrap">
                      {q.answer.transcribed_text}
                    </div>
                    {q.expected_keywords && (
                      <div className="flex flex-wrap gap-1.5 pt-1">
                        <span className="text-[9px] uppercase font-cyber text-cyber-text/40 self-center mr-1">EXPECTED KEYWORDS:</span>
                        {q.expected_keywords.split(',').map((kw, kidx) => (
                          <span key={kidx} className="text-[9px] font-tech bg-cyber-gray border border-cyber-gray/80 px-2 py-0.5 text-cyber-cyan">
                            {kw.trim()}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Right Column: AI Scoring */}
                  <div className="space-y-4">
                    <div className="bg-cyber-bg p-4 border border-cyber-gray space-y-3">
                      <div className="flex justify-between items-center text-xs font-cyber">
                        <span className="text-cyber-text/70 uppercase">SEMANTIC ALIGNMENT</span>
                        <span className="text-cyber-green font-tech font-extrabold">{q.answer.relevance_score}%</span>
                      </div>
                      
                      {/* Visual score bar */}
                      <div className="w-full h-2 bg-cyber-gray overflow-hidden">
                        <div 
                          className="h-full bg-cyber-green"
                          style={{ width: `${q.answer.relevance_score}%` }}
                        ></div>
                      </div>
                    </div>

                    <div className="bg-cyber-bg p-4 border border-cyber-gray space-y-2">
                      <div className="flex items-center gap-1.5 text-[10px] uppercase font-cyber text-cyber-text/50">
                        <ThumbsUp className="w-3.5 h-3.5 text-cyber-pink" />
                        <span>SYNAPSE CRITIQUE</span>
                      </div>
                      <p className="text-xs font-sans text-cyber-text leading-relaxed">
                        {q.answer.feedback || "No semantic evaluation processed."}
                      </p>
                    </div>
                  </div>

                </div>
              ) : (
                <div className="bg-cyber-pink/5 border border-dashed border-cyber-pink/20 p-6 text-center text-xs text-cyber-pink font-tech">
                  &gt; ERROR: NO COGNITIVE RESPONSES FOUND FOR THIS PROMPT BLOCK. PLEASE RUN SIMULATOR CAPTURE PROCESS.
                </div>
              )}

            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

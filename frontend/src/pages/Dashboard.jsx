import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { 
  Terminal, 
  Cpu, 
  Activity, 
  Layers, 
  Sparkles, 
  Clock, 
  FileCheck, 
  Play, 
  TrendingUp, 
  RefreshCw 
} from 'lucide-react';

export default function Dashboard() {
  const [stats, setStats] = useState({ total_interviews: 0, completed: 0, pending: 0, average_score: 0.0 });
  const [interviews, setInterviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [seeding, setSeeding] = useState(false);
  const [error, setError] = useState(null);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/dashboard');
      setStats(response.data.stats);
      setInterviews(response.data.interviews);
      setError(null);
    } catch (err) {
      console.error("Failed to load dashboard statistics:", err);
      setError("Failed to fetch dashboard feed. Ensure backend server is running on localhost:8000.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const triggerSeed = async () => {
    try {
      setSeeding(true);
      await axios.post('/api/seed');
      // Reload dashboard after successful seed
      await fetchDashboardData();
    } catch (err) {
      console.error("Seeding operation failed:", err);
      setError("Database seeding failed. Please check backend terminal output.");
    } finally {
      setSeeding(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Upper Terminal Banner */}
      <div className="cyber-panel p-6 bg-cyber-dark/80 relative overflow-hidden flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-2 max-w-2xl">
          <div className="flex items-center gap-2 text-cyber-cyan font-cyber font-bold tracking-wider text-sm">
            <Activity className="w-4 h-4 animate-pulse" />
            <span>NEURAL INTERVIEW OS // ONLINE</span>
          </div>
          <h1 className="text-3xl font-black text-white font-cyber tracking-tight uppercase">
            System Dashboard
          </h1>
          <p className="text-cyber-text text-sm font-sans">
            Offline AI Intelligence Suite for speech analysis, speech-to-text semantic matching, 
            acoustic sentiment scoring, and offline LLM performance indexing.
          </p>
        </div>
        
        <div className="flex flex-wrap gap-3">
          <button 
            onClick={fetchDashboardData}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 border border-cyber-cyan/30 bg-cyber-cyan/10 hover:bg-cyber-cyan/20 active:scale-95 text-cyber-cyan text-sm uppercase tracking-wider font-cyber font-semibold clip-slanted-sm transition duration-150 cursor-pointer"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh Feed</span>
          </button>
          
          <button 
            onClick={triggerSeed}
            disabled={seeding}
            className="flex items-center gap-2 px-4 py-2 border border-cyber-pink/30 bg-cyber-pink/10 hover:bg-cyber-pink/20 active:scale-95 text-cyber-pink text-sm uppercase tracking-wider font-cyber font-semibold clip-slanted-sm transition duration-150 cursor-pointer"
          >
            <Sparkles className="w-4 h-4" />
            <span>{seeding ? 'Syncing...' : 'Neural Seed'}</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-cyber-pink/10 border border-cyber-pink/40 text-cyber-pink rounded-none font-tech text-sm flex gap-3 items-center">
          <Terminal className="w-5 h-5 flex-shrink-0" />
          <span>[SYSTEM ERROR]: {error}</span>
        </div>
      )}

      {/* Grid Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="cyber-panel p-5 bg-cyber-dark/40 relative">
          <div className="flex justify-between items-start">
            <p className="text-xs uppercase tracking-wider text-cyber-text font-cyber">Total Sessions</p>
            <Cpu className="text-cyber-cyan w-5 h-5 opacity-70" />
          </div>
          <p className="text-4xl font-extrabold text-white mt-4 font-cyber tracking-tight">
            {stats.total_interviews.toString().padStart(2, '0')}
          </p>
          <div className="absolute bottom-0 right-0 w-24 h-1 bg-cyber-cyan/50"></div>
        </div>

        <div className="cyber-panel-pink p-5 bg-cyber-dark/40 relative">
          <div className="flex justify-between items-start">
            <p className="text-xs uppercase tracking-wider text-cyber-text font-cyber">Evaluation Completed</p>
            <FileCheck className="text-cyber-pink w-5 h-5 opacity-70" />
          </div>
          <p className="text-4xl font-extrabold text-white mt-4 font-cyber tracking-tight">
            {stats.completed.toString().padStart(2, '0')}
          </p>
          <div className="absolute bottom-0 right-0 w-24 h-1 bg-cyber-pink/50"></div>
        </div>

        <div className="cyber-panel p-5 bg-cyber-dark/40 relative">
          <div className="flex justify-between items-start">
            <p className="text-xs uppercase tracking-wider text-cyber-text font-cyber">Pending Analysis</p>
            <Clock className="text-cyber-yellow w-5 h-5 opacity-70" />
          </div>
          <p className="text-4xl font-extrabold text-white mt-4 font-cyber tracking-tight text-cyber-yellow">
            {stats.pending.toString().padStart(2, '0')}
          </p>
          <div className="absolute bottom-0 right-0 w-24 h-1 bg-cyber-yellow/50"></div>
        </div>

        <div className="cyber-panel p-5 bg-cyber-dark/40 relative">
          <div className="flex justify-between items-start">
            <p className="text-xs uppercase tracking-wider text-cyber-text font-cyber">Neural Mean Score</p>
            <TrendingUp className="text-cyber-green w-5 h-5 opacity-70" />
          </div>
          <p className="text-4xl font-extrabold mt-4 font-cyber tracking-tight text-cyber-green">
            {stats.average_score}%
          </p>
          <div className="absolute bottom-0 right-0 w-24 h-1 bg-cyber-green/50"></div>
        </div>
      </div>

      {/* Main Panel Content: Sessions list */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Side: Sessions Index */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center gap-2">
            <Layers className="text-cyber-cyan w-4 h-4" />
            <h2 className="text-xl font-bold font-cyber text-white uppercase tracking-wider">Active Memory Segments</h2>
          </div>

          {loading ? (
            <div className="cyber-panel p-12 flex flex-col items-center justify-center space-y-4 bg-cyber-dark/20 border border-cyber-cyan/10">
              <RefreshCw className="w-8 h-8 text-cyber-cyan animate-spin" />
              <p className="text-sm font-tech text-cyber-cyan">CONNECTING NEURAL CORRIDOR...</p>
            </div>
          ) : interviews.length === 0 ? (
            <div className="cyber-panel p-12 flex flex-col items-center justify-center space-y-6 bg-cyber-dark/20 text-center border border-dashed border-cyber-cyan/20">
              <p className="text-cyber-text text-sm">No neural evaluation sessions indexed in local SQLite storage.</p>
              <button 
                onClick={triggerSeed}
                disabled={seeding}
                className="px-6 py-2.5 bg-cyber-cyan text-black hover:bg-cyber-cyan/80 active:scale-95 text-xs font-cyber font-black uppercase tracking-wider clip-slanted transition"
              >
                {seeding ? "Populating Models..." : "Populate with Mock Neural Portfolio"}
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              {interviews.map((intv) => (
                <div 
                  key={intv.id} 
                  className={`cyber-panel p-5 bg-cyber-dark/60 border ${
                    intv.status === 'completed' 
                      ? 'border-cyber-cyan/10 hover:border-cyber-cyan/40 hover:shadow-cyan-glow' 
                      : 'border-cyber-pink/10 hover:border-cyber-pink/40 hover:shadow-pink-glow'
                  } transition duration-300 relative group flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4`}
                >
                  <div className="space-y-2">
                    <div className="flex items-center gap-3">
                      <span className="font-tech text-xs text-cyber-text/50">ID: {intv.id.toString().padStart(3, '0')}</span>
                      <span className={`text-[10px] uppercase font-cyber font-semibold px-2 py-0.5 tracking-wider ${
                        intv.status === 'completed' 
                          ? 'bg-cyber-cyan/10 text-cyber-cyan border border-cyber-cyan/20' 
                          : intv.status === 'pending'
                          ? 'bg-cyber-yellow/10 text-cyber-yellow border border-cyber-yellow/20 animate-pulse'
                          : 'bg-cyber-pink/10 text-cyber-pink border border-cyber-pink/20'
                      }`}>
                        {intv.status}
                      </span>
                    </div>
                    <h3 className="text-lg font-bold text-white group-hover:text-cyber-cyan transition">
                      {intv.title}
                    </h3>
                    <div className="flex items-center gap-4 text-xs font-sans text-cyber-text">
                      <span className="flex items-center gap-1">
                        <Clock className="w-3.5 h-3.5 text-cyber-cyan" />
                        {new Date(intv.created_at).toLocaleDateString()}
                      </span>
                      <span>•</span>
                      <span>{intv.questions_count} Questions</span>
                    </div>
                  </div>

                  <div className="flex items-center gap-4 self-end sm:self-center">
                    {intv.status === 'completed' && intv.performance_score !== null && (
                      <div className="text-right">
                        <span className="text-[10px] text-cyber-text/40 block font-cyber">NEURAL GRADE</span>
                        <span className="font-cyber font-black text-2xl text-cyber-green">{intv.performance_score}%</span>
                      </div>
                    )}
                    
                    {intv.status === 'completed' ? (
                      <Link 
                        to={`/analytics/${intv.id}`}
                        className="flex items-center gap-2 px-4 py-2 border border-cyber-cyan text-cyber-cyan hover:bg-cyber-cyan hover:text-black font-cyber text-xs uppercase font-bold tracking-wider clip-slanted-sm transition cursor-pointer"
                      >
                        <span>Inspect Feed</span>
                      </Link>
                    ) : (
                      <Link 
                        to={`/simulator/${intv.id}`}
                        className="flex items-center gap-2 px-4 py-2 bg-cyber-pink text-white hover:bg-cyber-pink/80 font-cyber text-xs uppercase font-bold tracking-wider clip-slanted-sm shadow-pink-glow hover:scale-105 active:scale-95 transition cursor-pointer"
                      >
                        <Play className="w-3.5 h-3.5 fill-current" />
                        <span>Run Simulation</span>
                      </Link>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right Side: Quick Action Terminal / Documentation */}
        <div className="space-y-6">
          <div className="flex items-center gap-2">
            <Terminal className="text-cyber-pink w-4 h-4" />
            <h2 className="text-xl font-bold font-cyber text-white uppercase tracking-wider">System Terminal</h2>
          </div>

          <div className="cyber-panel-pink p-5 bg-cyber-dark/80 crt-screen space-y-4">
            <div className="flex justify-between items-center border-b border-cyber-pink/20 pb-2">
              <span className="text-xs font-tech text-cyber-pink tracking-wider">ROOT@NEURAL-INTEL:~#</span>
              <span className="w-2.5 h-2.5 bg-cyber-pink rounded-full animate-ping"></span>
            </div>
            
            <div className="font-tech text-xs text-cyber-pink/90 space-y-3 leading-relaxed">
              <p>&gt; Offline speech analysis engine activated.</p>
              <p>&gt; Loading spacy en_core_web_sm: SUCCESS</p>
              <p>&gt; Initializing faster-whisper (Base model): SUCCESS</p>
              <p>&gt; Setting up local cognitive embedding matcher: READY</p>
              <p>&gt; Audio file path sandbox enabled: app/uploads/</p>
              <p className="border border-cyber-pink/30 p-2 bg-cyber-pink/5">
                Press [NEURAL SEED] at the top right to populate mock evaluation profiles containing sample user, transcripts, acoustic timelines, and sentiment scoring variables.
              </p>
            </div>
          </div>

          <div className="cyber-panel p-5 bg-cyber-dark/60 space-y-4">
            <h3 className="font-cyber font-bold text-sm text-white uppercase tracking-wider border-b border-cyber-gray pb-2">
              Offline Stack Diagnostics
            </h3>
            
            <div className="space-y-3 font-sans text-xs">
              <div className="flex justify-between items-center text-cyber-text">
                <span>Transcription Engine</span>
                <span className="text-cyber-cyan font-tech">faster-whisper v1.0.1</span>
              </div>
              <div className="flex justify-between items-center text-cyber-text">
                <span>Sentence Embeddings</span>
                <span className="text-cyber-cyan font-tech">MiniLM-L6-v2 (sentence-transformers)</span>
              </div>
              <div className="flex justify-between items-center text-cyber-text">
                <span>NLP Grammar Models</span>
                <span className="text-cyber-cyan font-tech">spaCy (Local Pipeline)</span>
              </div>
              <div className="flex justify-between items-center text-cyber-text">
                <span>Acoustic Frequency Analyzer</span>
                <span className="text-cyber-cyan font-tech">librosa / numpy</span>
              </div>
              <div className="flex justify-between items-center text-cyber-text">
                <span>SQL Engine Backend</span>
                <span className="text-cyber-cyan font-tech">SQLite3 Local File</span>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}

import React, { useState } from 'react';
import AppRouter from './router';
import { Link, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { 
  Terminal, 
  Cpu, 
  ShieldAlert, 
  Grid, 
  Disc, 
  LogOut,
  Info,
  UserCheck
} from 'lucide-react';

function AppLayout() {
  const location = useLocation();
  const [scanlines, setScanlines] = useState(true);
  const { user, logout, isAuthenticated } = useAuth();

  return (
    <div className={`min-h-screen text-cyber-text bg-cyber-bg tech-grid relative ${scanlines ? 'scanlines' : ''}`}>
      
      {/* Top Futuristic Navigation Bar */}
      <header className="border-b border-cyber-cyan/20 bg-cyber-dark/80 backdrop-filter backdrop-blur-md sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          
          {/* Logo HUD branding */}
          <Link to="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 border border-cyber-cyan bg-cyber-cyan/10 flex items-center justify-center group-hover:shadow-cyan-glow group-hover:bg-cyber-cyan/20 transition-all duration-300 clip-slanted-sm">
              <Cpu className="w-5 h-5 text-cyber-cyan animate-pulse" />
            </div>
            <div>
              <span className="font-cyber font-black tracking-tight text-white block text-sm group-hover:text-cyber-cyan transition">
                NEURAL INTERVIEW //
              </span>
              <span className="font-tech text-xs text-cyber-pink tracking-widest block uppercase">
                Offline Cognitive Assay OS
              </span>
            </div>
          </Link>

          {/* Toggle telemetry / scanline controls and User Auth HUD */}
          <div className="flex items-center gap-4">
            
            {/* Active User Email profile displaying if logged in */}
            {isAuthenticated && user && (
              <div className="hidden md:flex items-center gap-2 bg-cyber-light/40 border border-cyber-cyan/20 px-3 py-1.5 font-tech text-xs text-cyber-cyan rounded-none">
                <UserCheck className="w-3.5 h-3.5" />
                <span>{user.email}</span>
              </div>
            )}

            <button 
              onClick={() => setScanlines(!scanlines)}
              className={`flex items-center gap-2 px-3 py-1.5 border text-xs uppercase tracking-wider font-tech clip-slanted-sm transition duration-150 cursor-pointer ${
                scanlines 
                  ? 'border-cyber-pink/50 text-cyber-pink bg-cyber-pink/10 shadow-pink-glow' 
                  : 'border-cyber-text/30 text-cyber-text hover:border-cyber-cyan hover:text-cyber-cyan bg-cyber-dark'
              }`}
            >
              <Disc className={`w-3.5 h-3.5 ${scanlines ? 'animate-spin' : ''}`} />
              <span>CRT: {scanlines ? 'ON' : 'OFF'}</span>
            </button>

            {/* Logout button */}
            {isAuthenticated && (
              <button 
                onClick={logout}
                className="flex items-center gap-1.5 px-3 py-1.5 border border-cyber-pink text-cyber-pink hover:bg-cyber-pink hover:text-white text-xs uppercase tracking-wider font-tech clip-slanted-sm transition cursor-pointer"
              >
                <LogOut className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">Logout</span>
              </button>
            )}
            
            <div className="hidden lg:flex items-center gap-1.5 bg-cyber-gray px-3 py-1.5 border border-cyber-gray text-xs font-tech text-cyber-green">
              <span className="w-2 h-2 rounded-full bg-cyber-green animate-ping"></span>
              <span>LOCAL_ENGINE: ACTIVE</span>
            </div>
          </div>

        </div>
      </header>

      {/* Main Core Container Grid */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex flex-col md:flex-row gap-8">
        
        {/* Navigation Sidebar Panel - Only interactive if logged in */}
        <aside className="w-full md:w-64 flex-shrink-0 space-y-6">
          <div className="cyber-panel p-5 bg-cyber-dark/80 space-y-4">
            <h3 className="font-cyber font-bold text-xs uppercase tracking-widest text-cyber-pink border-b border-cyber-gray pb-2">
              Memory Hub
            </h3>
            <nav className="flex flex-col gap-2">
              {isAuthenticated ? (
                <Link 
                  to="/" 
                  className={`flex items-center gap-3 px-4 py-2 text-xs uppercase font-cyber tracking-wider clip-slanted-sm border transition duration-150 ${
                    location.pathname === '/' 
                      ? 'border-cyber-cyan text-cyber-cyan bg-cyber-cyan/5' 
                      : 'border-transparent text-cyber-text hover:border-cyber-cyan/30 hover:bg-cyber-light'
                  }`}
                >
                  <Grid className="w-4 h-4" />
                  <span>Session Matrix</span>
                </Link>
              ) : (
                <div className="p-3 bg-cyber-bg text-center border border-dashed border-cyber-gray text-xs text-cyber-text/50 font-tech">
                  SYSTEM GATES SHIELDED.
                </div>
              )}
            </nav>
          </div>

          {/* Quick Stats Panel Widgets */}
          <div className="cyber-panel-pink p-5 bg-cyber-dark/80 space-y-4">
            <h3 className="font-cyber font-bold text-xs uppercase tracking-widest text-cyber-cyan border-b border-cyber-gray pb-2 flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-cyber-pink" />
              <span>Security Terminal</span>
            </h3>
            <p className="text-xs text-cyber-text leading-relaxed font-sans">
              All database records (SQLite) and transcription pipelines execute directly on your local system architecture. <strong>No audio data or semantic tokens are transmitted to public clouds.</strong>
            </p>
          </div>

          <div className="cyber-panel p-5 bg-cyber-dark/80 flex items-start gap-3">
            <Info className="w-4 h-4 text-cyber-cyan mt-0.5 flex-shrink-0" />
            <div className="space-y-1">
              <span className="font-cyber font-bold text-[10px] text-white block uppercase">V3.5 FLASH COGNITIVE CORE</span>
              <p className="text-[10px] text-cyber-text/70 leading-normal">
                Using Gemini 3.5 Flash for high-speed coding synthesis. Code compiles offline perfectly.
              </p>
            </div>
          </div>
        </aside>

        {/* Dynamic Route View Content Area */}
        <main className="flex-1 min-w-0">
          <AppRouter />
        </main>

      </div>

      {/* Cyberpunk Telemetry Footer */}
      <footer className="border-t border-cyber-gray bg-cyber-bg py-6 mt-16 font-tech text-[10px] tracking-widest text-cyber-text/50 uppercase">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row justify-between items-center gap-4">
          <div className="flex items-center gap-2">
            <Terminal className="w-4 h-4 text-cyber-cyan" />
            <span>NEURAL EVALUATION SYSTEMS CORP © 2026 // OFFLINE SUITE</span>
          </div>
          <div className="flex items-center gap-4">
            <span>DATABASE: SQLITE3</span>
            <span>TRANSCRIPTIONS: WHISPER</span>
            <span>SECURITY: JWT TOKEN</span>
          </div>
        </div>
      </footer>

    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppLayout />
    </AuthProvider>
  );
}

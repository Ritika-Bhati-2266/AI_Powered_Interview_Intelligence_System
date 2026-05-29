import React, { useState } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import { 
  Lock, 
  Mail, 
  Terminal, 
  Cpu, 
  Sparkles, 
  ShieldAlert, 
  AlertTriangle 
} from 'lucide-react';

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [seeding, setSeeding] = useState(false);
  const [seedMessage, setSeedMessage] = useState(null);

  // Get the redirect path from navigation state or fallback to dashboard root '/'
  const from = location.state?.from?.pathname || "/";

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      setError("Please input valid decryption tokens (Email and Password).");
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const result = await login(email, password);
      if (result.success) {
        navigate(from, { replace: true });
      } else {
        setError(result.error);
      }
    } catch (err) {
      setError("Internal security core mismatch. Try again.");
    } finally {
      setLoading(false);
    }
  };

  const triggerSeed = async () => {
    try {
      setSeeding(true);
      setError(null);
      const response = await axios.post('/api/seed');
      setSeedMessage(response.data.message);
      // Pre-fill inputs with default mock credentials for easier user testing experience
      setEmail('test@antigravity.ai');
      setPassword('password123');
    } catch (err) {
      console.error(err);
      setError("Database seeding failed. Ensure your backend server on port 8000 is active.");
    } finally {
      setSeeding(false);
    }
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8 relative">
        
        {/* Decorative Background Accents */}
        <div className="absolute -top-10 -left-10 w-40 h-40 bg-cyber-cyan/5 rounded-full blur-3xl pointer-events-none"></div>
        <div className="absolute -bottom-10 -right-10 w-40 h-40 bg-cyber-pink/5 rounded-full blur-3xl pointer-events-none"></div>

        {/* Central Auth Cyber Panel Container */}
        <div className="cyber-panel p-8 bg-cyber-dark/85 backdrop-blur-xl relative crt-screen">
          
          {/* Header branding */}
          <div className="text-center space-y-4 mb-8 border-b border-cyber-gray pb-6">
            <div className="w-12 h-12 mx-auto border border-cyber-cyan bg-cyber-cyan/10 flex items-center justify-center clip-slanted-sm shadow-cyan-glow">
              <Lock className="w-5 h-5 text-cyber-cyan animate-pulse" />
            </div>
            <div>
              <h2 className="text-xl font-black text-white font-cyber tracking-tight uppercase">
                System Decryption Gateway
              </h2>
              <p className="text-xs font-tech text-cyber-pink mt-1 tracking-widest">
                VERIFY USER CREDENTIALS
              </p>
            </div>
          </div>

          {/* Seed Alert notice helper */}
          {!seedMessage && !error && (
            <div className="mb-6 p-4 bg-cyber-cyan/5 border border-cyber-cyan/20 text-xs font-sans text-cyber-text leading-relaxed flex items-start gap-3">
              <ShieldAlert className="w-5 h-5 text-cyber-cyan flex-shrink-0 mt-0.5" />
              <div>
                <span>Need test accounts? Click </span>
                <button 
                  type="button" 
                  onClick={triggerSeed}
                  disabled={seeding}
                  className="text-cyber-cyan underline hover:text-white font-bold cursor-pointer inline"
                >
                  {seeding ? 'Initializing Seeder...' : '[Run Seeder]'}
                </button>
                <span> to automatically register <strong>test@antigravity.ai</strong> in SQLite with password <strong>password123</strong>.</span>
              </div>
            </div>
          )}

          {seedMessage && (
            <div className="mb-6 p-4 bg-cyber-green/10 border border-cyber-green/30 text-cyber-green font-tech text-xs rounded-none flex items-center gap-3">
              <Sparkles className="w-5 h-5 flex-shrink-0" />
              <span>{seedMessage}</span>
            </div>
          )}

          {error && (
            <div className="mb-6 p-4 bg-cyber-pink/10 border border-cyber-pink/40 text-cyber-pink font-tech text-xs rounded-none flex items-center gap-3">
              <AlertTriangle className="w-5 h-5 flex-shrink-0 animate-bounce" />
              <span>{error}</span>
            </div>
          )}

          {/* Form */}
          <form className="space-y-6" onSubmit={handleSubmit}>
            
            {/* Email Field */}
            <div className="space-y-2">
              <label className="text-xs uppercase font-cyber font-semibold tracking-wider text-cyber-text block">
                User Security Email
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-cyber-text/50">
                  <Mail className="w-4 h-4" />
                </span>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-cyber-bg border border-cyber-gray focus:border-cyber-cyan p-3 pl-10 text-sm text-white font-tech rounded-none outline-none transition duration-150"
                  placeholder="name@antigravity.ai"
                />
              </div>
            </div>

            {/* Password Field */}
            <div className="space-y-2">
              <label className="text-xs uppercase font-cyber font-semibold tracking-wider text-cyber-text block">
                Security Password
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-cyber-text/50">
                  <Lock className="w-4 h-4" />
                </span>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-cyber-bg border border-cyber-gray focus:border-cyber-cyan p-3 pl-10 text-sm text-white font-tech rounded-none outline-none transition duration-150"
                  placeholder="••••••••••••"
                />
              </div>
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-cyber-cyan hover:bg-cyber-cyan/95 text-black hover:scale-[1.01] active:scale-[0.99] font-cyber text-xs uppercase font-black tracking-widest clip-slanted shadow-cyan-glow transition duration-150 cursor-pointer"
            >
              {loading ? 'Validating Token...' : 'Decrypt Grid Entrance'}
            </button>

          </form>

          {/* Footer router trigger */}
          <div className="mt-6 pt-6 border-t border-cyber-gray text-center text-xs font-sans text-cyber-text">
            <span>Don't have a secure identity node? </span>
            <Link to="/register" className="text-cyber-pink hover:text-white font-cyber uppercase tracking-wider transition underline cursor-pointer">
              Register Account
            </Link>
          </div>

        </div>

      </div>
    </div>
  );
}

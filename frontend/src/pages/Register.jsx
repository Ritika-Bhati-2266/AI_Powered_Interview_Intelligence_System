import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  UserPlus, 
  Lock, 
  Mail, 
  Terminal, 
  Sparkles, 
  AlertTriangle 
} from 'lucide-react';

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password || !confirmPassword) {
      setError("All credentials nodes must be specified.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passphrase mismatch. Confirmation must match password.");
      return;
    }

    if (password.length < 6) {
      setError("Passphrase too weak. Minimum 6 characters required.");
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const result = await register(email, password);
      if (result.success) {
        navigate('/', { replace: true });
      } else {
        setError(result.error);
      }
    } catch (err) {
      setError("Identity creation pipeline error. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8 relative">
        
        {/* Decorative Background Accents */}
        <div className="absolute -top-10 -left-10 w-40 h-40 bg-cyber-pink/5 rounded-full blur-3xl pointer-events-none"></div>
        <div className="absolute -bottom-10 -right-10 w-40 h-40 bg-cyber-cyan/5 rounded-full blur-3xl pointer-events-none"></div>

        {/* Central Auth Cyber Panel Container */}
        <div className="cyber-panel-pink p-8 bg-cyber-dark/85 backdrop-blur-xl relative crt-screen">
          
          {/* Header branding */}
          <div className="text-center space-y-4 mb-8 border-b border-cyber-gray pb-6">
            <div className="w-12 h-12 mx-auto border border-cyber-pink bg-cyber-pink/10 flex items-center justify-center clip-slanted-sm shadow-pink-glow">
              <UserPlus className="w-5 h-5 text-cyber-pink animate-pulse" />
            </div>
            <div>
              <h2 className="text-xl font-black text-white font-cyber tracking-tight uppercase">
                Secure Identity Provisioner
              </h2>
              <p className="text-xs font-tech text-cyber-cyan mt-1 tracking-widest">
                REGISTER SYSTEM NODE
              </p>
            </div>
          </div>

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
                Register Email Address
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
                  className="w-full bg-cyber-bg border border-cyber-gray focus:border-cyber-pink p-3 pl-10 text-sm text-white font-tech rounded-none outline-none transition duration-150"
                  placeholder="name@antigravity.ai"
                />
              </div>
            </div>

            {/* Password Field */}
            <div className="space-y-2">
              <label className="text-xs uppercase font-cyber font-semibold tracking-wider text-cyber-text block">
                Decryption Passphrase
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
                  className="w-full bg-cyber-bg border border-cyber-gray focus:border-cyber-pink p-3 pl-10 text-sm text-white font-tech rounded-none outline-none transition duration-150"
                  placeholder="•••••••••••• (Min 6 chars)"
                />
              </div>
            </div>

            {/* Confirm Password Field */}
            <div className="space-y-2">
              <label className="text-xs uppercase font-cyber font-semibold tracking-wider text-cyber-text block">
                Confirm Passphrase
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-cyber-text/50">
                  <Lock className="w-4 h-4" />
                </span>
                <input
                  type="password"
                  required
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="w-full bg-cyber-bg border border-cyber-gray focus:border-cyber-pink p-3 pl-10 text-sm text-white font-tech rounded-none outline-none transition duration-150"
                  placeholder="••••••••••••"
                />
              </div>
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-cyber-pink hover:bg-cyber-pink/95 text-white hover:scale-[1.01] active:scale-[0.99] font-cyber text-xs uppercase font-black tracking-widest clip-slanted shadow-pink-glow transition duration-150 cursor-pointer"
            >
              {loading ? 'Generating Node...' : 'Establish Secure Profile'}
            </button>

          </form>

          {/* Footer router trigger */}
          <div className="mt-6 pt-6 border-t border-cyber-gray text-center text-xs font-sans text-cyber-text">
            <span>Already have an active identity? </span>
            <Link to="/login" className="text-cyber-cyan hover:text-white font-cyber uppercase tracking-wider transition underline cursor-pointer">
              Decrypt Gateway
            </Link>
          </div>

        </div>

      </div>
    </div>
  );
}

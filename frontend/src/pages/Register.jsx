import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { User, Mail, Lock, Cpu, Eye, EyeOff, AlertCircle, CheckCircle } from 'lucide-react';
import { motion } from 'framer-motion';

const Register = () => {
  const { register } = useAuth();
  const navigate = useNavigate();

  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess(false);
    setSubmitting(true);

    try {
      await register(email, password, fullName);
      setSuccess(true);
      setTimeout(() => {
        navigate('/login');
      }, 1500);
    } catch (err) {
      setError(err);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center relative p-4 bg-neon-radial">
      {/* Background neon glows */}
      <div className="absolute top-1/4 left-1/4 w-72 h-72 bg-indigo-500/10 rounded-full blur-[100px]" />
      <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-purple-500/10 rounded-full blur-[100px]" />

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md p-8 rounded-3xl bg-slate-900/40 border border-white/5 backdrop-blur-xl shadow-neon-card relative z-10"
      >
        {/* Branding header */}
        <div className="flex flex-col items-center mb-8">
          <div className="w-12 h-12 rounded-2xl bg-indigo-600/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center mb-3 pulse-border-purple">
            <Cpu className="w-6 h-6" />
          </div>
          <h2 className="text-2xl font-bold font-outfit bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
            Create Account
          </h2>
          <p className="text-slate-500 text-xs mt-1 font-sans">
            AI Interview Intelligence Platform
          </p>
        </div>

        {error && (
          <div className="mb-6 px-4 py-3 rounded-2xl bg-red-500/10 border border-red-500/20 text-red-400 text-xs flex items-center gap-2 text-left">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {success && (
          <div className="mb-6 px-4 py-3 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs flex items-center gap-2 text-left">
            <CheckCircle className="w-4 h-4 shrink-0" />
            <span>Registration successful! Redirecting to login...</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="flex flex-col gap-4 text-left">
          {/* Full Name input */}
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-bold text-slate-400 font-outfit uppercase tracking-wider pl-1">
              Full Name
            </label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-500">
                <User className="w-4 h-4" />
              </span>
              <input
                type="text"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Jane Doe"
                className="w-full pl-10 pr-4 py-3 rounded-2xl bg-slate-950 border border-white/5 text-slate-100 placeholder-slate-600 text-sm focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/20 transition-all duration-300 outline-none"
              />
            </div>
          </div>

          {/* Email input field */}
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-bold text-slate-400 font-outfit uppercase tracking-wider pl-1">
              Email Address
            </label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-500">
                <Mail className="w-4 h-4" />
              </span>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="developer@aegis.ai"
                className="w-full pl-10 pr-4 py-3 rounded-2xl bg-slate-950 border border-white/5 text-slate-100 placeholder-slate-600 text-sm focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/20 transition-all duration-300 outline-none"
              />
            </div>
          </div>

          {/* Password input field */}
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-bold text-slate-400 font-outfit uppercase tracking-wider pl-1">
              Password
            </label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-500">
                <Lock className="w-4 h-4" />
              </span>
              <input
                type={showPassword ? 'text' : 'password'}
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Min. 6 characters"
                className="w-full pl-10 pr-10 py-3 rounded-2xl bg-slate-950 border border-white/5 text-slate-100 placeholder-slate-600 text-sm focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/20 transition-all duration-300 outline-none"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-500 hover:text-slate-300"
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          {/* Submit button */}
          <button
            type="submit"
            disabled={submitting || success}
            className="w-full mt-2 py-3 rounded-2xl font-outfit font-bold text-sm bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-indigo-500/30 flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {submitting ? 'Registering...' : 'Sign Up'}
          </button>
        </form>

        <p className="mt-8 text-center text-xs text-slate-500 font-sans">
          Already have an account?{' '}
          <Link
            to="/login"
            className="font-semibold text-indigo-400 hover:text-indigo-300 transition-all duration-200"
          >
            Sign in
          </Link>
        </p>
      </motion.div>
    </div>
  );
};

export default Register;

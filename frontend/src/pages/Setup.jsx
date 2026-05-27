import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { Code, Database, Globe, UserCheck, CheckCircle2, ArrowRight, Video } from 'lucide-react';
import { motion } from 'framer-motion';

const Setup = () => {
  const navigate = useNavigate();

  const [role, setRole] = useState('Software Engineer');
  const [difficulty, setDifficulty] = useState('Intermediate');
  const [submitting, setSubmitting] = useState(false);

  const roles = [
    {
      id: 'Software Engineer',
      title: 'Software Engineer',
      desc: 'Focuses on Core DSA, DBMS, OS algorithms, and Python backend mechanics.',
      icon: Code,
      color: 'indigo'
    },
    {
      id: 'Data Scientist',
      title: 'Data Scientist',
      desc: 'Focuses on Machine Learning foundations, Python data modules, and mathematical theory.',
      icon: Database,
      color: 'purple'
    },
    {
      id: 'Frontend Developer',
      title: 'Frontend Developer',
      desc: 'Focuses on UI engineering, JS contexts, CSS layouts, and basic systems.',
      icon: Globe,
      color: 'cyan'
    },
    {
      id: 'HR Interview',
      title: 'HR & Behavioral',
      desc: 'Focuses on team alignments, leadership scenarios, and organizational fit.',
      icon: UserCheck,
      color: 'emerald'
    }
  ];

  const difficulties = ['Beginner', 'Intermediate', 'Advanced'];

  const handleStart = async () => {
    setSubmitting(true);
    try {
      const response = await api.post('/interview/start', {
        role,
        difficulty
      });
      // Navigate to interview room passing the questions and role in state
      navigate(`/interview/${response.data.session_id}`, {
        state: {
          questions: response.data.questions,
          role: response.data.role,
          difficulty: response.data.difficulty
        }
      });
    } catch (err) {
      console.error("Error starting mock session:", err);
      alert("Error starting mock session. Make sure backend is running and seeded.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="flex flex-col gap-6 text-left max-w-4xl mx-auto">
      <div>
        <h1 className="text-3xl font-bold font-outfit text-white tracking-tight">Configure Interview Session</h1>
        <p className="text-slate-400 text-sm mt-1">Calibrate your mock profile. We will compile 3 randomized target questions.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Role select columns */}
        <div className="md:col-span-2 flex flex-col gap-3">
          <span className="text-xs font-bold text-slate-500 uppercase tracking-widest pl-1 font-outfit">
            1. Target Job Role
          </span>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {roles.map((item) => (
              <div
                key={item.id}
                onClick={() => setRole(item.id)}
                className={`p-5 rounded-2xl border cursor-pointer flex flex-col justify-between h-40 transition-all duration-300 ${
                  role === item.id
                    ? 'bg-indigo-600/10 border-indigo-500/30 shadow-neon-purple text-slate-100'
                    : 'bg-slate-900/40 border-white/5 text-slate-400 hover:bg-slate-900/60 hover:border-white/10'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className={`p-2 rounded-xl ${
                    role === item.id ? 'bg-indigo-500/20 text-indigo-400' : 'bg-slate-950 text-slate-500'
                  }`}>
                    <item.icon className="w-5 h-5" />
                  </div>
                  {role === item.id && <CheckCircle2 className="w-5 h-5 text-indigo-400 animate-bounce" />}
                </div>
                <div className="flex flex-col">
                  <span className="text-sm font-bold font-outfit text-slate-200">{item.title}</span>
                  <span className="text-[10px] mt-1 text-slate-500 leading-normal font-sans">{item.desc}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Difficulty configuration column */}
        <div className="flex flex-col gap-6">
          {/* Difficulty selection */}
          <div className="flex flex-col gap-3">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-widest pl-1 font-outfit">
              2. Complexity Grade
            </span>
            <div className="flex flex-col gap-2">
              {difficulties.map((level) => (
                <div
                  key={level}
                  onClick={() => setDifficulty(level)}
                  className={`px-5 py-4 rounded-2xl border cursor-pointer flex items-center justify-between transition-all duration-300 font-outfit ${
                    difficulty === level
                      ? 'bg-cyan-600/10 border-cyan-500/30 shadow-neon-cyan text-cyan-400 font-semibold'
                      : 'bg-slate-900/40 border-white/5 text-slate-400 hover:bg-slate-900/60 hover:border-white/10'
                  }`}
                >
                  <span className="text-sm">{level}</span>
                  {difficulty === level && <CheckCircle2 className="w-4 h-4 text-cyan-400" />}
                </div>
              ))}
            </div>
          </div>

          {/* Environmental calibration review */}
          <div className="p-4 rounded-2xl bg-slate-900/30 border border-white/5 flex flex-col gap-2">
            <div className="flex items-center gap-2 text-xs font-bold text-indigo-400 uppercase tracking-wider font-outfit">
              <Video className="w-4 h-4 animate-pulse" />
              <span>Camera Calibration</span>
            </div>
            <p className="text-[10px] text-slate-500 leading-relaxed font-sans">
              To evaluate gaze and head pose, please ensure you allow browser webcam access. Keep a neutral center position relative to the camera lens.
            </p>
          </div>

          {/* Action proceed trigger */}
          <button
            onClick={handleStart}
            disabled={submitting}
            className="w-full py-4 rounded-2xl bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white font-semibold font-outfit text-sm transition-all duration-300 flex items-center justify-center gap-2 disabled:opacity-50"
          >
            <span>{submitting ? 'Preparing Room...' : 'Enter AI Interview Room'}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default Setup;

import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import { Award, ArrowLeft, Printer, CheckCircle, HelpCircle, User, MessageSquare, AlertCircle } from 'lucide-react';
import { motion } from 'framer-motion';

const PerformanceReport = () => {
  const { sessionId } = useParams();
  const navigate = useNavigate();

  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState(0);

  useEffect(() => {
    const fetchReport = async () => {
      try {
        const response = await api.get(`/interview/${sessionId}`);
        setSession(response.data);
      } catch (err) {
        console.error("Error fetching mock report:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchReport();
  }, [sessionId]);

  if (loading) {
    return (
      <div className="min-h-[70vh] flex items-center justify-center">
        <div className="w-8 h-8 rounded-full border-2 border-indigo-500/20 border-t-indigo-500 animate-spin" />
      </div>
    );
  }

  if (!session) {
    return (
      <div className="p-8 rounded-3xl bg-slate-900/40 border border-white/5 text-center mt-12 max-w-lg mx-auto">
        <h2 className="text-lg font-bold text-white">Report not found.</h2>
        <button onClick={() => navigate('/')} className="mt-4 px-4 py-2 bg-indigo-600 rounded-xl text-xs text-white">
          Return to Dashboard
        </button>
      </div>
    );
  }

  // Calculate averaged sub-dimension metrics for visual circular dials
  const responses = session.responses || [];
  const avgTech = responses.length > 0 ? Math.round(responses.reduce((sum, r) => sum + r.technical_score, 0) / responses.length) : 0;
  const avgComm = responses.length > 0 ? Math.round(responses.reduce((sum, r) => sum + r.communication_score, 0) / responses.length) : 0;
  const avgConf = responses.length > 0 ? Math.round(responses.reduce((sum, r) => sum + r.confidence_score, 0) / responses.length) : 0;

  // Print trigger
  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="flex flex-col gap-6 text-left max-w-5xl mx-auto pb-16 print:p-0">
      {/* Navigation action rows */}
      <div className="flex items-center justify-between border-b border-white/5 pb-4 print:hidden">
        <button
          onClick={() => navigate('/')}
          className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl border border-white/5 bg-slate-950/40 text-slate-400 hover:text-slate-200 text-xs font-semibold transition-all duration-300"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Dashboard</span>
        </button>

        <button
          onClick={handlePrint}
          className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl border border-indigo-500/20 bg-indigo-600/10 text-indigo-400 hover:bg-indigo-600 hover:text-white text-xs font-semibold transition-all duration-300 animate-pulse"
        >
          <Printer className="w-4 h-4" />
          <span>Print Report Card</span>
        </button>
      </div>

      {/* Main summary card */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Left column: Circular scoring gauges */}
        <div className="md:col-span-1 p-6 rounded-3xl bg-slate-900/40 border border-white/5 backdrop-blur-xl shadow-neon-card flex flex-col gap-6 text-center justify-between">
          <div className="flex flex-col items-center">
            <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center mb-3">
              <Award className="w-6 h-6" />
            </div>
            <h2 className="text-base font-bold font-outfit text-white">Overall Performance</h2>
            <span className="text-[10px] uppercase font-bold text-slate-500 mt-1">{session.role} • {session.difficulty}</span>
          </div>

          {/* Large total score dial */}
          <div className="relative w-36 h-36 mx-auto flex items-center justify-center">
            <svg className="w-full h-full transform -rotate-90">
              <circle
                cx="72"
                cy="72"
                r="64"
                stroke="rgba(255,255,255,0.02)"
                strokeWidth="10"
                fill="transparent"
              />
              <circle
                cx="72"
                cy="72"
                r="64"
                stroke="#10b981"
                strokeWidth="10"
                fill="transparent"
                strokeDasharray={2 * Math.PI * 64}
                strokeDashoffset={2 * Math.PI * 64 * (1 - session.overall_score / 100)}
                strokeLinecap="round"
                className="transition-all duration-1000 ease-out"
              />
            </svg>
            <div className="absolute flex flex-col items-center">
              <span className="text-3xl font-extrabold font-outfit text-white">{session.overall_score}%</span>
              <span className="text-[8px] uppercase tracking-widest text-slate-500 font-bold mt-0.5">Rating</span>
            </div>
          </div>

          {/* Individual sub dials */}
          <div className="grid grid-cols-3 gap-1 border-t border-white/5 pt-4">
            <div className="flex flex-col text-center">
              <span className="text-[8px] text-slate-500 font-bold uppercase">Technical</span>
              <span className="text-sm font-bold text-indigo-400 mt-1">{avgTech}%</span>
            </div>
            <div className="flex flex-col text-center border-x border-white/5">
              <span className="text-[8px] text-slate-500 font-bold uppercase">Speech</span>
              <span className="text-sm font-bold text-cyan-400 mt-1">{avgComm}%</span>
            </div>
            <div className="flex flex-col text-center">
              <span className="text-[8px] text-slate-500 font-bold uppercase">Confidence</span>
              <span className="text-sm font-bold text-pink-400 mt-1">{avgConf}%</span>
            </div>
          </div>
        </div>

        {/* Right columns: Structured summary critique */}
        <div className="md:col-span-2 p-6 rounded-3xl bg-slate-900/40 border border-white/5 backdrop-blur-xl shadow-neon-card text-left flex flex-col justify-between">
          <div className="flex flex-col gap-2">
            <h2 className="text-base font-bold font-outfit text-white">Aggregated AI Assessment Review</h2>
            <p className="text-slate-500 text-xs font-sans">Compiled across {responses.length} answered sections.</p>
          </div>

          <div className="text-xs text-slate-400 leading-relaxed space-y-4 my-6 prose max-w-none">
            {session.overall_feedback.split('\n\n').map((para, i) => {
              if (para.startsWith('###')) {
                return <h3 key={i} className="text-xs font-bold text-slate-200 mt-4 mb-2">{para.replace('###', '')}</h3>;
              }
              if (para.startsWith('-')) {
                return (
                  <ul key={i} className="list-disc pl-4 space-y-1">
                    {para.split('\n').map((item, idx) => {
                      const cleanItem = item.replace('-', '').trim();
                      const isStrength = cleanItem.includes('Strength:');
                      return (
                        <li key={idx} className={isStrength ? 'text-emerald-400' : 'text-rose-400/90'}>
                          {cleanItem}
                        </li>
                      );
                    })}
                  </ul>
                );
              }
              return <p key={i}>{para}</p>;
            })}
          </div>

          <div className="p-3 rounded-2xl bg-indigo-500/5 border border-indigo-500/10 text-[10px] text-slate-500 font-sans leading-relaxed">
            *Performance rates are calculated using local CPU semantic token similarity and speech signal processing ratios. Standard parameters apply.
          </div>
        </div>
      </div>

      {/* Tabs to review individual questions */}
      {responses.length > 0 && (
        <div className="flex flex-col gap-4 mt-6">
          <h2 className="text-lg font-bold font-outfit text-white">Section Question Breakdown</h2>
          
          {/* Tabs selector */}
          <div className="flex gap-2 border-b border-white/5 pb-2">
            {responses.map((resp, i) => (
              <button
                key={resp.id}
                onClick={() => setActiveTab(i)}
                className={`px-4 py-2 rounded-xl text-xs font-semibold font-outfit transition-all duration-300 border ${
                  activeTab === i
                    ? 'bg-indigo-600/10 border-indigo-500/25 text-indigo-400'
                    : 'bg-transparent border-transparent text-slate-500 hover:text-slate-300'
                }`}
              >
                Question {i + 1}
              </button>
            ))}
          </div>

          {/* Active response card */}
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-6 rounded-3xl bg-slate-900/40 border border-white/5 shadow-neon-card flex flex-col gap-6"
          >
            {/* Header info */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center border-b border-white/5 pb-4 gap-2">
              <div className="flex items-center gap-2">
                <HelpCircle className="w-4 h-4 text-indigo-400" />
                <span className="text-xs font-bold font-outfit text-slate-200">
                  Question prompt details
                </span>
              </div>
              
              <div className="flex gap-2">
                <span className="text-[9px] bg-slate-950 px-2 py-0.5 rounded border border-white/5 text-indigo-400 font-mono">
                  Similarity Match: {responses[activeTab].similarity_score}%
                </span>
              </div>
            </div>

            {/* Prompt text */}
            <p className="text-sm font-semibold font-outfit text-slate-100">
              {responses[activeTab].question?.question_text}
            </p>

            {/* Ideal Answer vs user spoken answer side by side */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 rounded-2xl bg-slate-950 border border-white/5 text-left flex flex-col gap-2">
                <span className="text-[9px] uppercase font-bold text-slate-500 tracking-wider">Candidate spoken Transcript:</span>
                <p className="text-xs text-slate-300 italic leading-relaxed">
                  "{responses[activeTab].transcript || "No speech detected."}"
                </p>
              </div>

              <div className="p-4 rounded-2xl bg-slate-950 border border-cyan-500/10 text-left flex flex-col gap-2">
                <span className="text-[9px] uppercase font-bold text-cyan-400 tracking-wider">Ideal Reference Answer:</span>
                <p className="text-xs text-slate-300 leading-relaxed">
                  {responses[activeTab].question?.ideal_answer}
                </p>
              </div>
            </div>

            {/* Corrective feedback markdown */}
            <div className="p-5 rounded-2xl bg-slate-950/40 border border-white/5 text-left">
              <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest font-outfit">Detailed AI evaluation review</span>
              <div className="text-xs text-slate-400 space-y-3 leading-relaxed mt-3 prose max-w-none border-t border-white/5 pt-4">
                {responses[activeTab].feedback.split('\n\n').map((para, i) => {
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
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
};

export default PerformanceReport;

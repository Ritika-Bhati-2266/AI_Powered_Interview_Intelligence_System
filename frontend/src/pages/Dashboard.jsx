import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, BarChart, Bar, Legend } from 'recharts';
import { Video, Award, Brain, MessageSquare, Compass, Eye, Calendar, ArrowUpRight } from 'lucide-react';
import { motion } from 'framer-motion';

const Dashboard = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const statsRes = await api.get('/dashboard/stats');
        const historyRes = await api.get('/dashboard/history');
        setStats(statsRes.data);
        setHistory(historyRes.data);
      } catch (err) {
        console.error("Error fetching dashboard statistics:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-[70vh] flex items-center justify-center">
        <div className="w-8 h-8 rounded-full border-2 border-indigo-500/20 border-t-indigo-500 animate-spin" />
      </div>
    );
  }

  const cardVariants = {
    hidden: { opacity: 0, y: 10 },
    visible: { opacity: 1, y: 0 }
  };

  return (
    <div className="flex flex-col gap-6 text-left">
      {/* Upper header action banner */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold font-outfit text-white tracking-tight">Dashboard Overview</h1>
          <p className="text-slate-400 text-sm mt-1">Track your speaking speed, facial attention, and technical coding scores.</p>
        </div>
        <button
          onClick={() => navigate('/setup')}
          className="flex items-center gap-2 px-5 py-3 rounded-2xl bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white text-sm font-semibold font-outfit shadow-neon-purple hover:shadow-lg transition-all duration-300"
        >
          <Video className="w-4 h-4" />
          <span>New Mock Session</span>
        </button>
      </div>

      {stats && stats.total_interviews > 0 ? (
        <>
          {/* KPI Analytics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Total sessions */}
            <motion.div
              variants={cardVariants}
              initial="hidden"
              animate="visible"
              transition={{ duration: 0.3 }}
              className="p-5 rounded-2xl bg-slate-900/40 border border-white/5 shadow-neon-card flex items-center justify-between"
            >
              <div className="flex flex-col">
                <span className="text-slate-500 text-[10px] uppercase font-bold tracking-wider">Completed Sessions</span>
                <span className="text-2xl font-bold font-outfit text-white mt-1">{stats.total_interviews}</span>
              </div>
              <div className="w-10 h-10 rounded-xl bg-indigo-600/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center">
                <Video className="w-5 h-5" />
              </div>
            </motion.div>

            {/* Average rating */}
            <motion.div
              variants={cardVariants}
              initial="hidden"
              animate="visible"
              transition={{ duration: 0.3, delay: 0.05 }}
              className="p-5 rounded-2xl bg-slate-900/40 border border-white/5 shadow-neon-card flex items-center justify-between"
            >
              <div className="flex flex-col">
                <span className="text-slate-500 text-[10px] uppercase font-bold tracking-wider">Average Rating</span>
                <span className="text-2xl font-bold font-outfit text-emerald-400 mt-1">{stats.average_overall_score}%</span>
              </div>
              <div className="w-10 h-10 rounded-xl bg-emerald-600/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center">
                <Award className="w-5 h-5" />
              </div>
            </motion.div>

            {/* Top Strengths */}
            <motion.div
              variants={cardVariants}
              initial="hidden"
              animate="visible"
              transition={{ duration: 0.3, delay: 0.1 }}
              className="p-5 rounded-2xl bg-slate-900/40 border border-white/5 shadow-neon-card flex items-center justify-between"
            >
              <div className="flex flex-col max-w-[70%]">
                <span className="text-slate-500 text-[10px] uppercase font-bold tracking-wider">Focus Areas</span>
                <span className="text-sm font-semibold text-cyan-400 mt-2 truncate font-outfit">
                  {stats.strong_topics[0]}
                </span>
              </div>
              <div className="w-10 h-10 rounded-xl bg-cyan-600/10 border border-cyan-500/20 text-cyan-400 flex items-center justify-center">
                <Brain className="w-5 h-5 animate-pulse" />
              </div>
            </motion.div>

            {/* Weak topics */}
            <motion.div
              variants={cardVariants}
              initial="hidden"
              animate="visible"
              transition={{ duration: 0.3, delay: 0.15 }}
              className="p-5 rounded-2xl bg-slate-900/40 border border-white/5 shadow-neon-card flex items-center justify-between"
            >
              <div className="flex flex-col max-w-[70%]">
                <span className="text-slate-500 text-[10px] uppercase font-bold tracking-wider">Critical Reviews</span>
                <span className="text-sm font-semibold text-rose-400 mt-2 truncate font-outfit">
                  {stats.weak_topics[0]}
                </span>
              </div>
              <div className="w-10 h-10 rounded-xl bg-rose-600/10 border border-rose-500/20 text-rose-400 flex items-center justify-center">
                <MessageSquare className="w-5 h-5" />
              </div>
            </motion.div>
          </div>

          {/* Analytical Charts and Visualizations */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Score timeline graph */}
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4 }}
              className="p-5 rounded-3xl bg-slate-900/40 border border-white/5 backdrop-blur-xl shadow-neon-card"
            >
              <h2 className="text-base font-bold font-outfit text-white mb-4">Overall Score Trends</h2>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={stats.score_trends}>
                    <defs>
                      <linearGradient id="scoreGlow" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <XAxis dataKey="date" stroke="#64748b" fontSize={10} tickLine={false} />
                    <YAxis domain={[0, 100]} stroke="#64748b" fontSize={10} tickLine={false} />
                    <Tooltip
                      contentStyle={{ background: '#0f172a', borderColor: '#1f2937', borderRadius: '12px' }}
                      labelStyle={{ color: '#94a3b8', fontWeight: 'bold' }}
                    />
                    <Area type="monotone" dataKey="score" stroke="#6366f1" strokeWidth={2} fillOpacity={1} fill="url(#scoreGlow)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </motion.div>

            {/* Categorical Dimension Breakdown */}
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: 0.1 }}
              className="p-5 rounded-3xl bg-slate-900/40 border border-white/5 backdrop-blur-xl shadow-neon-card"
            >
              <h2 className="text-base font-bold font-outfit text-white mb-4">Dimension breakdown by Category</h2>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={stats.category_performance}>
                    <XAxis dataKey="category" stroke="#64748b" fontSize={10} tickLine={false} />
                    <YAxis domain={[0, 100]} stroke="#64748b" fontSize={10} tickLine={false} />
                    <Tooltip
                      contentStyle={{ background: '#0f172a', borderColor: '#1f2937', borderRadius: '12px' }}
                    />
                    <Legend iconType="circle" wrapperStyle={{ fontSize: 10 }} />
                    <Bar dataKey="technical" fill="#a855f7" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="communication" fill="#06b6d4" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="confidence" fill="#f43f5e" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </motion.div>
          </div>

          {/* Historical Logs List */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
            className="rounded-3xl bg-slate-900/40 border border-white/5 backdrop-blur-xl shadow-neon-card overflow-hidden"
          >
            <div className="p-5 border-b border-white/5 flex items-center justify-between">
              <h2 className="text-base font-bold font-outfit text-white">Interview History logs</h2>
              <span className="text-[10px] bg-indigo-500/10 text-indigo-400 px-2.5 py-1 rounded-full border border-indigo-500/20 font-bold uppercase">
                Mock Database
              </span>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-white/5 bg-slate-950/20">
                    <th className="py-4 px-6 text-[10px] font-bold text-slate-500 uppercase tracking-widest pl-6">Mock Role</th>
                    <th className="py-4 px-6 text-[10px] font-bold text-slate-500 uppercase tracking-widest">Difficulty</th>
                    <th className="py-4 px-6 text-[10px] font-bold text-slate-500 uppercase tracking-widest">Date Conducted</th>
                    <th className="py-4 px-6 text-[10px] font-bold text-slate-500 uppercase tracking-widest">Rating Score</th>
                    <th className="py-4 px-6 text-[10px] font-bold text-slate-500 uppercase tracking-widest pr-6">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((session) => (
                    <tr
                      key={session.id}
                      className="border-b border-white/5 hover:bg-slate-900/25 transition-all duration-200"
                    >
                      <td className="py-4 px-6 font-outfit text-sm font-semibold text-slate-200 pl-6">
                        {session.role}
                      </td>
                      <td className="py-4 px-6">
                        <span className={`text-[10px] px-2.5 py-1 rounded-full border font-bold uppercase tracking-wider ${
                          session.difficulty === 'Advanced'
                            ? 'bg-rose-500/10 border-rose-500/20 text-rose-400'
                            : session.difficulty === 'Intermediate'
                            ? 'bg-amber-500/10 border-amber-500/20 text-amber-400'
                            : 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400'
                        }`}>
                          {session.difficulty}
                        </span>
                      </td>
                      <td className="py-4 px-6 text-xs text-slate-400 flex items-center gap-1.5 mt-2">
                        <Calendar className="w-3.5 h-3.5 text-slate-500" />
                        <span>{new Date(session.created_at).toLocaleDateString()}</span>
                      </td>
                      <td className="py-4 px-6 font-outfit text-sm font-semibold text-emerald-400">
                        {session.overall_score > 0 ? `${session.overall_score}%` : 'Pending'}
                      </td>
                      <td className="py-4 px-6 pr-6">
                        <button
                          onClick={() => navigate(`/report/${session.id}`)}
                          className="flex items-center gap-1 px-3 py-1.5 rounded-lg border border-white/5 hover:border-indigo-500/30 bg-slate-950/40 text-slate-400 hover:text-indigo-400 text-xs font-semibold transition-all duration-300"
                        >
                          <Eye className="w-3.5 h-3.5" />
                          <span>View Report</span>
                          <ArrowUpRight className="w-3 h-3" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </motion.div>
        </>
      ) : (
        /* Empty welcome screen */
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-12 rounded-3xl bg-slate-900/40 border border-white/5 backdrop-blur-xl shadow-neon-card text-center flex flex-col items-center gap-4 max-w-2xl mx-auto mt-12"
        >
          <div className="w-16 h-16 rounded-2xl bg-indigo-600/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center pulse-border-purple">
            <Compass className="w-8 h-8" />
          </div>
          <h2 className="text-xl font-bold font-outfit text-white">Begin your AI Practice Sessions</h2>
          <p className="text-sm text-slate-500 leading-relaxed font-sans max-w-md">
            No mock runs have been initiated yet. Select your industry roles, choose difficulty thresholds, calibrate your webcam, and receive real-time, comprehensive speech evaluations.
          </p>
          <button
            onClick={() => navigate('/setup')}
            className="flex items-center gap-2 mt-2 px-6 py-3 rounded-2xl bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white text-sm font-semibold font-outfit transition-all duration-300"
          >
            <Video className="w-4 h-4" />
            <span>Launch Mock Interview Setup</span>
          </button>
        </motion.div>
      )}
    </div>
  );
};

export default Dashboard;

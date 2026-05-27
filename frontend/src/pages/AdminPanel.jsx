import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { PlusCircle, Trash2, HelpCircle, Shield, Award, Settings, Search, CheckCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const AdminPanel = () => {
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  
  // Form states
  const [role, setRole] = useState('Software Engineer');
  const [category, setCategory] = useState('DSA');
  const [difficulty, setDifficulty] = useState('Intermediate');
  const [questionText, setQuestionText] = useState('');
  const [idealAnswer, setIdealAnswer] = useState('');
  const [keywords, setKeywords] = useState('');

  const [formError, setFormError] = useState('');
  const [formSuccess, setFormSuccess] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const fetchQuestions = async () => {
    try {
      const response = await api.get('/question/');
      setQuestions(response.data);
    } catch (err) {
      console.error("Error fetching questions list:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQuestions();
  }, []);

  const handleAddQuestion = async (e) => {
    e.preventDefault();
    setFormError('');
    setFormSuccess(false);
    setSubmitting(true);

    if (!questionText || !idealAnswer) {
      setFormError("Question text and ideal answer are required fields.");
      setSubmitting(false);
      return;
    }

    try {
      await api.post('/question/', {
        role,
        category,
        difficulty,
        question_text: questionText,
        ideal_answer: idealAnswer,
        keywords: keywords
      });

      setFormSuccess(true);
      setQuestionText('');
      setIdealAnswer('');
      setKeywords('');
      
      // Reload list
      fetchQuestions();
      
      setTimeout(() => {
        setFormSuccess(false);
      }, 2000);
    } catch (err) {
      console.error("Error adding question:", err);
      setFormError(err.response?.data?.detail || "Error adding question. Check format.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (qId) => {
    if (!window.confirm("Are you sure you want to delete this question?")) return;
    try {
      await api.delete(`/question/${qId}`);
      setQuestions((prev) => prev.filter((q) => q.id !== qId));
    } catch (err) {
      console.error("Error deleting question:", err);
      alert("Error deleting question.");
    }
  };

  const filteredQuestions = questions.filter(
    (q) =>
      q.question_text.toLowerCase().includes(search.toLowerCase()) ||
      q.category.toLowerCase().includes(search.toLowerCase()) ||
      q.role.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="flex flex-col gap-6 text-left max-w-6xl mx-auto pb-12">
      {/* Header section */}
      <div>
        <h1 className="text-3xl font-bold font-outfit text-white tracking-tight flex items-center gap-2">
          <Shield className="w-8 h-8 text-cyan-400" />
          <span>System Administration Panel</span>
        </h1>
        <p className="text-slate-400 text-sm mt-1">Manage mock question categories, default banks, and review live DB nodes.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* 1. Left column: Add question form */}
        <div className="lg:col-span-4 p-6 rounded-3xl bg-slate-900/40 border border-white/5 backdrop-blur-xl shadow-neon-card">
          <h2 className="text-base font-bold font-outfit text-white mb-4 flex items-center gap-1.5">
            <PlusCircle className="w-5 h-5 text-indigo-400" />
            <span>Add Mock Question</span>
          </h2>

          {formError && (
            <div className="mb-4 p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-[10px] flex items-center gap-1.5 font-sans">
              <span>{formError}</span>
            </div>
          )}

          {formSuccess && (
            <div className="mb-4 p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[10px] flex items-center gap-1.5 font-sans">
              <CheckCircle className="w-4 h-4" />
              <span>Question added successfully!</span>
            </div>
          )}

          <form onSubmit={handleAddQuestion} className="flex flex-col gap-4 text-left">
            {/* Role select */}
            <div className="flex flex-col gap-1">
              <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider font-outfit">Job Role</label>
              <select
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="w-full px-3 py-2.5 rounded-xl bg-slate-950 border border-white/5 text-slate-300 text-xs focus:outline-none focus:border-indigo-500/30 font-sans"
              >
                <option value="Software Engineer">Software Engineer</option>
                <option value="Data Scientist">Data Scientist</option>
                <option value="Frontend Developer">Frontend Developer</option>
                <option value="HR Interview">HR Interview</option>
              </select>
            </div>

            {/* Category select */}
            <div className="flex flex-col gap-1">
              <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider font-outfit">Category</label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full px-3 py-2.5 rounded-xl bg-slate-950 border border-white/5 text-slate-300 text-xs focus:outline-none focus:border-indigo-500/30 font-sans"
              >
                <option value="DSA">DSA</option>
                <option value="Python">Python</option>
                <option value="DBMS">DBMS</option>
                <option value="OS">OS</option>
                <option value="Machine Learning">Machine Learning</option>
                <option value="HR">HR & Behavioral</option>
              </select>
            </div>

            {/* Difficulty select */}
            <div className="flex flex-col gap-1">
              <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider font-outfit">Difficulty</label>
              <select
                value={difficulty}
                onChange={(e) => setDifficulty(e.target.value)}
                className="w-full px-3 py-2.5 rounded-xl bg-slate-950 border border-white/5 text-slate-300 text-xs focus:outline-none focus:border-indigo-500/30 font-sans"
              >
                <option value="Beginner">Beginner</option>
                <option value="Intermediate">Intermediate</option>
                <option value="Advanced">Advanced</option>
              </select>
            </div>

            {/* Question Text */}
            <div className="flex flex-col gap-1">
              <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider font-outfit">Question prompt</label>
              <textarea
                rows={3}
                required
                value={questionText}
                onChange={(e) => setQuestionText(e.target.value)}
                placeholder="Explain the differences between processes and threads..."
                className="w-full px-3 py-2.5 rounded-xl bg-slate-950 border border-white/5 text-slate-200 text-xs focus:outline-none focus:border-indigo-500/30 font-sans resize-none"
              />
            </div>

            {/* Ideal Answer */}
            <div className="flex flex-col gap-1">
              <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider font-outfit">Ideal Model Answer</label>
              <textarea
                rows={4}
                required
                value={idealAnswer}
                onChange={(e) => setIdealAnswer(e.target.value)}
                placeholder="Processes have separate memory domains. Threads share memory space of their parent process..."
                className="w-full px-3 py-2.5 rounded-xl bg-slate-950 border border-white/5 text-slate-200 text-xs focus:outline-none focus:border-indigo-500/30 font-sans resize-none"
              />
            </div>

            {/* Keywords */}
            <div className="flex flex-col gap-1">
              <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider font-outfit">Semantic Keywords</label>
              <input
                type="text"
                value={keywords}
                onChange={(e) => setKeywords(e.target.value)}
                placeholder="shared memory, PCB, stack, virtual address (comma separated)"
                className="w-full px-3 py-2.5 rounded-xl bg-slate-950 border border-white/5 text-slate-200 text-xs focus:outline-none focus:border-indigo-500/30 font-sans"
              />
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={submitting}
              className="w-full mt-2 py-3 rounded-xl bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white text-xs font-semibold font-outfit transition-all duration-300 disabled:opacity-50"
            >
              {submitting ? 'Seeding Database...' : 'Save to Question Bank'}
            </button>
          </form>
        </div>

        {/* 2. Right column: Question bank listing */}
        <div className="lg:col-span-8 flex flex-col gap-4">
          <div className="rounded-3xl bg-slate-900/40 border border-white/5 backdrop-blur-xl shadow-neon-card overflow-hidden">
            {/* Table Search bar */}
            <div className="p-4 border-b border-white/5 flex flex-col sm:flex-row items-center justify-between gap-4">
              <h2 className="text-base font-bold font-outfit text-white">Active Question Bank ({questions.length})</h2>
              
              <div className="relative w-full sm:w-64">
                <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-500">
                  <Search className="w-3.5 h-3.5" />
                </span>
                <input
                  type="text"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Filter category or roles..."
                  className="w-full pl-9 pr-4 py-2 rounded-xl bg-slate-950 border border-white/5 text-slate-200 placeholder-slate-600 text-xs focus:outline-none focus:border-cyan-500/30 transition-all duration-300"
                />
              </div>
            </div>

            {/* Table grid */}
            {loading ? (
              <div className="py-20 flex items-center justify-center">
                <div className="w-6 h-6 rounded-full border-2 border-indigo-500/20 border-t-indigo-500 animate-spin" />
              </div>
            ) : filteredQuestions.length > 0 ? (
              <div className="overflow-x-auto max-h-[600px] overflow-y-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="border-b border-white/5 bg-slate-950/20">
                      <th className="py-3 px-5 text-[9px] font-bold text-slate-500 uppercase tracking-widest pl-5">Question prompt</th>
                      <th className="py-3 px-5 text-[9px] font-bold text-slate-500 uppercase tracking-widest">Role</th>
                      <th className="py-3 px-5 text-[9px] font-bold text-slate-500 uppercase tracking-widest">Category</th>
                      <th className="py-3 px-5 text-[9px] font-bold text-slate-500 uppercase tracking-widest">Diff.</th>
                      <th className="py-3 px-5 text-[9px] font-bold text-slate-500 uppercase tracking-widest pr-5">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredQuestions.map((q) => (
                      <tr
                        key={q.id}
                        className="border-b border-white/5 hover:bg-slate-900/25 transition-all duration-200"
                      >
                        <td className="py-3.5 px-5 text-xs text-slate-300 max-w-sm pl-5 truncate font-sans">
                          {q.question_text}
                        </td>
                        <td className="py-3.5 px-5 font-outfit text-xs font-semibold text-slate-400">
                          {q.role}
                        </td>
                        <td className="py-3.5 px-5">
                          <span className="text-[9px] bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 px-2 py-0.5 rounded font-bold uppercase font-outfit">
                            {q.category}
                          </span>
                        </td>
                        <td className="py-3.5 px-5">
                          <span className={`text-[9px] font-bold uppercase ${
                            q.difficulty === 'Advanced'
                              ? 'text-rose-400'
                              : q.difficulty === 'Intermediate'
                              ? 'text-amber-400'
                              : 'text-emerald-400'
                          }`}>
                            {q.difficulty}
                          </span>
                        </td>
                        <td className="py-3.5 px-5 pr-5">
                          <button
                            onClick={() => handleDelete(q.id)}
                            className="p-1.5 rounded-lg border border-white/5 hover:border-red-500/30 hover:bg-red-500/10 text-slate-500 hover:text-red-400 transition-all duration-300"
                            title="Delete question"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="py-20 text-center text-slate-500 text-xs font-sans">
                No matching questions found in DB.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminPanel;

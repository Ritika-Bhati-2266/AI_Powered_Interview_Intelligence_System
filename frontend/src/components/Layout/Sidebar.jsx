import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { LayoutDashboard, Video, Settings, FolderHeart, History, Info } from 'lucide-react';

const Sidebar = () => {
  const { user } = useAuth();

  const menuItems = [
    {
      path: '/',
      name: 'Dashboard',
      icon: LayoutDashboard,
    },
    {
      path: '/setup',
      name: 'New Mock Run',
      icon: Video,
    },
  ];

  return (
    <aside className="w-64 border-r border-white/5 bg-slate-950/45 backdrop-blur-xl h-[calc(100vh-4rem)] flex flex-col justify-between p-4 sticky top-16">
      {/* Upper Navigation section */}
      <div className="flex flex-col gap-2">
        <span className="text-[10px] uppercase font-bold text-slate-500 tracking-widest pl-2 mb-2">
          Mock Intelligence
        </span>
        {menuItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-xl border transition-all duration-300 font-outfit ${
                isActive
                  ? 'bg-indigo-600/10 border-indigo-500/20 text-indigo-400 text-shadow-purple font-medium'
                  : 'bg-transparent border-transparent text-slate-400 hover:bg-slate-900/60 hover:text-slate-200'
              }`
            }
          >
            <item.icon className="w-5 h-5" />
            <span className="text-sm">{item.name}</span>
          </NavLink>
        ))}

        {/* Admin panel conditional navigation */}
        {user && user.role === 'admin' && (
          <>
            <span className="text-[10px] uppercase font-bold text-slate-500 tracking-widest pl-2 mt-6 mb-2">
              System Administration
            </span>
            <NavLink
              to="/admin"
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-xl border transition-all duration-300 font-outfit ${
                  isActive
                    ? 'bg-cyan-600/10 border-cyan-500/20 text-cyan-400 font-medium'
                    : 'bg-transparent border-transparent text-slate-400 hover:bg-slate-900/60 hover:text-slate-200'
                }`
              }
            >
              <Settings className="w-5 h-5" />
              <span className="text-sm">Admin Panel</span>
            </NavLink>
          </>
        )}
      </div>

      {/* Footer Info tag */}
      <div className="p-3 rounded-2xl bg-slate-900/40 border border-white/5 flex flex-col gap-1.5 text-left">
        <div className="flex items-center gap-1.5 text-indigo-400 text-xs font-semibold">
          <Info className="w-3.5 h-3.5" />
          <span>Local Engine Status</span>
        </div>
        <p className="text-[10px] text-slate-500 leading-relaxed font-sans">
          FastAPI on port 8000. All data, audio waveforms, Whisper models and NLP inferences reside locally on your CPU.
        </p>
      </div>
    </aside>
  );
};

export default Sidebar;

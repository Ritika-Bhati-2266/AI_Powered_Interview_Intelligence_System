import React from 'react';
import { useAuth } from '../../context/AuthContext';
import { LogOut, User, Cpu, Shield } from 'lucide-react';

const Navbar = () => {
  const { user, logout } = useAuth();

  return (
    <nav className="h-16 border-b border-white/5 bg-slate-950/65 backdrop-blur-xl px-6 flex items-center justify-between sticky top-0 z-40">
      {/* Neon branding */}
      <div className="flex items-center gap-2">
        <div className="p-1.5 rounded-lg bg-indigo-600/10 border border-indigo-500/20 text-indigo-400">
          <Cpu className="w-5 h-5 pulse-border-purple" />
        </div>
        <span className="font-outfit font-bold text-lg bg-gradient-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent tracking-wide">
          AEGIS INTERVIEW INTELLIGENCE
        </span>
      </div>

      {/* User profile capsule */}
      {user && (
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2.5 px-3 py-1.5 rounded-full bg-slate-900/60 border border-white/5 shadow-neon-card">
            {user.role === 'admin' ? (
              <Shield className="w-4 h-4 text-cyan-400" />
            ) : (
              <User className="w-4 h-4 text-indigo-400" />
            )}
            <div className="flex flex-col text-left">
              <span className="text-xs font-semibold font-outfit text-slate-200">{user.name}</span>
              <span className="text-[9px] uppercase tracking-wider text-slate-500 font-bold">{user.role}</span>
            </div>
          </div>
          
          <button
            onClick={logout}
            className="p-2 rounded-full border border-white/5 hover:bg-red-500/10 hover:border-red-500/35 hover:text-red-400 transition-all duration-300 text-slate-400"
            title="Sign Out"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      )}
    </nav>
  );
};

export default Navbar;

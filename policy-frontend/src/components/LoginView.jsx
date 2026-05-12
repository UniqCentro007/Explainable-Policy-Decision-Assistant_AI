import React from 'react';
import { Shield, User, Lock } from 'lucide-react';

const LoginView = ({ handleLogin, userId, setUserId, password, setPassword }) => {
  return (
    <div className="login-container bg-cyber-grid">
      <div className="login-card relative overflow-hidden">
        <div className="mb-8">
          <h1 className="brand-title neon-glow text-4xl">Policy<span className="brand-accent">Audit</span></h1>
          <div className="cyber-bar mx-auto"></div>
          <p className="text-[9px] text-cyan-500/60 font-black uppercase tracking-[0.4em] mt-4">AI-Powered Policy Evaluation</p>
        </div>
        <div className="flex justify-center mb-8">
          <div className="p-4 bg-cyan-500/10 rounded-3xl border border-cyan-500/20 text-cyan-400"><Shield size={40} /></div>
        </div>
        <form onSubmit={handleLogin} className="space-y-5">
          <div className="relative group">
            <User className="absolute left-4 top-4 text-slate-500 group-focus-within:text-cyan-400 transition-colors" size={18} />
            <input type="text" placeholder="ANALYST ID" value={userId} onChange={(e) => setUserId(e.target.value.toUpperCase())} className="login-input pl-12 text-left" required />
          </div>
          <div className="relative group">
            <Lock className="absolute left-4 top-4 text-slate-500 group-focus-within:text-cyan-400 transition-colors" size={18} />
            <input type="password" placeholder="PASSWORD" value={password} onChange={(e) => setPassword(e.target.value)} className="login-input pl-12 text-left" required />
          </div>
          <button className="btn-primary w-full shadow-lg">Verify Identity</button>
        </form>
        <p className="mt-8 text-[10px] text-slate-600 font-bold uppercase tracking-widest">Secure Terminal Access</p>
      </div>
    </div>
  );
};

export default LoginView;
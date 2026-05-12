import React from 'react';
import { Cpu } from 'lucide-react';

const ThinkingState = () => (
  <div className="thinking-container">
    {/* 1. The Scanning Laser Beam */}
    <div className="scanning-beam" />

    {/* 2. The Animated Visual Core */}
    <div className="thinking-visual">
      {/* Rotating outer ring */}
      <div className="thinking-ring" />
      
      {/* Pulsing center core */}
      <div className="thinking-core">
        <Cpu size={24} className="text-slate-950" />
      </div>
    </div>

    {/* 3. The Textual Feedback */}
    <div className="relative z-20 flex flex-col items-center text-center space-y-3">
      <h3 className="text-cyan-400 font-black tracking-[0.4em] uppercase text-sm animate-pulse">
        Analyzing Policy Context
      </h3>
      <div className="flex items-center gap-3">
        <span className="w-1 h-1 bg-cyan-500 rounded-full animate-ping" />
        <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">
          Querying Vector Engine...
        </p>
      </div>
    </div>

    {/* 4. Subtle Background Glow Overlay */}
    <div className="absolute inset-0 bg-cyan-500/[0.03] animate-pulse pointer-events-none" />
  </div>
);

export default ThinkingState;
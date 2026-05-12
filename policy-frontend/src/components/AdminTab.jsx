import React, { useState } from 'react';
import { BarChart3, Upload, FileCheck, Loader2, AlertCircle, Cpu } from 'lucide-react';
import ArchitectureDiagram from '../ArchitectureDiagram';

const AdminTab = ({ metrics }) => {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState('idle'); // idle, uploading, success, error

  const handleUpload = async () => {
    if (!file) return;
    setStatus('uploading');

    const formData = new FormData();
    formData.append('file', file);

    try {
      // UPDATED: Port 8080 and full API path to match main.py
      const response = await fetch('http://127.0.0.1:8080/api/admin/upload-policy', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        console.log("Ingestion Success:", result.message);
        setStatus('success');
        setFile(null);
      } else {
        const errorData = await response.json();
        console.error("Ingestion failed:", errorData.detail);
        setStatus('error');
      }
    } catch (err) {
      console.error("Network or Upload failed", err);
      setStatus('error');
    }
  };

  return (
    <div className="h-full overflow-y-auto custom-scrollbar pr-4 animate-in space-y-10 pb-20">
      
      {/* --- HEADER --- */}
      <div className="flex items-center justify-between sticky top-0 bg-[#020617]/90 backdrop-blur-md z-50 py-4 border-b border-white/5">
        <h2 className="section-title flex items-center gap-3 text-white font-bold">
          <BarChart3 className="text-cyan-400" /> Intelligence Center
        </h2>
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></span>
          <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest">System Operational</span>
        </div>
      </div>
      
      {/* --- METRICS GRID --- */}
      {metrics && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-slate-900/40 p-8 rounded-[2.5rem] border border-white/5 shadow-lg backdrop-blur-sm">
            <p className="text-slate-500 uppercase text-[10px] font-black tracking-widest mb-2">Total Queries</p>
            <p className="text-4xl font-black text-cyan-400">{metrics.total_queries || 0}</p>
          </div>

          <div className="bg-slate-900/40 p-8 rounded-[2.5rem] border border-white/5 shadow-lg backdrop-blur-sm">
            <p className="text-slate-500 uppercase text-[10px] font-black tracking-widest mb-2">Avg Latency</p>
            <p className="text-4xl font-black text-white">{metrics.average_latency_seconds || 0}s</p>
          </div>

          <div className="bg-slate-900/40 p-8 rounded-[2.5rem] border border-white/5 shadow-lg backdrop-blur-sm">
            <p className="text-slate-500 uppercase text-[10px] font-black tracking-widest mb-2">Explainability Score</p>
            <p className="text-4xl font-black text-emerald-400">{metrics.user_clarity_score_percent || 0}%</p>
          </div>
        </div>
      )}

      {/* --- MANAGER UPLOAD SECTION --- */}
      <div className="bg-slate-900/40 rounded-[2.5rem] border border-white/5 p-10 shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 right-0 p-8 opacity-5">
            <Cpu size={120} />
        </div>

        <div className="max-w-2xl">
          <h3 className="text-xl font-bold text-white mb-2">Knowledge Base Expansion</h3>
          <p className="text-slate-400 text-sm mb-8 leading-relaxed">
            Upload new policy documentation to the unified vector engine. Files will be automatically 
            chunked and indexed for immediate RAG availability.
          </p>

          <div className="flex items-center gap-6">
            <div className="flex-1">
              <input 
                type="file" 
                id="admin-file-input" 
                className="hidden" 
                accept=".pdf,.txt"
                onChange={(e) => {
                  if (e.target.files && e.target.files[0]) {
                    setFile(e.target.files[0]);
                    setStatus('idle');
                  }
                }}
              />
              <label 
                htmlFor="admin-file-input" 
                className="flex items-center justify-between bg-slate-950 border border-white/10 rounded-2xl p-4 cursor-pointer hover:border-cyan-500/50 transition-all group"
              >
                <span className="text-slate-400 text-xs truncate max-w-[250px]">
                  {file ? file.name : "Select policy PDF or TXT..."}
                </span>
                <Upload size={16} className="text-slate-600 group-hover:text-cyan-400" />
              </label>
            </div>

            <button 
              onClick={handleUpload}
              disabled={!file || status === 'uploading'}
              className={`px-8 py-4 rounded-2xl font-black uppercase tracking-widest text-[10px] transition-all flex items-center gap-3
                ${!file ? 'bg-slate-800 text-slate-500 cursor-not-allowed' : 
                  status === 'uploading' ? 'bg-slate-800 text-cyan-400' : 'bg-cyan-500 text-slate-950 hover:bg-cyan-400 shadow-lg shadow-cyan-500/20'}`}
            >
              {status === 'uploading' ? (
                <>
                  <Loader2 className="animate-spin" size={16} /> Vectorizing...
                </>
              ) : status === 'success' ? (
                <>
                  <FileCheck size={16} /> Ingested
                </>
              ) : (
                <>
                  Sync Library
                </>
              )}
            </button>
          </div>

          {status === 'error' && (
            <div className="mt-4 flex items-center gap-2 text-red-500 text-[10px] font-bold uppercase tracking-tight">
              <AlertCircle size={14} /> Ingestion failed. Verify file format and server status.
            </div>
          )}
        </div>
      </div>

      {/* --- ARCHITECTURE SECTION --- */}
      <div className="relative border-t border-white/5 pt-10">
        <ArchitectureDiagram />
      </div>

    </div>
  );
};

export default AdminTab;
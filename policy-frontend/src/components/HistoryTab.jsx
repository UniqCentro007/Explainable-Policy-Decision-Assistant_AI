import React from 'react';
import { Clock, X, ChevronRight, Hash, User, Globe, FileText, ShieldCheck, MessageSquare, Download } from 'lucide-react';

const HistoryTab = ({ history, selectedAudit, setSelectedAudit }) => {
  
  // Helper to safely parse trace if it arrives as a string from the backend
  const getTraceArray = (trace) => {
    try {
      if (!trace) return [];
      return typeof trace === 'string' ? JSON.parse(trace) : trace;
    } catch (e) {
      console.error("Trace parsing failed", e);
      return [];
    }
  };

  // --- NATIVE PDF EXPORT FOR HISTORICAL AUDITS ---
  const handleExportPDF = () => {
    if (!selectedAudit) return;
    
    const printWindow = window.open('', '', 'height=800,width=800');
    const traceArray = getTraceArray(selectedAudit.reasoning_trace);
    
    const htmlContent = `
      <html>
        <head>
          <title>Historical Policy Audit - ${selectedAudit.id}</title>
          <style>
            /* Hides the default browser URL, Date, and Page Numbers at the top/bottom */
            @page { size: auto; margin: 12mm; } 
            
            /* Ensures background colors print perfectly */
            @media print {
              body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
            }
            
            /* Restored beautiful, spacious styling */
            body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; padding: 0; margin: 0; color: #1e293b; line-height: 1.6; }
            .header { border-bottom: 2px solid #e2e8f0; padding-bottom: 20px; margin-bottom: 30px; }
            h1 { color: #0f172a; margin: 0 0 10px 0; font-size: 24px; }
            .meta { color: #64748b; font-size: 12px; }
            h2 { color: #0ea5e9; margin-top: 30px; font-size: 18px; text-transform: uppercase; letter-spacing: 1px; }
            .query-box { background: #f8fafc; padding: 15px; border-radius: 6px; border: 1px solid #e2e8f0; font-style: italic; font-size: 15px; }
            .recommendation { background: #f0f9ff; padding: 20px; border-left: 4px solid #0ea5e9; font-weight: bold; font-size: 16px; margin: 20px 0; }
            
            /* 'page-break-inside: avoid' stops the massive blank gaps by keeping the whole box together */
            .step { margin-bottom: 20px; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px; page-break-inside: avoid; }
            .step-title { font-weight: bold; color: #0f172a; margin-bottom: 8px; font-size: 15px; }
            .step-analysis { color: #475569; font-size: 14px; margin-bottom: 12px; }
            .evidence { background: #f8fafc; padding: 15px; border-left: 3px solid #10b981; font-size: 13px; font-style: italic; color: #64748b; }
            .footer { margin-top: 50px; padding-top: 20px; border-top: 1px solid #e2e8f0; font-size: 10px; text-align: center; color: #94a3b8; page-break-inside: avoid; }
          </style>
        </head>
        <body>
          <div class="header">
            <h1>Historical Policy Audit Report</h1>
            <div class="meta">
              <strong>Exported:</strong> ${new Date().toLocaleString()}<br/>
              <strong>Analyst ID:</strong> ${selectedAudit.user_id || 'Unknown'}<br/>
              <strong>Audit ID:</strong> ${selectedAudit.id}
            </div>
          </div>
          
          <h2>1. Original Query</h2>
          <div class="query-box">"${selectedAudit.question}"</div>
          
          <h2>2. Final Recommendation</h2>
          <div class="recommendation">
            ${selectedAudit.recommendation}
          </div>
          
          <h2>3. Chain-of-Thought Reasoning Trace</h2>
          ${traceArray.map((step, index) => `
            <div class="step">
              <div class="step-title">Step ${index + 1}: ${step.title}</div>
              <div class="step-analysis">${step.analysis}</div>
              ${step.evidence && step.evidence !== 'N/A' ? `
                <div class="evidence">
                  "${step.evidence}"<br/><br/>
                  <strong style="font-size: 10px; text-transform: uppercase; color: #0ea5e9;">Source: ${step.source_file}</strong>
                </div>
              ` : ''}
            </div>
          `).join('')}
          
          <div class="footer">
            CONFIDENTIAL - INTERNAL USE ONLY<br/>
            Generated securely by the Explainable Policy Decision Assistant
          </div>
        </body>
      </html>
    `;
    
    printWindow.document.write(htmlContent);
    printWindow.document.close();
    printWindow.focus();
    
    setTimeout(() => {
      printWindow.print();
      printWindow.close();
    }, 250);
  };

  return (
    /* PARENT: Locked to available height to prevent window scroll */
    <div className="flex gap-8 h-full w-full overflow-hidden">
      
      {/* --- LEFT SIDE: MASTER AUDIT LIST --- */}
      <div className={`transition-all duration-500 ease-in-out flex flex-col h-full 
        ${selectedAudit ? 'w-1/3' : 'w-full'}`}>
        
        <div className="flex items-center justify-between mb-6 shrink-0">
          <h2 className="section-title flex items-center gap-3">
            <Clock className="text-cyan-400" size={20} /> Audit History
          </h2>
          <span className="text-[9px] font-black text-slate-500 uppercase tracking-[0.2em] bg-slate-900/50 px-3 py-1 rounded-full border border-white/5">
            {history.length} Records
          </span>
        </div>

        {/* Scrollable List Container */}
        <div className="flex-1 min-h-0 bg-slate-900/20 rounded-[2.5rem] border border-white/5 flex flex-col shadow-inner overflow-hidden">
          <div className="flex-1 overflow-y-auto custom-scrollbar">
            <table className="w-full text-left border-collapse">
              <thead className="sticky top-0 bg-[#0a0f1a] z-20 border-b border-white/10">
                <tr>
                  <th className="p-5 text-[10px] font-black text-slate-500 uppercase tracking-widest">Analyst</th>
                  <th className="p-5 text-[10px] font-black text-slate-500 uppercase tracking-widest">Question Asked</th>
                  {!selectedAudit && <th className="p-5 text-[10px] font-black text-slate-500 uppercase tracking-widest">Recommendation</th>}
                  <th className="p-5 text-[10px] font-black text-slate-500 uppercase tracking-widest text-right">Action</th>
                </tr>
              </thead>
              <tbody>
                {history.map((h) => (
                  <tr 
                    key={h.id} 
                    onClick={() => setSelectedAudit(h)} 
                    className={`group cursor-pointer border-b border-white/5 transition-all
                      ${selectedAudit?.id === h.id ? 'bg-cyan-500/10 border-l-2 border-l-cyan-500' : 'hover:bg-white/5'}`}
                  >
                    <td className="p-5">
                      <div className="flex items-center gap-2">
                        <User size={12} className="text-slate-500" />
                        <span className="font-bold text-cyan-500 text-sm uppercase">{h.user_id}</span>
                      </div>
                    </td>
                    <td className="p-5">
                      <div className="flex items-start gap-2 max-w-[200px]">
                        <MessageSquare size={12} className="text-slate-600 mt-1 shrink-0" />
                        <span className="text-xs text-slate-400 italic line-clamp-2 leading-relaxed">
                          {h.question || "Policy Inquiry"}
                        </span>
                      </div>
                    </td>
                    {!selectedAudit && (
                      <td className="p-5 text-sm font-medium text-slate-300 truncate max-w-xs">
                        {h.recommendation}
                      </td>
                    )}
                    <td className="p-5 text-right">
                      <div className={`inline-flex items-center gap-1 text-[10px] font-black tracking-tighter transition-all
                        ${selectedAudit?.id === h.id ? 'text-cyan-400' : 'text-slate-600 group-hover:text-cyan-400'}`}>
                        {selectedAudit?.id === h.id ? 'OPEN' : 'VIEW'}
                        <ChevronRight size={14} className={selectedAudit?.id === h.id ? 'translate-x-1' : ''} />
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* --- RIGHT SIDE: DETAILED RESEARCH LOG --- */}
      {selectedAudit && (
        <div className="w-2/3 flex flex-col h-full animate-in fade-in slide-in-from-right-10 duration-500">
          <div className="bg-slate-900/40 rounded-[2.5rem] border border-cyan-500/20 flex flex-col h-full overflow-hidden shadow-2xl backdrop-blur-sm">
            
            {/* Header Area (Pinned) */}
            <div className="p-8 border-b border-white/5 flex justify-between items-center bg-slate-900/30 shrink-0">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400 shadow-[0_0_20px_rgba(6,182,212,0.15)]">
                  <FileText size={24} />
                </div>
                <div className="space-y-1">
                  <h3 className="text-lg font-bold text-white tracking-tight leading-none">Audit Insight Trace</h3>
                  <div className="flex flex-wrap items-center gap-x-3">
                    <span className="text-[9px] text-slate-500 font-black uppercase tracking-widest flex items-center gap-1">
                      <Hash size={10} /> {selectedAudit.id}
                    </span>
                    <span className="w-1 h-1 rounded-full bg-slate-700" />
                    <span className="text-[9px] text-cyan-600 font-black uppercase tracking-widest flex items-center gap-1">
                      <MessageSquare size={10} /> INQUIRY LOG
                    </span>
                  </div>
                </div>
              </div>
              
              {/* PDF Download and Close Buttons */}
              <div className="flex items-center gap-3">
                <button 
                  onClick={handleExportPDF} 
                  className="w-10 h-10 rounded-full border border-white/10 flex items-center justify-center text-cyan-400 hover:text-white hover:bg-cyan-500/20 hover:border-cyan-500/30 transition-all"
                  title="Export Historical PDF"
                >
                  <Download size={18}/>
                </button>
                <button 
                  onClick={() => setSelectedAudit(null)} 
                  className="w-10 h-10 rounded-full border border-white/10 flex items-center justify-center text-slate-500 hover:text-white hover:bg-red-500/20 hover:border-red-500/30 transition-all"
                  title="Close Trace"
                >
                  <X size={18}/>
                </button>
              </div>
            </div>

            {/* Scrollable Trace Content (Right Side Independent) */}
            <div className="flex-1 min-h-0 overflow-y-auto p-8 custom-scrollbar space-y-8">
              
              {/* Question Context Box */}
              <div className="bg-slate-950/50 border border-white/5 p-6 rounded-[2rem] mb-4">
                 <h4 className="text-slate-500 font-black text-[9px] uppercase tracking-[0.3em] mb-2">Original Inquiry</h4>
                 <p className="text-sm italic text-slate-400 leading-relaxed">"{selectedAudit.question}"</p>
              </div>

              <div className="bg-cyan-950/20 border border-cyan-500/30 p-6 rounded-[2rem] relative overflow-hidden group shrink-0">
                <div className="absolute top-[-10px] right-[-10px] opacity-5 group-hover:opacity-10 transition-opacity">
                  <ShieldCheck size={120} />
                </div>
                <h4 className="text-cyan-500 font-black text-[10px] uppercase tracking-[0.3em] mb-3 flex items-center gap-2">
                  <ShieldCheck size={12}/> Primary Recommendation
                </h4>
                <p className="text-lg leading-relaxed text-slate-200 font-medium relative z-10">
                  {selectedAudit.recommendation}
                </p>
              </div>

              <div className="space-y-0 relative mt-4">
                <div className="absolute left-[19px] top-4 bottom-4 w-[1px] bg-gradient-to-b from-cyan-500/50 via-slate-800 to-transparent" />
                
                {getTraceArray(selectedAudit.reasoning_trace).map((step, idx) => (
                  <div key={idx} className="relative pl-14 pb-12 group last:pb-0">
                    <div className="absolute left-0 top-0 w-10 h-10 rounded-full bg-slate-950 border border-white/10 flex items-center justify-center text-[10px] font-black text-cyan-400 z-10 group-hover:border-cyan-500/50 transition-all shadow-lg group-hover:shadow-cyan-500/10">
                      {idx + 1}
                    </div>
                    
                    <div className="space-y-3">
                      <h4 className="text-sm font-bold text-white uppercase tracking-wider group-hover:text-cyan-400 transition-colors">
                        {step.title}
                      </h4>
                      <p className="text-sm text-slate-400 leading-relaxed max-w-2xl">
                        {step.analysis}
                      </p>
                      
                      {step.evidence && (
                        <div className="bg-white/5 border border-white/5 p-4 rounded-2xl border-l-2 border-l-cyan-500/40 shadow-inner group-hover:bg-white/[0.07] transition-colors">
                          <p className="text-xs italic text-slate-300 leading-relaxed">
                            "{step.evidence}"
                          </p>
                          <div className="text-[9px] font-black text-cyan-700 uppercase mt-3 tracking-widest flex items-center gap-2">
                            <FileText size={10}/> Source: {step.source_file || 'Policy Documentation'}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default HistoryTab;
import React, { useState, useEffect } from 'react';
import { Cpu, Send, Loader2, Download, CheckCircle, FileText, Trash2 } from 'lucide-react';
import ThinkingState from './ThinkingState';

const AuditTab = ({ 
  loading, 
  result, 
  onAudit, 
  domain, 
  setDomain, 
  question, 
  setQuestion, 
  handleFeedback,
  setResult 
}) => {
  const [feedbackSent, setFeedbackSent] = useState(false);

  // Reset feedback UI ONLY when a new result is generated
  useEffect(() => {
    setFeedbackSent(false);
  }, [result]);

  const handleClear = () => {
    setQuestion('');
    if (setResult) setResult(null);
    setFeedbackSent(false);
  };

  const processFeedback = async (isPositive) => {
    try {
      const success = await handleFeedback(isPositive);
      if (success) {
        setFeedbackSent(true);
      }
    } catch (err) {
      console.error("Feedback process failed:", err);
    }
  };

  // --- RESTORED PREMIUM PDF EXPORT WITH SMART PAGING ---
  const handleExportPDF = () => {
    if (!result) return;
    
    const printWindow = window.open('', '', 'height=800,width=800');
    
    const htmlContent = `
      <html>
        <head>
          <title>Policy Audit Report - ${result.id || 'Export'}</title>
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
            <h1>Policy Audit & Decision Report</h1>
            <div class="meta">
              <strong>Generated:</strong> ${new Date().toLocaleString()}<br/>
              <strong>Domain:</strong> ${domain || 'Unified'}<br/>
              <strong>Audit ID:</strong> ${result.id || 'Pending Validation'}
            </div>
          </div>
          
          <h2>1. Original Query</h2>
          <div class="query-box">"${question}"</div>
          
          <h2>2. Final Recommendation</h2>
          <div class="recommendation">
            ${result.recommendation}
          </div>
          <p style="font-size: 14px;"><strong>AI Confidence Score:</strong> ${result.confidence_score !== undefined ? (result.confidence_score * 100).toFixed(1) : 0}%</p>
          
          <h2>3. Chain-of-Thought Reasoning Trace</h2>
          ${(result.reasoning_trace || []).map(step => `
            <div class="step">
              <div class="step-title">Step ${step.step_number || '-'}: ${step.title}</div>
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
    <div className="audit-grid">
      
      {/* --- LEFT PANEL: CONTROL TERMINAL --- */}
      <section className="control-panel">
        <div className="flex justify-between items-center">
          <div className="input-label">
            <Cpu size={14} className="text-cyan-400 animate-pulse"/>
            Policy Terminal
          </div>
          <div className="flex items-center gap-2">
            <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-ping"></span>
            <span className="live-indicator text-[10px] font-black uppercase text-emerald-500 tracking-widest">Live</span>
          </div>
        </div>
        
        <form onSubmit={onAudit} className="flex flex-col gap-6">
          <div className="space-y-4">
            <label className="input-label text-slate-400">Your Inquiry</label>
            <textarea 
              value={question} 
              onChange={(e) => setQuestion(e.target.value)} 
              className="cyber-textarea" 
              placeholder="Ask any policy question..." 
              required
            />
          </div>
          
          <div className="flex flex-col gap-3">
            <button 
              type="submit" 
              disabled={loading}
              className="btn-execute"
            >
              {loading ? (
                <Loader2 className="animate-spin" size={20}/>
              ) : (
                <>
                  <Send size={18}/> 
                  <span>Execute Audit</span>
                </>
              )}
            </button>

            <button 
              type="button"
              onClick={handleClear}
              disabled={loading || (!question && !result)}
              className="w-full py-3 border border-white/5 bg-white/5 text-slate-400 rounded-2xl text-[10px] font-black uppercase tracking-widest hover:bg-red-500/10 hover:text-red-500 hover:border-red-500/20 transition-all flex items-center justify-center gap-2 disabled:opacity-30 disabled:cursor-not-allowed"
            >
              <Trash2 size={14} />
              Clear Terminal
            </button>
          </div>
        </form>

        <div className="mt-auto pt-6 border-t border-white/5">
          <p className="text-[9px] text-slate-600 font-medium uppercase tracking-[0.2em] text-center">
            Secure AI Terminal Access • v3.0.2
          </p>
        </div>
      </section>

      {/* --- RIGHT PANEL: OUTPUT DISPLAY --- */}
      <section className="preview-panel custom-scrollbar">
        {loading ? (
          <ThinkingState />
        ) : result ? (
          <div className="w-full space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500 pb-10">
            <div className="recommendation-box">
              <div className="flex justify-between items-start mb-4">
                <span className="input-label text-cyan-400">Audit Recommendation</span>
                <button 
                  type="button"
                  onClick={handleExportPDF} 
                  className="p-2 hover:bg-cyan-500/10 rounded-lg transition-colors text-cyan-400"
                  title="Export PDF Report"
                >
                  <Download size={18} />
                </button>
              </div>
              <p className="text-xl font-medium text-white leading-relaxed italic">
                "{result.recommendation}"
              </p>
            </div>

            <div className="px-2">
              <h3 className="input-label text-slate-400 mb-8">Step-by-Step Research Trace</h3>
              <div className="space-y-10 border-l border-white/5 ml-4">
                {(result.reasoning_trace || []).map((step, idx) => {
                  return (
                    <div key={idx} className="group relative pl-10">
                      <div className="absolute left-[-17px] top-0 w-8 h-8 rounded-full bg-slate-950 border border-white/10 flex items-center justify-center text-[10px] font-black group-hover:border-cyan-500/50 transition-colors text-cyan-400 shadow-lg">
                        {idx + 1}
                      </div>
                      <div className="space-y-3">
                        <h4 className="text-cyan-400 font-bold text-sm uppercase tracking-wider">{step.title}</h4>
                        
                        {/* Always render the analysis text to match the PDF exactly */}
                        <p className="text-slate-300 text-sm leading-relaxed">{step.analysis}</p>

                        {step.evidence && step.evidence !== 'N/A' && (
                          <div className="bg-white/5 p-4 rounded-2xl border-l-2 border-cyan-500/40 mt-3">
                            <p className="text-xs italic text-slate-400">"{step.evidence}"</p>
                            <div className="text-[9px] text-cyan-600 font-black uppercase mt-2 flex items-center gap-2">
                              <FileText size={10}/> Source: {step.source_file || 'Internal Policy'}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="trace-card flex items-center justify-between min-h-[120px]">
              {feedbackSent ? (
                <div className="flex items-center gap-4 animate-in zoom-in duration-500">
                  <div className="w-12 h-12 bg-emerald-500/20 rounded-full flex items-center justify-center text-emerald-500 border border-emerald-500/30">
                      <CheckCircle size={24} />
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-white uppercase tracking-widest">Feedback Received</h4>
                    <p className="text-[10px] text-slate-500 font-black uppercase mt-1">Audit log updated for system improvement</p>
                  </div>
                </div>
              ) : (
                <>
                  <div className="max-w-[60%]">
                    <p className="input-label text-slate-500 mb-1">Quality Assurance</p>
                    <h4 className="text-sm font-bold text-white">Was this reasoning trace clear and helpful?</h4>
                  </div>
                  <div className="flex gap-3">
                    <button type="button" onClick={() => processFeedback(true)} className="px-6 py-3 bg-emerald-500 text-slate-950 rounded-xl hover:bg-emerald-400 transition-all text-[10px] font-black uppercase shadow-[0_0_15px_rgba(16,185,129,0.3)]">Yes, Clear</button>
                    <button type="button" onClick={() => processFeedback(false)} className="px-6 py-3 bg-red-500/10 text-red-500 rounded-xl border border-red-500/20 hover:bg-red-500 hover:text-white transition-all text-[10px] font-black uppercase">No</button>
                  </div>
                </>
              )}
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-full">
            <div className="animate-float text-cyan-500/10">
              <FileText size={120} strokeWidth={0.5} />
            </div>
            <p className="mt-6 tracking-[0.5em] animate-pulse uppercase text-[10px] font-black text-slate-600">Awaiting Audit Input</p>
          </div>
        )}
      </section>
    </div>
  );
};

export default AuditTab;
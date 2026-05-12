import React, { useState, useEffect } from 'react';
import { Shield, LogOut } from 'lucide-react';
import { loginUser, evaluatePolicy, getAdminMetrics, getAuditHistory, submitFeedback } from './api';
import './App.css';

// Sub-components
import LoginView from './components/LoginView';
import AuditTab from './components/AuditTab';
import HistoryTab from './components/HistoryTab';
import AdminTab from './components/AdminTab';

function App() {
  const [userId, setUserId] = useState("");
  const [fullName, setFullName] = useState(""); // NEW: State for the original name
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("");
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [activeTab, setActiveTab] = useState("audit");
  const [question, setQuestion] = useState("");
  const [domain, setDomain] = useState("Unified"); 
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const [selectedAudit, setSelectedAudit] = useState(null);
  const [metrics, setMetrics] = useState(null);

  // --- SESSION CHECK ON MOUNT ---
  useEffect(() => {
    const savedUser = localStorage.getItem("policy_user");
    if (savedUser) {
      try {
        const data = JSON.parse(savedUser);
        if (data.isLoggedIn) {
          setIsLoggedIn(true);
          setRole(data.role);
          setUserId(data.userId);
          setFullName(data.fullName || ""); // Restore full name from session
        }
      } catch (e) {
        console.error("Session restoration failed", e);
        localStorage.removeItem("policy_user");
      }
    }
  }, []);

  // --- DATA FETCHING LOGIC ---
  useEffect(() => {
    if (isLoggedIn) {
      if (activeTab === "history") fetchHistory();
      if (activeTab === "admin" && role.toLowerCase() === "manager") fetchMetrics();
    }
  }, [activeTab, isLoggedIn, role]);

  const fetchHistory = async () => {
    try { 
      const data = await getAuditHistory(); 
      setHistory(data); 
    } catch (err) { 
      console.error("History fetch failed", err); 
    }
  };

  const fetchMetrics = async () => {
    try { 
      const data = await getAdminMetrics(); 
      setMetrics(data); 
    } catch (err) { 
      console.error("Metrics fetch failed", err); 
    }
  };

  // --- HANDLERS ---
  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const data = await loginUser(userId, password);
      
      // Capture the full_name from backend response
      const sessionData = { 
        isLoggedIn: true, 
        role: data.role, 
        userId: data.user_id,
        fullName: data.full_name // Save Magesh Dev to session
      };
      
      localStorage.setItem("policy_user", JSON.stringify(sessionData));
      setRole(data.role);
      setIsLoggedIn(true);
      setUserId(data.user_id);
      setFullName(data.full_name); 
      setPassword(""); 
    } catch (err) { 
      alert("ACCESS DENIED: Invalid Credentials"); 
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("policy_user");
    setIsLoggedIn(false);
    setRole("");
    setUserId("");
    setFullName("");
    setResult(null);
    setQuestion("");
    setActiveTab("audit");
    console.log("Session Terminated Safely");
  };

  const onAudit = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;
    setResult(null);
    setLoading(true);
    try {
      const data = await evaluatePolicy(question, domain, userId);
      setResult(data);
    } catch (err) { 
      alert("System Error: Vector Engine Offline"); 
      console.error(err);
    } finally { 
      setLoading(false); 
    }
  };

  const handleFeedbackSubmit = async (isPositive) => {
    if (!result || !result.id) return false;
    try {
      await submitFeedback(
        result.id, 
        isPositive, 
        `Analyst ${fullName || userId} marked as ${isPositive ? "Clear" : "Confusing"}`
      );
      return true; 
    } catch (err) {
      console.error("Feedback submission failed:", err);
      return false;
    }
  };

  // --- VIEW RENDERING ---
  if (!isLoggedIn) {
    return (
      <LoginView 
        handleLogin={handleLogin} 
        userId={userId} 
        setUserId={setUserId} 
        password={password} 
        setPassword={setPassword} 
      />
    );
  }

  return (
    <div className="app-shell bg-cyber-grid">
      <nav className="navbar">
        <div className="flex items-center gap-3">
          <div className="logo-icon-small"><Shield size={20}/></div>
          <h1 className="brand-title">POLICY<span className="brand-accent">AUDIT</span></h1>
        </div>
        
        <div className="tab-container">
          <button 
            onClick={() => setActiveTab("audit")} 
            className={`tab-btn ${activeTab === 'audit' ? 'active' : ''}`}
          >
            AUDIT
          </button>
          <button 
            onClick={() => setActiveTab("history")} 
            className={`tab-btn ${activeTab === 'history' ? 'active' : ''}`}
          >
            HISTORY
          </button>
          {/* Handle both "manager" and "Manager" roles */}
          {role.toLowerCase() === "manager" && (
            <button 
              onClick={() => setActiveTab("admin")} 
              className={`tab-btn ${activeTab === 'admin' ? 'active' : ''}`}
            >
              ADMIN
            </button>
          )}
        </div>

        <div className="flex items-center gap-4">
          <div className="text-right">
            <p className={`live-indicator ${role.toLowerCase() === 'manager' ? 'text-cyan-400' : 'text-slate-500'}`}>
              {role.toUpperCase()}
            </p>
            {/* FIXED: Displaying full_name instead of userId */}
            <p className="user-id-display text-[10px] font-bold text-white uppercase tracking-widest">
              {fullName || userId}
            </p>
          </div>
          <button onClick={handleLogout} className="logout-btn" title="Logout">
            <LogOut size={18}/>
          </button>
        </div>
      </nav>

      <main className="main-content">
        {activeTab === "audit" && (
          <AuditTab 
            loading={loading} 
            result={result} 
            onAudit={onAudit} 
            domain={domain} 
            setDomain={setDomain} 
            question={question} 
            setQuestion={setQuestion} 
            handleFeedback={handleFeedbackSubmit}
            setResult={setResult} 
          />
        )}
        
        {activeTab === "history" && (
          <HistoryTab 
            history={history} 
            selectedAudit={selectedAudit} 
            setSelectedAudit={setSelectedAudit} 
          />
        )}
        
        {activeTab === "admin" && role.toLowerCase() === "manager" && (
          <AdminTab metrics={metrics} />
        )}
      </main>
    </div>
  );
}

export default App;
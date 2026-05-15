'use client';
import { useEffect, useState, useMemo } from 'react';
import Link from 'next/link';
import {
  ShieldCheck, Activity, Search, AlertTriangle,
  CheckCircle, XCircle, Upload, FileText,
  TrendingUp, BarChart3, Clock, ArrowUpRight
} from 'lucide-react';

interface CaseSummary {
  case_id: string;
  doc_type: string;
  fraud_score: number;
  final_decision: string;
}

export default function Dashboard() {
  const [cases, setCases] = useState<CaseSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/cases')
      .then(res => res.json())
      .then(data => {
        setCases(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to fetch cases:", err);
        setLoading(false);
      });
  }, []);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files?.[0]) return;

    const formData = new FormData();
    formData.append("file", e.target.files[0]);

    setUploading(true);

    try {
      await fetch("http://127.0.0.1:8000/api/upload", {
        method: "POST",
        body: formData,
      });
      window.location.reload();
    } catch (err) {
      console.error(err);
      alert("Upload failed!");
      setUploading(false);
    }
  };

  const filteredCases = useMemo(() => {
    if (!searchQuery.trim()) return cases;
    const q = searchQuery.toLowerCase();
    return cases.filter(c =>
      c.case_id.toLowerCase().includes(q) ||
      c.doc_type.toLowerCase().includes(q) ||
      c.final_decision.toLowerCase().includes(q)
    );
  }, [cases, searchQuery]);

  // Stats
  const stats = useMemo(() => {
    const approved = cases.filter(c => c.final_decision === 'APPROVE').length;
    const rejected = cases.filter(c => c.final_decision === 'REJECT').length;
    const escalated = cases.filter(c => c.final_decision === 'ESCALATE').length;
    const avgFraud = cases.length > 0
      ? (cases.reduce((a, c) => a + c.fraud_score, 0) / cases.length * 100).toFixed(1)
      : '0.0';
    return { total: cases.length, approved, rejected, escalated, avgFraud };
  }, [cases]);

  const getDecisionBadge = (decision: string) => {
    switch (decision) {
      case 'APPROVE':
        return (
          <span className="badge badge-approve">
            <CheckCircle className="w-3 h-3" /> Approved
          </span>
        );
      case 'REJECT':
        return (
          <span className="badge badge-reject">
            <XCircle className="w-3 h-3" /> Rejected
          </span>
        );
      case 'ESCALATE':
        return (
          <span className="badge badge-escalate">
            <AlertTriangle className="w-3 h-3" /> Escalated
          </span>
        );
      default:
        return (
          <span className="badge badge-processing">
            <Clock className="w-3 h-3" /> Processing
          </span>
        );
    }
  };

  const getFraudColor = (score: number) => {
    if (score >= 0.7) return { bar: 'bg-gradient-to-r from-rose-500 to-red-400', glow: 'shadow-[0_0_10px_rgba(244,63,94,0.4)]', text: 'text-rose-400' };
    if (score >= 0.4) return { bar: 'bg-gradient-to-r from-amber-500 to-yellow-400', glow: '', text: 'text-amber-400' };
    return { bar: 'bg-gradient-to-r from-emerald-500 to-green-400', glow: '', text: 'text-emerald-400' };
  };

  return (
    <div className="min-h-screen p-6 lg:p-10 max-w-[1440px] mx-auto flex flex-col gap-7">

      {/* ===== HEADER ===== */}
      <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-5 animate-fade-in-up">
        <div>
          <div className="flex items-center gap-3.5 mb-1.5">
            <div className="relative">
              <div className="bg-blue-500/15 p-3 rounded-2xl border border-blue-500/20">
                <ShieldCheck className="w-8 h-8 text-blue-400 animate-pulse-glow" />
              </div>
              <div className="absolute -top-1 -right-1 w-3 h-3 bg-emerald-400 rounded-full border-2 border-[var(--bg-primary)]" />
            </div>
            <div>
              <h1 className="text-3xl lg:text-4xl font-extrabold tracking-tight bg-gradient-to-r from-blue-400 via-indigo-400 to-emerald-400 bg-clip-text text-transparent">
                MediShield AI
              </h1>
              <p className="text-sm text-[var(--text-muted)] font-medium mt-0.5">
                Document Intake & Adjudication Pipeline
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <label className="upload-btn cursor-pointer">
            <Upload className="w-4 h-4" />
            {uploading ? 'Processing...' : 'Upload Document'}
            <input type="file" className="hidden" onChange={handleUpload} accept="image/*" disabled={uploading} />
          </label>

          <div className="glass-panel rounded-xl px-4 py-2.5 flex items-center gap-2.5">
            <div className="relative flex items-center justify-center">
              <Activity className="w-4 h-4 text-emerald-400" />
              <span className="absolute w-2 h-2 bg-emerald-400 rounded-full animate-ping opacity-50" />
            </div>
            <span className="text-xs font-semibold tracking-widest text-[var(--text-secondary)] uppercase hidden sm:inline">Online</span>
          </div>
        </div>
      </header>

      {/* ===== STAT CARDS ===== */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 animate-fade-in-up stagger-1">
        <div className="stat-card stat-card-blue">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold uppercase tracking-widest text-[var(--text-muted)]">Total Cases</span>
            <FileText className="w-4 h-4 text-blue-400 opacity-60" />
          </div>
          <p className="text-3xl font-extrabold text-white">{stats.total}</p>
          <p className="text-xs text-[var(--text-muted)] mt-1">Documents processed</p>
        </div>

        <div className="stat-card stat-card-emerald">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold uppercase tracking-widest text-[var(--text-muted)]">Approved</span>
            <CheckCircle className="w-4 h-4 text-emerald-400 opacity-60" />
          </div>
          <p className="text-3xl font-extrabold text-emerald-400">{stats.approved}</p>
          <p className="text-xs text-[var(--text-muted)] mt-1">
            {stats.total > 0 ? `${((stats.approved / stats.total) * 100).toFixed(0)}% approval rate` : 'No data'}
          </p>
        </div>

        <div className="stat-card stat-card-rose">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold uppercase tracking-widest text-[var(--text-muted)]">Rejected</span>
            <XCircle className="w-4 h-4 text-rose-400 opacity-60" />
          </div>
          <p className="text-3xl font-extrabold text-rose-400">{stats.rejected}</p>
          <p className="text-xs text-[var(--text-muted)] mt-1">Claims denied</p>
        </div>

        <div className="stat-card stat-card-amber">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold uppercase tracking-widest text-[var(--text-muted)]">Avg. Risk</span>
            <TrendingUp className="w-4 h-4 text-amber-400 opacity-60" />
          </div>
          <p className="text-3xl font-extrabold text-amber-400">{stats.avgFraud}%</p>
          <p className="text-xs text-[var(--text-muted)] mt-1">Mean fraud score</p>
        </div>
      </div>

      {/* ===== MAIN TABLE ===== */}
      <main className="glass-panel rounded-3xl overflow-hidden flex flex-col animate-fade-in-up stagger-2">
        {/* Table header */}
        <div className="p-5 lg:p-6 border-b border-white/[0.05] flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div className="flex items-center gap-3">
            <BarChart3 className="w-5 h-5 text-blue-400" />
            <h2 className="text-lg font-bold tracking-tight">Recent Submissions</h2>
            <span className="bg-blue-500/15 text-blue-400 px-2.5 py-0.5 rounded-full text-xs font-bold">{filteredCases.length}</span>
          </div>
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-[var(--text-muted)]" />
            <input
              type="text"
              placeholder="Search by ID, type, or decision..."
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              className="search-input"
            />
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-black/20">
                <th className="p-5 text-[10px] uppercase tracking-[0.15em] font-bold text-[var(--text-muted)]">Case ID</th>
                <th className="p-5 text-[10px] uppercase tracking-[0.15em] font-bold text-[var(--text-muted)]">Document Type</th>
                <th className="p-5 text-[10px] uppercase tracking-[0.15em] font-bold text-[var(--text-muted)]">Fraud Risk</th>
                <th className="p-5 text-[10px] uppercase tracking-[0.15em] font-bold text-[var(--text-muted)] text-right">Decision</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={4} className="p-16 text-center">
                    <div className="flex flex-col items-center gap-4">
                      <div className="spinner" />
                      <span className="text-[var(--text-muted)] text-sm font-medium">Loading pipeline data...</span>
                    </div>
                  </td>
                </tr>
              ) : filteredCases.length === 0 ? (
                <tr>
                  <td colSpan={4} className="p-16 text-center">
                    <div className="flex flex-col items-center gap-3">
                      <FileText className="w-12 h-12 text-[var(--text-muted)] opacity-30" />
                      <p className="text-[var(--text-muted)] font-medium">
                        {searchQuery ? 'No cases match your search.' : 'No documents processed yet.'}
                      </p>
                      {!searchQuery && (
                        <p className="text-sm text-[var(--text-muted)] opacity-60">Upload a document to get started</p>
                      )}
                    </div>
                  </td>
                </tr>
              ) : filteredCases.map((c, idx) => {
                const fraudStyle = getFraudColor(c.fraud_score);
                return (
                  <tr
                    key={c.case_id}
                    className="table-row group animate-fade-in-up"
                    style={{ animationDelay: `${idx * 0.04}s` }}
                  >
                    <td className="p-5">
                      <Link
                        href={`/case/${c.case_id}`}
                        className="text-blue-400 font-mono text-sm hover:text-blue-300 transition-colors flex items-center gap-2"
                      >
                        {c.case_id.substring(0, 8)}...
                        <span className="tooltip-reveal text-[10px] bg-blue-500/15 text-blue-400 px-2 py-0.5 rounded-md font-sans font-semibold flex items-center gap-1">
                          View <ArrowUpRight className="w-3 h-3" />
                        </span>
                      </Link>
                    </td>
                    <td className="p-5">
                      <span className="text-sm font-medium text-[var(--text-secondary)] bg-white/[0.04] border border-white/[0.06] px-3 py-1.5 rounded-lg inline-block">
                        {c.doc_type || 'PROCESSING'}
                      </span>
                    </td>
                    <td className="p-5">
                      <div className="flex items-center gap-3">
                        <div className="w-28 h-2 bg-black/40 rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full animate-progress ${fraudStyle.bar} ${fraudStyle.glow}`}
                            style={{ width: `${Math.max(c.fraud_score * 100, 4)}%` }}
                          />
                        </div>
                        <span className={`text-xs font-mono font-semibold ${fraudStyle.text}`}>
                          {(c.fraud_score * 100).toFixed(0)}%
                        </span>
                      </div>
                    </td>
                    <td className="p-5 text-right">
                      {getDecisionBadge(c.final_decision)}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </main>

      {/* Footer */}
      <footer className="text-center py-4 animate-fade-in-up stagger-3">
        <p className="text-xs text-[var(--text-muted)]">
          MediShield AI v2.0 — Powered by LangGraph • Gemini • Qdrant
        </p>
      </footer>
    </div>
  );
}

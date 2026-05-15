'use client';
import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
  ArrowLeft, CheckCircle2, XCircle, FileText, Activity,
  Shield, AlertTriangle, Fingerprint, Brain,
  Eye, ChevronDown, ChevronUp, Zap, Sparkles
} from 'lucide-react';

export default function CaseDetail() {
  const params = useParams();
  const router = useRouter();
  const case_id = params?.id as string;
  const [caseData, setCaseData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    extraction: true,
    policy: true,
    fraud: true,
  });

  useEffect(() => {
    fetch(`http://127.0.0.1:8000/api/cases/${case_id}`)
      .then(res => res.json())
      .then(data => {
        setCaseData(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to fetch case details", err);
        setLoading(false);
      });
  }, [case_id]);

  const handleOverride = async (decision: string) => {
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/cases/${case_id}/override`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ decision })
      });
      if (res.ok) {
        setCaseData({
          ...caseData,
          final_decision: decision,
          justification: `[HUMAN OVERRIDE] ${caseData.justification}`
        });
      }
    } catch (err) {
      console.error(err);
    }
  };

  const toggleSection = (key: string) => {
    setExpandedSections(prev => ({ ...prev, [key]: !prev[key] }));
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="spinner" />
          <span className="text-[var(--text-muted)] text-sm font-medium">Loading case data...</span>
        </div>
      </div>
    );
  }

  if (!caseData) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <FileText className="w-16 h-16 text-[var(--text-muted)] opacity-30" />
          <p className="text-xl font-bold text-[var(--text-muted)]">Case Not Found</p>
          <button onClick={() => router.push('/')} className="upload-btn mt-2">
            <ArrowLeft className="w-4 h-4" /> Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  const isEscalated = caseData.final_decision === 'ESCALATE';

  const decisionConfig = caseData.final_decision === 'APPROVE'
    ? {
        bg: 'linear-gradient(135deg, rgba(16,185,129,0.12) 0%, rgba(16,185,129,0.04) 100%)',
        border: '1px solid rgba(16,185,129,0.25)',
        glow: '0 0 40px rgba(16,185,129,0.1)',
        text: 'text-emerald-400',
        label: 'APPROVED',
        icon: <CheckCircle2 className="w-10 h-10" />,
        accentBar: 'bg-gradient-to-r from-emerald-500 to-green-400',
      }
    : caseData.final_decision === 'REJECT'
    ? {
        bg: 'linear-gradient(135deg, rgba(244,63,94,0.12) 0%, rgba(244,63,94,0.04) 100%)',
        border: '1px solid rgba(244,63,94,0.25)',
        glow: '0 0 40px rgba(244,63,94,0.1)',
        text: 'text-rose-400',
        label: 'REJECTED',
        icon: <XCircle className="w-10 h-10" />,
        accentBar: 'bg-gradient-to-r from-rose-500 to-red-400',
      }
    : {
        bg: 'linear-gradient(135deg, rgba(245,158,11,0.12) 0%, rgba(245,158,11,0.04) 100%)',
        border: '1px solid rgba(245,158,11,0.25)',
        glow: '0 0 40px rgba(245,158,11,0.1)',
        text: 'text-amber-400',
        label: 'ESCALATED',
        icon: <AlertTriangle className="w-10 h-10" />,
        accentBar: 'bg-gradient-to-r from-amber-500 to-yellow-400',
      };

  const fraudPercent = (caseData.fraud_score * 100).toFixed(0);
  const fraudColor = caseData.fraud_score >= 0.7 ? 'from-rose-500 to-red-400' : caseData.fraud_score >= 0.4 ? 'from-amber-500 to-yellow-400' : 'from-emerald-500 to-green-400';

  const extractionData = caseData.doc_type === 'ID_DOCUMENT' ? caseData.kyc_result : caseData.extracted_data;

  return (
    <div className="min-h-screen p-5 lg:p-8 max-w-[1600px] mx-auto animate-fade-in-up">

      {/* ===== TOP BAR ===== */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <button
          onClick={() => router.push('/')}
          className="flex items-center gap-2 text-[var(--text-muted)] hover:text-white transition-colors font-medium text-sm group"
        >
          <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
          Back to Dashboard
        </button>
        <div className="flex items-center gap-3">
          <span className="bg-white/[0.04] border border-white/[0.06] px-3 py-1.5 rounded-lg text-xs font-mono text-[var(--text-muted)]">
            <Fingerprint className="w-3 h-3 inline mr-1.5 opacity-60" />
            {caseData.case_id}
          </span>
          <span className="bg-white/[0.04] border border-white/[0.06] px-3 py-1.5 rounded-lg text-xs font-medium text-[var(--text-secondary)]">
            {caseData.doc_type || 'UNKNOWN'}
          </span>
        </div>
      </div>

      {/* ===== ORCHESTRATOR DECISION — Full Width Hero ===== */}
      <div
        className="rounded-3xl p-6 lg:p-8 mb-6 relative overflow-hidden animate-scale-in"
        style={{
          background: decisionConfig.bg,
          border: decisionConfig.border,
          boxShadow: decisionConfig.glow,
        }}
      >
        {/* Accent bar at top */}
        <div className={`absolute top-0 left-0 right-0 h-1 ${decisionConfig.accentBar} opacity-80`} />

        <div className="relative z-10">
          {/* Row 1: Label + Decision */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-5">
            <div className="flex items-center gap-2.5">
              <Zap className="w-5 h-5 text-[var(--text-muted)]" />
              <span className="text-xs uppercase tracking-[0.15em] font-bold text-[var(--text-muted)]">
                Orchestrator Decision
              </span>
            </div>
            <div className={`flex items-center gap-3 ${decisionConfig.text}`}>
              {decisionConfig.icon}
              <span className="text-3xl lg:text-4xl font-black tracking-tight">
                {decisionConfig.label}
              </span>
            </div>
          </div>

          {/* Row 2: Justification */}
          <div className="bg-black/20 p-5 rounded-2xl border border-white/[0.06]">
            <div className="flex items-start gap-3">
              <Sparkles className="w-4 h-4 text-[var(--text-muted)] mt-0.5 shrink-0" />
              <div>
                <p className="text-[10px] uppercase tracking-[0.12em] font-bold text-[var(--text-muted)] mb-2">
                  AI Justification
                </p>
                <p className="text-sm lg:text-base leading-relaxed text-[var(--text-secondary)]">
                  {caseData.justification || 'No justification provided.'}
                </p>
              </div>
            </div>
          </div>

          {/* Row 3: Override Actions (only for ESCALATE) */}
          {isEscalated && (
            <div className="flex gap-4 mt-5">
              <button onClick={() => handleOverride('APPROVE')} className="override-btn override-btn-approve">
                <CheckCircle2 className="w-5 h-5" /> Override: Approve
              </button>
              <button onClick={() => handleOverride('REJECT')} className="override-btn override-btn-reject">
                <XCircle className="w-5 h-5" /> Override: Reject
              </button>
            </div>
          )}
        </div>
      </div>

      {/* ===== MAIN CONTENT — 1:1 Grid ===== */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* LEFT — Document Viewer */}
        <div className="glass-panel rounded-3xl p-5 lg:p-6 flex flex-col animate-fade-in-up stagger-1">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-bold flex items-center gap-2.5">
              <div className="bg-blue-500/15 p-1.5 rounded-lg">
                <Eye className="w-4 h-4 text-blue-400" />
              </div>
              Document Preview
            </h2>
          </div>
          <div className="flex-1 bg-black/30 rounded-2xl border border-white/[0.04] overflow-hidden flex items-center justify-center min-h-[350px] relative">
            {caseData.image_url ? (
              <img
                src={`http://127.0.0.1:8000${caseData.image_url}`}
                alt="Document"
                className="max-w-full max-h-full object-contain p-4 transition-transform duration-500 hover:scale-[1.02]"
              />
            ) : (
              <div className="flex flex-col items-center gap-3">
                <FileText className="w-16 h-16 text-[var(--text-muted)] opacity-20" />
                <span className="text-[var(--text-muted)] font-medium text-sm tracking-wide">No image preview available</span>
              </div>
            )}
          </div>
        </div>

        {/* RIGHT — Agent Intelligence Trace */}
        <div className="flex flex-col gap-5 animate-fade-in-up stagger-2">

          <div className="glass-panel rounded-3xl p-5 lg:p-6 flex flex-col gap-5">
            <h3 className="font-bold text-lg flex items-center gap-2.5">
              <div className="bg-indigo-500/15 p-2 rounded-xl">
                <Brain className="w-5 h-5 text-indigo-400" />
              </div>
              Agent Intelligence Trace
            </h3>

            {/* ---- Extraction Agent ---- */}
            <div className="agent-section">
              <button
                onClick={() => toggleSection('extraction')}
                className="w-full flex items-center justify-between text-left"
              >
                <h4 className="font-semibold text-sm text-[var(--text-secondary)] flex items-center gap-2">
                  <Activity className="w-4 h-4 text-purple-400" />
                  Extraction Agent
                </h4>
                {expandedSections.extraction
                  ? <ChevronUp className="w-4 h-4 text-[var(--text-muted)]" />
                  : <ChevronDown className="w-4 h-4 text-[var(--text-muted)]" />
                }
              </button>
              {expandedSections.extraction && extractionData && (
                <div className="grid grid-cols-2 gap-2.5 mt-4">
                  {Object.entries(extractionData).map(([k, v]) => (
                    <div key={k} className="data-chip">
                      <span className="data-chip-label">{k.replace(/_/g, ' ')}</span>
                      <span className="data-chip-value">
                        {Array.isArray(v) ? (v as string[]).join(', ') : String(v)}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* ---- Policy RAG Agent ---- */}
            {caseData.doc_type === 'CLAIM_FORM' && (
              <div className="agent-section">
                <button
                  onClick={() => toggleSection('policy')}
                  className="w-full flex items-center justify-between text-left"
                >
                  <h4 className="font-semibold text-sm text-[var(--text-secondary)] flex items-center gap-2">
                    <FileText className="w-4 h-4 text-amber-400" />
                    Policy RAG Agent
                  </h4>
                  {expandedSections.policy
                    ? <ChevronUp className="w-4 h-4 text-[var(--text-muted)]" />
                    : <ChevronDown className="w-4 h-4 text-[var(--text-muted)]" />
                  }
                </button>
                {expandedSections.policy && (
                  <div className="flex flex-col gap-3 mt-4">
                    <div className="flex items-center justify-between bg-black/25 p-3.5 rounded-xl border border-white/[0.04]">
                      <span className="text-xs text-[var(--text-muted)] uppercase tracking-wider font-bold">Coverage Status</span>
                      <span className={`text-sm font-bold font-mono ${
                        caseData.policy_check?.covered?.toLowerCase() === 'yes' || caseData.policy_check?.covered === true ? 'text-emerald-400' :
                        caseData.policy_check?.covered?.toLowerCase() === 'no' || caseData.policy_check?.covered === false ? 'text-rose-400' : 'text-amber-400'
                      }`}>
                        {String(caseData.policy_check?.covered ?? 'N/A').toUpperCase()}
                      </span>
                    </div>
                    <div className="bg-black/25 p-4 rounded-xl border border-white/[0.04]">
                      <span className="text-[10px] uppercase tracking-[0.12em] font-bold text-[var(--text-muted)] block mb-3">
                        Relevant Policy Clauses
                      </span>
                      <div className="flex flex-col gap-2">
                        {(caseData.policy_check?.policy_clause || 'None').split(' | ').map((clause: string, i: number) => (
                          <p
                            key={i}
                            className="text-sm leading-relaxed text-[var(--text-secondary)] bg-white/[0.03] p-3 rounded-lg border-l-2 border-amber-500/60"
                          >
                            {clause}
                          </p>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* ---- Fraud Detection Agent ---- */}
            <div className="agent-section">
              <button
                onClick={() => toggleSection('fraud')}
                className="w-full flex items-center justify-between text-left"
              >
                <h4 className="font-semibold text-sm text-[var(--text-secondary)] flex items-center gap-2">
                  <Shield className="w-4 h-4 text-rose-400" />
                  Fraud Detection Agent
                </h4>
                {expandedSections.fraud
                  ? <ChevronUp className="w-4 h-4 text-[var(--text-muted)]" />
                  : <ChevronDown className="w-4 h-4 text-[var(--text-muted)]" />
                }
              </button>
              {expandedSections.fraud && (
                <div className="flex flex-col gap-3 mt-4">
                  <div className="bg-black/25 p-4 rounded-xl border border-white/[0.04]">
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-xs text-[var(--text-muted)] uppercase tracking-wider font-bold">Risk Score</span>
                      <span className={`text-lg font-extrabold font-mono ${
                        caseData.fraud_score >= 0.7 ? 'text-rose-400' :
                        caseData.fraud_score >= 0.4 ? 'text-amber-400' : 'text-emerald-400'
                      }`}>
                        {fraudPercent}%
                      </span>
                    </div>
                    <div className="w-full h-3 bg-black/40 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full bg-gradient-to-r ${fraudColor} animate-progress`}
                        style={{ width: `${Math.max(caseData.fraud_score * 100, 3)}%` }}
                      />
                    </div>
                    <div className="flex justify-between mt-2">
                      <span className="text-[10px] text-emerald-400/60 font-semibold">Low</span>
                      <span className="text-[10px] text-amber-400/60 font-semibold">Medium</span>
                      <span className="text-[10px] text-rose-400/60 font-semibold">High</span>
                    </div>
                  </div>
                </div>
              )}
            </div>

          </div>
        </div>
      </div>
    </div>
  );
}

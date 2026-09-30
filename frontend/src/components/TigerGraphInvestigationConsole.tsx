import React, { useState, useEffect } from 'react';
import {
  fetchTigerGraphHealth,
  analyzeCaseGraphEvidence,
  testGraphTransactionIngestion,
} from '../services/api';
import { TigerGraphHealth, InvestigationResponse, KeyEvidenceItem } from '../types';
import {
  ShieldAlert,
  Search,
  CheckCircle2,
  AlertTriangle,
  Network,
  Cpu,
  RefreshCw,
  FileSearch,
  Database,
  Layers,
} from 'lucide-react';

export const TigerGraphInvestigationConsole: React.FC = () => {
  const [caseId, setCaseId] = useState<string>('CASE-TG-8042');
  const [loading, setLoading] = useState<boolean>(false);
  const [tgHealth, setTgHealth] = useState<TigerGraphHealth | null>(null);
  const [result, setResult] = useState<InvestigationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [ingestStatus, setIngestStatus] = useState<string | null>(null);

  useEffect(() => {
    checkHealth();
  }, []);

  const checkHealth = async () => {
    const health = await fetchTigerGraphHealth();
    setTgHealth(health);
  };

  const handleRunInvestigation = async (targetCase?: string) => {
    const target = targetCase || caseId;
    if (!target.trim()) return;

    setLoading(true);
    setError(null);
    setIngestStatus(null);

    try {
      const data = await analyzeCaseGraphEvidence(target.trim());
      setResult(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Investigation failed';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleTestIngestion = async () => {
    setIngestStatus('Ingesting test graph vertices & edges...');
    try {
      const res = await testGraphTransactionIngestion({
        transaction_id: `tx_${Date.now()}`,
        user_id: 'usr_808',
        amount: 499.99,
      });
      setIngestStatus(`Success: Ingested test transaction ${res.data.transaction_id} into FraudGraph.`);
      setTimeout(() => setIngestStatus(null), 4000);
    } catch (err: unknown) {
      setIngestStatus('Ingestion error (Ensure backend is running).');
    }
  };

  const getSignificanceBadge = (significance: KeyEvidenceItem['significance']) => {
    switch (significance) {
      case 'HIGH':
        return (
          <span className="px-2 py-0.5 text-xs font-semibold rounded bg-rose-500/10 text-rose-400 border border-rose-500/20">
            HIGH RISK
          </span>
        );
      case 'MEDIUM':
        return (
          <span className="px-2 py-0.5 text-xs font-semibold rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">
            MEDIUM
          </span>
        );
      case 'LOW':
        return (
          <span className="px-2 py-0.5 text-xs font-semibold rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
            LOW
          </span>
        );
      default:
        return (
          <span className="px-2 py-0.5 text-xs font-semibold rounded bg-slate-500/10 text-slate-400 border border-slate-500/20">
            INFO
          </span>
        );
    }
  };

  return (
    <div className="space-y-6">
      {/* Header & Connectivity Banner */}
      <div className="bg-[#151c2c] border border-[#1f2d40] rounded-xl p-6 shadow-lg">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-sky-500/10 border border-sky-500/20 rounded-lg">
              <Network className="w-6 h-6 text-sky-400" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
                TigerGraph Cloud Investigation Console
              </h2>
              <p className="text-sm text-slate-400">
                12-Step evidence graph reasoning over <code className="text-sky-300">FraudGraph</code> topology
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div
              className={`flex items-center gap-2 px-3 py-1.5 rounded-full border text-xs font-medium ${
                tgHealth?.status === 'healthy'
                  ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                  : 'bg-rose-500/10 text-rose-400 border-rose-500/20'
              }`}
            >
              <span
                className={`w-2 h-2 rounded-full ${
                  tgHealth?.status === 'healthy' ? 'bg-emerald-400 animate-pulse' : 'bg-rose-400'
                }`}
              ></span>
              TigerGraph: {tgHealth?.status === 'healthy' ? 'Connected' : 'Offline / Mock'}
            </div>

            <button
              onClick={handleTestIngestion}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-lg transition-colors"
            >
              <Database className="w-3.5 h-3.5 text-sky-400" />
              Ingest Test Graph
            </button>
          </div>
        </div>

        {ingestStatus && (
          <div className="mt-4 p-3 bg-sky-500/10 border border-sky-500/20 rounded-lg text-xs text-sky-300">
            {ingestStatus}
          </div>
        )}
      </div>

      {/* Case Input Control Bar */}
      <div className="bg-[#151c2c] border border-[#1f2d40] rounded-xl p-5 shadow-md">
        <div className="flex flex-col sm:flex-row items-center gap-3">
          <div className="relative flex-1 w-full">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              value={caseId}
              onChange={(e) => setCaseId(e.target.value)}
              placeholder="Enter ClosedCase Vertex ID (e.g., CASE-TG-8042)..."
              className="w-full bg-[#0b0f19] border border-[#1f2d40] focus:border-sky-500 text-slate-100 placeholder-slate-500 text-sm rounded-lg pl-10 pr-4 py-2.5 outline-none transition-all"
            />
          </div>

          <div className="flex items-center gap-2 w-full sm:w-auto">
            <button
              onClick={() => handleRunInvestigation()}
              disabled={loading}
              className="flex-1 sm:flex-initial flex items-center justify-center gap-2 px-5 py-2.5 bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 text-white font-medium text-sm rounded-lg shadow-md transition-all disabled:opacity-50"
            >
              {loading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  Traversing Graph...
                </>
              ) : (
                <>
                  <Cpu className="w-4 h-4" />
                  Analyze Graph Evidence
                </>
              )}
            </button>
          </div>
        </div>

        {/* Preset Sample Case Buttons */}
        <div className="flex items-center gap-2 mt-3 text-xs text-slate-400">
          <span className="font-semibold text-slate-500">Sample Cases:</span>
          {['CASE-TG-8042', 'CASE-TG-1011', 'CASE-TG-3002'].map((preset) => (
            <button
              key={preset}
              onClick={() => {
                setCaseId(preset);
                handleRunInvestigation(preset);
              }}
              className="px-2.5 py-1 rounded bg-[#0b0f19] hover:bg-slate-800 text-slate-300 border border-[#1f2d40] transition-colors"
            >
              {preset}
            </button>
          ))}
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl text-rose-300 flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
          <div>
            <h4 className="font-semibold text-sm">Investigation Error</h4>
            <p className="text-xs mt-0.5 text-rose-300/80">{error}</p>
          </div>
        </div>
      )}

      {/* Investigation Results Display */}
      {result && (
        <div className="space-y-6">
          {/* Executive Summary */}
          <div className="bg-[#151c2c] border border-[#1f2d40] rounded-xl p-6 shadow-md">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-400 mb-2 flex items-center gap-2">
              <FileSearch className="w-4 h-4 text-sky-400" /> Executive Investigation Summary
            </h3>
            <p className="text-slate-200 text-base leading-relaxed">{result.summary}</p>

            {/* Triggered Policy Rules */}
            <div className="mt-4 pt-4 border-t border-[#1f2d40]">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">
                Triggered Policy Rules ({result.relevant_rules.length})
              </span>
              <div className="flex flex-wrap gap-2">
                {result.relevant_rules.map((rule) => (
                  <span
                    key={rule}
                    className="px-3 py-1 bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs font-bold rounded-lg"
                  >
                    Rule {rule}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Key Findings & Graph Evidence Items */}
          <div className="bg-[#151c2c] border border-[#1f2d40] rounded-xl p-6 shadow-md">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-400 mb-4 flex items-center gap-2">
              <Layers className="w-4 h-4 text-sky-400" /> Mapped Graph Evidence Items ({result.key_evidence.length})
            </h3>
            <div className="space-y-3">
              {result.key_evidence.map((item) => (
                <div
                  key={item.evidence_id}
                  className="flex items-start justify-between gap-4 p-3.5 bg-[#0b0f19] border border-[#1f2d40] rounded-lg"
                >
                  <div className="flex items-start gap-3">
                    <span className="text-xs font-mono font-bold text-sky-400 bg-sky-500/10 px-2 py-0.5 rounded border border-sky-500/20 shrink-0">
                      {item.evidence_id}
                    </span>
                    <p className="text-sm text-slate-200">{item.finding}</p>
                  </div>
                  <div className="shrink-0">{getSignificanceBadge(item.significance)}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Two Column Grid: Patterns & Uncertainties */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Observed Fraud Patterns */}
            <div className="bg-[#151c2c] border border-[#1f2d40] rounded-xl p-6 shadow-md">
              <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-2">
                <ShieldAlert className="w-4 h-4 text-rose-400" /> Observed Fraud Patterns ({result.observed_patterns.length})
              </h3>
              {result.observed_patterns.length > 0 ? (
                <ul className="space-y-2">
                  {result.observed_patterns.map((pattern, idx) => (
                    <li
                      key={idx}
                      className="flex items-center gap-2.5 text-sm text-slate-300 p-2.5 bg-[#0b0f19] border border-[#1f2d40] rounded-lg"
                    >
                      <span className="w-1.5 h-1.5 rounded-full bg-rose-400 shrink-0"></span>
                      {pattern}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-xs text-slate-500 italic">No suspicious fraud patterns detected in current topology.</p>
              )}
            </div>

            {/* Uncertainties & Data Gaps */}
            <div className="bg-[#151c2c] border border-[#1f2d40] rounded-xl p-6 shadow-md">
              <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-400" /> Uncertainties & Data Gaps
              </h3>
              <div className="space-y-3">
                {result.uncertainties.map((unc, idx) => (
                  <div
                    key={idx}
                    className="p-2.5 bg-amber-500/5 border border-amber-500/20 rounded-lg text-xs text-amber-300 flex items-start gap-2"
                  >
                    <AlertTriangle className="w-3.5 h-3.5 text-amber-400 shrink-0 mt-0.5" />
                    <span>{unc}</span>
                  </div>
                ))}

                {result.missing_evidence.map((gap, idx) => (
                  <div
                    key={idx}
                    className="p-2.5 bg-slate-800/40 border border-slate-700/50 rounded-lg text-xs text-slate-400 flex items-start gap-2"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5 text-slate-500 shrink-0 mt-0.5" />
                    <span>Missing Link: {gap}</span>
                  </div>
                ))}

                {result.uncertainties.length === 0 && result.missing_evidence.length === 0 && (
                  <p className="text-xs text-slate-500 italic">Topology graph context is fully resolved without missing links.</p>
                )}
              </div>
            </div>
          </div>

          {/* Detailed Graph Analytical Reasoning */}
          <div className="bg-[#151c2c] border border-[#1f2d40] rounded-xl p-6 shadow-md">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-400 mb-2 flex items-center gap-2">
              <Cpu className="w-4 h-4 text-sky-400" /> Graph Analytical Reasoning
            </h3>
            <div className="bg-[#0b0f19] border border-[#1f2d40] rounded-lg p-4 font-mono text-xs text-sky-300/90 leading-relaxed whitespace-pre-wrap">
              {result.reasoning}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

import React, { useEffect, useState } from 'react';
import { fetchDashboardSummary, fetchHealthCheck } from '../services/api';
import { DashboardSummary } from '../types';
import { TigerGraphInvestigationConsole } from '../components/TigerGraphInvestigationConsole';
import { LayoutDashboard, Network } from 'lucide-react';

export const DashboardPage: React.FC = () => {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [backendStatus, setBackendStatus] = useState<string>('checking...');
  const [activeTab, setActiveTab] = useState<'graph' | 'overview'>('graph');

  useEffect(() => {
    fetchHealthCheck().then((data) => setBackendStatus(data.status));
    fetchDashboardSummary().then((data) => setSummary(data));
  }, []);

  return (
    <div className="dashboard-container max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <header className="header flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6 pb-4 border-b border-[#1f2d40]">
        <div>
          <h1 className="text-2xl font-bold bg-gradient-to-r from-sky-400 to-indigo-400 bg-clip-text text-transparent">
            Fraud Rule Engine & Reviewer Console
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Real-time transaction risk scoring, graph evidence analysis & reviewer dashboard
          </p>
        </div>
        <div className="status-badge flex items-center gap-2 px-3 py-1 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 rounded-full text-xs font-medium">
          <span className="dot w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          FastAPI: {backendStatus}
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="flex items-center gap-2 mb-6 border-b border-[#1f2d40] pb-2">
        <button
          onClick={() => setActiveTab('graph')}
          className={`flex items-center gap-2 px-4 py-2 text-sm font-semibold rounded-lg transition-all ${
            activeTab === 'graph'
              ? 'bg-sky-500/10 text-sky-400 border border-sky-500/20'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
          }`}
        >
          <Network className="w-4 h-4" />
          TigerGraph AI Investigation Agent
        </button>

        <button
          onClick={() => setActiveTab('overview')}
          className={`flex items-center gap-2 px-4 py-2 text-sm font-semibold rounded-lg transition-all ${
            activeTab === 'overview'
              ? 'bg-sky-500/10 text-sky-400 border border-sky-500/20'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
          }`}
        >
          <LayoutDashboard className="w-4 h-4" />
          Engine Metrics Overview
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === 'graph' ? (
        <TigerGraphInvestigationConsole />
      ) : (
        <div className="space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-[#151c2c] border border-[#1f2d40] rounded-xl p-5">
              <div className="text-slate-400 text-xs font-medium mb-1">Total Evaluated</div>
              <div className="text-2xl font-bold text-slate-100">{summary?.total_transactions ?? 0}</div>
              <div className="text-xs text-slate-500 mt-1">Ingested transactions</div>
            </div>

            <div className="bg-[#151c2c] border border-[#1f2d40] rounded-xl p-5">
              <div className="text-slate-400 text-xs font-medium mb-1">Flagged Fraud</div>
              <div className="text-2xl font-bold text-rose-400">{summary?.flagged_fraud ?? 0}</div>
              <div className="text-xs text-slate-500 mt-1">Auto-rejected transactions</div>
            </div>

            <div className="bg-[#151c2c] border border-[#1f2d40] rounded-xl p-5">
              <div className="text-slate-400 text-xs font-medium mb-1">Pending Review</div>
              <div className="text-2xl font-bold text-amber-400">{summary?.under_review ?? 0}</div>
              <div className="text-xs text-slate-500 mt-1">Awaiting analyst action</div>
            </div>

            <div className="bg-[#151c2c] border border-[#1f2d40] rounded-xl p-5">
              <div className="text-slate-400 text-xs font-medium mb-1">Approval Rate</div>
              <div className="text-2xl font-bold text-emerald-400">{summary?.approval_rate ?? 100}%</div>
              <div className="text-xs text-slate-500 mt-1">Clean ratio</div>
            </div>
          </div>

          <div className="bg-[#151c2c] border border-[#1f2d40] rounded-xl p-8 text-center text-slate-400">
            <h3 className="text-base font-semibold text-slate-200">Reviewer Queue & Rule Engine Console</h3>
            <p className="text-xs text-slate-400 mt-1">
              Dynamic rule creation, velocity scoring, and manual transaction review queues.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

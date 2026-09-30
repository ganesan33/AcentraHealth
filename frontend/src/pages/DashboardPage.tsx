import React, { useEffect, useState } from 'react';
import { fetchDashboardSummary, fetchHealthCheck } from '../services/api';
import { DashboardSummary } from '../types';

export const DashboardPage: React.FC = () => {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [backendStatus, setBackendStatus] = useState<string>('checking...');

  useEffect(() => {
    fetchHealthCheck().then((data) => setBackendStatus(data.status));
    fetchDashboardSummary().then((data) => setSummary(data));
  }, []);

  return (
    <div className="dashboard-container">
      <header className="header">
        <div>
          <h1>Fraud Rule Engine Console</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '0.25rem' }}>
            Real-time transaction risk scoring & review dashboard
          </p>
        </div>
        <div className="status-badge">
          <span className="dot"></span>
          Backend: {backendStatus}
        </div>
      </header>

      <div className="grid">
        <div className="card">
          <div className="card-title">Total Evaluated</div>
          <div className="card-value">{summary?.total_transactions ?? 0}</div>
          <div className="card-subtitle">Transactions ingested</div>
        </div>

        <div className="card">
          <div className="card-title">Flagged Fraud</div>
          <div className="card-value" style={{ color: 'var(--accent-rose)' }}>
            {summary?.flagged_fraud ?? 0}
          </div>
          <div className="card-subtitle">Auto-rejected transactions</div>
        </div>

        <div className="card">
          <div className="card-title">Pending Review</div>
          <div className="card-value" style={{ color: 'var(--accent-amber)' }}>
            {summary?.under_review ?? 0}
          </div>
          <div className="card-subtitle">Awaiting analyst action</div>
        </div>

        <div className="card">
          <div className="card-title">Approval Rate</div>
          <div className="card-value" style={{ color: 'var(--accent-emerald)' }}>
            {summary?.approval_rate ?? 100}%
          </div>
          <div className="card-subtitle">Clean transaction ratio</div>
        </div>
      </div>

      <div className="placeholder-section">
        <h3>Reviewer Queue & Rule Engine Console Placeholder</h3>
        <p style={{ marginTop: '0.5rem', fontSize: '0.9rem' }}>
          Rule creation, dynamic scoring parameters, and manual transaction review queues will be rendered here.
        </p>
      </div>
    </div>
  );
};

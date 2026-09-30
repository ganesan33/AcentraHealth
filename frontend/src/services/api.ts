import { DashboardSummary, TigerGraphHealth, InvestigationResponse } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

export async function fetchHealthCheck(): Promise<{ status: string }> {
  try {
    const res = await fetch('/health');
    return await res.json();
  } catch (error) {
    console.error('Failed to fetch health check', error);
    return { status: 'offline' };
  }
}

export async function fetchTigerGraphHealth(): Promise<TigerGraphHealth> {
  try {
    const res = await fetch('/health/tigergraph');
    if (!res.ok) throw new Error('Health check error');
    return await res.json();
  } catch (error) {
    console.error('Failed to fetch TigerGraph health check', error);
    return { status: 'unhealthy', service: 'TigerGraph', graph: 'FraudGraph', host: 'http://localhost' };
  }
}

export async function fetchDashboardSummary(): Promise<DashboardSummary> {
  try {
    const res = await fetch(`${API_BASE_URL}/dashboard/summary`);
    if (!res.ok) throw new Error('Network response was not ok');
    return await res.json();
  } catch (error) {
    console.error('Error fetching dashboard summary:', error);
    return {
      total_transactions: 0,
      flagged_fraud: 0,
      under_review: 0,
      approval_rate: 100,
      recent_alerts: [],
    };
  }
}

export async function analyzeCaseGraphEvidence(caseId: string): Promise<InvestigationResponse> {
  const res = await fetch(`${API_BASE_URL}/investigation/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ case_id: caseId }),
  });

  if (!res.ok) {
    const errData = await res.json().catch(() => ({ detail: 'Investigation failed' }));
    throw new Error(errData.detail || 'Failed to analyze case graph evidence');
  }

  return await res.json();
}

export async function testGraphTransactionIngestion(payload?: Record<string, unknown>): Promise<{ status: string; message: string; data: Record<string, unknown> }> {
  const res = await fetch(`${API_BASE_URL}/graph/test-transaction`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload || {}),
  });

  if (!res.ok) {
    throw new Error('Failed to ingest test transaction');
  }

  return await res.json();
}

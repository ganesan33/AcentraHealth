import { DashboardSummary } from '../types';

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

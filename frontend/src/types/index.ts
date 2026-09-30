export type FraudDecision = 'APPROVE' | 'REVIEW' | 'REJECT';

export interface RuleResult {
  rule_id: string;
  rule_name: string;
  triggered: boolean;
  score_impact: number;
  reason?: string;
  metadata?: Record<string, unknown>;
}

export interface FraudEvaluation {
  transaction_id: string;
  decision: FraudDecision;
  risk_score: number;
  triggered_rules: RuleResult[];
  all_rule_results: RuleResult[];
  evaluation_time_ms: number;
}

export interface DashboardSummary {
  total_transactions: number;
  flagged_fraud: number;
  under_review: number;
  approval_rate: number;
  recent_alerts: FraudEvaluation[];
}

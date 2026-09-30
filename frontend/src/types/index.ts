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

export type EvidenceSignificance = 'LOW' | 'MEDIUM' | 'HIGH' | 'NEUTRAL';

export interface KeyEvidenceItem {
  evidence_id: string;
  finding: string;
  significance: EvidenceSignificance;
}

export interface InvestigationRequest {
  case_id: string;
  include_raw_graph?: boolean;
}

export interface InvestigationResponse {
  summary: string;
  key_evidence: KeyEvidenceItem[];
  observed_patterns: string[];
  conflicting_evidence: string[];
  missing_evidence: string[];
  uncertainties: string[];
  relevant_rules: string[];
  reasoning: string;
}

export interface TigerGraphHealth {
  status: string;
  service: string;
  graph?: string;
  host?: string;
}

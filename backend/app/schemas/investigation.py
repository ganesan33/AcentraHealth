from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class EvidenceSignificance(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    NEUTRAL = "NEUTRAL"


class PolicyRule(str, Enum):
    R1 = "R1"  # Low Risk Baseline
    R2 = "R2"  # Pending Evidence
    R3 = "R3"  # Dispute
    R4 = "R4"  # Stolen Card
    R5 = "R5"  # VPN Spoofing
    R6 = "R6"  # Mismatch
    R7 = "R7"  # Historical Fraud
    R8 = "R8"  # Velocity Testing
    R9 = "R9"  # Risk Signal Only
    R10 = "R10"  # Pending Override


class KeyEvidenceItem(BaseModel):
    evidence_id: str = Field(..., description="Unique evidence tracking ID (e.g., EV-1)")
    finding: str = Field(..., description="Factual observation from graph traversal")
    significance: EvidenceSignificance = Field(..., description="Risk significance level")


class InvestigationRequest(BaseModel):
    case_id: str = Field(..., description="Target ClosedCase vertex ID to investigate")
    include_raw_graph: bool = Field(False, description="Whether to include raw graph topology in response metadata")


class InvestigationResponse(BaseModel):
    summary: str = Field(..., description="Concise summary of the case and graph topology findings")
    key_evidence: List[KeyEvidenceItem] = Field(..., description="Mapped graph findings with significance levels")
    observed_patterns: List[str] = Field(default_factory=list, description="List of observed fraud velocity/device/location patterns")
    conflicting_evidence: List[str] = Field(default_factory=list, description="List of contradictory graph observations")
    missing_evidence: List[str] = Field(default_factory=list, description="List of unlinked vertices or missing data gaps")
    uncertainties: List[str] = Field(default_factory=list, description="Open questions or unverified graph facts")
    relevant_rules: List[PolicyRule] = Field(default_factory=list, description="Triggered policy rules from R1-R10")
    reasoning: str = Field(..., description="Detailed graph-driven analytical reasoning")

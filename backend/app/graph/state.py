from typing import TypedDict, Optional, List, Dict, Any
from datetime import datetime


class ClaimState(TypedDict):
    # ── Input ─────────────────────────────────────────
    claim_id: str
    company_slug: str
    description: str
    customer_name: Optional[str]
    policy_number: Optional[str]

    # ── Classifier output ──────────────────────────────
    claim_type: Optional[str]           # health|motor|property|life|travel|liability
    claim_type_confidence: Optional[float]

    # ── Policy validator output ────────────────────────
    is_covered: Optional[bool]
    coverage_details: Optional[str]
    policy_references: Optional[List[str]]

    # ── Fraud scorer output ────────────────────────────
    fraud_score: Optional[int]          # 1-5
    fraud_flags: Optional[List[str]]

    # ── Priority scorer output ─────────────────────────
    priority_score: Optional[int]       # 1-5
    priority_reason: Optional[str]

    # ── Router output ──────────────────────────────────
    assigned_department: Optional[str]
    status: Optional[str]               # routed|flagged|needs_info

    # ── Response composer output ───────────────────────
    customer_response: Optional[str]
    documents_required: Optional[List[str]]
    estimated_timeline: Optional[str]

    # ── Trace ──────────────────────────────────────────
    agent_traces: List[Dict[str, Any]]
    errors: List[str]
    start_time: Optional[str]

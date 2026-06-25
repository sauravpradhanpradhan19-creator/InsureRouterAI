from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ClaimType(str, Enum):
    HEALTH    = "health"
    MOTOR     = "motor"
    PROPERTY  = "property"
    LIFE      = "life"
    TRAVEL    = "travel"
    LIABILITY = "liability"


class ClaimStatus(str, Enum):
    PENDING    = "pending"
    PROCESSING = "processing"
    ROUTED     = "routed"
    FLAGGED    = "flagged"
    NEEDS_INFO = "needs_info"


# ── Requests ──────────────────────────────────────────────────────────────────

class SubmitClaimRequest(BaseModel):
    company_slug: str = Field(..., description="Company identifier e.g. demo_hdfc, demo_star")
    description: str = Field(..., min_length=10, max_length=3000)
    customer_name: Optional[str] = None
    policy_number: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "company_slug": "demo_hdfc",
                "description": "I was hospitalized for 3 days due to dengue fever. Total bill is Rs 45,000. I have all original bills and discharge summary.",
                "customer_name": "Rahul Sharma",
                "policy_number": "HDFC-2024-98765",
            }
        }


class IngestPDFRequest(BaseModel):
    company_slug: str
    company_name: str


# ── Responses ─────────────────────────────────────────────────────────────────

class AgentTraceResponse(BaseModel):
    agent_name: str
    status: str
    input_summary: Optional[str]
    output_summary: Optional[str]
    time_ms: Optional[int]
    error: Optional[str]


class SubmitClaimResponse(BaseModel):
    claim_id: str
    status: ClaimStatus
    claim_type: Optional[ClaimType]
    claim_type_confidence: Optional[float]
    is_covered: Optional[bool]
    coverage_details: Optional[str]
    fraud_score: Optional[int]
    priority_score: Optional[int]
    assigned_department: Optional[str]
    customer_response: str
    documents_required: List[str]
    estimated_timeline: Optional[str]
    policy_references: List[str]
    agent_traces: List[AgentTraceResponse]
    processing_time_ms: int
    created_at: datetime


class ClaimSummaryResponse(BaseModel):
    claim_id: str
    company_slug: str
    status: str
    claim_type: Optional[str]
    priority_score: Optional[int]
    fraud_score: Optional[int]
    assigned_department: Optional[str]
    customer_name: Optional[str]
    processing_time_ms: int
    created_at: datetime


class MetricsResponse(BaseModel):
    total_claims: int
    routed_count: int
    flagged_count: int
    routing_rate: float
    flag_rate: float
    avg_processing_time_ms: float
    claims_by_type: Dict[str, int]


class CompanyResponse(BaseModel):
    id: str
    name: str
    slug: str
    is_active: bool

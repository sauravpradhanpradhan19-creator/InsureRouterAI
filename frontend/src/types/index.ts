export type ClaimType = 'health' | 'motor' | 'property' | 'life' | 'travel' | 'liability'
export type ClaimStatus = 'pending' | 'processing' | 'routed' | 'flagged' | 'needs_info'

export interface AgentTrace {
  agent_name: string
  status: string
  input_summary: string | null
  output_summary: string | null
  time_ms: number | null
  error: string | null
}

export interface ClaimResult {
  claim_id: string
  status: ClaimStatus
  claim_type: ClaimType | null
  claim_type_confidence: number | null
  is_covered: boolean | null
  coverage_details: string | null
  fraud_score: number | null
  priority_score: number | null
  assigned_department: string | null
  customer_response: string
  documents_required: string[]
  estimated_timeline: string | null
  policy_references: string[]
  agent_traces: AgentTrace[]
  processing_time_ms: number
  created_at: string
}

export interface ClaimSummary {
  claim_id: string
  company_slug: string
  status: string
  claim_type: string | null
  priority_score: number | null
  fraud_score: number | null
  assigned_department: string | null
  customer_name: string | null
  processing_time_ms: number
  created_at: string
}

export interface Company {
  id: string
  name: string
  slug: string
  is_active: boolean
}

export interface Metrics {
  total_claims: number
  routed_count: number
  flagged_count: number
  routing_rate: number
  flag_rate: number
  avg_processing_time_ms: number
  claims_by_type: Record<string, number>
}

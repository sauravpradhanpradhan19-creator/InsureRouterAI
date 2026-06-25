import time
import uuid
import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.database import crud
from app.api.models import SubmitClaimRequest, SubmitClaimResponse, ClaimSummaryResponse
from app.graph.pipeline import claim_graph
from app.graph.state import ClaimState

router = APIRouter()


@router.post("/submit", response_model=SubmitClaimResponse)
async def submit_claim(req: SubmitClaimRequest, db: AsyncSession = Depends(get_db)):
    """Submit a new insurance claim — runs through full LangGraph pipeline."""

    # Validate company exists
    company = await crud.get_company_by_slug(db, req.company_slug)
    if not company:
        raise HTTPException(status_code=404, detail=f"Company '{req.company_slug}' not found")

    # Create claim record in DB
    claim = await crud.create_claim(
        db,
        company_id=company.id,
        company_slug=req.company_slug,
        description=req.description,
        customer_name=req.customer_name,
        policy_number=req.policy_number,
    )

    # Update status to processing
    await crud.update_claim(db, claim.id, status="processing")

    # Build initial state
    initial_state: ClaimState = {
        "claim_id": claim.id,
        "company_slug": req.company_slug,
        "description": req.description,
        "customer_name": req.customer_name,
        "policy_number": req.policy_number,
        "claim_type": None,
        "claim_type_confidence": None,
        "is_covered": None,
        "coverage_details": None,
        "policy_references": [],
        "fraud_score": None,
        "fraud_flags": [],
        "priority_score": None,
        "priority_reason": None,
        "assigned_department": None,
        "status": None,
        "customer_response": None,
        "documents_required": [],
        "estimated_timeline": None,
        "agent_traces": [],
        "errors": [],
        "start_time": datetime.utcnow().isoformat(),
    }

    # Run LangGraph pipeline
    t0 = time.time()
    try:
        final_state = await claim_graph.ainvoke(initial_state)
    except Exception as e:
        await crud.update_claim(db, claim.id, status="failed")
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")

    processing_time = int((time.time() - t0) * 1000)

    # Persist results
    await crud.update_claim(
        db,
        claim.id,
        claim_type=final_state.get("claim_type"),
        claim_type_confidence=final_state.get("claim_type_confidence"),
        is_covered=final_state.get("is_covered"),
        coverage_details=final_state.get("coverage_details"),
        policy_references=json.dumps(final_state.get("policy_references", [])),
        fraud_score=final_state.get("fraud_score"),
        priority_score=final_state.get("priority_score"),
        assigned_department=final_state.get("assigned_department"),
        status=final_state.get("status", "routed"),
        customer_response=final_state.get("customer_response"),
        documents_required=json.dumps(final_state.get("documents_required", [])),
        agent_traces=final_state.get("agent_traces", []),
        processing_time_ms=processing_time,
    )

    return SubmitClaimResponse(
        claim_id=claim.id,
        status=final_state.get("status", "routed"),
        claim_type=final_state.get("claim_type"),
        claim_type_confidence=final_state.get("claim_type_confidence"),
        is_covered=final_state.get("is_covered"),
        coverage_details=final_state.get("coverage_details"),
        fraud_score=final_state.get("fraud_score"),
        priority_score=final_state.get("priority_score"),
        assigned_department=final_state.get("assigned_department"),
        customer_response=final_state.get("customer_response", ""),
        documents_required=final_state.get("documents_required", []),
        estimated_timeline=final_state.get("estimated_timeline"),
        policy_references=final_state.get("policy_references", []),
        agent_traces=final_state.get("agent_traces", []),
        processing_time_ms=processing_time,
        created_at=claim.created_at,
    )


@router.get("/{claim_id}", response_model=SubmitClaimResponse)
async def get_claim(claim_id: str, db: AsyncSession = Depends(get_db)):
    claim = await crud.get_claim(db, claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    return SubmitClaimResponse(
        claim_id=claim.id,
        status=claim.status,
        claim_type=claim.claim_type,
        claim_type_confidence=claim.claim_type_confidence,
        is_covered=claim.is_covered,
        coverage_details=claim.coverage_details,
        fraud_score=claim.fraud_score,
        priority_score=claim.priority_score,
        assigned_department=claim.assigned_department,
        customer_response=claim.customer_response or "",
        documents_required=json.loads(claim.documents_required or "[]"),
        estimated_timeline=None,
        policy_references=json.loads(claim.policy_references or "[]"),
        agent_traces=claim.agent_traces or [],
        processing_time_ms=claim.processing_time_ms,
        created_at=claim.created_at,
    )


@router.get("/", response_model=list[ClaimSummaryResponse])
async def list_claims(db: AsyncSession = Depends(get_db)):
    claims = await crud.get_all_claims(db)
    return [
        ClaimSummaryResponse(
            claim_id=c.id,
            company_slug=c.company_slug,
            status=c.status,
            claim_type=c.claim_type,
            priority_score=c.priority_score,
            fraud_score=c.fraud_score,
            assigned_department=c.assigned_department,
            customer_name=c.customer_name,
            processing_time_ms=c.processing_time_ms,
            created_at=c.created_at,
        )
        for c in claims
    ]

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database.models import Claim, Company, AgentTrace
from datetime import datetime
from typing import List, Optional, Dict, Any
import json


# ── Company CRUD ──────────────────────────────────────────────────────────────

async def create_company(db: AsyncSession, name: str, slug: str, kb_path: str) -> Company:
    company = Company(name=name, slug=slug, kb_path=kb_path)
    db.add(company)
    await db.commit()
    await db.refresh(company)
    return company


async def get_company_by_slug(db: AsyncSession, slug: str) -> Optional[Company]:
    result = await db.execute(select(Company).where(Company.slug == slug))
    return result.scalar_one_or_none()


async def get_all_companies(db: AsyncSession) -> List[Company]:
    result = await db.execute(select(Company).where(Company.is_active == True))
    return result.scalars().all()


# ── Claim CRUD ────────────────────────────────────────────────────────────────

async def create_claim(
    db: AsyncSession,
    company_id: str,
    company_slug: str,
    description: str,
    customer_name: Optional[str] = None,
    policy_number: Optional[str] = None,
) -> Claim:
    claim = Claim(
        company_id=company_id,
        company_slug=company_slug,
        description=description,
        customer_name=customer_name,
        policy_number=policy_number,
        status="pending",
    )
    db.add(claim)
    await db.commit()
    await db.refresh(claim)
    return claim


async def update_claim(db: AsyncSession, claim_id: str, **kwargs) -> Optional[Claim]:
    result = await db.execute(select(Claim).where(Claim.id == claim_id))
    claim = result.scalar_one_or_none()
    if claim:
        for key, value in kwargs.items():
            setattr(claim, key, value)
        claim.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(claim)
    return claim


async def get_claim(db: AsyncSession, claim_id: str) -> Optional[Claim]:
    result = await db.execute(select(Claim).where(Claim.id == claim_id))
    return result.scalar_one_or_none()


async def get_all_claims(db: AsyncSession, limit: int = 50) -> List[Claim]:
    result = await db.execute(
        select(Claim).order_by(Claim.created_at.desc()).limit(limit)
    )
    return result.scalars().all()


async def get_flagged_claims(db: AsyncSession) -> List[Claim]:
    result = await db.execute(
        select(Claim)
        .where(Claim.status == "flagged")
        .order_by(Claim.fraud_score.desc())
    )
    return result.scalars().all()


# ── Metrics ───────────────────────────────────────────────────────────────────

async def get_metrics(db: AsyncSession) -> Dict[str, Any]:
    total = (await db.execute(select(func.count(Claim.id)))).scalar() or 0
    routed = (await db.execute(select(func.count(Claim.id)).where(Claim.status == "routed"))).scalar() or 0
    flagged = (await db.execute(select(func.count(Claim.id)).where(Claim.status == "flagged"))).scalar() or 0
    avg_time = (await db.execute(select(func.avg(Claim.processing_time_ms)).where(Claim.processing_time_ms > 0))).scalar() or 0

    claim_types: Dict[str, int] = {}
    for ct in ["health", "motor", "property", "life", "travel", "liability"]:
        count = (await db.execute(select(func.count(Claim.id)).where(Claim.claim_type == ct))).scalar() or 0
        claim_types[ct] = count

    return {
        "total_claims": total,
        "routed_count": routed,
        "flagged_count": flagged,
        "routing_rate": round((routed / total * 100), 2) if total else 0,
        "flag_rate": round((flagged / total * 100), 2) if total else 0,
        "avg_processing_time_ms": round(avg_time, 2),
        "claims_by_type": claim_types,
    }

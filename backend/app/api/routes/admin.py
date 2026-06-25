from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
import tempfile
import os

from app.database.connection import get_db
from app.database import crud
from app.api.models import MetricsResponse, CompanyResponse, IngestPDFRequest
from app.rag.knowledge_base import ingest_pdf

router = APIRouter()


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics(db: AsyncSession = Depends(get_db)):
    return await crud.get_metrics(db)


@router.get("/companies", response_model=list[CompanyResponse])
async def list_companies(db: AsyncSession = Depends(get_db)):
    companies = await crud.get_all_companies(db)
    return [CompanyResponse(id=c.id, name=c.name, slug=c.slug, is_active=c.is_active) for c in companies]


@router.post("/companies")
async def create_company(name: str, slug: str, db: AsyncSession = Depends(get_db)):
    existing = await crud.get_company_by_slug(db, slug)
    if existing:
        raise HTTPException(status_code=400, detail="Company slug already exists")
    from app.config import settings
    kb_path = os.path.join(settings.KB_BASE_PATH, slug)
    company = await crud.create_company(db, name=name, slug=slug, kb_path=kb_path)
    return CompanyResponse(id=company.id, name=company.name, slug=company.slug, is_active=company.is_active)


@router.post("/ingest-pdf")
async def ingest_company_pdf(
    company_slug: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Upload a policy PDF and ingest it into the company's knowledge base."""
    company = await crud.get_company_by_slug(db, company_slug)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files supported")

    # Save to temp file and ingest
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        chunks = ingest_pdf(tmp_path, company_slug)
    finally:
        os.unlink(tmp_path)

    return {"message": f"Ingested {chunks} chunks from {file.filename}", "company_slug": company_slug}


@router.get("/flagged")
async def get_flagged_claims(db: AsyncSession = Depends(get_db)):
    claims = await crud.get_flagged_claims(db)
    return [{"claim_id": c.id, "fraud_score": c.fraud_score,
             "company_slug": c.company_slug, "description": c.description[:200],
             "created_at": c.created_at} for c in claims]

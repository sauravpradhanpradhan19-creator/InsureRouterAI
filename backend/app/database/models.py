from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy import String, Float, Boolean, Integer, DateTime, Text, JSON
from datetime import datetime
import uuid


class Base(DeclarativeBase):
    pass


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)  # e.g. "hdfc", "star"
    kb_path: Mapped[str] = mapped_column(String(500), nullable=False)            # path to FAISS index
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Claim(Base):
    __tablename__ = "claims"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id: Mapped[str] = mapped_column(String, nullable=False)
    company_slug: Mapped[str] = mapped_column(String(100), nullable=False)
    customer_name: Mapped[str] = mapped_column(String(200), nullable=True)
    policy_number: Mapped[str] = mapped_column(String(100), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Classification results
    claim_type: Mapped[str] = mapped_column(String(100), nullable=True)
    claim_type_confidence: Mapped[float] = mapped_column(Float, default=0.0)

    # Scores
    priority_score: Mapped[int] = mapped_column(Integer, default=0)    # 1-5
    fraud_score: Mapped[int] = mapped_column(Integer, default=0)        # 1-5

    # Routing
    assigned_department: Mapped[str] = mapped_column(String(200), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending")  # pending | processing | routed | flagged

    # Policy validation
    is_covered: Mapped[bool] = mapped_column(Boolean, nullable=True)
    coverage_details: Mapped[str] = mapped_column(Text, nullable=True)
    policy_references: Mapped[str] = mapped_column(Text, nullable=True)  # JSON list of source pages

    # Response
    customer_response: Mapped[str] = mapped_column(Text, nullable=True)
    documents_required: Mapped[str] = mapped_column(Text, nullable=True)  # JSON list

    # Agent traces (JSON)
    agent_traces: Mapped[dict] = mapped_column(JSON, default=list)

    processing_time_ms: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AgentTrace(Base):
    __tablename__ = "agent_traces"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    claim_id: Mapped[str] = mapped_column(String, nullable=False)
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    input_summary: Mapped[str] = mapped_column(Text, nullable=True)
    output_summary: Mapped[str] = mapped_column(Text, nullable=True)
    time_ms: Mapped[int] = mapped_column(Integer, default=0)
    error: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

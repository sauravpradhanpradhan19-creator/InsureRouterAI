import os
import json
from pathlib import Path
from typing import Optional, List, Dict
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from app.config import settings

import logging
logger = logging.getLogger(__name__)


# ── Shared embedding model (loaded once) ──────────────────────────────────────

_embeddings: Optional[HuggingFaceEmbeddings] = None

def get_embeddings() -> HuggingFaceEmbeddings:
    global _embeddings
    if _embeddings is None:
        logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
        _embeddings = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
    return _embeddings


# ── Vector store registry ─────────────────────────────────────────────────────

_stores: Dict[str, FAISS] = {}   # company_slug → FAISS index
_shared_store: Optional[FAISS] = None


def load_all_stores():
    """Load all existing FAISS indexes from disk on startup."""
    global _shared_store
    kb_base = Path(settings.KB_BASE_PATH)
    emb = get_embeddings()

    # Load shared KB
    shared_path = kb_base / "shared"
    if (shared_path / "index.faiss").exists():
        _shared_store = FAISS.load_local(str(shared_path), emb, allow_dangerous_deserialization=True)
        logger.info("✅ Shared KB loaded")
    else:
        logger.warning("⚠️  No shared KB found at kb/shared/ — skipping")

    # Load company KBs
    for folder in kb_base.iterdir():
        if folder.is_dir() and folder.name != "shared":
            index_file = folder / "index.faiss"
            if index_file.exists():
                try:
                    _stores[folder.name] = FAISS.load_local(
                        str(folder), emb, allow_dangerous_deserialization=True
                    )
                    logger.info(f"✅ KB loaded for company: {folder.name}")
                except Exception as e:
                    logger.error(f"Failed to load KB for {folder.name}: {e}")


def get_retriever(company_slug: str):
    """Return a retriever that merges company KB + shared KB."""
    from langchain.retrievers import MergerRetriever

    retrievers = []

    if company_slug in _stores:
        retrievers.append(
            _stores[company_slug].as_retriever(search_kwargs={"k": settings.RAG_TOP_K})
        )
    else:
        logger.warning(f"No KB found for company: {company_slug}")

    if _shared_store:
        retrievers.append(
            _shared_store.as_retriever(search_kwargs={"k": 2})
        )

    if not retrievers:
        return None

    if len(retrievers) == 1:
        return retrievers[0]

    return MergerRetriever(retrievers=retrievers)


# ── Ingestion pipeline ────────────────────────────────────────────────────────

def ingest_pdf(pdf_path: str, company_slug: str) -> int:
    """
    Ingest a PDF into a company's FAISS index.
    Creates or updates the index. Returns number of chunks added.
    """
    import fitz  # PyMuPDF

    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    # Extract text
    doc = fitz.open(str(pdf_path))
    raw_text = ""
    for page_num, page in enumerate(doc):
        text = page.get_text()
        raw_text += f"\n[Page {page_num + 1}]\n{text}"
    doc.close()

    if not raw_text.strip():
        raise ValueError("PDF appears to be empty or scanned (no extractable text)")

    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " "],
    )
    chunks = splitter.create_documents(
        texts=[raw_text],
        metadatas=[{"source": pdf_path.name, "company": company_slug}],
    )

    emb = get_embeddings()
    kb_path = Path(settings.KB_BASE_PATH) / company_slug

    if (kb_path / "index.faiss").exists():
        # Update existing index
        store = FAISS.load_local(str(kb_path), emb, allow_dangerous_deserialization=True)
        store.add_documents(chunks)
    else:
        # Create new index
        kb_path.mkdir(parents=True, exist_ok=True)
        store = FAISS.from_documents(chunks, emb)

    store.save_local(str(kb_path))
    _stores[company_slug] = store

    logger.info(f"Ingested {len(chunks)} chunks for {company_slug} from {pdf_path.name}")
    return len(chunks)


def ingest_text(text: str, company_slug: str, source_name: str = "manual") -> int:
    """Ingest raw text (useful for demo data without real PDFs)."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
    )
    chunks = splitter.create_documents(
        texts=[text],
        metadatas=[{"source": source_name, "company": company_slug}],
    )

    emb = get_embeddings()
    kb_path = Path(settings.KB_BASE_PATH) / company_slug

    if (kb_path / "index.faiss").exists():
        store = FAISS.load_local(str(kb_path), emb, allow_dangerous_deserialization=True)
        store.add_documents(chunks)
    else:
        kb_path.mkdir(parents=True, exist_ok=True)
        store = FAISS.from_documents(chunks, emb)

    store.save_local(str(kb_path))
    _stores[company_slug] = store
    return len(chunks)


def query_kb(company_slug: str, query: str, k: int = 4) -> List[Document]:
    """Direct KB query — returns relevant chunks."""
    retriever = get_retriever(company_slug)
    if retriever is None:
        return []
    return retriever.get_relevant_documents(query)

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

# Set LangSmith env vars before any langchain import
os.environ["LANGCHAIN_TRACING_V2"]  = str(settings.LANGCHAIN_TRACING_V2).lower()
os.environ["LANGCHAIN_API_KEY"]     = settings.LANGCHAIN_API_KEY
os.environ["LANGCHAIN_PROJECT"]     = settings.LANGCHAIN_PROJECT
os.environ["LANGCHAIN_ENDPOINT"]    = settings.LANGCHAIN_ENDPOINT


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"🚀 Starting {settings.APP_NAME}")

    # Init database
    from app.database.connection import init_db
    await init_db()
    print("✅ Database ready")

    # Seed demo companies
    from app.database.connection import AsyncSessionLocal
    from app.database import crud
    async with AsyncSessionLocal() as db:
        for slug, name in [("demo_hdfc", "HDFC Ergo"), ("demo_star", "Star Health")]:
            existing = await crud.get_company_by_slug(db, slug)
            if not existing:
                from app.config import settings as s
                import os
                await crud.create_company(
                    db, name=name, slug=slug,
                    kb_path=os.path.join(s.KB_BASE_PATH, slug)
                )
                print(f"✅ Company registered: {name}")

    # Seed demo KB
    from app.rag.demo_seed import seed_demo_kb
    await seed_demo_kb()
    print("✅ Knowledge base ready")

    # Load all FAISS indexes
    from app.rag.knowledge_base import load_all_stores
    load_all_stores()
    print("✅ Vector stores loaded")

    yield
    print("👋 Shutting down InsurRoute AI")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered insurance claim routing using LangGraph + Groq",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.routes import claims, admin, health
app.include_router(health.router, tags=["Health"])
app.include_router(claims.router, prefix="/claims", tags=["Claims"])
app.include_router(admin.router,  prefix="/admin",  tags=["Admin"])


@app.get("/")
async def root():
    return {"name": settings.APP_NAME, "version": settings.APP_VERSION,
            "status": "running", "docs": "/docs"}

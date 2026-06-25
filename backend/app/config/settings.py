from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # App
    APP_NAME: str = "InsurRoute AI"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # LLM
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.1-8b-instant"          # fast + free
    GROQ_MODEL_LARGE: str = "llama-3.1-70b-versatile" # for complex tasks

    # LangSmith
    LANGCHAIN_API_KEY: str = ""
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_PROJECT: str = "insurance-claim-router"
    LANGCHAIN_ENDPOINT: str = "https://api.smith.langchain.com"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/claims.db"

    # RAG
    KB_BASE_PATH: str = "./kb"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"  # free, runs locally
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    RAG_TOP_K: int = 4

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:5173"

    @property
    def cors_origins(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()

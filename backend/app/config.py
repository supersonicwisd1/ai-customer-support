from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Keys
    openai_api_key: str
    pinecone_api_key: str
    pinecone_environment: str = "us-east-1-gcp"

    # Database 
    database_url: str = "sqlite:///./aven_ai.db"
    redis_url: str = "redis://localhost:6379"

    # Search APIs 
    google_search_api_key: Optional[str] = None
    google_search_engine_id: Optional[str] = None

    # Pinecone
    pinecone_index: Optional[str] = None
    pinecone_index_name: Optional[str] = None

    # Firecrawl
    firecrawl_api_key: Optional[str] = None

    # APP Settings
    debug: bool = False
    cors_origins: list[str] = ["*"]

    base_url: str = "https://aven.com"

    # OpenAI
    class Config:
        env_file = ".env"

settings = Settings()
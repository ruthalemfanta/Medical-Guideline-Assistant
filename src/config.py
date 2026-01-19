"""Configuration management for the Medical Guideline Assistant."""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with validation."""
    
    # API Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    google_api_key: Optional[str] = Field(None, env="GOOGLE_API_KEY")
    
    # Database Configuration
    chroma_persist_directory: str = Field("./data/chroma_db", env="CHROMA_PERSIST_DIRECTORY")
    
    # Retrieval Configuration
    max_retrieval_docs: int = Field(10, env="MAX_RETRIEVAL_DOCS")
    rerank_top_k: int = Field(5, env="RERANK_TOP_K")
    chunk_size: int = Field(1000, env="CHUNK_SIZE")
    chunk_overlap: int = Field(200, env="CHUNK_OVERLAP")
    
    # Safety Configuration
    enable_safety_checks: bool = Field(True, env="ENABLE_SAFETY_CHECKS")
    require_citations: bool = Field(True, env="REQUIRE_CITATIONS")
    educational_disclaimer: bool = Field(True, env="EDUCATIONAL_DISCLAIMER")
    
    # Logging
    log_level: str = Field("INFO", env="LOG_LEVEL")
    
    # Supported guideline sources
    supported_sources: List[str] = [
        "WHO", "CDC", "NICE", "AHA", "ESC", "ACP", "USPSTF"
    ]
    
    # Medical intent categories
    medical_intents: List[str] = [
        "definition", "recommendation", "contraindication", 
        "procedure", "diagnosis", "treatment", "scope_violation"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
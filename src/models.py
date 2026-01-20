"""Data models for the Medical Guideline Assistant."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class MedicalIntent(str, Enum):
    """Medical query intent categories."""
    DEFINITION = "definition"
    RECOMMENDATION = "recommendation"
    CONTRAINDICATION = "contraindication"
    PROCEDURE = "procedure"
    DIAGNOSIS = "diagnosis"
    TREATMENT = "treatment"
    CONVERSATIONAL = "conversational"
    SCOPE_VIOLATION = "scope_violation"


class PopulationType(str, Enum):
    """Patient population types."""
    ADULT = "adult"
    PEDIATRIC = "pediatric"
    ELDERLY = "elderly"
    PREGNANT = "pregnant"
    GENERAL = "general"


class GuidelineMetadata(BaseModel):
    """Metadata for medical guideline documents."""
    guideline_name: str
    organization: str
    publication_year: int
    version: Optional[str] = None
    country: Optional[str] = None
    specialty: Optional[str] = None
    last_updated: Optional[datetime] = None


class ChunkMetadata(BaseModel):
    """Metadata for document chunks."""
    guideline: str
    section: str
    subsection: Optional[str] = None
    population: PopulationType = PopulationType.GENERAL
    page_number: Optional[int] = None
    chunk_id: str
    guideline_metadata: GuidelineMetadata


class QueryAnalysis(BaseModel):
    """Analysis of user query."""
    original_query: str
    intent: MedicalIntent
    population: Optional[PopulationType] = None
    condition: Optional[str] = None
    intervention: Optional[str] = None
    is_safe: bool = True
    risk_factors: List[str] = []
    decomposed_queries: List[str] = []


class RetrievedDocument(BaseModel):
    """Retrieved document with metadata."""
    content: str
    metadata: ChunkMetadata
    relevance_score: float
    rerank_score: Optional[float] = None


class Citation(BaseModel):
    """Citation information."""
    guideline_name: str
    section: str
    page_number: Optional[int] = None
    organization: str
    year: int
    quote: str
    
    @property
    def source(self) -> str:
        """Get source name for frontend compatibility."""
        return self.guideline_name


class SafetyCheck(BaseModel):
    """Safety validation results."""
    is_safe: bool
    violations: List[str] = []
    requires_disclaimer: bool = True
    refusal_reason: Optional[str] = None


class MedicalResponse(BaseModel):
    """Complete medical guideline response."""
    query: str
    answer: str
    citations: List[Citation]
    safety_check: SafetyCheck
    confidence_score: float
    retrieved_documents: List[RetrievedDocument]
    disclaimer: str
    timestamp: datetime = Field(default_factory=datetime.now)
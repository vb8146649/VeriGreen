"""Pydantic schemas matching SPEC.md §3.2."""

from pydantic import BaseModel, Field
from typing import Optional


class AuditRequest(BaseModel):
    """Input for starting an audit."""
    source_type: str = Field(default="file", description="'file' or 'url'")
    source_value: Optional[str] = None
    company_name: str
    report_year: Optional[str] = None


class AuditResponse(BaseModel):
    """Returned immediately after POST /audit."""
    audit_id: str
    status: str = "processing"
    message: str = "Audit started. Poll GET /audit/{id} for results."


class EvidenceSnippet(BaseModel):
    """A single evidence snippet retrieved from the vector store."""
    chunk_index: Optional[int] = None
    snippet: str = ""
    source_page: Optional[int] = None
    relevance_score: Optional[float] = None


class ClaimSchema(BaseModel):
    """A single ESG claim detected in a report."""
    claim_id: str
    chunk_index: int = 0
    text: str
    pillar: str = ""
    score: int = 0
    final_score: int = 0
    reason: str = ""
    verdict: str = ""
    evidence: list[EvidenceSnippet] = []
    citations: list[str] = []


class PillarScores(BaseModel):
    Environmental: float = 0.0
    Social: float = 0.0
    Governance: float = 0.0


class AuditSummary(BaseModel):
    total_claims: int = 0
    verified: int = 0
    flagged: int = 0
    pillar_scores: PillarScores = PillarScores()
    overall_score: float = 0.0


class AuditReport(BaseModel):
    """Full audit result returned by GET /audit/{id}."""
    audit_id: str
    company_name: str = ""
    report_year: str = ""
    status: str = "pending"
    created_at: str = ""
    completed_at: Optional[str] = None
    summary: AuditSummary = AuditSummary()
    claims: list[ClaimSchema] = []
    report_pdf_path: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    api: str = "ok"
    ollama: str = "unknown"
    ollama_model: str = ""
    chromadb: str = "unknown"
    sqlite: str = "unknown"
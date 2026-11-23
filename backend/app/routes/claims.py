"""Claims listing endpoint."""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import json

from app.database import get_db, get_claims_by_audit
from app.models.schemas import ClaimSchema, EvidenceSnippet
from app.config import settings

router = APIRouter()


@router.get("/claims/{audit_id}")
async def list_claims(
    audit_id: str,
    pillar: Optional[str] = Query(None, description="Filter by pillar: Environmental, Social, Governance"),
    max_score: Optional[int] = Query(None, ge=1, le=5, description="Maximum score to include"),
    sort: Optional[str] = Query("score", description="Sort by: score or pillar"),
):
    """List all claims for an audit with optional filters."""
    db = await get_db(settings.DATABASE_URL)
    claims_raw = await get_claims_by_audit(db, audit_id)
    await db.close()

    if not claims_raw:
        return []

    claims = []
    for c in claims_raw:
        evidence = []
        if isinstance(c.get("evidence"), list):
            for ev in c["evidence"]:
                evidence.append(EvidenceSnippet(
                    chunk_index=ev.get("chunk_index"),
                    snippet=ev.get("snippet", ""),
                    source_page=ev.get("source_page"),
                    relevance_score=ev.get("relevance_score"),
                ))

        citations = c.get("citations", [])
        if isinstance(citations, str):
            try:
                citations = json.loads(citations)
            except Exception:
                citations = []

        claim = ClaimSchema(
            claim_id=c["id"],
            chunk_index=c.get("chunk_index", 0),
            text=c.get("text", ""),
            pillar=c.get("pillar", ""),
            score=c.get("score", 0),
            final_score=c.get("final_score", 0),
            reason=c.get("reason", ""),
            verdict=c.get("verdict", ""),
            evidence=evidence,
            citations=citations,
        )
        claims.append(claim)

    # Apply filters
    if pillar:
        claims = [c for c in claims if c.pillar == pillar]
    if max_score:
        claims = [c for c in claims if (c.final_score or c.score) <= max_score]

    # Sort
    if sort == "pillar":
        claims.sort(key=lambda c: c.pillar)
    else:
        claims.sort(key=lambda c: c.final_score or c.score)

    return claims

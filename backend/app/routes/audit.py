"""Audit routes: POST /audit and GET /audit/{audit_id}."""

import os
import uuid
import json
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks, HTTPException, Query
from fastapi.responses import FileResponse
from typing import Optional

from app.config import settings
from app.database import get_db, create_audit, update_audit, get_audit, get_claims_by_audit, get_recent_audits, get_claim
from app.models.schemas import AuditResponse, AuditReport, AuditSummary, PillarScores, ClaimSchema, EvidenceSnippet
from app.services.scorer import ESGScorer

router = APIRouter()

DATA_DIR = settings.DATA_DIR


async def _run_audit_pipeline(audit_id: str, pdf_path: str, company: str, year: str):
    """Background task that runs the full audit pipeline."""
    try:
        db = await get_db(settings.DATABASE_URL)
        await update_audit(db, audit_id, status="processing")

        scorer = ESGScorer(
            ollama_host=settings.OLLAMA_HOST,
            model=settings.OLLAMA_MODEL,
            embed_model=settings.OLLAMA_EMBED_MODEL,
        )
        await scorer.run_audit(audit_id, pdf_path, company, year, db)
        await db.close()
    except Exception as e:
        try:
            db = await get_db(settings.DATABASE_URL)
            await update_audit(db, audit_id, status="error")
            await db.close()
        except Exception:
            pass


@router.post("/audit", status_code=202)
async def start_audit(
    background_tasks: BackgroundTasks,
    file: Optional[UploadFile] = File(None),
    url: Optional[str] = Form(None),
    company_name: str = Form(...),
    report_year: Optional[str] = Form(None),
):
    """Start a new ESG audit. Accepts a PDF file upload or a URL."""
    if bool(file) == bool(url):
        raise HTTPException(status_code=400, detail="Either 'file' or 'url' must be provided.")

    # Ensure upload directory exists
    upload_dir = os.path.join(DATA_DIR, "files", "uploads")
    os.makedirs(upload_dir, exist_ok=True)

    # Save uploaded file or prepare URL
    pdf_path = ""
    if file:
        filename = f"{uuid.uuid4()}.pdf"
        pdf_path = os.path.join(upload_dir, filename)
        content = await file.read()
        if not content.startswith(b"%PDF-"):
            raise HTTPException(status_code=400, detail="The uploaded file is not a valid PDF.")
        with open(pdf_path, "wb") as f:
            f.write(content)
    elif url:
        # Download will happen in the background pipeline
        pdf_path = url  # scorer.run_audit handles URL vs file

    # Create audit record
    db = await get_db(settings.DATABASE_URL)
    audit_id = await create_audit(db, company_name, report_year or "")
    await db.close()

    # Launch background task
    background_tasks.add_task(_run_audit_pipeline, audit_id, pdf_path, company_name, report_year or "")

    return AuditResponse(audit_id=audit_id, status="processing")


@router.get("/audit/{audit_id}")
async def get_audit_detail(audit_id: str):
    """Get audit status and full results."""
    db = await get_db(settings.DATABASE_URL)
    audit = await get_audit(db, audit_id)
    if not audit:
        await db.close()
        raise HTTPException(status_code=404, detail="Audit not found.")

    claims_raw = await get_claims_by_audit(db, audit_id)
    await db.close()

    # Build claim schemas
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

        claims.append(ClaimSchema(
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
        ))

    # Compute summary
    total = len(claims)
    flagged = sum(1 for c in claims if (c.final_score or c.score) <= 3)
    verified = total - flagged

    pillar_scores = {}
    for pillar in ("Environmental", "Social", "Governance"):
        pillar_claims = [c for c in claims if c.pillar == pillar]
        if pillar_claims:
            pillar_scores[pillar] = round(sum(c.final_score or c.score for c in pillar_claims) / len(pillar_claims), 1)
        else:
            pillar_scores[pillar] = 0.0

    overall = round(sum(pillar_scores.values()) / max(len([v for v in pillar_scores.values() if v > 0]), 1), 1)

    return AuditReport(
        audit_id=audit_id,
        company_name=audit.get("company", ""),
        report_year=audit.get("report_year", ""),
        status=audit.get("status", "pending"),
        created_at=audit.get("created_at", ""),
        completed_at=audit.get("completed_at"),
        summary=AuditSummary(
            total_claims=total,
            verified=verified,
            flagged=flagged,
            pillar_scores=PillarScores(**pillar_scores),
            overall_score=overall,
        ),
        claims=claims,
        report_pdf_path=audit.get("report_path"),
    )


@router.get("/audits")
async def list_audits(limit: int = Query(50, ge=1, le=200)):
    db = await get_db(settings.DATABASE_URL)
    audits = await get_recent_audits(db, limit)
    await db.close()
    return audits


@router.get("/report/{audit_id}/download")
async def download_report(audit_id: str):
    db = await get_db(settings.DATABASE_URL)
    audit = await get_audit(db, audit_id)
    await db.close()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found.")
    report_path = audit.get("report_path")
    if not report_path or not Path(report_path).is_file():
        raise HTTPException(status_code=404, detail="Report is not available yet.")
    return FileResponse(report_path, media_type="application/pdf", filename=f"verigreen_{audit_id}.pdf")


@router.get("/badge/{claim_id}")
async def download_badge(claim_id: str):
    db = await get_db(settings.DATABASE_URL)
    claim = await get_claim(db, claim_id)
    await db.close()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found.")
    badge_path = Path(settings.BADGE_DIR) / f"{claim_id}.pdf"
    if not badge_path.is_file():
        raise HTTPException(status_code=404, detail="Badge is not available yet.")
    return FileResponse(badge_path, media_type="application/pdf", filename=f"verigreen_badge_{claim_id}.pdf")

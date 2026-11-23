"""
VeriGreen AI — ESG scoring orchestrator.

Runs the full audit pipeline:
  parse → chunk → embed → detect claims → evidence retrieval → re-score → report.
"""

from __future__ import annotations

import json
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from app.config import settings
from app.database import create_claim, update_audit, get_claims_by_audit
from app.services.chunker import chunk_text
from app.services.llm import OllamaClient
from app.services.parser import extract_text_from_pdf
from app.services.report_gen import ReportGenerator
from app.services.vectorstore import VectorStore

logger = logging.getLogger(__name__)

# Prompts from SPEC.md §7
CLAIM_DETECTION_SYSTEM = (
    "You are an ESG compliance auditor. You ONLY output valid JSON."
)

CLAIM_DETECTION_USER = '''Analyze the following excerpt from a corporate sustainability report.

EXCERPT:
"""
{chunk_text}
"""

Respond with a JSON object:
{{
  "contains_claim": true | false,
  "claim_text": "<exact quoted claim or null>",
  "pillar": "Environmental" | "Social" | "Governance" | null,
  "credibility_score": <1-5>,
  "reason": "<one-sentence justification>"
}}

Scoring guide:
1 = Vague marketing language, no data
2 = Specific claim but no evidence cited
3 = Claim with partial evidence (e.g., percentage but no baseline)
4 = Claim with strong internal evidence
5 = Claim backed by third-party audit / certification'''

RESCORE_SYSTEM = (
    "You are an ESG compliance auditor performing evidence verification. "
    "Output valid JSON only."
)

RESCORE_USER = '''A corporate report claims:
CLAIM: "{claim_text}"
Initial score: {initial_score}/5

The following evidence snippets were retrieved from the same report:
{evidence_snippets}

Re-evaluate the claim. Respond with:
{{
  "final_score": <1-5>,
  "citations": ["page X, Table Y", ...],
  "verdict": "verified" | "partially_verified" | "unverified" | "contradicted",
  "explanation": "<brief reasoning>"
}}'''


class ESGScorer:
    """Core ESG audit pipeline orchestrator."""

    def __init__(self, ollama_host=None, model=None, embed_model=None, chroma_path=None) -> None:
        self.llm = OllamaClient(host=ollama_host, model=model, embed_model=embed_model)
        self.vector_store = VectorStore(chroma_path or settings.CHROMA_PATH)
        self.report_gen = ReportGenerator()

    async def run_audit(
        self,
        audit_id: str,
        pdf_path: str,
        company_name: str,
        report_year: Optional[str] = None,
        db=None,
    ) -> None:
        """Execute the complete audit pipeline.

        Steps:
          1. Parse PDF → pages
          2. Chunk pages → chunks
          3. Embed chunks → store in ChromaDB
          4. Detect claims via LLM
          5. Re-score low-score claims with evidence
          6. Save claims to SQLite
          7. Generate report + badge PDFs
          8. Update audit status to 'done'

        On error, sets the audit status to 'error'.
        """
        try:
            await update_audit(db, audit_id, status="processing")

            # 1. Parse
            logger.info("Parsing PDF: %s", pdf_path)
            if pdf_path.startswith(("http://", "https://")):
                from app.services.scraper import download_pdf
                local_path = os.path.join(settings.DATA_DIR, "files", "uploads", f"{audit_id}.pdf")
                await download_pdf(pdf_path, local_path)
                pdf_path = local_path
            pages = extract_text_from_pdf(pdf_path)

            # 2. Chunk
            chunks = chunk_text(pages, chunk_size=200, overlap=50)
            if not chunks:
                await update_audit(db, audit_id, status="error")
                return

            # 3. Embed and store
            chunk_texts = [c["text"] for c in chunks]
            embeddings = await self.llm.embed(chunk_texts)
            if len(embeddings) != len(chunk_texts):
                raise RuntimeError("Embedding service returned an incomplete response")

            ids = [f"{audit_id}_chunk_{c['chunk_index']}" for c in chunks]
            metadatas = [
                {"audit_id": audit_id, "source_page": c["source_page"], "chunk_index": c["chunk_index"]}
                for c in chunks
            ]
            self.vector_store.add(
                ids=ids,
                documents=chunk_texts,
                embeddings=embeddings,
                metadatas=metadatas,
            )

            # 4. Detect claims
            detected_claims: list[dict[str, Any]] = []
            for chunk in chunks:
                prompt = CLAIM_DETECTION_USER.format(chunk_text=chunk["text"])
                raw = await self.llm.generate(prompt, system=CLAIM_DETECTION_SYSTEM)
                parsed = OllamaClient.extract_json(raw)

                if parsed and parsed.get("contains_claim"):
                    try:
                        score = max(1, min(5, int(parsed.get("credibility_score", 3))))
                    except (TypeError, ValueError):
                        score = 3
                    pillar = parsed.get("pillar")
                    if pillar not in {"Environmental", "Social", "Governance"}:
                        pillar = "Environmental"
                    claim_text = parsed.get("claim_text")
                    if not isinstance(claim_text, str) or not claim_text.strip():
                        claim_text = chunk["text"][:500]
                    detected_claims.append({
                        "claim_id": f"c{uuid.uuid4().hex[:8]}",
                        "chunk_index": chunk["chunk_index"],
                        "text": claim_text,
                        "pillar": pillar,
                        "score": score,
                        "reason": parsed.get("reason") if isinstance(parsed.get("reason"), str) else "",
                        "final_score": score,
                        "verdict": "",
                        "evidence": [],
                        "citations": [],
                    })

            # 5. Re-score low-scoring claims
            for claim in detected_claims:
                if claim["score"] <= 3:
                    try:
                        claim_embedding = (await self.llm.embed([claim["text"]]))[0]
                        evidence = self.vector_store.query(claim_embedding, top_k=5, audit_id=audit_id)
                        claim["evidence"] = [{
                            "chunk_index": e["metadata"].get("chunk_index"),
                            "source_page": e["metadata"].get("source_page"),
                            "snippet": e.get("document", "")[:300],
                            "relevance_score": round(1 - float(e.get("distance", 1)), 3),
                        } for e in evidence]
                        evidence_text = "\n".join(
                            f"[Chunk {e['metadata'].get('chunk_index', '?')}, "
                            f"Page {e['metadata'].get('source_page', '?')}]: "
                            f"{e['document'][:300]}"
                            for e in evidence
                        )

                        rescore_prompt = RESCORE_USER.format(
                            claim_text=claim["text"],
                            initial_score=claim["score"],
                            evidence_snippets=evidence_text,
                        )
                        raw = await self.llm.generate(rescore_prompt, system=RESCORE_SYSTEM)
                        parsed = OllamaClient.extract_json(raw)

                        if parsed:
                            try:
                                claim["final_score"] = max(1, min(5, int(parsed.get("final_score", claim["score"]))))
                            except (TypeError, ValueError):
                                claim["final_score"] = claim["score"]
                            citations = parsed.get("citations", [])
                            claim["citations"] = [str(item) for item in citations] if isinstance(citations, list) else []
                            claim["verdict"] = parsed.get("verdict", "")
                    except Exception as exc:
                        logger.warning("Re-scoring failed for %s: %s", claim["claim_id"], exc)

            # 6. Save claims to DB
            for claim in detected_claims:
                await create_claim(db, audit_id, claim)

            # 7. Generate report + badges
            report_dir = settings.REPORT_DIR
            badge_dir = settings.BADGE_DIR
            os.makedirs(report_dir, exist_ok=True)
            os.makedirs(badge_dir, exist_ok=True)

            report_path = os.path.join(report_dir, f"{audit_id}.pdf")
            self.report_gen.generate_report(
                audit_id=audit_id,
                company=company_name,
                claims=detected_claims,
                output_path=report_path,
                report_year=report_year,
            )

            badge_paths: list[str] = []
            for claim in detected_claims:
                badge_path = os.path.join(badge_dir, f"{claim['claim_id']}.pdf")
                self.report_gen.generate_badge(claim, badge_path)
                badge_paths.append(badge_path)

            # 8. Update audit status
            total = len(detected_claims)
            flagged = sum(1 for c in detected_claims if (c.get("final_score") or c.get("score", 3)) <= 3)
            scores = [c.get("final_score") or c.get("score", 3) for c in detected_claims]
            overall = round(sum(scores) / len(scores), 2) if scores else 0.0

            await update_audit(
                db, audit_id,
                status="done",
                total_claims=total,
                flagged=flagged,
                overall_score=overall,
                report_path=report_path,
                completed_at=datetime.now(timezone.utc).isoformat(),
            )

            logger.info("Audit %s completed: %d claims, overall %.2f", audit_id, total, overall)

        except Exception as exc:
            logger.exception("Audit %s failed: %s", audit_id, exc)
            try:
                await update_audit(db, audit_id, status="error")
            except Exception:
                pass

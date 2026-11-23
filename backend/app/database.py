"""Async SQLite database helper for audit metadata."""

import aiosqlite
import os
import json
import uuid
from datetime import datetime, timezone


DATABASE_URL = os.getenv("DATABASE_URL", "./data/verigreen.db")


async def init_db(db_path: str | None = None):
    """Create the audits and claims tables if they don't exist."""
    path = db_path or DATABASE_URL
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    async with aiosqlite.connect(path) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS audits (
                id          TEXT PRIMARY KEY,
                company     TEXT NOT NULL,
                report_year TEXT,
                status      TEXT DEFAULT 'pending',
                total_claims INTEGER DEFAULT 0,
                flagged     INTEGER DEFAULT 0,
                overall_score REAL,
                created_at  TEXT,
                completed_at TEXT,
                report_path TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS claims (
                id          TEXT PRIMARY KEY,
                audit_id    TEXT REFERENCES audits(id),
                chunk_index INTEGER,
                text        TEXT,
                pillar      TEXT,
                score       INTEGER,
                final_score INTEGER,
                reason      TEXT,
                verdict     TEXT,
                evidence    TEXT,
                citations   TEXT,
                created_at  TEXT
            )
        """)
        await db.commit()


async def get_db(db_path: str | None = None):
    """Return an aiosqlite connection."""
    path = db_path or DATABASE_URL
    db = await aiosqlite.connect(path)
    db.row_factory = aiosqlite.Row
    return db


async def create_audit(db, company: str, report_year: str = "") -> str:
    """Insert a new audit row and return its ID."""
    audit_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    await db.execute(
        "INSERT INTO audits (id, company, report_year, status, created_at) VALUES (?, ?, ?, 'pending', ?)",
        (audit_id, company, report_year, now),
    )
    await db.commit()
    return audit_id


async def update_audit(db, audit_id: str, **kwargs):
    """Update fields on an audit row."""
    allowed = {"status", "total_claims", "flagged", "overall_score", "completed_at", "report_path"}
    sets = []
    vals = []
    for k, v in kwargs.items():
        if k in allowed:
            sets.append(f"{k} = ?")
            vals.append(v)
    if not sets:
        return
    vals.append(audit_id)
    await db.execute(f"UPDATE audits SET {', '.join(sets)} WHERE id = ?", vals)
    await db.commit()


async def get_audit(db, audit_id: str) -> dict | None:
    """Fetch an audit by ID."""
    cursor = await db.execute("SELECT * FROM audits WHERE id = ?", (audit_id,))
    row = await cursor.fetchone()
    if not row:
        return None
    return dict(row)


async def get_recent_audits(db, limit: int = 50) -> list[dict]:
    cursor = await db.execute(
        "SELECT * FROM audits ORDER BY created_at DESC LIMIT ?", (limit,)
    )
    return [dict(row) for row in await cursor.fetchall()]


async def get_claim(db, claim_id: str) -> dict | None:
    cursor = await db.execute("SELECT * FROM claims WHERE id = ?", (claim_id,))
    row = await cursor.fetchone()
    return dict(row) if row else None


async def create_claim(db, audit_id: str, claim_data: dict) -> str:
    """Insert a claim row and return its ID."""
    claim_id = claim_data.get("claim_id", str(uuid.uuid4()))
    now = datetime.now(timezone.utc).isoformat()
    evidence_json = json.dumps(claim_data.get("evidence", []))
    citations_json = json.dumps(claim_data.get("citations", []))
    await db.execute(
        """INSERT INTO claims (id, audit_id, chunk_index, text, pillar, score, final_score, reason, verdict, evidence, citations, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            claim_id, audit_id,
            claim_data.get("chunk_index", 0),
            claim_data.get("text", ""),
            claim_data.get("pillar", ""),
            claim_data.get("score", 0),
            claim_data.get("final_score", claim_data.get("score", 0)),
            claim_data.get("reason", ""),
            claim_data.get("verdict", ""),
            evidence_json,
            citations_json,
            now,
        ),
    )
    await db.commit()
    return claim_id


async def get_claims_by_audit(db, audit_id: str) -> list[dict]:
    """Fetch all claims for an audit."""
    cursor = await db.execute("SELECT * FROM claims WHERE audit_id = ? ORDER BY chunk_index", (audit_id,))
    rows = await cursor.fetchall()
    results = []
    for row in rows:
        d = dict(row)
        # Parse JSON fields
        for field in ("evidence", "citations"):
            try:
                d[field] = json.loads(d[field]) if d[field] else []
            except (json.JSONDecodeError, TypeError):
                d[field] = []
        results.append(d)
    return results

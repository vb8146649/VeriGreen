"""Health check endpoint."""

from fastapi import APIRouter
import httpx
import os

from app.config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """Check the status of all subsystems."""
    result = {
        "api": "ok",
        "ollama": "unreachable",
        "ollama_model": settings.OLLAMA_MODEL,
        "chromadb": "ok",
        "sqlite": "ok",
    }

    # Check Ollama
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{settings.OLLAMA_HOST}/api/tags")
            if resp.status_code == 200:
                result["ollama"] = "ok"
    except Exception:
        pass

    # Check SQLite
    try:
        import aiosqlite
        db_path = settings.DATABASE_URL
        async with aiosqlite.connect(db_path) as db:
            await db.execute("SELECT 1")
        result["sqlite"] = "ok"
    except Exception:
        result["sqlite"] = "error"

    # Check ChromaDB
    try:
        chroma_path = settings.CHROMA_PATH
        if os.path.isdir(chroma_path) or not os.path.exists(chroma_path):
            result["chromadb"] = "ok"
        else:
            result["chromadb"] = "error"
    except Exception:
        result["chromadb"] = "error"

    return result
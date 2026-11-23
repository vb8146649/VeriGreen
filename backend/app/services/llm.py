"""
VeriGreen AI — Ollama LLM client.

Provides async methods for text generation and embedding via the
Ollama HTTP API, with retry logic and JSON extraction helpers.
"""

from __future__ import annotations

import asyncio
import json
import re
from typing import Any, Optional

import httpx

from app.config import settings


class OllamaClient:
    """Async HTTP client for the Ollama API."""

    def __init__(
        self,
        host: Optional[str] = None,
        model: Optional[str] = None,
        embed_model: Optional[str] = None,
        max_retries: int = 3,
    ) -> None:
        self.host = (host or settings.OLLAMA_HOST).rstrip("/")
        self.model = model or settings.OLLAMA_MODEL
        self.embed_model = embed_model or settings.OLLAMA_EMBED_MODEL
        self.max_retries = max_retries

    # ----- public methods ---------------------------------------------------

    async def generate(self, prompt: str, system: Optional[str] = None) -> str:
        """Send a generate request to Ollama and return the response text.

        Args:
            prompt: The user prompt.
            system: Optional system prompt.

        Returns:
            The model's response string.
        """
        payload: dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }
        if system:
            payload["system"] = system

        data = await self._post("/api/generate", payload)
        return data.get("response", "")

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Embed a list of texts and return their vector representations.

        Args:
            texts: List of text strings to embed.

        Returns:
            A list of embedding vectors (list of floats).
        """
        payload: dict[str, Any] = {
            "model": self.embed_model,
            "input": texts,
        }
        data = await self._post("/api/embed", payload)
        # Ollama returns {"embeddings": [[...], [...]]}
        return data.get("embeddings", [])

    # ----- JSON extraction helper -------------------------------------------

    @staticmethod
    def extract_json(text: str) -> Any:
        """Try to extract a JSON object from LLM output.

        Handles common issues like markdown code fences and
        leading/trailing text.

        Returns:
            Parsed JSON object, or ``None`` if extraction fails.
        """
        # Strip markdown code fences
        fenced = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
        if fenced:
            text = fenced.group(1)

        # Try direct parse
        text = text.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try to find first { ... } or [ ... ]
        for start_char, end_char in [("{", "}"), ("[", "]")]:
            start = text.find(start_char)
            end = text.rfind(end_char)
            if start != -1 and end != -1 and end > start:
                try:
                    return json.loads(text[start : end + 1])
                except json.JSONDecodeError:
                    continue

        return None

    # ----- internal ---------------------------------------------------------

    async def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        """POST to Ollama with exponential-backoff retry."""
        url = f"{self.host}{path}"
        last_exc: Optional[Exception] = None

        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=300.0) as client:
                    resp = await client.post(url, json=payload)
                    resp.raise_for_status()
                    return resp.json()
            except (httpx.HTTPError, json.JSONDecodeError) as exc:
                last_exc = exc
                wait = 2 ** attempt
                await asyncio.sleep(wait)

        raise RuntimeError(
            f"Ollama request to {url} failed after {self.max_retries} attempts: {last_exc}"
        )

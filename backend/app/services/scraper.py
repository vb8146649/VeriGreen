"""
VeriGreen AI — PDF / URL scraper service.

Downloads a PDF from a URL using httpx.  Falls back to Playwright
(headless Chromium) for JS-rendered pages that don't return a direct PDF.
"""

from __future__ import annotations

import os
from typing import Optional

import httpx


async def download_pdf(url: str, save_path: str) -> str:
    """Download a PDF from *url* and save it to *save_path*.

    1. First attempt: plain HTTP GET with httpx (fast path).
    2. Fallback: if the response is not a PDF (e.g. JS-rendered page),
       use Playwright to navigate and print-to-PDF.

    Returns:
        The local file path where the PDF was saved.

    Raises:
        RuntimeError: If both strategies fail.
    """
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    # --- Fast path: direct HTTP download ---
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=60.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            content_type = resp.headers.get("content-type", "")
            if "pdf" in content_type or url.lower().endswith(".pdf"):
                with open(save_path, "wb") as f:
                    f.write(resp.content)
                return save_path
    except httpx.HTTPError:
        pass  # fall through to Playwright

    # --- Fallback: Playwright print-to-PDF ---
    try:
        from playwright.async_api import async_playwright

        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, wait_until="networkidle", timeout=30_000)
            await page.pdf(path=save_path, format="A4")
            await browser.close()
        return save_path
    except Exception as exc:
        raise RuntimeError(
            f"Failed to download PDF from {url}: {exc}"
        ) from exc

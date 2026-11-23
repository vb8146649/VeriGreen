"""
VeriGreen AI — PDF text extraction service.

Uses *pdfplumber* for layout-aware text and table extraction.
Falls back to *pytesseract* OCR when a page yields no text
(common with scanned / image-only PDFs).
"""

from __future__ import annotations

import io
from typing import Any

import pdfplumber


def _ocr_page(page: Any) -> str:
    """Run OCR on a pdfplumber page image using pytesseract."""
    try:
        import pytesseract
        from PIL import Image

        img = page.to_image(resolution=300).original
        text: str = pytesseract.image_to_string(img)
        return text.strip()
    except Exception:
        return ""


def extract_text_from_pdf(pdf_path: str) -> list[dict[str, Any]]:
    """Extract text from every page of a PDF.

    Args:
        pdf_path: Filesystem path to the PDF file.

    Returns:
        A list of dicts, one per page::

            {
                "page_number": int,   # 1-indexed
                "text": str,
                "tables": list[list[list[str]]]
            }
    """
    pages: list[dict[str, Any]] = []

    with pdfplumber.open(pdf_path) as pdf:
        for idx, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""

            # OCR fallback for pages with no extractable text
            if not text.strip():
                text = _ocr_page(page)

            # Extract tables (list of list-of-lists)
            raw_tables = page.extract_tables() or []
            tables: list[list[list[str]]] = []
            for tbl in raw_tables:
                cleaned = [
                    [(cell or "") for cell in row]
                    for row in tbl
                ]
                tables.append(cleaned)

            pages.append({
                "page_number": idx,
                "text": text,
                "tables": tables,
            })

    return pages

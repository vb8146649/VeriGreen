"""
VeriGreen AI — Text chunking service.

Splits extracted page text into overlapping word-window chunks
suitable for embedding and claim detection.
"""

from __future__ import annotations

from typing import Any


def chunk_text(
    pages: list[dict[str, Any]],
    chunk_size: int = 200,
    overlap: int = 50,
) -> list[dict[str, Any]]:
    """Split page-level text into overlapping word-window chunks.

    Args:
        pages: Output of :func:`parser.extract_text_from_pdf`.
        chunk_size: Number of words per chunk.
        overlap: Number of overlapping words between consecutive chunks.

    Returns:
        A list of chunk dicts::

            {
                "chunk_index": int,
                "text": str,
                "source_page": int
            }
    """
    chunks: list[dict[str, Any]] = []
    chunk_idx = 0

    for page in pages:
        words = page["text"].split()
        page_num = page["page_number"]

        if not words:
            continue

        step = max(chunk_size - overlap, 1)
        start = 0
        while start < len(words):
            end = start + chunk_size
            chunk_words = words[start:end]
            chunks.append({
                "chunk_index": chunk_idx,
                "text": " ".join(chunk_words),
                "source_page": page_num,
            })
            chunk_idx += 1
            start += step

    return chunks

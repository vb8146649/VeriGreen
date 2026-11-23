"""
VeriGreen AI — ChromaDB vector store wrapper.

Provides a thin abstraction over a persistent ChromaDB collection
used to store and query ESG document embeddings.
"""

from __future__ import annotations

from typing import Any, Optional

import chromadb
from chromadb.config import Settings as ChromaSettings


class VectorStore:
    """Wrapper around a ChromaDB persistent collection."""

    COLLECTION_NAME = "esg_corpus"

    def __init__(self, persist_dir: str) -> None:
        """Create or load a persistent ChromaDB client.

        Args:
            persist_dir: Filesystem path for ChromaDB persistence.
        """
        self._client = chromadb.PersistentClient(
            path=persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self._collection = self._client.get_or_create_collection(
            name=self.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    # ---- public API --------------------------------------------------------

    def add(
        self,
        ids: list[str],
        documents: list[str],
        embeddings: list[list[float]],
        metadatas: Optional[list[dict[str, Any]]] = None,
    ) -> None:
        """Add vectors to the collection.

        Args:
            ids: Unique identifiers for each document.
            documents: Raw text content.
            embeddings: Pre-computed embedding vectors.
            metadatas: Optional metadata dicts per document.
        """
        kwargs: dict[str, Any] = {
            "ids": ids,
            "documents": documents,
            "embeddings": embeddings,
        }
        if metadatas:
            kwargs["metadatas"] = metadatas
        self._collection.add(**kwargs)

    def query(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        audit_id: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """Query the collection and return the top-k nearest results.

        Args:
            query_embedding: The query vector.
            top_k: Number of results to return.

        Returns:
            List of dicts with keys: id, document, metadata, distance.
        """
        kwargs: dict[str, Any] = {}
        if audit_id:
            kwargs["where"] = {"audit_id": audit_id}
        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
            **kwargs,
        )

        items: list[dict[str, Any]] = []
        if not results or not results.get("ids"):
            return items

        for i, doc_id in enumerate(results["ids"][0]):
            items.append({
                "id": doc_id,
                "document": results["documents"][0][i] if results.get("documents") else "",
                "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                "distance": results["distances"][0][i] if results.get("distances") else 0.0,
            })

        return items

    def delete_collection(self, audit_id: Optional[str] = None) -> None:
        """Delete the collection (useful for cleanup).

        Args:
            audit_id: If provided, only delete documents with this audit_id
                      in their metadata. Otherwise delete the entire collection.
        """
        if audit_id:
            # Delete by metadata filter
            try:
                self._collection.delete(where={"audit_id": audit_id})
            except Exception:
                pass
        else:
            try:
                self._client.delete_collection(self.COLLECTION_NAME)
            except Exception:
                pass

    @property
    def collection(self) -> Any:
        """Return the underlying ChromaDB collection object."""
        return self._collection

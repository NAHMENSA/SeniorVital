"""ChromaDB vector store for SeniorVital RAG chunks.

Provides a modular wrapper that can be replaced later by a pgvector-based store
without changing the retriever interface.
"""

import json
from pathlib import Path
from typing import Any

import chromadb
from chromadb.config import Settings

from rag.constants import AGENT_TO_MACRODOMAIN, MACRODOMAIN_TO_AGENT
from rag.embeddings import EmbeddingGenerator


class SeniorVitalVectorStore:
    """ChromaDB-backed vector store for SeniorVital knowledge chunks.

    Args:
        persist_directory: Directory where ChromaDB persists its files.
        collection_name: Name of the ChromaDB collection.
        embedder: Object with `embed_text(text)` and `embed_batch(texts)` methods.
            If None, an `EmbeddingGenerator` is instantiated lazily.
    """

    def __init__(
        self,
        persist_directory: str | Path,
        collection_name: str = "seniorvital_kb",
        embedder: EmbeddingGenerator | None = None,
    ) -> None:
        self.persist_directory = Path(persist_directory)
        self.collection_name = collection_name
        self._embedder = embedder
        self._client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(anonymized_telemetry=False),
        )
        self._collection = self._client.get_or_create_collection(name=self.collection_name)

    @property
    def embedder(self) -> EmbeddingGenerator:
        if self._embedder is None:
            self._embedder = EmbeddingGenerator()
        return self._embedder

    @property
    def collection(self) -> chromadb.Collection:
        return self._collection

    def _prepare_metadata(self, chunk: dict[str, Any]) -> dict[str, Any]:
        """Return ChromaDB-compatible metadata for a chunk.

        ChromaDB only accepts scalar metadata values (str, int, float, bool).
        """
        meta: dict[str, Any] = {}
        scalar_keys = [
            "chunk_id",
            "document_name",
            "source_path",
            "macrodomain",
            "macrodomain_name",
            "section_path",
            "chunk_type",
            "chunk_index",
            "total_chunks",
            "char_count",
            "word_count",
            "has_markdown_headers",
            "level",
            "pathology",
        ]
        for key in scalar_keys:
            value = chunk.get(key)
            if value is None:
                continue
            if isinstance(value, bool):
                meta[key] = value
            elif isinstance(value, (int, float)):
                meta[key] = value
            else:
                meta[key] = str(value)

        keywords = chunk.get("keywords")
        if isinstance(keywords, list) and keywords:
            meta["keywords"] = ",".join(str(k) for k in keywords)

        return meta

    def _extract_ids(self, chunks: list[dict[str, Any]]) -> list[str]:
        return [str(chunk["chunk_id"]) for chunk in chunks]

    def add_chunks(
        self,
        chunks: list[dict[str, Any]],
        embeddings: list[list[float]] | None = None,
    ) -> None:
        """Add chunks and optional precomputed embeddings to the store.

        If embeddings are not provided, they are computed from chunk contents.
        """
        if not chunks:
            return

        contents = [chunk["content"] for chunk in chunks]
        if embeddings is None:
            embeddings = self.embedder.embed_batch(contents)

        ids = self._extract_ids(chunks)
        metadatas = [self._prepare_metadata(chunk) for chunk in chunks]

        self._collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=contents,
            metadatas=metadatas,
        )

    def upsert_chunks(
        self,
        chunks: list[dict[str, Any]],
        embeddings: list[list[float]] | None = None,
    ) -> None:
        """Add or overwrite chunks in the store."""
        if not chunks:
            return

        contents = [chunk["content"] for chunk in chunks]
        if embeddings is None:
            embeddings = self.embedder.embed_batch(contents)

        ids = self._extract_ids(chunks)
        metadatas = [self._prepare_metadata(chunk) for chunk in chunks]

        self._collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=contents,
            metadatas=metadatas,
        )

    def create_or_load(
        self,
        chunks: list[dict[str, Any]] | None = None,
        embeddings: list[list[float]] | None = None,
        clear: bool = False,
    ) -> chromadb.Collection:
        """Create a fresh collection or load an existing one.

        Args:
            chunks: Optional chunks to index immediately.
            embeddings: Optional precomputed embeddings for the chunks.
            clear: If True, delete the existing collection and recreate it.
        """
        if clear:
            self.delete_all()
        if chunks:
            self.add_chunks(chunks, embeddings=embeddings)
        return self._collection

    def search(
        self,
        query_text: str,
        k: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Return the k most similar chunks to a natural-language query."""
        query_embedding = self.embedder.embed_text(query_text)
        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            where=filters,
            include=["documents", "metadatas", "distances"],
        )
        return self._normalize_results(results)

    def search_by_agent(
        self,
        query_text: str,
        agent_name: str,
        k: int = 5,
    ) -> list[dict[str, Any]]:
        """Search within the macrodomain associated with an agent."""
        macrodomain = AGENT_TO_MACRODOMAIN.get(agent_name)
        if macrodomain is None:
            raise ValueError(f"Unknown agent: {agent_name}")
        return self.search(query_text, k=k, filters={"macrodomain": macrodomain})

    def search_by_macrodomain(
        self,
        query_text: str,
        macrodomain: str,
        k: int = 5,
    ) -> list[dict[str, Any]]:
        """Search within a single macrodomain."""
        return self.search(query_text, k=k, filters={"macrodomain": macrodomain})

    def search_by_filters(
        self,
        query_text: str,
        filters: dict[str, Any],
        k: int = 5,
    ) -> list[dict[str, Any]]:
        """Search with arbitrary metadata filters."""
        return self.search(query_text, k=k, filters=filters)

    def get_by_chunk_id(self, chunk_id: str) -> dict[str, Any] | None:
        """Retrieve a single chunk by its ID."""
        result = self._collection.get(
            ids=[chunk_id],
            include=["documents", "metadatas", "embeddings"],
        )
        normalized = self._normalize_results(
            {
                "ids": [result.get("ids", [])],
                "documents": [result.get("documents", [])],
                "metadatas": [result.get("metadatas", [])],
                "distances": [[0.0]],
            }
        )
        return normalized[0] if normalized else None

    def count(self) -> int:
        """Return the number of indexed chunks."""
        return self._collection.count()

    def delete_all(self) -> None:
        """Delete the collection and recreate it empty."""
        try:
            self._client.delete_collection(name=self.collection_name)
        except Exception:
            pass
        self._collection = self._client.get_or_create_collection(name=self.collection_name)

    def _normalize_results(self, raw: dict[str, Any]) -> list[dict[str, Any]]:
        """Convert ChromaDB query result into a flat list of result dicts."""
        ids_batch = raw.get("ids", [[]])
        documents_batch = raw.get("documents", [[]])
        metadatas_batch = raw.get("metadatas", [[]])
        distances_batch = raw.get("distances", [[]])

        output: list[dict[str, Any]] = []
        for ids, docs, metas, dists in zip(ids_batch, documents_batch, metadatas_batch, distances_batch):
            if not ids:
                continue
            for idx, chunk_id in enumerate(ids):
                metadata = metas[idx] if metas and idx < len(metas) else {}
                keywords = metadata.get("keywords")
                if keywords and isinstance(keywords, str):
                    metadata["keywords"] = [k.strip() for k in keywords.split(",") if k.strip()]
                output.append(
                    {
                        "chunk_id": chunk_id,
                        "content": docs[idx] if docs and idx < len(docs) else "",
                        "metadata": metadata,
                        "distance": dists[idx] if dists and idx < len(dists) else None,
                    }
                )
        return output

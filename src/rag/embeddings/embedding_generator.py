"""Embedding generator for SeniorVital RAG chunks."""

import os
from pathlib import Path
from typing import Any

from langchain_huggingface import HuggingFaceEmbeddings

from .cache import EmbeddingCache


DEFAULT_EMBEDDING_MODEL = "intfloat/multilingual-e5-small"


class EmbeddingGenerator:
    """Generate vector embeddings for text chunks using local HuggingFace models."""

    def __init__(
        self,
        model_name: str | None = None,
        cache: EmbeddingCache | None = None,
    ) -> None:
        self.model_name = model_name or os.getenv(
            "EMBEDDING_MODEL_NAME", DEFAULT_EMBEDDING_MODEL
        )
        self._embeddings: HuggingFaceEmbeddings | None = None
        self._cache = cache

    @property
    def embeddings(self) -> HuggingFaceEmbeddings:
        """Lazy-load local HuggingFace embeddings."""
        if self._embeddings is None:
            self._embeddings = HuggingFaceEmbeddings(
                model_name=self.model_name,
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True},
            )
        return self._embeddings

    def embed_text(self, text: str) -> list[float]:
        """Return the embedding vector for a single text."""
        if self._cache is not None:
            cached = self._cache.get(text)
            if cached is not None:
                return cached
        vector = self.embeddings.embed_query(text)
        if self._cache is not None:
            self._cache.put(text, vector)
        return vector

    def embed_batch(self, texts: list[str], batch_size: int = 32) -> list[list[float]]:
        """Return embeddings for a list of texts.

        Uses cache for individual texts when available.
        """
        if not texts:
            return []
        # Check cache for each text, collect uncached indices
        results: list[list[float] | None] = [None] * len(texts)
        uncached_indices: list[int] = []

        if self._cache is not None:
            for i, text in enumerate(texts):
                cached = self._cache.get(text)
                if cached is not None:
                    results[i] = cached
                else:
                    uncached_indices.append(i)
        else:
            uncached_indices = list(range(len(texts)))

        # Compute embeddings for uncached texts
        if uncached_indices:
            uncached_texts = [texts[i] for i in uncached_indices]
            computed = self.embeddings.embed_documents(uncached_texts)
            for idx, vector in zip(uncached_indices, computed):
                results[idx] = vector
                if self._cache is not None:
                    self._cache.put(texts[idx], vector)

        return [r for r in results if r is not None]

    def generate_for_chunks(
        self,
        chunks: list[dict[str, Any]],
        batch_size: int = 32,
        content_key: str = "content",
    ) -> list[dict[str, Any]]:
        """Add an 'embedding' field to every chunk dict.

        The original chunks are copied so the input is not mutated.
        """
        if not chunks:
            return []
        texts = [chunk.get(content_key, "") for chunk in chunks]
        vectors = self.embed_batch(texts, batch_size=batch_size)
        results = []
        for chunk, vector in zip(chunks, vectors):
            enriched = dict(chunk)
            enriched["embedding"] = vector
            results.append(enriched)
        return results

    def dimension(self) -> int:
        """Return the embedding dimensionality."""
        return len(self.embed_text("test"))

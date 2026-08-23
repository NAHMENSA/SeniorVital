"""Indexing pipeline: chunks + embeddings → vector store."""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from rag.embeddings import EmbeddingGenerator, load_embeddings
from rag.vector_store import SeniorVitalVectorStore


@dataclass
class IndexingStats:
    """Result of an indexing run."""
    chunks_loaded: int = 0
    embeddings_loaded: int = 0
    chunks_indexed: int = 0
    skipped_missing_embeddings: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return len(self.errors) == 0 and self.chunks_indexed > 0


class IndexingPipeline:
    """Orchestrate chunks + embeddings → vector store.

    Supports two modes:
    1. Pre-computed embeddings: load from disk, match by chunk_id order.
    2. On-the-fly embeddings: generate from chunk content via EmbeddingGenerator.

    Args:
        vector_store: Target vector store instance.
        embedder: EmbeddingGenerator for on-the-fly mode. If None, pre-computed
            embeddings must be provided.
    """

    def __init__(
        self,
        vector_store: SeniorVitalVectorStore,
        embedder: EmbeddingGenerator | None = None,
    ) -> None:
        self._store = vector_store
        self._embedder = embedder

    @staticmethod
    def load_chunks(path: Path) -> list[dict[str, Any]]:
        """Load chunks from a JSON file."""
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def load_precomputed_embeddings(
        embeddings_dir: Path,
    ) -> tuple[list[dict[str, Any]], np.ndarray]:
        """Load pre-computed embeddings from disk.

        Returns:
            Tuple of (metadata_list, embeddings_array).
        """
        return load_embeddings(embeddings_dir)

    def index(
        self,
        chunks: list[dict[str, Any]],
        embeddings: list[list[float]] | np.ndarray | None = None,
        clear: bool = True,
    ) -> IndexingStats:
        """Index chunks into the vector store.

        Args:
            chunks: Chunk dicts with at least 'chunk_id' and 'content'.
            embeddings: Optional pre-computed embeddings (list or numpy array).
                If None, embeddings are generated on-the-fly using the embedder.
            clear: If True, clear existing data before indexing.

        Returns:
            IndexingStats with counts and any errors.
        """
        stats = IndexingStats(chunks_loaded=len(chunks))

        if not chunks:
            return stats

        # Validate chunks have required keys
        valid_chunks: list[dict[str, Any]] = []
        for chunk in chunks:
            if "chunk_id" not in chunk or "content" not in chunk:
                stats.errors.append(
                    f"Chunk missing required keys (chunk_id/content): {chunk.get('chunk_id', '?')}"
                )
                continue
            valid_chunks.append(chunk)

        if not valid_chunks:
            stats.errors.append("No valid chunks to index")
            return stats

        # Resolve embeddings
        embeddings_list: list[list[float]] | None = None

        if embeddings is not None:
            # Pre-computed mode
            if isinstance(embeddings, np.ndarray):
                embeddings_list = embeddings.tolist()
            else:
                embeddings_list = embeddings

            # Validate count match
            if len(embeddings_list) != len(valid_chunks):
                stats.errors.append(
                    f"Embedding count mismatch: {len(valid_chunks)} chunks vs {len(embeddings_list)} embeddings"
                )
                return stats

            stats.embeddings_loaded = len(embeddings_list)
        elif self._embedder is not None:
            # On-the-fly generation mode
            contents = [c["content"] for c in valid_chunks]
            embeddings_list = self._embedder.embed_batch(contents)
            stats.embeddings_loaded = len(embeddings_list)
        else:
            stats.errors.append(
                "No embeddings provided and no embedder available for on-the-fly generation"
            )
            return stats

        # Index into vector store
        try:
            self._store.create_or_load(
                chunks=valid_chunks,
                embeddings=embeddings_list,
                clear=clear,
            )
            stats.chunks_indexed = self._store.count()
        except Exception as e:
            stats.errors.append(f"Vector store indexing failed: {e}")

        return stats

    def index_from_files(
        self,
        chunks_path: Path,
        embeddings_dir: Path | None = None,
        clear: bool = True,
    ) -> IndexingStats:
        """Convenience: load chunks (and optionally pre-computed embeddings) from disk, then index.

        Args:
            chunks_path: Path to all_chunks.json.
            embeddings_dir: Optional directory with pre-computed embeddings.
                If None, generates embeddings on-the-fly using the embedder.
            clear: If True, clear existing data before indexing.

        Returns:
            IndexingStats.
        """
        # Load chunks
        if not chunks_path.exists():
            stats = IndexingStats()
            stats.errors.append(f"Chunks file not found: {chunks_path}")
            return stats

        chunks = self.load_chunks(chunks_path)

        # Load pre-computed embeddings if available
        embeddings_array: np.ndarray | None = None
        if embeddings_dir is not None and embeddings_dir.exists():
            _, embeddings_array = self.load_precomputed_embeddings(embeddings_dir)
            stats_partial = IndexingStats(chunks_loaded=len(chunks), embeddings_loaded=len(embeddings_array))
        else:
            stats_partial = IndexingStats(chunks_loaded=len(chunks))

        # Index
        return self.index(chunks, embeddings=embeddings_array, clear=clear)

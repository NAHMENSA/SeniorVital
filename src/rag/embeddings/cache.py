"""MD5-based embedding cache for SeniorVital RAG.

Caches embeddings by file content hash to avoid redundant recomputation.
"""

import hashlib
import json
from pathlib import Path

import numpy as np


class EmbeddingCache:
    """File-based embedding cache keyed by MD5 of content.

    Cache structure:
        <cache_dir>/
            <md5_hash>.npy       — embedding vector
            <md5_hash>.json      — metadata (original text length, model, etc.)

    Args:
        cache_dir: Directory for cached embeddings.
    """

    def __init__(self, cache_dir: str | Path) -> None:
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _hash_text(text: str) -> str:
        """Return MD5 hex digest of the input text."""
        return hashlib.md5(text.encode("utf-8")).hexdigest()

    def has(self, text: str) -> bool:
        """Check if an embedding exists for the given text."""
        key = self._hash_text(text)
        return (self.cache_dir / f"{key}.npy").exists()

    def get(self, text: str) -> list[float] | None:
        """Retrieve cached embedding for the text, or None if not cached."""
        key = self._hash_text(text)
        npy_path = self.cache_dir / f"{key}.npy"
        if not npy_path.exists():
            return None
        vector = np.load(npy_path)
        return vector.tolist()

    def put(self, text: str, embedding: list[float]) -> None:
        """Store an embedding in the cache."""
        key = self._hash_text(text)
        np.save(self.cache_dir / f"{key}.npy", np.array(embedding))
        # Store metadata for debugging
        meta_path = self.cache_dir / f"{key}.json"
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump({"text_length": len(text), "dim": len(embedding)}, f)

    def invalidate(self, text: str) -> bool:
        """Remove a cached embedding. Returns True if it existed."""
        key = self._hash_text(text)
        npy_path = self.cache_dir / f"{key}.npy"
        meta_path = self.cache_dir / f"{key}.json"
        existed = npy_path.exists()
        npy_path.unlink(missing_ok=True)
        meta_path.unlink(missing_ok=True)
        return existed

    def clear(self) -> int:
        """Remove all cached embeddings. Returns number of entries removed."""
        count = 0
        for f in self.cache_dir.glob("*.npy"):
            f.unlink()
            count += 1
        for f in self.cache_dir.glob("*.json"):
            f.unlink()
        return count

    def count(self) -> int:
        """Return number of cached entries."""
        return sum(1 for _ in self.cache_dir.glob("*.npy"))

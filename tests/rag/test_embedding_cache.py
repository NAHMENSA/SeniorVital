"""Tests for EmbeddingCache."""

from pathlib import Path

import numpy as np
import pytest

from rag.embeddings.cache import EmbeddingCache


@pytest.fixture
def cache(tmp_path: Path) -> EmbeddingCache:
    return EmbeddingCache(cache_dir=tmp_path / "cache")


class TestEmbeddingCachePutGet:
    def test_put_and_get(self, cache: EmbeddingCache) -> None:
        embedding = [0.1, 0.2, 0.3]
        cache.put("hello world", embedding)
        result = cache.get("hello world")
        assert result is not None
        np.testing.assert_allclose(result, embedding)

    def test_get_missing_returns_none(self, cache: EmbeddingCache) -> None:
        assert cache.get("nonexistent") is None

    def test_same_text_returns_same(self, cache: EmbeddingCache) -> None:
        embedding = [0.5, 0.6, 0.7]
        cache.put("test", embedding)
        r1 = cache.get("test")
        r2 = cache.get("test")
        assert r1 == r2

    def test_different_texts_different_keys(self, cache: EmbeddingCache) -> None:
        cache.put("a", [0.1])
        cache.put("b", [0.2])
        assert cache.get("a") == [0.1]
        assert cache.get("b") == [0.2]


class TestEmbeddingCacheHas:
    def test_has_after_put(self, cache: EmbeddingCache) -> None:
        cache.put("text", [0.1])
        assert cache.has("text") is True

    def test_has_missing(self, cache: EmbeddingCache) -> None:
        assert cache.has("missing") is False


class TestEmbeddingCacheInvalidate:
    def test_invalidate_existing(self, cache: EmbeddingCache) -> None:
        cache.put("text", [0.1])
        assert cache.invalidate("text") is True
        assert cache.get("text") is None

    def test_invalidate_missing(self, cache: EmbeddingCache) -> None:
        assert cache.invalidate("missing") is False


class TestEmbeddingCacheClear:
    def test_clear_removes_all(self, cache: EmbeddingCache) -> None:
        cache.put("a", [0.1])
        cache.put("b", [0.2])
        count = cache.clear()
        assert count == 2
        assert cache.count() == 0

    def test_clear_empty(self, cache: EmbeddingCache) -> None:
        assert cache.clear() == 0


class TestEmbeddingCacheCount:
    def test_count_empty(self, cache: EmbeddingCache) -> None:
        assert cache.count() == 0

    def test_count_after_puts(self, cache: EmbeddingCache) -> None:
        cache.put("a", [0.1])
        cache.put("b", [0.2])
        assert cache.count() == 2

    def test_count_after_overwrite(self, cache: EmbeddingCache) -> None:
        cache.put("a", [0.1])
        cache.put("a", [0.99])
        assert cache.count() == 1


class TestEmbeddingCachePersistence:
    def test_cache_persists_across_instances(self, tmp_path: Path) -> None:
        cache_dir = tmp_path / "cache"
        c1 = EmbeddingCache(cache_dir=cache_dir)
        c1.put("persistent", [0.42])

        c2 = EmbeddingCache(cache_dir=cache_dir)
        result = c2.get("persistent")
        assert result is not None
        np.testing.assert_allclose(result, [0.42])

"""Tests for IndexingPipeline."""

import json
import tempfile
from pathlib import Path

import numpy as np
import pytest

from rag.indexing.pipeline import IndexingPipeline, IndexingStats


@pytest.fixture
def sample_chunks() -> list[dict]:
    return [
        {
            "chunk_id": "c1",
            "content": "Ejercicios de equilibrio para ancianos",
            "macrodomain": "A",
            "document_name": "guia_fisioterapia.md",
        },
        {
            "chunk_id": "c2",
            "content": "Rutinas de fortalecimiento muscular",
            "macrodomain": "B",
            "document_name": "ejercicios.md",
        },
        {
            "chunk_id": "c3",
            "content": "Plan nutricional para diabetes tipo 2",
            "macrodomain": "E",
            "document_name": "nutricion.md",
        },
    ]


@pytest.fixture
def sample_embeddings() -> list[list[float]]:
    return [[0.1] * 384, [0.2] * 384, [0.3] * 384]


@pytest.fixture
def sample_embeddings_array() -> np.ndarray:
    return np.array([[0.1] * 384, [0.2] * 384, [0.3] * 384])


class TestIndexingStats:
    def test_empty_stats(self) -> None:
        stats = IndexingStats()
        assert not stats.success
        assert stats.chunks_loaded == 0
        assert stats.errors == []

    def test_success_when_indexed(self) -> None:
        stats = IndexingStats(chunks_loaded=5, chunks_indexed=5)
        assert stats.success

    def test_failure_when_errors(self) -> None:
        stats = IndexingStats(chunks_loaded=5, chunks_indexed=5, errors=["fail"])
        assert not stats.success

    def test_failure_when_zero_indexed(self) -> None:
        stats = IndexingStats(chunks_loaded=0, chunks_indexed=0)
        assert not stats.success


class TestLoadChunks:
    def test_load_valid_json(self, tmp_path: Path, sample_chunks: list[dict]) -> None:
        path = tmp_path / "chunks.json"
        path.write_text(json.dumps(sample_chunks), encoding="utf-8")
        loaded = IndexingPipeline.load_chunks(path)
        assert len(loaded) == 3
        assert loaded[0]["chunk_id"] == "c1"

    def test_load_missing_file(self, tmp_path: Path) -> None:
        path = tmp_path / "nonexistent.json"
        with pytest.raises(FileNotFoundError):
            IndexingPipeline.load_chunks(path)


class TestIndex:
    def test_index_with_precomputed_list(
        self, tmp_path: Path, sample_chunks: list[dict], sample_embeddings: list[list[float]]
    ) -> None:
        from rag.vector_store import SeniorVitalVectorStore
        store = SeniorVitalVectorStore(persist_directory=tmp_path / "vs")
        pipeline = IndexingPipeline(vector_store=store)

        stats = pipeline.index(sample_chunks, embeddings=sample_embeddings, clear=True)

        assert stats.success
        assert stats.chunks_loaded == 3
        assert stats.chunks_indexed == 3
        assert stats.embeddings_loaded == 3
        assert store.count() == 3

    def test_index_with_numpy_array(
        self, tmp_path: Path, sample_chunks: list[dict], sample_embeddings_array: np.ndarray
    ) -> None:
        from rag.vector_store import SeniorVitalVectorStore
        store = SeniorVitalVectorStore(persist_directory=tmp_path / "vs")
        pipeline = IndexingPipeline(vector_store=store)

        stats = pipeline.index(sample_chunks, embeddings=sample_embeddings_array, clear=True)

        assert stats.success
        assert stats.chunks_indexed == 3

    def test_index_empty_chunks(self, tmp_path: Path) -> None:
        from rag.vector_store import SeniorVitalVectorStore
        store = SeniorVitalVectorStore(persist_directory=tmp_path / "vs")
        pipeline = IndexingPipeline(vector_store=store)

        stats = pipeline.index([], embeddings=[], clear=True)

        assert not stats.success
        assert stats.chunks_loaded == 0

    def test_index_chunk_missing_keys(self, tmp_path: Path) -> None:
        from rag.vector_store import SeniorVitalVectorStore
        store = SeniorVitalVectorStore(persist_directory=tmp_path / "vs")
        pipeline = IndexingPipeline(vector_store=store)

        bad_chunks = [{"content": "no chunk_id"}, {"chunk_id": "c2"}]
        stats = pipeline.index(bad_chunks, embeddings=[[0.1] * 384, [0.2] * 384], clear=True)

        assert not stats.success
        assert any("missing required keys" in e for e in stats.errors)
        assert any("no valid chunks" in e.lower() for e in stats.errors)

    def test_index_embedding_count_mismatch(
        self, tmp_path: Path, sample_chunks: list[dict]
    ) -> None:
        from rag.vector_store import SeniorVitalVectorStore
        store = SeniorVitalVectorStore(persist_directory=tmp_path / "vs")
        pipeline = IndexingPipeline(vector_store=store)

        stats = pipeline.index(
            sample_chunks,
            embeddings=[[0.1] * 384],  # Only 1 embedding for 3 chunks
            clear=True,
        )

        assert not stats.success
        assert "mismatch" in stats.errors[0].lower()

    def test_index_no_embeddings_no_embedder(self, tmp_path: Path, sample_chunks: list[dict]) -> None:
        from rag.vector_store import SeniorVitalVectorStore
        store = SeniorVitalVectorStore(persist_directory=tmp_path / "vs")
        pipeline = IndexingPipeline(vector_store=store)

        stats = pipeline.index(sample_chunks, embeddings=None, clear=True)

        assert not stats.success
        assert "no embedder" in stats.errors[0].lower()

    def test_index_clear_false_preserves_existing(
        self, tmp_path: Path, sample_embeddings: list[list[float]]
    ) -> None:
        from rag.vector_store import SeniorVitalVectorStore
        store = SeniorVitalVectorStore(persist_directory=tmp_path / "vs")
        pipeline = IndexingPipeline(vector_store=store)

        # Index first batch
        chunks1 = [
            {"chunk_id": "c1", "content": "primero", "macrodomain": "A"},
        ]
        pipeline.index(chunks1, embeddings=[sample_embeddings[0]], clear=True)
        assert store.count() == 1

        # Index second batch without clear
        chunks2 = [
            {"chunk_id": "c2", "content": "segundo", "macrodomain": "B"},
        ]
        pipeline.index(chunks2, embeddings=[sample_embeddings[1]], clear=False)
        assert store.count() == 2


class TestIndexFromFiles:
    def test_index_from_files_precomputed(
        self, tmp_path: Path, sample_chunks: list[dict], sample_embeddings: list[list[float]]
    ) -> None:
        from rag.vector_store import SeniorVitalVectorStore

        chunks_path = tmp_path / "chunks.json"
        chunks_path.write_text(json.dumps(sample_chunks), encoding="utf-8")

        emb_dir = tmp_path / "embeddings"
        emb_dir.mkdir()
        np.save(emb_dir / "embeddings.npy", np.array(sample_embeddings))
        meta = [{"chunk_id": c["chunk_id"]} for c in sample_chunks]
        with open(emb_dir / "embeddings_metadata.json", "w") as f:
            json.dump(meta, f)

        store = SeniorVitalVectorStore(persist_directory=tmp_path / "vs")
        pipeline = IndexingPipeline(vector_store=store)

        stats = pipeline.index_from_files(chunks_path, embeddings_dir=emb_dir, clear=True)

        assert stats.success
        assert stats.chunks_indexed == 3

    def test_index_from_files_missing_chunks(self, tmp_path: Path) -> None:
        from rag.vector_store import SeniorVitalVectorStore
        store = SeniorVitalVectorStore(persist_directory=tmp_path / "vs")
        pipeline = IndexingPipeline(vector_store=store)

        stats = pipeline.index_from_files(tmp_path / "nonexistent.json", clear=True)

        assert not stats.success
        assert "not found" in stats.errors[0].lower()

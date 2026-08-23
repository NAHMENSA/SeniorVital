"""Tests for SeniorVital embedding generation and persistence."""

from pathlib import Path

import numpy as np
import pytest

from rag.embeddings import EmbeddingGenerator, get_embeddings_output_dir, load_embeddings, save_embeddings


class FakeEmbeddings:
    """Mock HuggingFace-compatible embeddings object."""

    def __init__(self, dimension: int = 384) -> None:
        self.dimension = dimension

    def embed_query(self, text: str) -> list[float]:
        return [float(ord(c)) for c in text[: self.dimension]] + [0.0] * (
            self.dimension - min(len(text), self.dimension)
        )

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_query(text) for text in texts]


class TestEmbeddingGenerator:
    """Unit tests for EmbeddingGenerator."""

    def test_embed_text(self) -> None:
        gen = EmbeddingGenerator(model_name="intfloat/multilingual-e5-small")
        gen._embeddings = FakeEmbeddings(dimension=384)
        vector = gen.embed_text("hola")
        assert len(vector) == 384
        assert isinstance(vector, list)
        assert all(isinstance(v, float) for v in vector)

    def test_embed_batch(self) -> None:
        gen = EmbeddingGenerator()
        gen._embeddings = FakeEmbeddings(dimension=384)
        vectors = gen.embed_batch(["uno", "dos", "tres"])
        assert len(vectors) == 3
        assert all(len(v) == 384 for v in vectors)

    def test_embed_batch_empty(self) -> None:
        gen = EmbeddingGenerator()
        gen._embeddings = FakeEmbeddings(dimension=384)
        assert gen.embed_batch([]) == []

    def test_generate_for_chunks(self) -> None:
        gen = EmbeddingGenerator()
        gen._embeddings = FakeEmbeddings(dimension=384)
        chunks = [
            {"chunk_id": "a", "content": "one"},
            {"chunk_id": "b", "content": "two"},
        ]
        enriched = gen.generate_for_chunks(chunks)
        assert len(enriched) == 2
        assert all("embedding" in c for c in enriched)
        assert all(len(c["embedding"]) == 384 for c in enriched)
        # Original chunks should not be mutated.
        assert "embedding" not in chunks[0]

    def test_generate_for_chunks_empty(self) -> None:
        gen = EmbeddingGenerator()
        gen._embeddings = FakeEmbeddings(dimension=384)
        assert gen.generate_for_chunks([]) == []

    def test_dimension(self) -> None:
        gen = EmbeddingGenerator()
        gen._embeddings = FakeEmbeddings(dimension=384)
        assert gen.dimension() == 384


class TestPersistence:
    """Unit tests for save_embeddings / load_embeddings roundtrip."""

    def test_save_and_load_embeddings(self, tmp_path: Path) -> None:
        data = [
            {"chunk_id": "1", "content": "a", "embedding": [1.0, 2.0, 3.0]},
            {"chunk_id": "2", "content": "b", "embedding": [4.0, 5.0, 6.0]},
        ]
        save_embeddings(data, tmp_path, model_name="test/model", chunk_source="chunks.json")

        metadata, vectors = load_embeddings(tmp_path)
        assert len(metadata) == 2
        assert vectors.shape == (2, 3)
        assert metadata[0]["chunk_id"] == "1"
        assert "embedding" not in metadata[0]
        assert np.allclose(vectors[0], [1.0, 2.0, 3.0])

    def test_manifest_is_written(self, tmp_path: Path) -> None:
        data = [
            {"chunk_id": "1", "content": "a", "embedding": [0.0, 0.0]},
        ]
        save_embeddings(data, tmp_path, model_name="test/model", chunk_source="chunks.json")

        manifest_path = tmp_path / "manifest.json"
        assert manifest_path.exists()
        import json

        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        assert manifest["model"] == "test/model"
        assert manifest["dimension"] == 2
        assert manifest["chunk_count"] == 1
        assert manifest["chunk_source"] == "chunks.json"

    def test_empty_embeddings_raises(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError):
            save_embeddings([], tmp_path, model_name="test/model")

    def test_inconsistent_dimensions_raises(self, tmp_path: Path) -> None:
        data = [
            {"chunk_id": "1", "embedding": [1.0, 2.0]},
            {"chunk_id": "2", "embedding": [1.0, 2.0, 3.0]},
        ]
        with pytest.raises(ValueError):
            save_embeddings(data, tmp_path, model_name="test/model")

    def test_load_missing_files_raises(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            load_embeddings(tmp_path)

    def test_get_embeddings_output_dir(self, tmp_path: Path) -> None:
        out = get_embeddings_output_dir(tmp_path, "org/model-name")
        assert out == tmp_path / "org_model-name"

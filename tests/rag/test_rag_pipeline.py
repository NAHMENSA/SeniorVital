"""Integration tests for SeniorVitalRAGPipeline (mock Ollama, real ChromaDB)."""

from pathlib import Path
from unittest.mock import AsyncMock

import numpy as np
import pytest

from rag.pipeline.query_pipeline import SeniorVitalRAGPipeline
from rag.vector_store import SeniorVitalVectorStore


class FakeEmbedder:
    """Deterministic embedder for tests."""

    def __init__(self, dimension: int = 32) -> None:
        self.dimension = dimension

    def embed_text(self, text: str) -> list[float]:
        rng = np.random.RandomState(hash(text) % (2**31))
        return rng.randn(self.dimension).astype(np.float32).tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_text(t) for t in texts]


@pytest.fixture()
def sample_chunks() -> list[dict]:
    return [
        {
            "chunk_id": "c1",
            "content": "Ejercicio aeróbico para caminar 30 minutos diarios mejora la salud cardiovascular.",
            "document_name": "guia_ejercicio.pdf",
            "macrodomain": "B",
            "chunk_type": "semantic",
        },
        {
            "chunk_id": "c2",
            "content": "La sarcopenia se diagnostica con evaluación de fuerza muscular y masa corporal.",
            "document_name": "sarcopenia.pdf",
            "macrodomain": "A",
            "chunk_type": "fallback",
        },
        {
            "chunk_id": "c3",
            "content": "Dieta balanceada con proteínas magras y vegetales para diabeticos.",
            "document_name": "nutricion.pdf",
            "macrodomain": "E",
            "chunk_type": "semantic",
        },
    ]


@pytest.fixture()
def pipeline(tmp_path: Path, sample_chunks: list[dict]):
    embedder = FakeEmbedder(dimension=32)
    vs = SeniorVitalVectorStore(
        persist_directory=tmp_path,
        collection_name="test_pipeline",
        embedder=embedder,
    )
    vs.add_chunks(sample_chunks, embeddings=embedder.embed_batch(
        [c["content"] for c in sample_chunks]
    ))

    from rag.generation.ollama_client import OllamaClient
    mock_ollama = OllamaClient()
    mock_ollama.generate = AsyncMock(  # type: ignore
        return_value="Según la base de conocimiento, el ejercicio aeróbico de caminar es recomendado para mejorar la salud cardiovascular."
    )

    pipe = SeniorVitalRAGPipeline(
        vector_store=vs,
        ollama_client=mock_ollama,
    )
    return pipe


class TestPipelineProcessQuery:
    @pytest.mark.asyncio
    async def test_returns_structured_result(self, pipeline: SeniorVitalRAGPipeline) -> None:
        result = await pipeline.process_query("¿Qué ejercicios debo hacer?")
        assert "answer" in result
        assert "sources" in result
        assert "agent" in result
        assert "macrodomain" in result
        assert "query_info" in result

    @pytest.mark.asyncio
    async def test_auto_detects_agent(self, pipeline: SeniorVitalRAGPipeline) -> None:
        result = await pipeline.process_query("¿Qué ejercicios de fuerza son seguros?")
        assert result["query_info"]["detected_macrodomain"] == "B"
        assert result["query_info"]["detected_agent"] == "Exercise Architect"

    @pytest.mark.asyncio
    async def test_explicit_agent_overrides(self, pipeline: SeniorVitalRAGPipeline) -> None:
        result = await pipeline.process_query("test", agent_name="Nutri-Buddy")
        assert result["agent"] == "Nutri-Buddy"
        assert result["macrodomain"] == "E"

    @pytest.mark.asyncio
    async def test_retrieves_chunks(self, pipeline: SeniorVitalRAGPipeline) -> None:
        result = await pipeline.process_query("ejercicio aeróbico caminar")
        assert len(result["sources"]) > 0

    @pytest.mark.asyncio
    async def test_ollama_called(self, pipeline: SeniorVitalRAGPipeline) -> None:
        await pipeline.process_query("test")
        pipeline.ollama.generate.assert_called_once()  # type: ignore

    @pytest.mark.asyncio
    async def test_explicit_macrodomain(self, pipeline: SeniorVitalRAGPipeline) -> None:
        result = await pipeline.process_query("test", macrodomain="E")
        assert result["macrodomain"] == "E"
        assert result["agent"] == "Nutri-Buddy"

    @pytest.mark.asyncio
    async def test_custom_k(self, pipeline: SeniorVitalRAGPipeline) -> None:
        result = await pipeline.process_query("ejercicio", k=2)
        assert len(result["sources"]) <= 2


class TestPipelineHealthCheck:
    @pytest.mark.asyncio
    async def test_health_check_returns_dict(self, pipeline: SeniorVitalRAGPipeline) -> None:
        # Mock health_check to avoid Ollama connection.
        pipeline.ollama.health_check = AsyncMock(return_value=True)  # type: ignore
        result = await pipeline.health_check()
        assert "ollama_available" in result
        assert "vector_store_count" in result
        assert "pipeline_ready" in result
        assert result["vector_store_count"] == 3

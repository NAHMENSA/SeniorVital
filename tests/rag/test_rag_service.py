"""Tests for RAG service HTTP endpoints."""

import importlib.util
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

# Add src/ to path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

# Import rag-service/main.py as a module (directory has hyphen, can't use normal import)
_spec = importlib.util.spec_from_file_location(
    "rag_service_main",
    str(ROOT_DIR / "rag-service" / "main.py"),
)
rag_service_main = importlib.util.module_from_spec(_spec)
sys.modules["rag_service_main"] = rag_service_main
_spec.loader.exec_module(rag_service_main)

from httpx import ASGITransport, AsyncClient


@pytest.fixture
def mock_pipeline() -> MagicMock:
    """Create a mock SeniorVitalRAGPipeline."""
    mock = MagicMock()
    mock.process_query = AsyncMock(return_value={
        "answer": "Los ejercicios de equilibrio son importantes para prevenir caídas.",
        "sources": [
            {
                "chunk_id": "c1",
                "content": "Ejercicios de equilibrio para ancianos",
                "metadata": {"macrodomain": "A", "document_name": "guia.md"},
                "distance": 0.35,
            }
        ],
        "agent": "Physio-Evaluator",
        "macrodomain": "A",
        "warnings": [],
        "query_info": {
            "normalized_query": "ejercicios de equilibrio",
            "detected_macrodomain": "A",
            "detected_agent": "Physio-Evaluator",
            "filters": {"macrodomain": "A"},
        },
    })
    mock.health_check = AsyncMock(return_value={
        "ollama_available": True,
        "vector_store_count": 363,
        "pipeline_ready": True,
    })
    mock.vector_store = MagicMock()
    mock.vector_store.count.return_value = 363
    return mock


@pytest.fixture
def app_with_mock(mock_pipeline: MagicMock):
    """Create FastAPI app with mocked pipeline."""
    from rag_service_main import app
    import rag_service_main as mod

    mod.pipeline = mock_pipeline
    return app


@pytest.mark.asyncio
async def test_rag_query_returns_answer(app_with_mock) -> None:
    transport = ASGITransport(app=app_with_mock)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/rag/query", json={"query": "¿Qué ejercicios de equilibrio debo hacer?"})

    assert resp.status_code == 200
    data = resp.json()
    assert "answer" in data
    assert data["agent"] == "Physio-Evaluator"
    assert data["macrodomain"] == "A"
    assert len(data["sources"]) == 1


@pytest.mark.asyncio
async def test_rag_query_with_explicit_agent(app_with_mock) -> None:
    transport = ASGITransport(app=app_with_mock)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/rag/query", json={
            "query": "dame un plan de comidas",
            "agent_name": "Nutri-Buddy",
        })

    assert resp.status_code == 200
    data = resp.json()
    assert "answer" in data


@pytest.mark.asyncio
async def test_rag_query_empty_query(app_with_mock) -> None:
    transport = ASGITransport(app=app_with_mock)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/rag/query", json={"query": ""})

    assert resp.status_code == 422  # Pydantic validation: min_length=1


@pytest.mark.asyncio
async def test_rag_health(app_with_mock) -> None:
    transport = ASGITransport(app=app_with_mock)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/rag/health")

    assert resp.status_code == 200
    data = resp.json()
    assert data["ollama_available"] is True
    assert data["vector_store_count"] == 363
    assert data["pipeline_ready"] is True


@pytest.mark.asyncio
async def test_rag_stats(app_with_mock) -> None:
    transport = ASGITransport(app=app_with_mock)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/rag/stats")

    assert resp.status_code == 200
    data = resp.json()
    assert data["vector_store_count"] == 363


@pytest.mark.asyncio
async def test_rag_query_pipeline_error(app_with_mock, mock_pipeline) -> None:
    mock_pipeline.process_query.side_effect = RuntimeError("Ollama timeout")

    transport = ASGITransport(app=app_with_mock)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/rag/query", json={"query": "test"})

    assert resp.status_code == 500
    assert "RAG pipeline error" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_rag_query_no_pipeline() -> None:
    """When pipeline is None, should return 503."""
    import rag_service_main as mod
    original = mod.pipeline
    mod.pipeline = None
    try:
        from rag_service_main import app
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post("/rag/query", json={"query": "test"})
        assert resp.status_code == 503
    finally:
        mod.pipeline = original

"""Tests for SeniorVital vector store and retriever."""

import json
from pathlib import Path

import numpy as np
import pytest


class FakeEmbedder:
    """Deterministic embedder for tests. Returns stable vectors from text."""

    def __init__(self, dimension: int = 32) -> None:
        self.dimension = dimension
        self.call_count = 0

    def embed_text(self, text: str) -> list[float]:
        self.call_count += 1
        rng = np.random.RandomState(hash(text) % (2**31))
        vec = rng.randn(self.dimension).astype(np.float32).tolist()
        return vec

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_text(t) for t in texts]


@pytest.fixture()
def fake_chunks() -> list[dict]:
    return [
        {
            "chunk_id": "chunk-001",
            "content": "Ejercicio aeróbico para adultos mayores",
            "document_name": "guia_ejercicio.pdf",
            "source_path": "guia_ejercicio.pdf",
            "macrodomain": "B",
            "macrodomain_name": "Exercise Architect",
            "section_path": "Aeróbico > Caminata",
            "chunk_type": "semantic",
            "chunk_index": 0,
            "total_chunks": 3,
            "char_count": 120,
            "word_count": 15,
            "has_markdown_headers": False,
            "level": "principiante",
            "pathology": "hipertension",
            "keywords": ["caminata", "cardio", "seguro"],
        },
        {
            "chunk_id": "chunk-002",
            "content": "Evaluación fisioterapéutica del paciente",
            "document_name": "fisioterapia.pdf",
            "source_path": "fisioterapia.pdf",
            "macrodomain": "A",
            "macrodomain_name": "Physio-Evaluator",
            "section_path": "Evaluación > Movilidad",
            "chunk_type": "structural",
            "chunk_index": 1,
            "total_chunks": 4,
            "char_count": 200,
            "word_count": 25,
            "has_markdown_headers": True,
            "level": "intermedio",
            "pathology": "artritis",
            "keywords": ["movilidad", "evaluación"],
        },
        {
            "chunk_id": "chunk-003",
            "content": "Nutrición para recuperación muscular",
            "document_name": "nutricion.pdf",
            "source_path": "nutricion.pdf",
            "macrodomain": "E",
            "macrodomain_name": "Nutri-Buddy",
            "section_path": "Nutrición > Proteínas",
            "chunk_type": "semantic",
            "chunk_index": 0,
            "total_chunks": 2,
            "char_count": 150,
            "word_count": 18,
            "has_markdown_headers": True,
            "level": "avanzado",
            "pathology": "diabetes",
            "keywords": ["proteínas", "recuperación"],
        },
    ]


@pytest.fixture()
def vector_store(tmp_path: Path, fake_chunks: list[dict]):
    from rag.vector_store import SeniorVitalVectorStore

    store = SeniorVitalVectorStore(
        persist_directory=tmp_path,
        collection_name="test_kb",
        embedder=FakeEmbedder(dimension=32),
    )
    store.add_chunks(fake_chunks)
    return store


class TestVectorStore:
    def test_add_and_count(self, vector_store, fake_chunks) -> None:
        assert vector_store.count() == len(fake_chunks)

    def test_add_empty_noop(self, vector_store) -> None:
        before = vector_store.count()
        vector_store.add_chunks([])
        assert vector_store.count() == before

    def test_get_by_chunk_id(self, vector_store, fake_chunks) -> None:
        result = vector_store.get_by_chunk_id("chunk-001")
        assert result is not None
        assert result["content"] == fake_chunks[0]["content"]
        assert result["metadata"]["macrodomain"] == "B"

    def test_get_missing_chunk_id(self, vector_store) -> None:
        result = vector_store.get_by_chunk_id("nonexistent")
        assert result is None

    def test_search_returns_results(self, vector_store) -> None:
        results = vector_store.search("ejercicio", k=3)
        assert len(results) > 0
        assert len(results) <= 3
        for r in results:
            assert "chunk_id" in r
            assert "content" in r
            assert "metadata" in r
            assert "distance" in r

    def test_search_by_agent(self, vector_store) -> None:
        results = vector_store.search_by_agent("ejercicio", agent_name="Exercise Architect")
        assert all(r["metadata"]["macrodomain"] == "B" for r in results)

    def test_search_by_agent_unknown_raises(self, vector_store) -> None:
        with pytest.raises(ValueError, match="Unknown agent"):
            vector_store.search_by_agent("test", agent_name="Invalid Agent")

    def test_search_by_macrodomain(self, vector_store) -> None:
        results = vector_store.search_by_macrodomain("nutrición", macrodomain="E")
        assert all(r["metadata"]["macrodomain"] == "E" for r in results)

    def test_search_by_filters(self, vector_store) -> None:
        results = vector_store.search_by_filters(
            "ejercicio", filters={"pathology": "artritis"}
        )
        assert all(r["metadata"]["pathology"] == "artritis" for r in results)

    def test_delete_all(self, vector_store) -> None:
        vector_store.delete_all()
        assert vector_store.count() == 0

    def test_upsert_updates(self, vector_store, fake_chunks) -> None:
        updated = {**fake_chunks[0], "content": "Contenido actualizado"}
        vector_store.upsert_chunks([updated])
        result = vector_store.get_by_chunk_id("chunk-001")
        assert result["content"] == "Contenido actualizado"
        assert vector_store.count() == 3

    def test_create_or_load_clear(self, vector_store, fake_chunks) -> None:
        vector_store.create_or_load(chunks=fake_chunks[:1], clear=True)
        assert vector_store.count() == 1


class TestRetriever:
    def test_retrieve(self, vector_store, fake_chunks) -> None:
        from rag.retriever import SeniorVitalRetriever

        retriever = SeniorVitalRetriever(vector_store)
        results = retriever.retrieve("ejercicio", k=3)
        assert len(results) > 0
        assert len(results) <= 3

    def test_retrieve_for_agent(self, vector_store) -> None:
        from rag.retriever import SeniorVitalRetriever

        retriever = SeniorVitalRetriever(vector_store)
        results = retriever.retrieve_for_agent("ejercicio", agent_name="Exercise Architect")
        assert all(r["metadata"]["macrodomain"] == "B" for r in results)

    def test_retrieve_by_macrodomain(self, vector_store) -> None:
        from rag.retriever import SeniorVitalRetriever

        retriever = SeniorVitalRetriever(vector_store)
        results = retriever.retrieve_by_macrodomain("nutrición", macrodomain="E")
        assert all(r["metadata"]["macrodomain"] == "E" for r in results)

    def test_list_agents(self, vector_store) -> None:
        from rag.retriever import SeniorVitalRetriever

        retriever = SeniorVitalRetriever(vector_store)
        agents = retriever.list_agents()
        assert "Exercise Architect" in agents
        assert "Nutri-Buddy" in agents
        assert len(agents) == 6


class TestMetadataPreparation:
    def test_keywords_comma_joined(self, tmp_path) -> None:
        from rag.vector_store import SeniorVitalVectorStore

        store = SeniorVitalVectorStore(
            persist_directory=tmp_path,
            collection_name="test_meta",
            embedder=FakeEmbedder(32),
        )
        chunk = {
            "chunk_id": "meta-1",
            "content": "test",
            "macrodomain": "B",
            "keywords": ["a", "b", "c"],
        }
        meta = store._prepare_metadata(chunk)
        assert meta["keywords"] == "a,b,c"

    def test_empty_keywords_omitted(self, tmp_path) -> None:
        from rag.vector_store import SeniorVitalVectorStore

        store = SeniorVitalVectorStore(
            persist_directory=tmp_path,
            collection_name="test_meta2",
            embedder=FakeEmbedder(32),
        )
        chunk = {"chunk_id": "meta-2", "content": "test"}
        meta = store._prepare_metadata(chunk)
        assert "keywords" not in meta

    def test_none_values_omitted(self, tmp_path) -> None:
        from rag.vector_store import SeniorVitalVectorStore

        store = SeniorVitalVectorStore(
            persist_directory=tmp_path,
            collection_name="test_meta3",
            embedder=FakeEmbedder(32),
        )
        chunk = {"chunk_id": "meta-3", "content": "test", "macrodomain": None}
        meta = store._prepare_metadata(chunk)
        assert "macrodomain" not in meta


class TestAgentMapping:
    def test_all_agents_map_to_macrodomains(self) -> None:
        from rag.vector_store import AGENT_TO_MACRODOMAIN, MACRODOMAIN_TO_AGENT

        assert len(AGENT_TO_MACRODOMAIN) == 6
        for agent, domain in AGENT_TO_MACRODOMAIN.items():
            assert domain in MACRODOMAIN_TO_AGENT
            assert MACRODOMAIN_TO_AGENT[domain] == agent

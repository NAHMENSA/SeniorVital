"""Tests for RAG evaluation framework."""

import json
from pathlib import Path

import pytest

from rag.evaluation.metrics import (
    precision_at_k,
    recall_at_k,
    mrr,
    hit_rate,
    macrodomain_accuracy,
)
from rag.evaluation.quality import (
    keyword_coverage,
    citation_check,
    hallucination_flag,
    answer_length_stats,
)
from rag.evaluation.runner import load_query_set, compute_metrics


# ── Retrieval Metrics ──

class TestPrecisionAtK:
    def test_perfect_precision(self) -> None:
        assert precision_at_k(["a", "b", "c"], ["a", "b", "c"], k=3) == 1.0

    def test_zero_precision(self) -> None:
        assert precision_at_k(["x", "y", "z"], ["a", "b", "c"], k=3) == 0.0

    def test_partial_precision(self) -> None:
        assert precision_at_k(["a", "x", "b"], ["a", "b", "c"], k=3) == pytest.approx(2 / 3)

    def test_k_larger_than_results(self) -> None:
        assert precision_at_k(["a"], ["a", "b"], k=5) == pytest.approx(1 / 5)

    def test_k_zero(self) -> None:
        assert precision_at_k(["a"], ["a"], k=0) == 0.0


class TestRecallAtK:
    def test_perfect_recall(self) -> None:
        assert recall_at_k(["a", "b", "c"], ["a", "b"], k=3) == 1.0

    def test_zero_recall(self) -> None:
        assert recall_at_k(["x", "y"], ["a", "b"], k=5) == 0.0

    def test_partial_recall(self) -> None:
        assert recall_at_k(["a", "x"], ["a", "b", "c"], k=3) == pytest.approx(1 / 3)

    def test_no_relevant_ids(self) -> None:
        assert recall_at_k(["a", "b"], [], k=5) == 0.0


class TestMRR:
    def test_first_rank(self) -> None:
        assert mrr(["a", "b", "c"], ["a"]) == 1.0

    def test_second_rank(self) -> None:
        assert mrr(["x", "a", "b"], ["a"]) == pytest.approx(0.5)

    def test_third_rank(self) -> None:
        assert mrr(["x", "y", "a"], ["a"]) == pytest.approx(1 / 3)

    def test_no_match(self) -> None:
        assert mrr(["x", "y", "z"], ["a"]) == 0.0

    def test_multiple_relevant(self) -> None:
        # Returns reciprocal rank of FIRST relevant
        assert mrr(["x", "b", "a"], ["a", "b"]) == pytest.approx(0.5)


class TestHitRate:
    def test_all_hits(self) -> None:
        results = [
            {"retrieved_ids": ["a", "b"], "relevant_ids": ["a"]},
            {"retrieved_ids": ["c", "d"], "relevant_ids": ["c"]},
        ]
        assert hit_rate(results, k=2) == 1.0

    def test_no_hits(self) -> None:
        results = [
            {"retrieved_ids": ["x", "y"], "relevant_ids": ["a"]},
        ]
        assert hit_rate(results, k=2) == 0.0

    def test_partial_hits(self) -> None:
        results = [
            {"retrieved_ids": ["a", "b"], "relevant_ids": ["a"]},
            {"retrieved_ids": ["x", "y"], "relevant_ids": ["a"]},
        ]
        assert hit_rate(results, k=2) == pytest.approx(0.5)

    def test_empty_results(self) -> None:
        assert hit_rate([], k=5) == 0.0


class TestMacrodomainAccuracy:
    def test_perfect(self) -> None:
        assert macrodomain_accuracy(["A", "B", "C"], ["A", "B", "C"]) == 1.0

    def test_zero(self) -> None:
        assert macrodomain_accuracy(["A", "B"], ["C", "D"]) == 0.0

    def test_partial(self) -> None:
        assert macrodomain_accuracy(["A", "B", "A"], ["A", "C", "B"]) == pytest.approx(1 / 3)


# ── Quality Metrics ──

class TestKeywordCoverage:
    def test_all_found(self) -> None:
        assert keyword_coverage("diabetes y ejercicio", ["diabetes", "ejercicio"]) == 1.0

    def test_none_found(self) -> None:
        assert keyword_coverage("hola mundo", ["diabetes", "ejercicio"]) == 0.0

    def test_partial(self) -> None:
        assert keyword_coverage("diabetes y más", ["diabetes", "ejercicio", "nutrición"]) == pytest.approx(1 / 3)

    def test_empty_keywords(self) -> None:
        assert keyword_coverage("cualquier cosa", []) == 1.0

    def test_case_insensitive(self) -> None:
        assert keyword_coverage("DIABETES", ["diabetes"]) == 1.0


class TestCitationCheck:
    def test_detects_numbered_citation(self) -> None:
        assert citation_check("Ejercicio [1] ayuda", [{"content": "x"}]) is True

    def test_detects_segun(self) -> None:
        assert citation_check("Según el documento, esto es así", [{"content": "x"}]) is True

    def test_detects_fuente(self) -> None:
        assert citation_check("Fuente 1: estudio clínico", [{"content": "x"}]) is True

    def test_no_citation(self) -> None:
        assert citation_check("Esto es una respuesta simple", [{"content": "x"}]) is False

    def test_empty_sources(self) -> None:
        assert citation_check("respuesta", []) is False


class TestHallucinationFlag:
    def test_grounded_answer(self) -> None:
        chunks = [{"content": "La diabetes es una enfermedad crónica que afecta la producción de insulina."}]
        answer = "La diabetes es una enfermedad crónica."
        result = hallucination_flag(answer, chunks)
        assert result["flagged"] is False

    def test_potential_hallucination(self) -> None:
        chunks = [{"content": "Ejercicio ligero es recomendado."}]
        answer = "El estudio clínico de 2024 demostró que la medicina alternativa cura el cáncer."
        result = hallucination_flag(answer, chunks)
        # Should flag since most words aren't in context
        assert result["flagged"] is True or len(result["unsupported_claims"]) > 0

    def test_empty_answer(self) -> None:
        result = hallucination_flag("", [{"content": "x"}])
        assert result["flagged"] is False

    def test_empty_chunks(self) -> None:
        result = hallucination_flag("respuesta larga con palabras significativas", [])
        assert result["flagged"] is False


class TestAnswerLengthStats:
    def test_basic_stats(self) -> None:
        results = [
            {"answer": "uno dos tres"},
            {"answer": "uno dos tres cuatro cinco"},
            {"answer": "uno dos"},
        ]
        stats = answer_length_stats(results)
        assert stats["min"] == 2
        assert stats["max"] == 5
        assert stats["mean"] == 3.3

    def test_empty_results(self) -> None:
        stats = answer_length_stats([])
        assert stats["min"] == 0
        assert stats["max"] == 0


# ── Runner ──

class TestLoadQuerySet:
    def test_loads_queries(self) -> None:
        queries = load_query_set()
        assert len(queries) == 30
        assert all("id" in q for q in queries)
        assert all("query" in q for q in queries)
        assert all("expected_macrodomain" in q for q in queries)
        assert all("relevant_chunk_ids" in q for q in queries)

    def test_query_ids_unique(self) -> None:
        queries = load_query_set()
        ids = [q["id"] for q in queries]
        assert len(ids) == len(set(ids))

    def test_all_domains_covered(self) -> None:
        queries = load_query_set()
        domains = set(q["expected_macrodomain"] for q in queries)
        assert domains == {"A", "B", "C", "D", "E", "F"}


class TestComputeMetrics:
    def test_compute_metrics_basic(self) -> None:
        results = [
            {
                "query_id": "T01",
                "error": None,
                "retrieved_ids": ["a", "b", "c"],
                "relevant_chunk_ids": ["a", "b"],
                "expected_macrodomain": "A",
                "detected_macrodomain": "A",
                "answer": "Respuesta sobre diabetes y ejercicio.",
                "sources": [{"content": "diabetes ejercicio"}],
                "expected_answer_keywords": ["diabetes", "ejercicio"],
                "difficulty": "easy",
            },
        ]
        metrics = compute_metrics(results, k=3)
        assert metrics["valid_queries"] == 1
        assert metrics["retrieval"]["precision_at_k"] == 0.667
        assert metrics["retrieval"]["recall_at_k"] == 1.0
        assert metrics["detection"]["macrodomain_accuracy"] == 1.0

    def test_compute_metrics_with_error(self) -> None:
        results = [
            {
                "query_id": "T01",
                "error": "Ollama timeout",
                "retrieved_ids": [],
                "relevant_chunk_ids": ["a"],
                "expected_macrodomain": "A",
                "detected_macrodomain": None,
                "answer": "",
                "sources": [],
                "expected_answer_keywords": ["x"],
                "difficulty": "easy",
            },
            {
                "query_id": "T02",
                "error": None,
                "retrieved_ids": ["a"],
                "relevant_chunk_ids": ["a"],
                "expected_macrodomain": "B",
                "detected_macrodomain": "B",
                "answer": "test answer with diabetes keyword.",
                "sources": [{"content": "test"}],
                "expected_answer_keywords": ["diabetes"],
                "difficulty": "easy",
            },
        ]
        metrics = compute_metrics(results, k=5)
        assert metrics["valid_queries"] == 1
        assert metrics["errored_queries"] == 1

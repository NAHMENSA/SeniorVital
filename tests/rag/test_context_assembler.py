"""Tests for ContextAssembler."""

import pytest

from rag.pipeline.context_assembler import ContextAssembler


class TestDeduplicate:
    def test_removes_duplicates(self) -> None:
        ca = ContextAssembler()
        chunks = [
            {"content": "Ejercicio aeróbico para caminar", "metadata": {"document_name": "a.pdf"}},
            {"content": "Ejercicio aeróbico para caminar", "metadata": {"document_name": "a.pdf"}},
            {"content": "Nutrición para diabeticos", "metadata": {"document_name": "b.pdf"}},
        ]
        result = ca._deduplicate(chunks)
        assert len(result) == 2

    def test_keeps_different_chunks(self) -> None:
        ca = ContextAssembler()
        chunks = [
            {"content": "Ejercicio aeróbico", "metadata": {}},
            {"content": "Nutrición saludable", "metadata": {}},
        ]
        result = ca._deduplicate(chunks)
        assert len(result) == 2

    def test_empty_input(self) -> None:
        ca = ContextAssembler()
        assert ca._deduplicate([]) == []


class TestTruncateToBudget:
    def test_keeps_all_when_under_budget(self) -> None:
        ca = ContextAssembler(max_context_tokens=4096)
        chunks = [
            {"content": "short text", "metadata": {}},
            {"content": "another short text", "metadata": {}},
        ]
        result = ca._truncate_to_budget(chunks)
        assert len(result) == 2

    def test_truncates_when_over_budget(self) -> None:
        ca = ContextAssembler(max_context_tokens=200)
        long_content = "palabra " * 500  # ~4000 chars
        chunks = [
            {"content": long_content, "metadata": {}},
            {"content": "more text", "metadata": {}},
        ]
        result = ca._truncate_to_budget(chunks)
        assert len(result) >= 1
        # First chunk should be truncated.
        assert result[0]["content"].endswith("...")

    def test_empty_input(self) -> None:
        ca = ContextAssembler()
        assert ca._truncate_to_budget([]) == []


class TestAssemble:
    def test_dedup_then_truncate(self) -> None:
        ca = ContextAssembler(max_context_tokens=4096)
        chunks = [
            {"content": "same content", "metadata": {}},
            {"content": "same content", "metadata": {}},
            {"content": "different", "metadata": {}},
        ]
        result = ca.assemble(chunks)
        assert len(result) == 2

    def test_empty_returns_empty(self) -> None:
        ca = ContextAssembler()
        assert ca.assemble([]) == []


class TestFormatContext:
    def test_formats_chunks_with_source(self) -> None:
        ca = ContextAssembler()
        chunks = [
            {"content": "Ejercicio seguro", "metadata": {"document_name": "guia.pdf"}},
        ]
        result = ca.format_context(chunks)
        assert "guia.pdf" in result
        assert "Ejercicio seguro" in result

    def test_numbered_sources(self) -> None:
        ca = ContextAssembler()
        chunks = [
            {"content": "a", "metadata": {"document_name": "x.pdf"}},
            {"content": "b", "metadata": {"document_name": "y.pdf"}},
        ]
        result = ca.format_context(chunks)
        assert "[1]" in result
        assert "[2]" in result

    def test_empty_message(self) -> None:
        ca = ContextAssembler()
        result = ca.format_context([])
        assert "No se encontró" in result

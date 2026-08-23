"""Tests for SeniorVital knowledge-base chunking components."""

from pathlib import Path

import pytest

from knowledge.chunking import ChunkingOrchestrator, SemanticChunkerWrapper, StructuralChunker
from knowledge.chunking.fallback_chunker import FallbackChunker
from knowledge.chunking.preprocessor import (
    has_markdown_headers,
    markdown_table_to_text,
    normalize_whitespace,
    preprocess_document,
    preprocess_file,
    remove_code_block_fences,
)


class TestPreprocessor:
    """Unit tests for the preprocessing utilities."""

    def test_remove_code_block_fences(self) -> None:
        text = "```python\nprint('hello')\n```\nMore text."
        assert "```" not in remove_code_block_fences(text)
        assert "print('hello')" in remove_code_block_fences(text)

    def test_normalize_whitespace(self) -> None:
        text = "Line one.\n\n\n\nLine two.\n   \nLine three."
        normalized = normalize_whitespace(text)
        assert normalized == "Line one.\n\nLine two.\n\nLine three."

    def test_markdown_table_to_text(self) -> None:
        text = "| A | B |\n|---|---|\n| 1 | 2 |"
        result = markdown_table_to_text(text)
        assert "Tabla:" in result
        assert "A, B" in result
        assert "1, 2" in result

    def test_has_markdown_headers(self) -> None:
        assert has_markdown_headers("# Title\nBody")
        assert not has_markdown_headers("Just body text")

    def test_preprocess_document(self) -> None:
        text = "```\ncode\n```\n\n\n| x | y |\n|---|---|\n| 1 | 2 |"
        processed = preprocess_document(text)
        assert "```" not in processed
        assert "Tabla:" in processed
        assert "code" in processed

    def test_preprocess_file(self, tmp_path: Path) -> None:
        doc = tmp_path / "test.md"
        doc.write_text("# Title\n\nParagraph.\n", encoding="utf-8")
        text, has_headers = preprocess_file(doc)
        assert has_headers
        assert "# Title" in text
        assert "Paragraph." in text


class TestFallbackChunker:
    """Unit tests for the recursive fallback chunker."""

    def test_split_returns_fallback_chunks(self) -> None:
        text = " ".join(["word"] * 500)
        chunker = FallbackChunker(chunk_size=100, chunk_overlap=10)
        chunks = chunker.split(text)
        assert all(c["chunk_type"] == "fallback" for c in chunks)
        assert all(c["section_path"] == "" for c in chunks)
        assert all(len(c["content"]) <= 100 for c in chunks)

    def test_split_respects_overlap(self) -> None:
        text = "\n\n".join(f"Paragraph {i}." for i in range(20))
        chunker = FallbackChunker(chunk_size=80, chunk_overlap=20)
        chunks = chunker.split(text)
        assert len(chunks) > 1
        # Each chunk should be at most the configured chunk size.
        assert all(len(c["content"]) <= chunker.chunk_size for c in chunks)

    def test_split_file(self, tmp_path: Path) -> None:
        doc = tmp_path / "fallback.md"
        doc.write_text("# Title\n\n" + "\n\n".join(["Sentence."] * 50), encoding="utf-8")
        chunker = FallbackChunker(chunk_size=200, chunk_overlap=20)
        chunks = chunker.split_file(doc)
        assert len(chunks) >= 1
        assert all(c["chunk_type"] == "fallback" for c in chunks)


class TestStructuralChunker:
    """Unit tests for the Markdown header chunker."""

    def test_split_preserves_headers(self) -> None:
        text = "# Section 1\nBody one.\n\n## Subsection\nBody two.\n\n# Section 2\nBody three."
        chunker = StructuralChunker()
        chunks = chunker.split(text)
        assert len(chunks) >= 2
        assert any("Section 1" in c["section_path"] for c in chunks)
        assert all(c["chunk_type"] == "structural" for c in chunks)

    def test_split_file_skips_when_no_headers(self, tmp_path: Path) -> None:
        doc = tmp_path / "plain.md"
        doc.write_text("No headers here.\n", encoding="utf-8")
        result, has_headers = StructuralChunker().split_file(doc)
        assert not has_headers
        assert result == []


class TestSemanticChunkerWrapper:
    """Tests for the semantic chunker wrapper."""

    def test_is_available_true(self) -> None:
        assert SemanticChunkerWrapper().is_available()

    def test_split_on_tiny_text(self) -> None:
        """Semantic chunking of a very short text should return a single chunk."""
        chunker = SemanticChunkerWrapper()
        text = "This is a single small paragraph."
        chunks = chunker.split(text)
        assert len(chunks) == 1
        assert chunks[0]["content"] == text
        assert chunks[0]["chunk_type"] == "semantic"

    @pytest.mark.slow
    def test_split_on_medium_text(self) -> None:
        """Semantic chunking should split a medium text into multiple chunks."""
        text = "\n\n".join(f"Distinct paragraph number {i} about exercise and older adults." for i in range(20))
        chunker = SemanticChunkerWrapper(breakpoint_threshold_amount=85)
        chunks = chunker.split(text)
        assert len(chunks) > 1
        assert all(c["chunk_type"] == "semantic" for c in chunks)




class TestChunkingOrchestratorMerge:
    """Tests for the chunking orchestrator merge logic."""

    def test_merge_small_chunks_with_next(self) -> None:
        orchestrator = ChunkingOrchestrator()
        chunks = [
            {"content": "short one", "chunk_type": "semantic", "chunk_index": 0},
            {"content": "word " * 90, "chunk_type": "semantic", "chunk_index": 1},
        ]
        merged = orchestrator._merge_small_chunks(chunks)
        assert len(merged) == 1
        assert merged[0]["chunk_type"] == "semantic"
        assert len(merged[0]["content"].split()) > 80

    def test_merge_does_not_exceed_max_merge_chars(self) -> None:
        orchestrator = ChunkingOrchestrator()
        small = "a " * 30  # ~60 chars, 30 words
        large = "b " * 500  # ~1000 chars, 500 words
        chunks = [
            {"content": small, "chunk_type": "semantic", "chunk_index": 0},
            {"content": large, "chunk_type": "fallback", "chunk_index": 1},
        ]
        merged = orchestrator._merge_small_chunks(chunks)
        # The small chunk cannot be merged because combined would exceed 1,000 chars.
        assert len(merged) == 2

    def test_merge_backward_for_trailing_small_chunk(self) -> None:
        orchestrator = ChunkingOrchestrator()
        chunks = [
            {"content": "word " * 90, "chunk_type": "semantic", "chunk_index": 0},
            {"content": "small ending", "chunk_type": "semantic", "chunk_index": 1},
        ]
        merged = orchestrator._merge_small_chunks(chunks)
        assert len(merged) == 1

    def test_empty_and_single_chunk(self) -> None:
        orchestrator = ChunkingOrchestrator()
        assert orchestrator._merge_small_chunks([]) == []
        single = [{"content": "only chunk", "chunk_type": "semantic", "chunk_index": 0}]
        assert orchestrator._merge_small_chunks(single) == single


class TestChunkingOrchestratorEndToEnd:
    """End-to-end tests for the orchestrator with a mock semantic chunker."""

    def test_process_short_document_uses_fallback(self, tmp_path: Path) -> None:
        doc = tmp_path / "short.md"
        doc.write_text("Short doc.\n\nAnother paragraph.", encoding="utf-8")
        orchestrator = ChunkingOrchestrator()
        chunks = orchestrator.process_document(doc, "A", "Test")
        assert len(chunks) >= 1
        assert all(c["macrodomain"] == "A" for c in chunks)
        assert all(c["document_name"] == "short.md" for c in chunks)
        assert all(c["chunk_id"] for c in chunks)

    def test_process_with_mock_semantic_chunker(self, tmp_path: Path) -> None:
        doc = tmp_path / "semantic.md"
        content = "\n\n".join([f"Paragraph {i} with enough words for semantic chunking." for i in range(10)])
        doc.write_text(content, encoding="utf-8")
        # Mock returns two chunks: one too small, one large enough.
        mock = MockSemanticChunker(
            chunks=[
                "Small beginning. " * 5,
                "Large continuation. " * 60,
            ]
        )
        orchestrator = ChunkingOrchestrator(semantic_chunker=mock)
        chunks = orchestrator.process_document(doc, "B", "Exercise")
        assert len(chunks) >= 1
        assert all(c["macrodomain"] == "B" for c in chunks)
        assert all(c["word_count"] > 0 for c in chunks)
        assert all(c["char_count"] > 0 for c in chunks)

    def test_metadata_enrichment(self, tmp_path: Path) -> None:
        doc = tmp_path / "metadata.md"
        doc.write_text(
            "# Diabetes y ejercicio\n\nLos pacientes con diabetes tipo 2 deben hacer ejercicio aeróbico. "
            "Los ejercicios de fuerza mejoran la sensibilidad a la insulina.\n",
            encoding="utf-8",
        )
        orchestrator = ChunkingOrchestrator()
        chunks = orchestrator.process_document(doc, "C", "Pathologies")
        assert len(chunks) >= 1
        for c in chunks:
            assert c["document_name"] == "metadata.md"
            assert c["macrodomain"] == "C"
            assert c["macrodomain_name"] == "Pathologies"
            assert c["chunk_type"] in ("semantic", "fallback", "structural")
            assert c["chunk_index"] >= 0
            assert c["total_chunks"] >= 1


class MockSemanticChunker:
    """Mock semantic chunker that returns deterministic chunks for tests."""

    def __init__(self, chunks: list[str]) -> None:
        self._chunks = chunks

    def is_available(self) -> bool:
        return True

    def split(self, text: str) -> list[dict]:
        return [
            {
                "content": content,
                "section_path": "",
                "chunk_type": "semantic",
                "chunk_index": i,
            }
            for i, content in enumerate(self._chunks)
        ]

"""Tests for RAGGenerator (mocks OllamaClient)."""

from unittest.mock import AsyncMock

import pytest

from rag.generation.generator import RAGGenerator
from rag.generation.ollama_client import OllamaClient
from rag.generation.prompt_builder import PromptBuilder
from rag.generation.response_parser import ResponseParser


@pytest.fixture()
def mock_ollama() -> OllamaClient:
    client = OllamaClient()
    client.generate = AsyncMock(return_value="Respuesta generada por el modelo.")  # type: ignore
    return client


class TestRAGGenerator:
    @pytest.mark.asyncio
    async def test_generate_returns_structured_result(self, mock_ollama: OllamaClient) -> None:
        gen = RAGGenerator(mock_ollama)
        chunks = [{"content": "info relevante", "metadata": {"document_name": "doc.pdf", "macrodomain": "B"}}]
        result = await gen.generate("¿Qué ejercicios debo hacer?", chunks, agent_name="Exercise Architect")

        assert result["answer"] == "Respuesta generada por el modelo."
        assert result["agent"] == "Exercise Architect"
        assert result["macrodomain"] is None
        assert len(result["sources"]) == 1

    @pytest.mark.asyncio
    async def test_generate_calls_ollama_with_prompt(self, mock_ollama: OllamaClient) -> None:
        gen = RAGGenerator(mock_ollama)
        await gen.generate("test", [], agent_name="Nutri-Buddy")

        mock_ollama.generate.assert_called_once()  # type: ignore
        call_args = mock_ollama.generate.call_args  # type: ignore
        # The prompt passed to Ollama is the full user prompt built by PromptBuilder.
        assert "test" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_generate_with_macrodomain(self, mock_ollama: OllamaClient) -> None:
        gen = RAGGenerator(mock_ollama)
        result = await gen.generate("test", [], macrodomain="E")
        assert result["macrodomain"] == "E"

    @pytest.mark.asyncio
    async def test_generate_empty_context(self, mock_ollama: OllamaClient) -> None:
        gen = RAGGenerator(mock_ollama)
        result = await gen.generate("test", [])
        assert result["answer"] == "Respuesta generada por el modelo."
        assert result["sources"] == []

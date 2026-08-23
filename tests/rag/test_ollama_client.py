"""Tests for OllamaClient."""

import json
from unittest.mock import AsyncMock, patch, MagicMock

import pytest

from rag.generation.ollama_client import OllamaClient


class TestOllamaClientInit:
    def test_default_values(self) -> None:
        client = OllamaClient()
        assert client.base_url == "http://localhost:11434"
        assert client.model == "phi3:mini"
        assert client.timeout == 60.0

    def test_custom_values(self) -> None:
        client = OllamaClient(base_url="http://my-host:11434", model="llama3", timeout=30.0)
        assert client.base_url == "http://my-host:11434"
        assert client.model == "llama3"
        assert client.timeout == 30.0

    def test_strips_trailing_slash(self) -> None:
        client = OllamaClient(base_url="http://localhost:11434/")
        assert client.base_url == "http://localhost:11434"


class TestBuildUrls:
    def test_single_url_when_no_localhost(self) -> None:
        client = OllamaClient(base_url="http://my-server:11434")
        urls = client._build_urls()
        assert urls == ["http://my-server:11434"]

    def test_fallback_for_localhost(self) -> None:
        client = OllamaClient(base_url="http://localhost:11434")
        urls = client._build_urls()
        assert urls == ["http://localhost:11434", "http://127.0.0.1:11434"]


class TestGenerate:
    @pytest.mark.asyncio
    async def test_full_response(self) -> None:
        client = OllamaClient()
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"response": "hola mundo"}
        mock_resp.raise_for_status = MagicMock()

        with patch("rag.generation.ollama_client.httpx.AsyncClient") as MockClient:
            instance = AsyncMock()
            instance.post = AsyncMock(return_value=mock_resp)
            instance.__aenter__ = AsyncMock(return_value=instance)
            instance.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = instance

            result = await client.generate("test prompt")

        assert result == "hola mundo"

    @pytest.mark.asyncio
    async def test_builds_correct_payload(self) -> None:
        client = OllamaClient(model="test-model")
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"response": "ok"}
        mock_resp.raise_for_status = MagicMock()

        with patch("rag.generation.ollama_client.httpx.AsyncClient") as MockClient:
            instance = AsyncMock()
            instance.post = AsyncMock(return_value=mock_resp)
            instance.__aenter__ = AsyncMock(return_value=instance)
            instance.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = instance

            await client.generate("q", system="sys", format_json=True, num_predict=100)

            call_args = instance.post.call_args
            payload = call_args[1]["json"]
            assert payload["model"] == "test-model"
            assert payload["prompt"] == "q"
            assert payload["system"] == "sys"
            assert payload["format"] == "json"
            assert payload["options"]["num_predict"] == 100

    @pytest.mark.asyncio
    async def test_connection_error_raises(self) -> None:
        client = OllamaClient(base_url="http://nonexistent:11434")
        with pytest.raises(ConnectionError, match="Could not connect"):
            await client.generate("test")


class TestHealthCheck:
    @pytest.mark.asyncio
    async def test_returns_true_when_model_found(self) -> None:
        client = OllamaClient(model="phi3:mini")
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"models": [{"name": "phi3:mini"}]}

        with patch("rag.generation.ollama_client.httpx.AsyncClient") as MockClient:
            instance = AsyncMock()
            instance.get = AsyncMock(return_value=mock_resp)
            instance.__aenter__ = AsyncMock(return_value=instance)
            instance.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = instance

            assert await client.health_check() is True

    @pytest.mark.asyncio
    async def test_returns_false_when_model_missing(self) -> None:
        client = OllamaClient(model="phi3:mini")
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"models": [{"name": "llama3"}]}

        with patch("rag.generation.ollama_client.httpx.AsyncClient") as MockClient:
            instance = AsyncMock()
            instance.get = AsyncMock(return_value=mock_resp)
            instance.__aenter__ = AsyncMock(return_value=instance)
            instance.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = instance

            assert await client.health_check() is False

    @pytest.mark.asyncio
    async def test_returns_false_on_connection_error(self) -> None:
        client = OllamaClient(base_url="http://nonexistent:11434")
        assert await client.health_check() is False

"""Tests for ResponseParser."""

import pytest

from rag.generation.response_parser import ResponseParser


class TestParse:
    def test_basic_parse(self) -> None:
        parser = ResponseParser()
        result = parser.parse("Esta es la respuesta.", sources=[], agent="Test")
        assert result["answer"] == "Esta es la respuesta."
        assert result["agent"] == "Test"
        assert result["sources"] == []
        assert result["warnings"] == []

    def test_strips_markdown_fences(self) -> None:
        parser = ResponseParser()
        result = parser.parse("```json\n{'key': 'val'}\n```")
        assert "```" not in result["answer"]
        assert "{'key': 'val'}" in result["answer"]

    def test_extracts_warnings(self) -> None:
        parser = ResponseParser()
        text = "Respuesta normal.\nAdvertencia: No hacer ejercicio con dolor agudo.\nFin."
        result = parser.parse(text)
        assert len(result["warnings"]) == 1
        assert "dolor agudo" in result["warnings"][0]

    def test_extracts_multiple_warnings(self) -> None:
        parser = ResponseParser()
        text = "Advertencia: riesgo de caída.\nPrecaución: consultar médico.\nFin."
        result = parser.parse(text)
        assert len(result["warnings"]) >= 2

    def test_no_warnings_when_absent(self) -> None:
        parser = ResponseParser()
        result = parser.parse("Todo bien, sin problemas.")
        assert result["warnings"] == []


class TestParseJson:
    def test_valid_json(self) -> None:
        parser = ResponseParser()
        result = parser.parse_json('{"key": "value"}')
        assert result == {"key": "value"}

    def test_json_in_code_block(self) -> None:
        parser = ResponseParser()
        result = parser.parse_json('```json\n{"answer": "sí"}\n```')
        assert result == {"answer": "sí"}

    def test_json_array(self) -> None:
        parser = ResponseParser()
        result = parser.parse_json('[{"name": "ej1"}, {"name": "ej2"}]')
        assert len(result) == 2
        assert result[0]["name"] == "ej1"

    def test_invalid_json_returns_none(self) -> None:
        parser = ResponseParser()
        result = parser.parse_json("esto no es json")
        assert result is None

    def test_json_with_surrounding_text(self) -> None:
        parser = ResponseParser()
        result = parser.parse_json('Aquí está el JSON:\n{"a": 1}\nFin.')
        assert result == {"a": 1}

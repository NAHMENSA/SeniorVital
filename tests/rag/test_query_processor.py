"""Tests for QueryProcessor."""

import pytest

from rag.pipeline.query_processor import QueryProcessor


class TestNormalize:
    def test_lowercase_and_strip(self) -> None:
        qp = QueryProcessor()
        result = qp._normalize("  Hola Mundo  ")
        assert result == "hola mundo"

    def test_collapse_whitespace(self) -> None:
        qp = QueryProcessor()
        result = qp._normalize("muchos   espacios   aquí")
        assert result == "muchos espacios aquí"


class TestDetectMacrodomain:
    def test_detects_domain_a(self) -> None:
        qp = QueryProcessor()
        result = qp._detect_macrodomain("tengo sarcopenia y dolor articular")
        assert result == "A"

    def test_detects_domain_b(self) -> None:
        qp = QueryProcessor()
        result = qp._detect_macrodomain("necesito una rutina de ejercicios")
        assert result == "B"

    def test_detects_domain_c(self) -> None:
        qp = QueryProcessor()
        result = qp._detect_macrodomain("adaptar ejercicio al hogar y clima")
        assert result == "C"

    def test_detects_domain_d(self) -> None:
        qp = QueryProcessor()
        result = qp._detect_macrodomain("riesgo de contraindicación con diabetes")
        assert result == "D"

    def test_detects_domain_e(self) -> None:
        qp = QueryProcessor()
        result = qp._detect_macrodomain("dieta y alimentación para diabéticos")
        assert result == "E"

    def test_detects_domain_f(self) -> None:
        qp = QueryProcessor()
        result = qp._detect_macrodomain("ejercicios de memoria y concentración")
        assert result == "F"

    def test_returns_none_when_no_keywords(self) -> None:
        qp = QueryProcessor()
        result = qp._detect_macrodomain("hola qué tal")
        assert result is None


class TestProcess:
    def test_explicit_agent(self) -> None:
        qp = QueryProcessor()
        result = qp.process("test", agent_name="Nutri-Buddy")
        assert result["detected_agent"] == "Nutri-Buddy"
        assert result["detected_macrodomain"] == "E"
        assert result["filters"]["macrodomain"] == "E"

    def test_explicit_macrodomain(self) -> None:
        qp = QueryProcessor()
        result = qp.process("test", macrodomain="B")
        assert result["detected_macrodomain"] == "B"
        assert result["detected_agent"] == "Exercise Architect"

    def test_auto_detect(self) -> None:
        qp = QueryProcessor()
        result = qp.process("¿Qué ejercicios de fuerza son seguros?")
        assert result["detected_macrodomain"] == "B"
        assert result["detected_agent"] == "Exercise Architect"

    def test_normalized_query_in_result(self) -> None:
        qp = QueryProcessor()
        result = qp.process("  MUCHOS Espacios  ")
        assert result["normalized_query"] == "muchos espacios"

    def test_filters_include_macrodomain(self) -> None:
        qp = QueryProcessor()
        result = qp.process("dieta para diabeticos")
        assert "macrodomain" in result["filters"]

    def test_both_agent_and_macrodomain_explicit(self) -> None:
        qp = QueryProcessor()
        result = qp.process("test", agent_name="Nutri-Buddy", macrodomain="E")
        assert result["detected_agent"] == "Nutri-Buddy"
        assert result["detected_macrodomain"] == "E"

    def test_no_detection_when_no_match(self) -> None:
        qp = QueryProcessor()
        result = qp.process("hola qué tal")
        assert result["detected_macrodomain"] is None
        assert result["detected_agent"] is None
        assert result["filters"] == {}

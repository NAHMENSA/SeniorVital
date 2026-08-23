"""Tests for PromptBuilder."""

import pytest

from rag.generation.prompt_builder import (
    AGENT_SYSTEM_PROMPTS,
    MACRODOMAIN_TO_AGENT,
    PromptBuilder,
)


class TestPromptBuilderSystemPrompt:
    def test_by_agent_name(self) -> None:
        builder = PromptBuilder()
        prompt = builder.get_system_prompt(agent_name="Nutri-Buddy")
        assert "Nutri-Buddy" in prompt
        assert "nutrición" in prompt.lower()

    def test_by_macrodomain(self) -> None:
        builder = PromptBuilder()
        prompt = builder.get_system_prompt(macrodomain="F")
        assert "Mind & Soul" in prompt

    def test_default_when_no_match(self) -> None:
        builder = PromptBuilder()
        prompt = builder.get_system_prompt(agent_name="Nonexistent")
        assert "SeniorVital" in prompt

    def test_agent_takes_priority_over_macrodomain(self) -> None:
        builder = PromptBuilder()
        prompt = builder.get_system_prompt(agent_name="Nutri-Buddy", macrodomain="A")
        assert "Nutri-Buddy" in prompt

    def test_all_agents_have_prompts(self) -> None:
        expected_agents = ["Physio-Evaluator", "Exercise Architect", "Context-Adaptor",
                           "Safety Guardian", "Nutri-Buddy", "Mind & Soul"]
        for agent in expected_agents:
            assert agent in AGENT_SYSTEM_PROMPTS

    def test_all_macrodomains_mapped(self) -> None:
        assert len(MACRODOMAIN_TO_AGENT) == 6
        for letter in "ABCDEF":
            assert letter in MACRODOMAIN_TO_AGENT


class TestPromptBuilderBuild:
    def test_build_returns_tuple(self) -> None:
        builder = PromptBuilder()
        system, user = builder.build("test query", [])
        assert isinstance(system, str)
        assert isinstance(user, str)

    def test_context_chunks_appears_in_user_prompt(self) -> None:
        builder = PromptBuilder()
        chunks = [
            {"content": "Ejercicio aeróbico recomendado", "metadata": {"document_name": "guia.pdf", "macrodomain": "B"}},
            {"content": "Dieta para diabeticos", "metadata": {"document_name": "nutricion.md", "macrodomain": "E"}},
        ]
        _, user = builder.build("¿Qué ejercicios debo hacer?", chunks)
        assert "Ejercicio aeróbico recomendado" in user
        assert "Dieta para diabeticos" in user
        assert "guia.pdf" in user

    def test_empty_chunks_message(self) -> None:
        builder = PromptBuilder()
        _, user = builder.build("test", [])
        assert "No se encontró información" in user

    def test_query_appears_in_user_prompt(self) -> None:
        builder = PromptBuilder()
        _, user = builder.build("¿Cuáles son los ejercicios seguros?", [])
        assert "¿Cuáles son los ejercicios seguros?" in user

    def test_system_prompt_includes_role(self) -> None:
        builder = PromptBuilder()
        system, _ = builder.build("test", [], agent_name="Exercise Architect")
        assert "Exercise Architect" in system
        assert "ejercicio" in system.lower()

    def test_chunk_metadata_includes_source(self) -> None:
        builder = PromptBuilder()
        chunks = [
            {"content": "text", "metadata": {"document_name": "doc.pdf", "macrodomain": "A", "chunk_type": "semantic"}},
        ]
        _, user = builder.build("q", chunks)
        assert "doc.pdf" in user
        assert "semantic" in user

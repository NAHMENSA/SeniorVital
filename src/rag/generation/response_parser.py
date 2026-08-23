"""Response parser for SeniorVital RAG generation."""

import json
import re
from typing import Any


class ResponseParser:
    """Parse and structure LLM responses from SeniorVital RAG pipeline."""

    def parse(
        self,
        raw_response: str,
        *,
        sources: list[dict[str, Any]] | None = None,
        agent: str | None = None,
        macrodomain: str | None = None,
    ) -> dict[str, Any]:
        """Parse raw LLM output into a structured response.

        Args:
            raw_response: The text returned by the LLM.
            sources: The chunks used as context.
            agent: The agent that generated the response.
            macrodomain: The macrodomain consulted.

        Returns:
            Structured dict with 'answer', 'sources', 'agent', 'macrodomain', 'warnings'.
        """
        cleaned = self._clean_response(raw_response)
        warnings = self._extract_warnings(cleaned)

        return {
            "answer": cleaned,
            "sources": sources or [],
            "agent": agent,
            "macrodomain": macrodomain,
            "warnings": warnings,
        }

    def parse_json(self, raw_response: str) -> dict[str, Any] | None:
        """Try to extract a JSON object from the LLM response.

        Returns None if no valid JSON is found.
        """
        cleaned = self._clean_response(raw_response)

        # Try direct parse.
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # Try extracting from markdown code blocks.
        match = re.search(r"```(?:json)?\s*(.+?)\s*```", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        # Try finding first { ... } or [ ... ] block.
        for opener, closer in [("{", "}"), ("[", "]")]:
            start = cleaned.find(opener)
            end = cleaned.rfind(closer)
            if start != -1 and end > start:
                try:
                    return json.loads(cleaned[start : end + 1])
                except json.JSONDecodeError:
                    continue

        return None

    def _clean_response(self, text: str) -> str:
        """Remove markdown fences and leading/trailing whitespace."""
        text = text.strip()
        match = re.search(r"```(?:json)?\s*(.+?)\s*```", text, re.DOTALL)
        if match:
            text = match.group(1).strip()
        return text

    def _extract_warnings(self, text: str) -> list[str]:
        """Extract safety warnings from the response text."""
        warnings: list[str] = []
        warning_patterns = [
            r"(?i)advertencia[s]?:\s*(.+?)(?:\n|$)",
            r"(?i)precaución:\s*(.+?)(?:\n|$)",
            r"(?i)riesgo[s]?:\s*(.+?)(?:\n|$)",
            r"(?i)contraindicación(?:es)?:\s*(.+?)(?:\n|$)",
            r"(?i)peligro:\s*(.+?)(?:\n|$)",
        ]
        for pattern in warning_patterns:
            for match in re.finditer(pattern, text):
                warning = match.group(1).strip()
                if warning and warning not in warnings:
                    warnings.append(warning)
        return warnings

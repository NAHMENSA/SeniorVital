"""Context assembly for SeniorVital RAG — formats chunks for the LLM context window."""

from typing import Any


# Approximate chars-per-token ratio for Spanish text (conservative).
CHARS_PER_TOKEN = 4

# Overhead budget for system prompt + instructions (in tokens).
PROMPT_OVERHEAD_TOKENS = 300


class ContextAssembler:
    """Assemble retrieved chunks into a context string that fits the LLM window.

    Handles deduplication, truncation by token budget, and formatting.
    """

    def __init__(self, max_context_tokens: int = 4096) -> None:
        self.max_context_tokens = max_context_tokens
        self.available_tokens = max_context_tokens - PROMPT_OVERHEAD_TOKENS

    def assemble(self, chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Deduplicate, rank, and truncate chunks to fit the context window.

        Args:
            chunks: Retrieved chunks sorted by relevance (highest first).

        Returns:
            Filtered and truncated list of chunks that fit within the token budget.
        """
        if not chunks:
            return []

        deduplicated = self._deduplicate(chunks)
        return self._truncate_to_budget(deduplicated)

    def _deduplicate(self, chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Remove near-duplicate chunks based on content similarity."""
        seen_contents: set[str] = set()
        unique: list[dict[str, Any]] = []

        for chunk in chunks:
            content = chunk.get("content", "").strip()
            # Use first 200 chars as dedup key (enough to detect near-duplicates).
            key = content[:200].lower()
            if key not in seen_contents:
                seen_contents.add(key)
                unique.append(chunk)

        return unique

    def _truncate_to_budget(self, chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Keep chunks that fit within the available token budget."""
        result: list[dict[str, Any]] = []
        tokens_used = 0

        for i, chunk in enumerate(chunks):
            content = chunk.get("content", "")
            chunk_tokens = len(content) // CHARS_PER_TOKEN

            if tokens_used + chunk_tokens <= self.available_tokens:
                result.append(chunk)
                tokens_used += chunk_tokens
            else:
                remaining_tokens = self.available_tokens - tokens_used
                if remaining_tokens > 50:
                    truncated = content[: remaining_tokens * CHARS_PER_TOKEN]
                    truncated_chunk = dict(chunk)
                    truncated_chunk["content"] = truncated + "..."
                    result.append(truncated_chunk)
                elif not result:
                    # Always include at least part of the first chunk.
                    min_budget = max(remaining_tokens, 50)
                    truncated_chunk = dict(chunk)
                    truncated_chunk["content"] = content[: min_budget * CHARS_PER_TOKEN] + "..."
                    result.append(truncated_chunk)
                break

        return result

    def format_context(self, chunks: list[dict[str, Any]]) -> str:
        """Format chunks into a context string for embedding in the prompt."""
        if not chunks:
            return "No se encontró información relevante en la base de conocimiento."

        parts: list[str] = []
        for i, chunk in enumerate(chunks, 1):
            meta = chunk.get("metadata", {})
            source = meta.get("document_name", meta.get("source_path", "desconocido"))
            content = chunk.get("content", "").strip()
            parts.append(f"[{i}] Fuente: {source}\n{content}")

        return "\n\n".join(parts)

"""RAG generator — orchestrates prompt construction, LLM call, and response parsing."""

from typing import Any

from .ollama_client import OllamaClient
from .prompt_builder import PromptBuilder
from .response_parser import ResponseParser


class RAGGenerator:
    """Generate answers from retrieved context using an Ollama LLM.

    Ties together PromptBuilder, OllamaClient, and ResponseParser into a
    single generate() call.
    """

    def __init__(
        self,
        ollama_client: OllamaClient,
        prompt_builder: PromptBuilder | None = None,
        response_parser: ResponseParser | None = None,
    ) -> None:
        self.ollama = ollama_client
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.response_parser = response_parser or ResponseParser()

    async def generate(
        self,
        query: str,
        context_chunks: list[dict[str, Any]],
        *,
        agent_name: str | None = None,
        macrodomain: str | None = None,
        stream: bool = False,
    ) -> dict[str, Any]:
        """Generate a RAG response.

        Args:
            query: The user's question.
            context_chunks: Retrieved chunks from the vector store.
            agent_name: Optional agent name for prompt selection.
            macrodomain: Optional macrodomain letter.
            stream: Whether to stream the LLM response.

        Returns:
            Structured dict with answer, sources, agent, macrodomain, warnings.
        """
        system_prompt, user_prompt = self.prompt_builder.build(
            query, context_chunks, agent_name=agent_name, macrodomain=macrodomain
        )

        raw_response = await self.ollama.generate(
            user_prompt,
            system=system_prompt,
            stream=stream,
            format_json=False,
        )

        return self.response_parser.parse(
            raw_response,
            sources=context_chunks,
            agent=agent_name,
            macrodomain=macrodomain,
        )

"""SeniorVital RAG pipeline — end-to-end query → retrieve → generate."""

from pathlib import Path
from typing import Any

from rag.generation import RAGGenerator, OllamaClient, PromptBuilder, ResponseParser
from rag.retriever import SeniorVitalRetriever
from rag.vector_store import SeniorVitalVectorStore

from .context_assembler import ContextAssembler
from .query_processor import QueryProcessor


class SeniorVitalRAGPipeline:
    """End-to-end RAG pipeline for SeniorVital.

    Wires together: query processing → retrieval → context assembly → LLM generation.
    """

    def __init__(
        self,
        *,
        vector_store: SeniorVitalVectorStore | None = None,
        retriever: SeniorVitalRetriever | None = None,
        ollama_client: OllamaClient | None = None,
        prompt_builder: PromptBuilder | None = None,
        response_parser: ResponseParser | None = None,
        context_assembler: ContextAssembler | None = None,
        query_processor: QueryProcessor | None = None,
        persist_directory: str | Path = "data/vector_store",
        default_k: int = 5,
    ) -> None:
        self.default_k = default_k

        # Allow injecting pre-built components or create defaults.
        if vector_store is not None:
            self.vector_store = vector_store
        else:
            self.vector_store = SeniorVitalVectorStore(
                persist_directory=Path(persist_directory)
            )

        self.retriever = retriever or SeniorVitalRetriever(self.vector_store)
        self.ollama = ollama_client or OllamaClient()
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.response_parser = response_parser or ResponseParser()
        self.context_assembler = context_assembler or ContextAssembler()
        self.query_processor = query_processor or QueryProcessor()
        self.generator = RAGGenerator(
            self.ollama, self.prompt_builder, self.response_parser
        )

    async def process_query(
        self,
        query: str,
        *,
        agent_name: str | None = None,
        macrodomain: str | None = None,
        filters: dict[str, Any] | None = None,
        k: int | None = None,
        stream: bool = False,
    ) -> dict[str, Any]:
        """Process a user query through the full RAG pipeline.

        Args:
            query: The user's natural-language question.
            agent_name: Optional agent name to scope retrieval and generation.
            macrodomain: Optional macrodomain letter (A-F).
            filters: Optional metadata filters for retrieval.
            k: Number of chunks to retrieve (default: self.default_k).
            stream: Whether to stream the LLM response.

        Returns:
            {
                "answer": str,
                "sources": list[dict],
                "agent": str | None,
                "macrodomain": str | None,
                "warnings": list[str],
                "query_info": dict,  # preprocessing metadata
            }
        """
        k = k or self.default_k

        # Step 1: Process the query (normalize, detect intent).
        query_info = self.query_processor.process(
            query, agent_name=agent_name, macrodomain=macrodomain
        )

        # Merge explicit filters with detected filters.
        effective_filters = dict(query_info.get("filters", {}))
        if filters:
            effective_filters.update(filters)
        if macrodomain:
            effective_filters["macrodomain"] = macrodomain

        effective_agent = agent_name or query_info.get("detected_agent")
        effective_macrodomain = macrodomain or query_info.get("detected_macrodomain")

        # Step 2: Retrieve relevant chunks.
        if effective_agent:
            chunks = self.retriever.retrieve_for_agent(
                query, agent_name=effective_agent, k=k
            )
        elif effective_filters:
            chunks = self.retriever.retrieve_with_filters(
                query, filters=effective_filters, k=k
            )
        else:
            chunks = self.retriever.retrieve(query, k=k)

        # Step 3: Assemble context (deduplicate, truncate to fit window).
        assembled_chunks = self.context_assembler.assemble(chunks)

        # Step 4: Generate answer via LLM.
        result = await self.generator.generate(
            query,
            assembled_chunks,
            agent_name=effective_agent,
            macrodomain=effective_macrodomain,
            stream=stream,
        )

        result["query_info"] = query_info
        return result

    async def health_check(self) -> dict[str, Any]:
        """Check that the pipeline components are operational.

        Returns:
            Dict with 'ollama_available', 'vector_store_count', 'pipeline_ready'.
        """
        ollama_ok = await self.ollama.health_check()
        vs_count = self.vector_store.count()
        return {
            "ollama_available": ollama_ok,
            "vector_store_count": vs_count,
            "pipeline_ready": ollama_ok and vs_count > 0,
        }

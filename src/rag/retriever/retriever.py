"""Retriever for SeniorVital RAG."""

from typing import Any

from rag.vector_store import AGENT_TO_MACRODOMAIN, SeniorVitalVectorStore


class SeniorVitalRetriever:
    """Retrieve relevant knowledge chunks for SeniorVital agents.

    Thin wrapper around a vector store. The store can be swapped (e.g. for a
    pgvector implementation) without changing the retriever interface.
    """

    def __init__(self, vector_store: SeniorVitalVectorStore) -> None:
        self.vector_store = vector_store

    def retrieve(
        self,
        query: str,
        k: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Retrieve the k most relevant chunks for a query."""
        return self.vector_store.search(query, k=k, filters=filters)

    def retrieve_for_agent(
        self,
        query: str,
        agent_name: str,
        k: int = 5,
    ) -> list[dict[str, Any]]:
        """Retrieve chunks scoped to the macrodomain of a given agent."""
        return self.vector_store.search_by_agent(query, agent_name=agent_name, k=k)

    def retrieve_by_macrodomain(
        self,
        query: str,
        macrodomain: str,
        k: int = 5,
    ) -> list[dict[str, Any]]:
        """Retrieve chunks scoped to a single macrodomain."""
        return self.vector_store.search_by_macrodomain(query, macrodomain=macrodomain, k=k)

    def retrieve_with_filters(
        self,
        query: str,
        filters: dict[str, Any],
        k: int = 5,
    ) -> list[dict[str, Any]]:
        """Retrieve chunks using arbitrary metadata filters."""
        return self.vector_store.search_by_filters(query, filters=filters, k=k)

    def list_agents(self) -> list[str]:
        """Return the names of supported agents."""
        return list(AGENT_TO_MACRODOMAIN.keys())

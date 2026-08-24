"""RAG Search Tool — consulta la base de conocimiento RAG."""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from src.tools import ToolResult


class RAGSearchTool:
    """Consulta la base de conocimiento de bienestar para adultos mayores.

    Precondiciones: RAG pipeline inicializado (ChromaDB + embeddings).
    Postcondiciones: Retorna respuesta basada en conocimiento recuperado.
    Efectos secundarios: None (solo lectura del vector store).
    """

    name = "rag_search"
    description = "Consulta la base de conocimiento de bienestar para adultos mayores"

    def __init__(self, rag_pipeline=None) -> None:
        self._pipeline = rag_pipeline

    def validate_args(self, **kwargs) -> bool:
        return "query" in kwargs and isinstance(kwargs["query"], str) and len(kwargs["query"].strip()) > 0

    async def execute(self, **kwargs) -> ToolResult:
        """Consulta el pipeline RAG.

        Args:
            query: Pregunta del usuario.
            macrodomain: Dominio opcional (A-F) para filtrar.
            k: Número de chunks a recuperar (default: 5).

        Returns:
            ToolResult con data={"answer": "...", "sources": [...], "agent": "..."}.
        """
        if not self.validate_args(**kwargs):
            return ToolResult(success=False, error="query required", tool_name=self.name)

        if self._pipeline is None:
            return ToolResult(
                success=False,
                error="RAG pipeline not available",
                tool_name=self.name,
            )

        try:
            query = kwargs["query"]
            macrodomain = kwargs.get("macrodomain")
            k = kwargs.get("k", 5)

            result = await self._pipeline.process_query(
                query, macrodomain=macrodomain
            )

            return ToolResult(
                success=True,
                data={
                    "answer": result.get("answer", ""),
                    "sources": result.get("sources", []),
                    "agent": result.get("agent", ""),
                    "macrodomain": result.get("macrodomain", ""),
                    "warnings": result.get("warnings", []),
                },
                tool_name=self.name,
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e), tool_name=self.name)

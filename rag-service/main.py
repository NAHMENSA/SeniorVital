"""SeniorVital RAG microservice.

Provides a REST API for the RAG pipeline: query → retrieve → generate.
Port 8007 (next available after notification-service on 8006).
"""

import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Add src/ to path for rag imports
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT_DIR, "src"))

from rag.pipeline import SeniorVitalRAGPipeline

VECTOR_STORE_DIR = os.getenv(
    "VECTOR_STORE_DIR",
    os.path.join(ROOT_DIR, "data", "vector_store"),
)
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "phi3:mini")

pipeline: SeniorVitalRAGPipeline | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global pipeline
    pipeline = SeniorVitalRAGPipeline(
        persist_directory=VECTOR_STORE_DIR,
    )
    yield
    pipeline = None


app = FastAPI(
    title="SeniorVital RAG Service",
    version="1.0.0",
    description="RAG pipeline: query → retrieve → generate for elderly wellness knowledge.",
    lifespan=lifespan,
)


# ── Request / Response schemas ──

class RAGQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000, description="Natural-language question.")
    agent_name: str | None = Field(None, description="Agent name to scope retrieval (e.g. 'Nutri-Buddy').")
    macrodomain: str | None = Field(None, description="Macrodomain letter (A-F).")
    filters: dict[str, Any] | None = Field(None, description="Additional metadata filters.")
    k: int = Field(5, ge=1, le=20, description="Number of chunks to retrieve.")


class RAGSource(BaseModel):
    chunk_id: str
    content: str
    metadata: dict[str, Any]
    distance: float | None = None


class RAGQueryResponse(BaseModel):
    answer: str
    sources: list[RAGSource]
    agent: str | None = None
    macrodomain: str | None = None
    warnings: list[str]
    query_info: dict[str, Any]


class HealthResponse(BaseModel):
    ollama_available: bool
    vector_store_count: int
    pipeline_ready: bool


# ── Endpoints ──

@app.post("/rag/query", response_model=RAGQueryResponse, tags=["RAG"])
async def rag_query(req: RAGQueryRequest) -> RAGQueryResponse:
    """Query the RAG pipeline with a natural-language question.

    The pipeline automatically detects the relevant macrodomain/agent
    from the query text, retrieves matching knowledge chunks, and
    generates an answer via the local LLM.
    """
    if pipeline is None:
        raise HTTPException(status_code=503, detail="RAG pipeline not initialized")

    try:
        result = await pipeline.process_query(
            query=req.query,
            agent_name=req.agent_name,
            macrodomain=req.macrodomain,
            filters=req.filters,
            k=req.k,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG pipeline error: {e}")

    return RAGQueryResponse(
        answer=result["answer"],
        sources=[
            RAGSource(
                chunk_id=s["chunk_id"],
                content=s["content"],
                metadata=s.get("metadata", {}),
                distance=s.get("distance"),
            )
            for s in result.get("sources", [])
        ],
        agent=result.get("agent"),
        macrodomain=result.get("macrodomain"),
        warnings=result.get("warnings", []),
        query_info=result.get("query_info", {}),
    )


@app.get("/rag/health", response_model=HealthResponse, tags=["RAG"])
async def rag_health() -> HealthResponse:
    """Health check for the RAG pipeline."""
    if pipeline is None:
        return HealthResponse(
            ollama_available=False,
            vector_store_count=0,
            pipeline_ready=False,
        )

    health = await pipeline.health_check()
    return HealthResponse(**health)


@app.get("/rag/stats", tags=["RAG"])
async def rag_stats() -> dict[str, Any]:
    """Return basic stats about the RAG vector store."""
    if pipeline is None:
        raise HTTPException(status_code=503, detail="RAG pipeline not initialized")

    return {
        "vector_store_count": pipeline.vector_store.count(),
        "persist_directory": str(VECTOR_STORE_DIR),
    }

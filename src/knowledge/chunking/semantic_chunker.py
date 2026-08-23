"""Semantic chunker using LangChain SemanticChunker with local embeddings."""

import os
from pathlib import Path
from typing import Any

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_experimental.text_splitter import SemanticChunker

from .fallback_chunker import FallbackChunker
from .preprocessor import preprocess_file


DEFAULT_EMBEDDING_MODEL = "intfloat/multilingual-e5-small"


class SemanticChunkerWrapper:
    """Chunk documents by semantic similarity using local HuggingFace embeddings."""

    def __init__(
        self,
        model_name: str | None = None,
        breakpoint_threshold_type: str = "percentile",
        breakpoint_threshold_amount: int = 85,
    ) -> None:
        self.model_name = model_name or os.getenv(
            "EMBEDDING_MODEL_NAME", DEFAULT_EMBEDDING_MODEL
        )
        self.breakpoint_threshold_type = breakpoint_threshold_type
        self.breakpoint_threshold_amount = breakpoint_threshold_amount
        self._embeddings = None

    @property
    def embeddings(self) -> HuggingFaceEmbeddings:
        """Lazy-load local HuggingFace embeddings."""
        if self._embeddings is None:
            self._embeddings = HuggingFaceEmbeddings(
                model_name=self.model_name,
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True},
            )
        return self._embeddings

    def split(self, text: str) -> list[dict[str, Any]]:
        """Split text into semantically coherent chunks."""
        splitter = SemanticChunker(
            embeddings=self.embeddings,
            breakpoint_threshold_type=self.breakpoint_threshold_type,
            breakpoint_threshold_amount=self.breakpoint_threshold_amount,
        )
        docs = splitter.create_documents([text])

        chunks = []
        for idx, doc in enumerate(docs):
            chunks.append(
                {
                    "content": doc.page_content,
                    "section_path": "",
                    "chunk_type": "semantic",
                    "chunk_index": idx,
                }
            )
        return chunks

    def split_file(self, filepath: Path) -> list[dict[str, Any]]:
        """Read a file, preprocess it, and split semantically."""
        text, _ = preprocess_file(filepath)
        return self.split(text)

    def is_available(self) -> bool:
        """Return True: local embeddings do not require an external API key."""
        return True

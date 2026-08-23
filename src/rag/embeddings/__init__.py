"""Embeddings package for SeniorVital RAG."""

from .cache import EmbeddingCache
from .embedding_generator import DEFAULT_EMBEDDING_MODEL, EmbeddingGenerator
from .persistence import (
    get_embeddings_output_dir,
    load_embeddings,
    save_embeddings,
)

__all__ = [
    "DEFAULT_EMBEDDING_MODEL",
    "EmbeddingCache",
    "EmbeddingGenerator",
    "get_embeddings_output_dir",
    "load_embeddings",
    "save_embeddings",
]

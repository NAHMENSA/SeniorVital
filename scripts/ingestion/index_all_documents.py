#!/usr/bin/env python3
"""Index SeniorVital knowledge chunks into the vector store.

Usage:
    python scripts/ingestion/index_all_documents.py [--no-clear]

Modes:
    - With pre-computed embeddings (default):
        Expects data/processed/chunks/all_chunks.json
        and data/processed/embeddings/<model>/ to exist.

    - Without pre-computed embeddings (pass --generate):
        Generates embeddings on-the-fly from chunk content.
        Requires the embedding model to be installed locally.
"""

import sys
from pathlib import Path

# Add src/ to path for rag imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from rag.embeddings import DEFAULT_EMBEDDING_MODEL
from rag.indexing import IndexingPipeline
from rag.vector_store import SeniorVitalVectorStore


CHUNKS_PATH = PROJECT_ROOT / "data" / "processed" / "chunks" / "all_chunks.json"
EMBEDDINGS_BASE_DIR = PROJECT_ROOT / "data" / "processed" / "embeddings"
VECTOR_STORE_DIR = PROJECT_ROOT / "data" / "vector_store"


def main() -> int:
    clear = "--no-clear" not in sys.argv

    print(f"Chunks file:    {CHUNKS_PATH}")
    print(f"Embeddings dir: {EMBEDDINGS_BASE_DIR}")
    print(f"Vector store:   {VECTOR_STORE_DIR}")
    print(f"Clear before:   {clear}")
    print()

    vector_store = SeniorVitalVectorStore(persist_directory=VECTOR_STORE_DIR)
    pipeline = IndexingPipeline(vector_store=vector_store)

    # Try pre-computed embeddings first
    embeddings_dir = EMBEDDINGS_BASE_DIR / DEFAULT_EMBEDDING_MODEL.replace("/", "_")
    if embeddings_dir.exists():
        print(f"Using pre-computed embeddings from {embeddings_dir}")
        stats = pipeline.index_from_files(
            chunks_path=CHUNKS_PATH,
            embeddings_dir=embeddings_dir,
            clear=clear,
        )
    else:
        print("No pre-computed embeddings found. Generate with:")
        print("  python scripts/ingestion/generate_embeddings.py")
        stats = pipeline.index_from_files(
            chunks_path=CHUNKS_PATH,
            embeddings_dir=None,
            clear=clear,
        )

    print(f"\nChunks loaded:     {stats.chunks_loaded}")
    print(f"Embeddings loaded: {stats.embeddings_loaded}")
    print(f"Chunks indexed:    {stats.chunks_indexed}")
    if stats.errors:
        print(f"\nErrors ({len(stats.errors)}):")
        for err in stats.errors:
            print(f"  - {err}")
        return 1

    print("\nIndexing complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())

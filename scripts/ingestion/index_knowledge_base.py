"""Index SeniorVital knowledge chunks into the vector store."""

import json
import sys
from pathlib import Path

import numpy as np

from rag.embeddings import get_embeddings_output_dir, load_embeddings
from rag.vector_store import SeniorVitalVectorStore


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CHUNKS_PATH = PROJECT_ROOT / "data" / "processed" / "chunks" / "all_chunks.json"
EMBEDDINGS_BASE_DIR = PROJECT_ROOT / "data" / "processed" / "embeddings"
VECTOR_STORE_DIR = PROJECT_ROOT / "data" / "vector_store"
DEFAULT_MODEL = "intfloat/multilingual-e5-small"


def load_chunks(path: Path) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    if not CHUNKS_PATH.exists():
        print(f"Chunks file not found: {CHUNKS_PATH}", file=sys.stderr)
        print("Run scripts/indexing/run_chunking.py first.", file=sys.stderr)
        return 1

    chunks = load_chunks(CHUNKS_PATH)
    print(f"Loaded {len(chunks)} chunks")

    embeddings_dir = get_embeddings_output_dir(EMBEDDINGS_BASE_DIR, DEFAULT_MODEL)
    if not embeddings_dir.exists():
        print(f"Embeddings directory not found: {embeddings_dir}", file=sys.stderr)
        print("Run scripts/ingestion/generate_embeddings.py first.", file=sys.stderr)
        return 1

    metadata, embeddings = load_embeddings(embeddings_dir)
    print(f"Loaded embeddings: {embeddings.shape}")

    if len(metadata) != len(chunks):
        print(
            f"Mismatch: {len(chunks)} chunks vs {len(metadata)} embeddings",
            file=sys.stderr,
        )
        return 1

    vector_store = SeniorVitalVectorStore(persist_directory=VECTOR_STORE_DIR)
    vector_store.create_or_load(chunks=chunks, embeddings=embeddings.tolist(), clear=True)

    count = vector_store.count()
    print(f"Indexed {count} chunks into {VECTOR_STORE_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Generate embeddings for all chunked knowledge-base documents."""

import json
import sys
from pathlib import Path

from rag.embeddings import (
    DEFAULT_EMBEDDING_MODEL,
    EmbeddingGenerator,
    get_embeddings_output_dir,
    save_embeddings,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CHUNKS_PATH = PROJECT_ROOT / "data" / "processed" / "chunks" / "all_chunks.json"
BASE_OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "embeddings"


def load_chunks(path: Path) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    if not CHUNKS_PATH.exists():
        print(f"Chunks file not found: {CHUNKS_PATH}", file=sys.stderr)
        print("Run scripts/indexing/run_chunking.py first.", file=sys.stderr)
        return 1

    chunks = load_chunks(CHUNKS_PATH)
    print(f"Loaded {len(chunks)} chunks from {CHUNKS_PATH}")

    generator = EmbeddingGenerator()
    print(f"Using embedding model: {generator.model_name}")

    print("Generating embeddings...")
    enriched = generator.generate_for_chunks(chunks)

    dimension = len(enriched[0]["embedding"])
    print(f"Embedding dimension: {dimension}")

    output_dir = get_embeddings_output_dir(BASE_OUTPUT_DIR, generator.model_name)
    save_embeddings(
        enriched,
        output_dir,
        model_name=generator.model_name,
        chunk_source=str(CHUNKS_PATH.relative_to(PROJECT_ROOT)),
    )

    print(f"Saved embeddings to {output_dir}")
    print(f"  - metadata: {output_dir / 'embeddings_metadata.json'}")
    print(f"  - vectors:  {output_dir / 'embeddings.npy'}")
    print(f"  - manifest: {output_dir / 'manifest.json'}")
    print(f"Chunks processed: {len(enriched)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

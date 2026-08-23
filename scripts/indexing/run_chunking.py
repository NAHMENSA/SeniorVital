"""Script to run the chunking pipeline over the SeniorVital knowledge base."""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

from dotenv import load_dotenv

from knowledge.chunking import ChunkingOrchestrator


def main() -> None:
    load_dotenv()

    root_dir = Path(__file__).resolve().parent.parent.parent
    kb_dir = root_dir / "data" / "knowledge_base"
    processed_dir = root_dir / "data" / "processed"
    chunks_dir = processed_dir / "chunks"
    inventory_path = processed_dir / "document_inventory.json"
    stats_path = processed_dir / "chunking_stats.json"

    if not inventory_path.exists():
        print(f"Inventory not found at {inventory_path}. Run scripts/indexing/inventory_documents.py first.")
        sys.exit(1)

    with open(inventory_path, "r", encoding="utf-8") as f:
        inventory = json.load(f)

    orchestrator = ChunkingOrchestrator()
    all_chunks = orchestrator.process_all_documents(kb_dir, inventory)
    orchestrator.save_chunks(all_chunks, chunks_dir, per_document=True)

    stats = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_documents": inventory["total_documents"],
        "total_chunks": len(all_chunks),
        "chunks_by_macrodomain": {},
        "chunks_by_type": {},
        "avg_chunk_chars": sum(len(c["content"]) for c in all_chunks) / max(len(all_chunks), 1),
        "avg_chunk_words": sum(c["word_count"] for c in all_chunks) / max(len(all_chunks), 1),
    }

    for chunk in all_chunks:
        stats["chunks_by_macrodomain"][chunk["macrodomain"]] = (
            stats["chunks_by_macrodomain"].get(chunk["macrodomain"], 0) + 1
        )
        stats["chunks_by_type"][chunk["chunk_type"]] = (
            stats["chunks_by_type"].get(chunk["chunk_type"], 0) + 1
        )

    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    print(f"Chunking complete.")
    print(f"Total chunks: {stats['total_chunks']}")
    print(f"Chunks by type: {stats['chunks_by_type']}")
    print(f"Chunks by macrodomain: {stats['chunks_by_macrodomain']}")
    print(f"Output directory: {chunks_dir}")
    print(f"Stats file: {stats_path}")


if __name__ == "__main__":
    main()

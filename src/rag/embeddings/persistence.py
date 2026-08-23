"""Flat persistence for embeddings: JSON metadata + NumPy vectors."""

import json
from pathlib import Path
from typing import Any

import numpy as np


METADATA_FILE = "embeddings_metadata.json"
VECTORS_FILE = "embeddings.npy"
MANIFEST_FILE = "manifest.json"


def _sanitize_model_name(model_name: str) -> str:
    """Convert a HuggingFace model name into a filesystem-safe directory name."""
    return model_name.replace("/", "_").replace("\\", "_")


def _get_embedding_dir(base_dir: Path, model_name: str) -> Path:
    """Return the output directory for a given model."""
    return base_dir / _sanitize_model_name(model_name)


def _validate_vectors(metadata: list[dict[str, Any]], vectors: np.ndarray) -> None:
    """Ensure metadata length and vector dimensions are consistent."""
    if len(metadata) != vectors.shape[0]:
        raise ValueError(
            f"Metadata length ({len(metadata)}) does not match vectors count ({vectors.shape[0]})."
        )
    if vectors.ndim != 2:
        raise ValueError(f"Expected 2D embeddings array, got {vectors.ndim}D.")


def save_embeddings(
    embeddings_data: list[dict[str, Any]],
    output_dir: Path,
    model_name: str,
    chunk_source: str | None = None,
) -> None:
    """Persist embeddings as JSON metadata plus a NumPy matrix.

    Args:
        embeddings_data: List of chunk dicts including an "embedding" key.
        output_dir: Directory where files will be written.
        model_name: Name of the embedding model used.
        chunk_source: Optional path to the source chunks file.
    """
    if not embeddings_data:
        raise ValueError("Cannot save empty embeddings data.")

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    vectors = np.array([item["embedding"] for item in embeddings_data], dtype=np.float32)
    metadata = []
    for item in embeddings_data:
        chunk_meta = {k: v for k, v in item.items() if k != "embedding"}
        metadata.append(chunk_meta)

    _validate_vectors(metadata, vectors)

    metadata_path = output_dir / METADATA_FILE
    vectors_path = output_dir / VECTORS_FILE
    manifest_path = output_dir / MANIFEST_FILE

    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    np.save(vectors_path, vectors)

    manifest = {
        "model": model_name,
        "dimension": int(vectors.shape[1]),
        "chunk_count": int(vectors.shape[0]),
        "chunk_source": chunk_source,
        "metadata_file": METADATA_FILE,
        "vectors_file": VECTORS_FILE,
    }
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)


def load_embeddings(output_dir: Path) -> tuple[list[dict[str, Any]], np.ndarray]:
    """Load persisted embeddings and metadata.

    Returns:
        Tuple of (metadata list, embeddings matrix).
    """
    output_dir = Path(output_dir)
    metadata_path = output_dir / METADATA_FILE
    vectors_path = output_dir / VECTORS_FILE
    manifest_path = output_dir / MANIFEST_FILE

    if not metadata_path.exists() or not vectors_path.exists():
        raise FileNotFoundError(f"Missing embeddings files in {output_dir}")

    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    vectors = np.load(vectors_path)

    _validate_vectors(metadata, vectors)

    if manifest_path.exists():
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        if manifest.get("chunk_count") != len(metadata):
            raise ValueError("Manifest chunk_count does not match loaded metadata length.")

    return metadata, vectors


def get_embeddings_output_dir(base_dir: Path, model_name: str) -> Path:
    """Return the standard output directory for a given model name."""
    return _get_embedding_dir(base_dir, model_name)

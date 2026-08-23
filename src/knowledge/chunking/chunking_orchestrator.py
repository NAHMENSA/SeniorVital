"""Chunking orchestrator for SeniorVital knowledge base documents."""

import json
import os
import re
import uuid
from pathlib import Path
from typing import Any

from .fallback_chunker import FallbackChunker
from .preprocessor import preprocess_file
from .semantic_chunker import SemanticChunkerWrapper
from .structural_chunker import StructuralChunker


class ChunkingOrchestrator:
    """Orchestrate hybrid chunking (structural, semantic, fallback) for documents."""

    def __init__(
        self,
        semantic_chunker: SemanticChunkerWrapper | None = None,
        structural_chunker: StructuralChunker | None = None,
        fallback_chunker: FallbackChunker | None = None,
        min_chunk_size: int = 500,
        max_chunk_size: int = 800,
        short_doc_threshold: int = 500,
    ) -> None:
        self.semantic_chunker = semantic_chunker or SemanticChunkerWrapper()
        self.structural_chunker = structural_chunker or StructuralChunker()
        self.fallback_chunker = fallback_chunker or FallbackChunker()
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
        self.short_doc_threshold = short_doc_threshold

    def _word_count(self, text: str) -> int:
        """Approximate word count for a text."""
        return len(text.split())

    def _select_strategy(self, text: str, has_headers: bool) -> str:
        """Select the chunking strategy for a document."""
        if has_headers:
            return "structural"
        if self._word_count(text) < self.short_doc_threshold:
            return "fallback"
        if self.semantic_chunker.is_available():
            return "semantic"
        return "fallback"

    def _chunk_by_strategy(self, text: str, strategy: str) -> list[dict[str, Any]]:
        """Apply the selected chunking strategy."""
        if strategy == "structural":
            return self.structural_chunker.split(text)
        if strategy == "semantic":
            try:
                return self.semantic_chunker.split(text)
            except Exception as exc:
                print(f"Semantic chunking failed: {exc}. Falling back to recursive chunking.")
                return self.fallback_chunker.split(text)
        return self.fallback_chunker.split(text)

    def _post_process(
        self,
        chunks: list[dict[str, Any]],
        strategy: str,
    ) -> list[dict[str, Any]]:
        """Validate chunk sizes and re-chunk oversized pieces with fallback.

        Structural chunks are preserved intact unless they exceed a much larger
        semantic limit (4000 chars), so that section boundaries and tables are
        not broken. Semantic and fallback chunks are constrained to the normal
        [min_chunk_size, max_chunk_size] range.
        """
        STRUCTURAL_MAX = 1000
        processed = []
        for chunk in chunks:
            content = chunk["content"]
            chunk_type = chunk.get("chunk_type", "fallback")
            size_limit = STRUCTURAL_MAX if chunk_type == "structural" else self.max_chunk_size

            if len(content) > size_limit:
                fallback_chunks = self.fallback_chunker.split(content)
                for fb in fallback_chunks:
                    processed.append({**chunk, **fb, "chunk_type": "fallback"})
            elif len(content) < self.min_chunk_size and len(chunks) > 1:
                # Keep small chunks but mark them; they will be merged later if possible.
                processed.append(chunk)
            else:
                processed.append(chunk)
        return processed

    def _merge_small_chunks(
        self,
        chunks: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Merge consecutive chunks that are below the minimum word count.

        Greedy forward merge: a chunk with fewer than 80 words is merged with
        the next chunk as long as the combined text stays below 1,000 chars.
        A final backward pass absorbs a trailing small chunk into the previous
        one under the same size limit. After merging, mixed types are marked
        as 'fallback'.
        """
        if not chunks:
            return chunks
        if len(chunks) == 1:
            return [dict(chunks[0])]

        max_merge_chars = 1000
        min_words = 80

        # Forward pass: merge small chunks with the next chunk.
        merged = [dict(chunks[0])]
        for current in chunks[1:]:
            previous = merged[-1]
            prev_words = len(previous["content"].split())
            combined_len = len(previous["content"]) + len(current["content"]) + 2  # separators
            if prev_words < min_words and combined_len < max_merge_chars:
                previous["content"] += "\n\n" + current["content"]
                if previous["chunk_type"] != current["chunk_type"]:
                    previous["chunk_type"] = "fallback"
            else:
                merged.append(dict(current))

        # Backward pass: absorb a trailing small chunk if possible.
        if len(merged) > 1:
            last = merged[-1]
            if len(last["content"].split()) < min_words:
                prev = merged[-2]
                combined_len = len(prev["content"]) + len(last["content"]) + 2
                if combined_len < max_merge_chars:
                    prev["content"] += "\n\n" + last["content"]
                    if prev["chunk_type"] != last["chunk_type"]:
                        prev["chunk_type"] = "fallback"
                    merged.pop()

        return merged

    def _enrich_metadata(
        self,
        chunks: list[dict[str, Any]],
        filepath: Path,
        macrodomain: str,
        macrodomain_name: str,
        has_headers: bool,
    ) -> list[dict[str, Any]]:
        """Add document-level and chunk-level metadata."""
        total = len(chunks)
        enriched = []
        abs_filepath = filepath.resolve()
        root_dir = self._root_dir()
        try:
            source_path = str(abs_filepath.relative_to(root_dir)).replace("\\", "/")
        except ValueError:
            source_path = str(filepath).replace("\\", "/")
        for idx, chunk in enumerate(chunks):
            content = chunk["content"].strip()
            enriched.append(
                {
                    "chunk_id": str(uuid.uuid4()),
                    "document_name": filepath.name,
                    "source_path": source_path,
                    "macrodomain": macrodomain,
                    "macrodomain_name": macrodomain_name,
                    "section_path": chunk.get("section_path", ""),
                    "chunk_type": chunk.get("chunk_type", "fallback"),
                    "chunk_index": idx,
                    "total_chunks": total,
                    "char_count": len(content),
                    "word_count": self._word_count(content),
                    "has_markdown_headers": has_headers,
                    "level": self._extract_level(content),
                    "pathology": self._extract_pathology(content),
                    "keywords": self._extract_keywords(content),
                    "content": content,
                }
            )
        return enriched

    def _root_dir(self) -> Path:
        """Return project root directory."""
        return Path(__file__).resolve().parent.parent.parent.parent

    def _extract_level(self, text: str) -> str | None:
        """Infer functional level from chunk content."""
        lower = text.lower()
        if any(term in lower for term in ["frágil", "fragil", "atención prioritaria", "silla", "postrado"]):
            return "Frágil"
        if any(term in lower for term in ["muy activo", "activo avanzado", "alto rendimiento"]):
            return "Muy Activo"
        if any(term in lower for term in ["activo", "resiliente", "independiente"]):
            return "Activo"
        return None

    def _extract_pathology(self, text: str) -> str | None:
        """Infer main pathology from chunk content."""
        pathologies = [
            "osteoporosis",
            "diabetes",
            "artritis",
            "hipertensión",
            "hipertension",
            "depresión",
            "demencia",
            "sarcopenia",
            "obesidad",
            "enfermedad cardiovascular",
        ]
        lower = text.lower()
        for p in pathologies:
            if p in lower:
                return p
        return None

    def _extract_keywords(self, text: str) -> list[str]:
        """Extract simple keywords from chunk content."""
        lower = text.lower()
        keywords = []
        keyword_map = {
            "fuerza": ["fuerza", "musculación", "levantar pesas"],
            "equilibrio": ["equilibrio", "caídas", "estabilidad"],
            "flexibilidad": ["flexibilidad", "estiramiento", "movilidad articular"],
            "aeróbico": ["aeróbico", "resistencia", "caminar", "cardiovascular"],
            "nutrición": ["nutrición", "alimentación", "dieta", "proteína"],
            "seguridad": ["seguridad", "precaución", "consulta médica"],
        }
        for keyword, terms in keyword_map.items():
            if any(term in lower for term in terms):
                keywords.append(keyword)
        return keywords

    def process_document(
        self,
        filepath: Path,
        macrodomain: str,
        macrodomain_name: str,
    ) -> list[dict[str, Any]]:
        """Process a single document end-to-end."""
        text, has_headers = preprocess_file(filepath)
        strategy = self._select_strategy(text, has_headers)
        chunks = self._chunk_by_strategy(text, strategy)
        chunks = self._post_process(chunks, strategy)
        chunks = self._merge_small_chunks(chunks)
        return self._enrich_metadata(chunks, filepath, macrodomain, macrodomain_name, has_headers)

    def process_all_documents(
        self,
        kb_dir: Path,
        inventory: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Process all documents in the knowledge base using the inventory metadata."""
        all_chunks = []
        doc_index = {d["filename"]: d for d in inventory["documents"]}

        for filepath in sorted(kb_dir.glob("*.md")):
            if filepath.name == ".gitkeep":
                continue
            info = doc_index.get(filepath.name, {})
            macrodomain = info.get("macrodomain", "UNKNOWN")
            macrodomain_name = info.get("macrodomain_name", "Desconocido")
            print(f"Processing {filepath.name} (strategy: {self._select_strategy(*preprocess_file(filepath))})")
            chunks = self.process_document(filepath, macrodomain, macrodomain_name)
            all_chunks.extend(chunks)

        return all_chunks

    def save_chunks(
        self,
        chunks: list[dict[str, Any]],
        output_dir: Path,
        per_document: bool = True,
    ) -> None:
        """Save chunks to JSON files."""
        output_dir.mkdir(parents=True, exist_ok=True)

        if per_document:
            by_doc: dict[str, list[dict[str, Any]]] = {}
            for chunk in chunks:
                by_doc.setdefault(chunk["document_name"], []).append(chunk)
            for doc_name, doc_chunks in by_doc.items():
                safe_name = re.sub(r"[^\w\-_.]", "_", doc_name).replace(".md", "")
                out_path = output_dir / f"{safe_name}.chunks.json"
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(doc_chunks, f, ensure_ascii=False, indent=2)

        all_path = output_dir / "all_chunks.json"
        with open(all_path, "w", encoding="utf-8") as f:
            json.dump(chunks, f, ensure_ascii=False, indent=2)

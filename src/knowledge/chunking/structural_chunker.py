"""Structural chunker using MarkdownHeaderTextSplitter."""

from pathlib import Path
from typing import Any

from langchain_text_splitters import MarkdownHeaderTextSplitter

from .preprocessor import preprocess_file


class StructuralChunker:
    """Chunk documents by Markdown headers, preserving section hierarchy."""

    def __init__(
        self,
        headers_to_split_on: list[tuple[str, str]] | None = None,
        strip_headers: bool = False,
    ) -> None:
        self.headers_to_split_on = headers_to_split_on or [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
        ]
        self.strip_headers = strip_headers

    def split(self, text: str) -> list[dict[str, Any]]:
        """Split preprocessed text by Markdown headers."""
        splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=self.headers_to_split_on,
            strip_headers=self.strip_headers,
        )
        docs = splitter.split_text(text)

        chunks = []
        for idx, doc in enumerate(docs):
            metadata = doc.metadata or {}
            section_path = " > ".join(
                str(metadata.get(key, "")) for key in ["Header 1", "Header 2", "Header 3"]
            ).strip(" >")
            chunks.append(
                {
                    "content": doc.page_content,
                    "section_path": section_path,
                    "chunk_type": "structural",
                    "chunk_index": idx,
                }
            )
        return chunks

    def split_file(self, filepath: Path) -> tuple[list[dict[str, Any]], bool]:
        """Read a file, preprocess it, and split by headers."""
        text, headers_present = preprocess_file(filepath)
        if not headers_present:
            return [], False
        return self.split(text), True

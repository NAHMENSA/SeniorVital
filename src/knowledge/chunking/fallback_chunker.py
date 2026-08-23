"""Fallback chunker using RecursiveCharacterTextSplitter."""

from pathlib import Path
from typing import Any

from langchain_text_splitters import RecursiveCharacterTextSplitter

from .preprocessor import preprocess_file


class FallbackChunker:
    """Chunk documents recursively when semantic or structural chunking is unsuitable."""

    def __init__(
        self,
        chunk_size: int = 700,
        chunk_overlap: int = 80,
        separators: list[str] | None = None,
    ) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", ". ", " ", ""]

    def split(self, text: str) -> list[dict[str, Any]]:
        """Split text recursively by separators."""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=self.separators,
            length_function=len,
        )
        docs = splitter.create_documents([text])

        chunks = []
        for idx, doc in enumerate(docs):
            chunks.append(
                {
                    "content": doc.page_content,
                    "section_path": "",
                    "chunk_type": "fallback",
                    "chunk_index": idx,
                }
            )
        return chunks

    def split_file(self, filepath: Path) -> list[dict[str, Any]]:
        """Read a file, preprocess it, and split recursively."""
        text, _ = preprocess_file(filepath)
        return self.split(text)

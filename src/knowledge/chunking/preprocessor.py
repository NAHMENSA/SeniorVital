"""Preprocessing utilities for SeniorVital knowledge documents."""

import re
from pathlib import Path


def remove_code_block_fences(text: str) -> str:
    """Remove Markdown code-block fences (single wrapping block or multiple blocks)."""
    lines = text.splitlines()
    result = []
    in_code_block = False
    for line in lines:
        if re.match(r"^```\s*\w*\s*$", line):
            in_code_block = not in_code_block
            continue
        result.append(line)
    # If the whole document was wrapped in a single fence, the first/last fence
    # toggled the flag and was skipped. If fences were unbalanced, drop the
    # remaining flag but keep the content.
    return "\n".join(result)


def normalize_whitespace(text: str) -> str:
    """Collapse multiple blank lines and trim leading/trailing whitespace."""
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
    return text.strip()


def markdown_table_to_text(text: str) -> str:
    """Convert simple Markdown tables to structured text representation."""
    lines = text.splitlines()
    result = []
    table_lines = []
    in_table = False

    for line in lines:
        if re.match(r"^\|.*\|.*\|$", line):
            in_table = True
            table_lines.append(line)
        else:
            if in_table:
                result.append(_render_table(table_lines))
                table_lines = []
                in_table = False
            result.append(line)

    if in_table:
        result.append(_render_table(table_lines))

    return "\n".join(result)


def _render_table(lines: list[str]) -> str:
    """Render a Markdown table as a text paragraph."""
    rows = []
    for line in lines:
        cells = [cell.strip() for cell in line.split("|")]
        cells = [c for c in cells if c]
        if cells and not all(re.match(r"^-+$", c) for c in cells):
            rows.append(", ".join(cells))
    return "Tabla: " + "; ".join(rows) + "."


def has_markdown_headers(text: str) -> bool:
    """Return True if the text contains at least one Markdown header."""
    return bool(re.search(r"^#{1,6}\s+", text, flags=re.MULTILINE))


def preprocess_document(text: str) -> str:
    """Apply full preprocessing pipeline to a document."""
    text = remove_code_block_fences(text)
    text = markdown_table_to_text(text)
    text = normalize_whitespace(text)
    return text


def preprocess_file(filepath: Path) -> tuple[str, bool]:
    """Read and preprocess a document file.

    Returns the preprocessed text and a boolean indicating whether the original
    text had Markdown headers.
    """
    raw_text = filepath.read_text(encoding="utf-8")
    headers_present = has_markdown_headers(raw_text)
    processed = preprocess_document(raw_text)
    return processed, headers_present

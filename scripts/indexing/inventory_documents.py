"""Inventory script for SeniorVital knowledge base documents.

Analyzes all Markdown files in data/knowledge_base/ and generates
a JSON inventory with size, header structure, word counts, paragraph
counts, code-block wrapping and estimated macrodomain classification.
"""

import json
import os
import re
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
KB_DIR = ROOT_DIR / "data" / "knowledge_base"
OUTPUT_DIR = ROOT_DIR / "data" / "processed"
OUTPUT_FILE = OUTPUT_DIR / "document_inventory.json"

MACRODOMAIN_MAP = {
    "Sarcopenia y dinapenia.md": "A",
    "Movilidad articular en adultos mayores + ejercicios - ESHI.md": "A",
    "Cómo frenar la osteoporosis 8 claves basadas en la evidencia - ESHI.md": "A",
    "La diabetes.md": "A",
    "Mejores ejercicios de fuerza para mayores de 60 años - Guía.md": "B",
    "Los tres tipos de ejercicio que pueden mejorar su salud y capacidad física.md": "B",
    "guia-ejercicio-mayores-segg.md": "B",
    "Entrenamiento en adultos mayores - guía completa - ESHI.md": "B",
    "Manual_ejercicio_persona_mayor_domicilio2.md": "C",
    "Exercising Outdoors_ Safety Tips for Older Adults.md": "C",
    "Tips for Getting and Staying Active as You Age.md": "C",
    "Hacer ejercicio con enfermedades crónicas.md": "D",
    "Alimentación saludable para personas mayores.md": "E",
    "WEB-GUIA-MAYORES-version-publicacion.md": "F",
    "Gimnasia para mayores guía oficial para una vida activa y feliz.md": "F",
    "Ejercicio_y_actividad_fisicasmaller-39-100.md": "B",
    "Diferencias en el entrenamiento entre hombres y mujeres lo que dice la ciencia - ESHI.md": "B",
    "Cómo pueden las personas mayores comenzar a hacer ejercicio.md": "B",
    "DOCUMENTO DE CONOCIMIENTO SENIORVITAL.md": "B",
}

MACRODOMAIN_NAMES = {
    "A": "Fundamentos fisiológicos y patologías",
    "B": "Taxonomía del ejercicio",
    "C": "Contexto y entorno",
    "D": "Comorbilidades y seguridad clínica",
    "E": "Nutrición y metabolismo",
    "F": "Estimulación cognitiva y bienestar emocional",
}


def extract_headers(text: str) -> list[dict]:
    """Extract Markdown headers with their level and title."""
    headers = []
    for line in text.splitlines():
        match = re.match(r"^(#{1,6})\s+(.+)$", line)
        if match:
            level = len(match.group(1))
            title = match.group(2).strip()
            headers.append({"level": level, "title": title})
    return headers


def count_tables(text: str) -> int:
    """Count Markdown tables (simple heuristic)."""
    return len(re.findall(r"^\|.*\|.*\|$", text, flags=re.MULTILINE)) // 2


def count_lists(text: str) -> int:
    """Count Markdown list items."""
    return len(re.findall(r"^\s*[-*+]\s+", text, flags=re.MULTILINE))


def count_paragraphs(text: str) -> int:
    """Count paragraphs separated by blank lines (after normalizing)."""
    normalized = re.sub(r"\n\s*\n+", "\n\n", text.strip())
    return len([p for p in normalized.split("\n\n") if p.strip()])


def is_wrapped_in_code_block(text: str) -> bool:
    """Detect if the document starts and ends with a code fence."""
    stripped = text.strip()
    return stripped.startswith("```") and stripped.endswith("```")


def analyze_document(filepath: Path) -> dict:
    """Analyze a single Markdown document."""
    raw_text = filepath.read_text(encoding="utf-8")
    headers = extract_headers(raw_text)
    header_levels = [h["level"] for h in headers]
    words = len(raw_text.split())
    chars = len(raw_text)
    filename = filepath.name
    macrodomain = MACRODOMAIN_MAP.get(filename, "UNKNOWN")

    return {
        "filename": filename,
        "source_path": str(filepath.relative_to(ROOT_DIR)).replace("\\", "/"),
        "macrodomain": macrodomain,
        "macrodomain_name": MACRODOMAIN_NAMES.get(macrodomain, "Desconocido"),
        "size_bytes": os.path.getsize(filepath),
        "word_count": words,
        "char_count": chars,
        "paragraph_count": count_paragraphs(raw_text),
        "has_markdown_headers": len(headers) > 0,
        "header_count": len(headers),
        "header_levels": header_levels,
        "headers": headers[:20],
        "max_header_level": max(header_levels) if header_levels else 0,
        "min_header_level": min(header_levels) if header_levels else 0,
        "table_count": count_tables(raw_text),
        "list_item_count": count_lists(raw_text),
        "wrapped_in_code_block": is_wrapped_in_code_block(raw_text),
    }


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    documents = []
    for filepath in sorted(KB_DIR.glob("*.md")):
        if filepath.name == ".gitkeep":
            continue
        documents.append(analyze_document(filepath))

    inventory = {
        "total_documents": len(documents),
        "total_words": sum(d["word_count"] for d in documents),
        "total_chars": sum(d["char_count"] for d in documents),
        "documents_with_headers": sum(1 for d in documents if d["has_markdown_headers"]),
        "documents_wrapped_in_code_blocks": sum(
            1 for d in documents if d["wrapped_in_code_block"]
        ),
        "macrodomain_counts": {},
        "documents": documents,
    }

    for d in documents:
        inventory["macrodomain_counts"][d["macrodomain"]] = (
            inventory["macrodomain_counts"].get(d["macrodomain"], 0) + 1
        )

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(inventory, f, ensure_ascii=False, indent=2)

    print(f"Inventory saved to {OUTPUT_FILE}")
    print(f"Documents analyzed: {inventory['total_documents']}")
    print(f"Total words: {inventory['total_words']}")
    print(f"Documents with headers: {inventory['documents_with_headers']}")
    print(f"Documents wrapped in code blocks: {inventory['documents_wrapped_in_code_blocks']}")
    print(f"Macrodomain counts: {inventory['macrodomain_counts']}")


if __name__ == "__main__":
    main()

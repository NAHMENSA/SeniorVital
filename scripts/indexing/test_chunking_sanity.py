"""Quick sanity test for chunking modules."""

from pathlib import Path

from knowledge.chunking import ChunkingOrchestrator, FallbackChunker, StructuralChunker

KB_DIR = Path("data/knowledge_base")


def test_preprocessor():
    from knowledge.chunking.preprocessor import preprocess_file

    text, has_headers = preprocess_file(KB_DIR / "Alimentación saludable para personas mayores.md")
    print(f"Preprocessor: has_headers={has_headers}, length={len(text)}, fences={text.count('```')}")


def test_structural():
    chunker = StructuralChunker()
    chunks, ok = chunker.split_file(KB_DIR / "DOCUMENTO DE CONOCIMIENTO SENIORVITAL.md")
    print(f"Structural chunks: {len(chunks)} (ok={ok})")
    for c in chunks[:3]:
        print(f"  [{c['chunk_index']}] {c['section_path']}: {c['content'][:80]}...")


def test_fallback():
    chunker = FallbackChunker()
    chunks = chunker.split_file(KB_DIR / "Alimentación saludable para personas mayores.md")
    print(f"Fallback chunks: {len(chunks)}")
    for c in chunks[:3]:
        print(f"  [{c['chunk_index']}] {c['content'][:80]}...")


def test_orchestrator():
    orchestrator = ChunkingOrchestrator()
    chunks = orchestrator.process_document(
        KB_DIR / "Alimentación saludable para personas mayores.md",
        macrodomain="E",
        macrodomain_name="Nutrición y metabolismo",
    )
    print(f"Orchestrator chunks: {len(chunks)}")
    for c in chunks[:2]:
        print(f"  [{c['chunk_index']}] type={c['chunk_type']} words={c['word_count']} chars={c['char_count']}")
        print(f"    content: {c['content'][:80]}...")


if __name__ == "__main__":
    test_preprocessor()
    test_structural()
    test_fallback()
    test_orchestrator()

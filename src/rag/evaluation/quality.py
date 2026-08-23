"""Response quality metrics for RAG evaluation.

Heuristic-based metrics that do NOT require an external LLM judge.
"""

from __future__ import annotations

import re
from collections import Counter


def keyword_coverage(answer: str, expected_keywords: list[str]) -> float:
    """Fraction of expected keywords found in the answer (case-insensitive).

    Args:
        answer: Generated answer text.
        expected_keywords: List of keywords that should appear.

    Returns:
        Coverage in [0.0, 1.0]. Returns 1.0 if no keywords expected.
    """
    if not expected_keywords:
        return 1.0
    answer_lower = answer.lower()
    hits = sum(1 for kw in expected_keywords if kw.lower() in answer_lower)
    return hits / len(expected_keywords)


def citation_check(answer: str, sources: list[dict]) -> bool:
    """Check if the answer references any of its sources.

    Looks for patterns like "fuente", "según", "de acuerdo con", or
    numbered references [1], [2], etc.

    Args:
        answer: Generated answer text.
        sources: List of source dicts with 'chunk_id' or 'content'.

    Returns:
        True if the answer appears to cite sources.
    """
    if not sources:
        return False
    citation_patterns = [
        r"\[\d+\]",                    # [1], [2], etc.
        r"fuente\s*\d+",               # fuente 1, fuente 2
        r"según\s",                    # según el documento
        r"de acuerdo con",
        r"conforme a",
        r"extraído de",
        r"extraída de",
    ]
    answer_lower = answer.lower()
    return any(re.search(p, answer_lower) for p in citation_patterns)


def hallucination_flag(answer: str, context_chunks: list[dict]) -> dict:
    """Detect potential hallucinations by checking if key claims are grounded.

    Heuristic: extracts sentences from the answer and checks if any
    significant noun/number appears that is NOT in the context.

    Returns a dict with:
    - 'flagged': bool — whether potential hallucination detected
    - 'unsupported_claims': list[str] — sentences that may be unsupported

    Args:
        answer: Generated answer text.
        context_chunks: List of context chunk dicts with 'content'.
    """
    if not context_chunks or not answer:
        return {"flagged": False, "unsupported_claims": []}

    # Build context text
    context_text = " ".join(
        chunk.get("content", "") for chunk in context_chunks
    ).lower()

    # Split answer into sentences
    sentences = re.split(r"[.!?]+", answer)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

    unsupported = []
    for sentence in sentences:
        # Extract meaningful words (>= 5 chars, not stopwords)
        words = re.findall(r"\b[a-záéíóúñ]{5,}\b", sentence.lower())
        # Check if most words appear in context
        if words:
            grounded = sum(1 for w in words if w in context_text)
            ratio = grounded / len(words)
            if ratio < 0.3:  # Less than 30% of words grounded in context
                unsupported.append(sentence.strip())

    return {
        "flagged": len(unsupported) > 0,
        "unsupported_claims": unsupported,
    }


def answer_length_stats(results: list[dict]) -> dict:
    """Compute descriptive statistics for answer lengths.

    Args:
        results: List of dicts with 'answer' field.

    Returns:
        Dict with min, max, mean, median, std of answer word counts.
    """
    import statistics

    lengths = [len(r.get("answer", "").split()) for r in results]
    if not lengths:
        return {"min": 0, "max": 0, "mean": 0, "median": 0, "std": 0}

    return {
        "min": min(lengths),
        "max": max(lengths),
        "mean": round(statistics.mean(lengths), 1),
        "median": round(statistics.median(lengths), 1),
        "std": round(statistics.stdev(lengths), 1) if len(lengths) > 1 else 0,
    }

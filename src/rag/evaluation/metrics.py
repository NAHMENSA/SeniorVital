"""Retrieval metrics for RAG evaluation.

All functions operate on chunk_id strings and are model-agnostic.
"""

from __future__ import annotations


def precision_at_k(retrieved_ids: list[str], relevant_ids: list[str], k: int) -> float:
    """Fraction of top-k retrieved items that are relevant.

    Args:
        retrieved_ids: Ordered list of retrieved chunk IDs.
        relevant_ids: Set of ground-truth relevant chunk IDs.
        k: Number of top results to evaluate.

    Returns:
        Precision@k in [0.0, 1.0]. Returns 0.0 if k <= 0.
    """
    if k <= 0:
        return 0.0
    top_k = retrieved_ids[:k]
    relevant_set = set(relevant_ids)
    hits = sum(1 for cid in top_k if cid in relevant_set)
    return hits / k


def recall_at_k(retrieved_ids: list[str], relevant_ids: list[str], k: int) -> float:
    """Fraction of relevant items found in top-k results.

    Args:
        retrieved_ids: Ordered list of retrieved chunk IDs.
        relevant_ids: Set of ground-truth relevant chunk IDs.
        k: Number of top results to evaluate.

    Returns:
        Recall@k in [0.0, 1.0]. Returns 0.0 if no relevant items exist.
    """
    if not relevant_ids or k <= 0:
        return 0.0
    top_k = retrieved_ids[:k]
    relevant_set = set(relevant_ids)
    hits = sum(1 for cid in top_k if cid in relevant_set)
    return hits / len(relevant_ids)


def mrr(retrieved_ids: list[str], relevant_ids: list[str]) -> float:
    """Mean Reciprocal Rank — 1/rank of the first relevant result.

    Args:
        retrieved_ids: Ordered list of retrieved chunk IDs.
        relevant_ids: Set of ground-truth relevant chunk IDs.

    Returns:
        MRR in [0.0, 1.0]. Returns 0.0 if no relevant item is found.
    """
    relevant_set = set(relevant_ids)
    for i, cid in enumerate(retrieved_ids):
        if cid in relevant_set:
            return 1.0 / (i + 1)
    return 0.0


def hit_rate(results: list[dict], k: int = 5) -> float:
    """Fraction of queries that have at least one relevant result in top-k.

    Args:
        results: List of dicts, each with 'retrieved_ids' and 'relevant_ids'.
        k: Number of top results to check.

    Returns:
        Hit rate in [0.0, 1.0].
    """
    if not results:
        return 0.0
    hits = 0
    relevant_set_all = set()
    for r in results:
        relevant_set = set(r["relevant_ids"])
        top_k = r["retrieved_ids"][:k]
        if any(cid in relevant_set for cid in top_k):
            hits += 1
    return hits / len(results)


def macrodomain_accuracy(detected: list[str], expected: list[str]) -> float:
    """Fraction of queries where detected macrodomain matches expected.

    Args:
        detected: List of detected macrodomain letters.
        expected: List of expected macrodomain letters.

    Returns:
        Accuracy in [0.0, 1.0].
    """
    if not expected:
        return 0.0
    matches = sum(1 for d, e in zip(detected, expected) if d == e)
    return matches / len(expected)

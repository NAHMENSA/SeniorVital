"""Evaluation module for SeniorVital RAG pipeline."""

from .metrics import (
    precision_at_k,
    recall_at_k,
    mrr,
    hit_rate,
    macrodomain_accuracy,
)
from .quality import (
    keyword_coverage,
    citation_check,
    hallucination_flag,
    answer_length_stats,
)

__all__ = [
    "precision_at_k",
    "recall_at_k",
    "mrr",
    "hit_rate",
    "macrodomain_accuracy",
    "keyword_coverage",
    "citation_check",
    "hallucination_flag",
    "answer_length_stats",
]

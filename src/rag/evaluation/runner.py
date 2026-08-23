"""RAG evaluation runner.

Executes the test query set against the live pipeline and computes metrics.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

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


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DEFAULT_QUERY_SET = PROJECT_ROOT / "data" / "evaluation" / "test_queries.json"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "evaluation" / "results"


def load_query_set(path: Path | None = None) -> list[dict]:
    """Load the test query set from JSON."""
    path = path or DEFAULT_QUERY_SET
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["queries"]


async def run_single_query(
    pipeline: Any,
    query_entry: dict,
    k: int = 5,
) -> dict:
    """Execute a single test query and capture results.

    Returns a dict with:
    - query info (id, query, expected_macrodomain, etc.)
    - pipeline result (answer, sources, detected agent/macrodomain)
    - timing info
    """
    start = time.perf_counter()
    try:
        result = await pipeline.process_query(
            query=query_entry["query"],
            k=k,
        )
        elapsed = time.perf_counter() - start
        return {
            "query_id": query_entry["id"],
            "query": query_entry["query"],
            "expected_macrodomain": query_entry["expected_macrodomain"],
            "expected_agent": query_entry["expected_agent"],
            "relevant_chunk_ids": query_entry["relevant_chunk_ids"],
            "difficulty": query_entry["difficulty"],
            "category": query_entry["category"],
            "expected_answer_keywords": query_entry["expected_answer_keywords"],
            "detected_macrodomain": result.get("query_info", {}).get("detected_macrodomain"),
            "detected_agent": result.get("query_info", {}).get("detected_agent"),
            "answer": result.get("answer", ""),
            "sources": result.get("sources", []),
            "warnings": result.get("warnings", []),
            "retrieved_ids": [s["chunk_id"] for s in result.get("sources", [])],
            "elapsed_seconds": round(elapsed, 3),
            "error": None,
        }
    except Exception as e:
        elapsed = time.perf_counter() - start
        return {
            "query_id": query_entry["id"],
            "query": query_entry["query"],
            "expected_macrodomain": query_entry["expected_macrodomain"],
            "expected_agent": query_entry["expected_agent"],
            "relevant_chunk_ids": query_entry["relevant_chunk_ids"],
            "difficulty": query_entry["difficulty"],
            "category": query_entry["category"],
            "expected_answer_keywords": query_entry["expected_answer_keywords"],
            "detected_macrodomain": None,
            "detected_agent": None,
            "answer": "",
            "sources": [],
            "warnings": [],
            "retrieved_ids": [],
            "elapsed_seconds": round(elapsed, 3),
            "error": str(e),
        }


def compute_metrics(results: list[dict], k: int = 5) -> dict:
    """Compute all metrics from a list of query results.

    Returns a dict with:
    - retrieval: precision, recall, MRR, hit_rate
    - detection: macrodomain accuracy
    - quality: keyword coverage, citation rate, hallucination rate, length stats
    - per_domain: per-macrodomain breakdown
    - per_difficulty: per-difficulty breakdown
    """
    # Filter out errored results
    valid = [r for r in results if r["error"] is None]

    if not valid:
        return {"error": "No valid results to evaluate"}

    # Retrieval metrics
    precisions = [precision_at_k(r["retrieved_ids"], r["relevant_chunk_ids"], k) for r in valid]
    recalls = [recall_at_k(r["retrieved_ids"], r["relevant_chunk_ids"], k) for r in valid]
    mrrs = [mrr(r["retrieved_ids"], r["relevant_chunk_ids"]) for r in valid]
    hr = hit_rate([{"retrieved_ids": r["retrieved_ids"], "relevant_ids": r["relevant_chunk_ids"]} for r in valid], k)

    # Detection metrics
    detected_domains = [r["detected_macrodomain"] for r in valid]
    expected_domains = [r["expected_macrodomain"] for r in valid]
    domain_acc = macrodomain_accuracy(detected_domains, expected_domains)

    # Quality metrics
    kw_coverages = [keyword_coverage(r["answer"], r["expected_answer_keywords"]) for r in valid]
    citation_rates = [citation_check(r["answer"], r["sources"]) for r in valid]
    hallucination_checks = [hallucination_flag(r["answer"], r["sources"]) for r in valid]
    length_stats = answer_length_stats(valid)

    # Per-domain breakdown
    per_domain = {}
    for domain in set(expected_domains):
        domain_results = [r for r in valid if r["expected_macrodomain"] == domain]
        if domain_results:
            d_precisions = [precision_at_k(r["retrieved_ids"], r["relevant_chunk_ids"], k) for r in domain_results]
            d_recalls = [recall_at_k(r["retrieved_ids"], r["relevant_chunk_ids"], k) for r in domain_results]
            d_kws = [keyword_coverage(r["answer"], r["expected_answer_keywords"]) for r in domain_results]
            per_domain[domain] = {
                "count": len(domain_results),
                "precision_at_k": round(sum(d_precisions) / len(d_precisions), 3),
                "recall_at_k": round(sum(d_recalls) / len(d_recalls), 3),
                "keyword_coverage": round(sum(d_kws) / len(d_kws), 3),
            }

    # Per-difficulty breakdown
    per_difficulty = {}
    for diff in set(r["difficulty"] for r in valid):
        diff_results = [r for r in valid if r["difficulty"] == diff]
        if diff_results:
            dd_precisions = [precision_at_k(r["retrieved_ids"], r["relevant_chunk_ids"], k) for r in diff_results]
            dd_recalls = [recall_at_k(r["retrieved_ids"], r["relevant_chunk_ids"], k) for r in diff_results]
            dd_kws = [keyword_coverage(r["answer"], r["expected_answer_keywords"]) for r in diff_results]
            per_difficulty[diff] = {
                "count": len(diff_results),
                "precision_at_k": round(sum(dd_precisions) / len(dd_precisions), 3),
                "recall_at_k": round(sum(dd_recalls) / len(dd_recalls), 3),
                "keyword_coverage": round(sum(dd_kws) / len(dd_kws), 3),
            }

    return {
        "total_queries": len(results),
        "valid_queries": len(valid),
        "errored_queries": len(results) - len(valid),
        "k": k,
        "retrieval": {
            "precision_at_k": round(sum(precisions) / len(precisions), 3),
            "recall_at_k": round(sum(recalls) / len(recalls), 3),
            "mrr": round(sum(mrrs) / len(mrrs), 3),
            "hit_rate": round(hr, 3),
        },
        "detection": {
            "macrodomain_accuracy": round(domain_acc, 3),
        },
        "quality": {
            "keyword_coverage": round(sum(kw_coverages) / len(kw_coverages), 3),
            "citation_rate": round(sum(citation_rates) / len(citation_rates), 3),
            "hallucination_rate": round(sum(1 for h in hallucination_checks if h["flagged"]) / len(hallucination_checks), 3),
            "answer_length": length_stats,
        },
        "per_domain": per_domain,
        "per_difficulty": per_difficulty,
    }


def save_results(
    results: list[dict],
    metrics: dict,
    output_dir: Path | None = None,
) -> Path:
    """Save evaluation results and metrics to disk.

    Returns the output directory path.
    """
    output_dir = output_dir or DEFAULT_OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save raw results
    with open(output_dir / "raw_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # Save metrics summary
    with open(output_dir / "metrics_summary.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    return output_dir

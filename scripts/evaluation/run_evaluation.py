#!/usr/bin/env python3
"""Run RAG evaluation against the live pipeline.

Usage:
    PYTHONPATH=src python scripts/evaluation/run_evaluation.py [--k 5] [--output data/evaluation/results]

Requires:
    - Ollama running locally with phi3:mini model
    - ChromaDB vector store populated (data/vector_store/)
"""

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path

# Add src/ to path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from rag.evaluation.runner import (
    load_query_set,
    run_single_query,
    compute_metrics,
    save_results,
)
from rag.pipeline import SeniorVitalRAGPipeline


async def main(k: int = 5, output_dir: str | None = None) -> int:
    print("=" * 60)
    print("SeniorVital RAG Evaluation")
    print("=" * 60)

    # Load query set
    queries = load_query_set()
    print(f"\nLoaded {len(queries)} test queries")

    # Initialize pipeline
    print("Initializing RAG pipeline...")
    pipeline = SeniorVitalRAGPipeline(
        persist_directory=ROOT_DIR / "data" / "vector_store",
    )

    # Health check
    health = await pipeline.health_check()
    print(f"  Vector store: {health['vector_store_count']} chunks")
    print(f"  Ollama: {'available' if health['ollama_available'] else 'UNAVAILABLE'}")
    if not health["pipeline_ready"]:
        print("\nERROR: Pipeline not ready. Check Ollama and vector store.")
        return 1

    # Run evaluation
    print(f"\nRunning {len(queries)} queries (k={k})...")
    results = []
    start_total = time.perf_counter()

    for i, query_entry in enumerate(queries, 1):
        print(f"  [{i:2d}/{len(queries)}] {query_entry['id']}: {query_entry['query'][:50]}...", end=" ", flush=True)
        result = await run_single_query(pipeline, query_entry, k=k)
        results.append(result)
        status = "OK" if result["error"] is None else f"ERROR: {result['error'][:30]}"
        print(f"{status} ({result['elapsed_seconds']:.1f}s)")

    elapsed_total = time.perf_counter() - start_total
    print(f"\nTotal time: {elapsed_total:.1f}s ({elapsed_total/len(queries):.1f}s/query)")

    # Compute metrics
    print("\nComputing metrics...")
    metrics = compute_metrics(results, k=k)

    # Save results
    out = Path(output_dir) if output_dir else None
    saved_dir = save_results(results, metrics, output_dir=out)
    print(f"\nResults saved to: {saved_dir}")

    # Print summary
    print("\n" + "=" * 60)
    print("METRICS SUMMARY")
    print("=" * 60)
    print(f"\nRetrieval:")
    print(f"  Precision@{k}: {metrics['retrieval']['precision_at_k']:.3f}")
    print(f"  Recall@{k}:    {metrics['retrieval']['recall_at_k']:.3f}")
    print(f"  MRR:           {metrics['retrieval']['mrr']:.3f}")
    print(f"  Hit Rate:      {metrics['retrieval']['hit_rate']:.3f}")
    print(f"\nDetection:")
    print(f"  Macrodomain accuracy: {metrics['detection']['macrodomain_accuracy']:.3f}")
    print(f"\nQuality:")
    print(f"  Keyword coverage:  {metrics['quality']['keyword_coverage']:.3f}")
    print(f"  Citation rate:     {metrics['quality']['citation_rate']:.3f}")
    print(f"  Hallucination rate: {metrics['quality']['hallucination_rate']:.3f}")
    print(f"  Answer length:     {metrics['quality']['answer_length']['mean']:.0f} words (avg)")

    print(f"\nPer-domain breakdown:")
    for domain, stats in sorted(metrics.get("per_domain", {}).items()):
        print(f"  {domain}: P={stats['precision_at_k']:.3f} R={stats['recall_at_k']:.3f} KW={stats['keyword_coverage']:.3f} (n={stats['count']})")

    print(f"\nPer-difficulty breakdown:")
    for diff, stats in sorted(metrics.get("per_difficulty", {}).items()):
        print(f"  {diff}: P={stats['precision_at_k']:.3f} R={stats['recall_at_k']:.3f} KW={stats['keyword_coverage']:.3f} (n={stats['count']})")

    # Identify problem queries
    print(f"\nTop 5 problem queries (lowest recall):")
    sorted_by_recall = sorted(results, key=lambda r: (
        1.0 if r["error"] else
        sum(1 for cid in r["retrieved_ids"][:k] if cid in r["relevant_chunk_ids"]) / max(len(r["relevant_chunk_ids"]), 1)
    ))
    for r in sorted_by_recall[:5]:
        recall = sum(1 for cid in r["retrieved_ids"][:k] if cid in r["relevant_chunk_ids"]) / max(len(r["relevant_chunk_ids"]), 1)
        print(f"  {r['query_id']}: recall={recall:.2f} | {r['query'][:60]}")

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run RAG evaluation")
    parser.add_argument("--k", type=int, default=5, help="Number of chunks to retrieve")
    parser.add_argument("--output", type=str, default=None, help="Output directory")
    args = parser.parse_args()

    exit_code = asyncio.run(main(k=args.k, output_dir=args.output))
    sys.exit(exit_code)

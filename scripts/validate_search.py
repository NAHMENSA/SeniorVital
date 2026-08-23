"""Quick validation script for the vector store."""
import sys
sys.path.insert(0, "E:/SeniorVital-master/src")

from rag.vector_store import SeniorVitalVectorStore
from pathlib import Path

store = SeniorVitalVectorStore(persist_directory=Path("E:/SeniorVital-master/data/vector_store"))
print(f"Total indexed: {store.count()} chunks")
print()

results = store.search("ejercicio aerobico para caminar", k=3)
for i, r in enumerate(results):
    md = r["metadata"]["macrodomain"]
    content = r["content"][:80]
    dist = r["distance"]
    print(f"{i+1}. [{md}] {content}...")
    print(f"   Distance: {dist:.4f}")
print()

results = store.search_by_agent("dolor articular", agent_name="Physio-Evaluator", k=2)
for i, r in enumerate(results):
    md = r["metadata"]["macrodomain"]
    content = r["content"][:80]
    print(f"{i+1}. [{md}] {content}...")
print()

results = store.search_by_filters("dieta", filters={"pathology": "diabetes"}, k=2)
for i, r in enumerate(results):
    md = r["metadata"]["macrodomain"]
    content = r["content"][:80]
    print(f"{i+1}. [{md}] {content}...")

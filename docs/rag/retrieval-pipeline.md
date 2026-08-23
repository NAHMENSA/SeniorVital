# Retrieval Pipeline — SeniorVital RAG

## Flujo completo

```
1. Ingesta (una vez)
   all_chunks.json → index_knowledge_base.py → ChromaDB

2. Consulta (en tiempo real)
   Query del agente → Retriever → ChromaDB → Top-K chunks
```

## Componentes

### 1. Ingesta

```bash
# Generar chunks (S1-02)
PYTHONPATH=src python scripts/indexing/run_chunking.py

# Generar embeddings (S1-03)
PYTHONPATH=src python scripts/ingestion/generate_embeddings.py

# Indexar en ChromaDB (S1-04)
PYTHONPATH=src python scripts/ingestion/index_knowledge_base.py
```

### 2. Retriever

```python
from rag.retriever import SeniorVitalRetriever
from rag.vector_store import SeniorVitalVectorStore
from pathlib import Path

store = SeniorVitalVectorStore(persist_directory=Path("data/vector_store"))
retriever = SeniorVitalRetriever(store)

# Búsqueda general
chunks = retriever.retrieve("ejercicio para caminar", k=5)

# Por agente (filtra por macrodominio)
chunks = retriever.retrieve_for_agent("dolor de rodilla", agent_name="Exercise Architect")

# Por macrodominio
chunks = retriever.retrieve_by_macrodomain("nutrición", macrodomain="E")
```

### 3. Uso por agente

Cada agente autonomía consulta su macrodominio:

| Agente | Macrodominio | Ejemplo de query |
|---|---|---|
| Physio-Evaluator | A | "evaluación fisioterapéutica rodilla" |
| Exercise Architect | B | "ejercicio aeróbico caminar" |
| Context-Adaptor | C | "adaptabilidad hogar" |
| Safety Guardian | D | "precauciones osteoporosis" |
| Nutri-Buddy | E | "dieta recuperación muscular" |
| Mind & Soul | F | "ansiedad ejercicio" |

## Métricas de validación

- **Chunks indexados**: 363
- **Dimensión embeddings**: 384 (multilingual-e5-small)
- **Búsqueda por agente**: filtra correctamente por macrodominio
- **Búsqueda por filtros**: filtra por pathology, level, chunk_type
- **Tiempo de indexación**: ~30s (363 chunks)
- **Tiempo de búsqueda**: <1s por query

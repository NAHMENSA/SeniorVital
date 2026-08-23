# Sprint S1-04 — Vector Store & Retriever

**Fecha**: 2026-08-22
**Estado**: COMPLETADO

## Resumen

Implementación de la capa de almacenamiento vectorial con ChromaDB y retriever para la pipeline RAG de SeniorVital.

## Decisión técnica

**pgvector → ChromaDB**: pgvector requiere compilar extensión en Windows con MSVC. ChromaDB es pip install y funciona directamente. pgvector queda en backlog para fase de escalabilidad.

## Archivos creados/modificados

### Código

| Archivo | Descripción |
|---|---|
| `src/rag/vector_store/__init__.py` | Package init con exports |
| `src/rag/vector_store/chroma_store.py` | SeniorVitalVectorStore — interfaz modular |
| `src/rag/retriever/__init__.py` | Package init |
| `src/rag/retriever/retriever.py` | SeniorVitalRetriever — wrapper de búsqueda |
| `scripts/ingestion/index_knowledge_base.py` | Script de indexación chunks→ChromaDB |

### Tests

| Archivo | Tests |
|---|---|
| `tests/rag/test_vector_store.py` | 20 tests (vector store + retriever + metadata + mapping) |

### Documentación

| Archivo | Contenido |
|---|---|
| `docs/rag/vector-database.md` | Arquitectura, interfaz, metadatos, migración |
| `docs/rag/retrieval-pipeline.md` | Flujo completo, uso por agente |

### Correcciones

| Archivo | Fix |
|---|---|
| `tests/rag/conftest.py` | Path sys.path insert corregido (3 niveles dirname) |
| `src/rag/vector_store/chroma_store.py` | IncludeEnum removido (ChromaDB 1.5.x) |

## Resultados

- **363 chunks** indexados en ChromaDB
- **Embeddings**: 384 dims (intfloat/multilingual-e5-small)
- **53/53 tests** pasando (suite RAG completa)
- **Búsqueda validada**: 3 queries con resultados relevantes
- **Filtros funcionando**: macrodominio, agente, pathology

## Interfaz pública

```python
from rag.vector_store import SeniorVitalVectorStore
from rag.retriever import SeniorVitalRetriever

store = SeniorVitalVectorStore(persist_directory=Path("data/vector_store"))
retriever = SeniorVitalRetriever(store)

# Métodos disponibles
store.search(query, k=5, filters=None)
store.search_by_agent(query, agent_name, k=5)
store.search_by_macrodomain(query, macrodomain, k=5)
store.search_by_filters(query, filters, k=5)
store.add_chunks(chunks, embeddings=None)
store.upsert_chunks(chunks, embeddings=None)
store.get_by_chunk_id(chunk_id)
store.delete_all()
store.count()
```

## Pendiente

- Docs de usage en el README del proyecto
- Integración con los servicios FastAPI (fase S2)
- pgvector como alternativa de escalabilidad (backlog)

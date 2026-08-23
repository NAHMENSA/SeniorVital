# Vector Database — ChromaDB

## Decisión

ChromaDB como base vectorial local para SeniorVital RAG. pgvector queda en backlog para fase de escalabilidad.

## Por qué ChromaDB

- **Sin compilar**: pgvector en Windows requiere extensión compilada con MSVC. ChromaDB es pip install.
- **Embeddings locales**: genera embeddings internamente con sentence-transformers.
- **Filtros por metadatos**: soporta filtros por macrodominio, patología, nivel.
- **Persistencia**: `PersistentClient` guarda datos en disco.

## Interfaz

```python
from rag.vector_store import SeniorVitalVectorStore

store = SeniorVitalVectorStore(persist_directory="data/vector_store")

# Búsqueda general
results = store.search("ejercicio aeróbico", k=5)

# Búsqueda por agente (filtra macrodominio)
results = store.search_by_agent("dolor articular", agent_name="Physio-Evaluator")

# Búsqueda por macrodominio
results = store.search_by_macrodomain("nutrición", macrodomain="E")

# Búsqueda con filtros arbitrarios
results = store.search_by_filters("dieta", filters={"pathology": "diabetes"})

# CRUD
store.add_chunks(chunks, embeddings=embeddings)
store.upsert_chunks(chunks)
store.get_by_chunk_id("chunk-001")
store.delete_all()
store.count()
```

## Metadatos indexados

| Campo | Tipo | Descripción |
|---|---|---|
| `chunk_id` | str | ID único del chunk |
| `document_name` | str | Nombre del documento fuente |
| `macrodomain` | str | Letra A-F del dominio |
| `macrodomain_name` | str | Nombre del agente |
| `section_path` | str | Jerarquía de secciones |
| `chunk_type` | str | semantic / structural / fallback |
| `level` | str | principiante / intermedio / avanzado |
| `pathology` | str | Patología asociada |
| `keywords` | str | Coma-separadas |
| `char_count` | int | Caracteres |
| `word_count` | int | Palabras |

## Almacenamiento

```
data/vector_store/
├── chroma.sqlite3       # Base de datos SQLite
└── seniorvital_kb/      # Collection data
```

## Migración futura a pgvector

La interfaz `SeniorVitalVectorStore` está diseñada para ser reemplazable. Para migrar a pgvector:
1. Crear `pgvector_store.py` con la misma interfaz
2. Mantener el mismo patrón de métodos
3. No cambiar el retriever ni los scripts

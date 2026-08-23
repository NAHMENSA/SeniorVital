# Estrategia de Embeddings — SeniorVital RAG

## Objetivo

Transformar los chunks de la base de conocimiento de SeniorVital en representaciones vectoriales que puedan ser utilizadas posteriormente para búsqueda semántica y recuperación de información dentro del sistema RAG.

## Modelo seleccionado

| Atributo | Valor |
|---|---|
| Modelo | `intfloat/multilingual-e5-small` |
| Tipo | Sentence embeddings basado en transformers |
| Dimensión | 384 |
| Licencia / costo | Gratuito, descarga local desde HuggingFace |
| Idiomas | Multilingüe, incluido español |
| Framework | `langchain-huggingface` + `sentence-transformers` |

### Justificación

- **Local-first**: no requiere `OPENAI_API_KEY` ni llamadas a API externas, alineado con la filosofía de SeniorVital (Ollama + PostgreSQL + DuckDB local).
- **Rendimiento adecuado**: `multilingual-e5-small` ofrece buen balance entre calidad semántica, velocidad y uso de memoria en CPU.
- **Idioma**: entrena con textos multilingües, incluido español, que es el idioma principal del corpus.
- **Reutilización**: es el mismo modelo utilizado por `SemanticChunkerWrapper` durante la fase de chunking, lo que garantiza coherencia entre segmentación y recuperación.

## Formato de persistencia

Se utiliza persistencia plana (JSON + NumPy) para evitar dependencias adicionales de bases de datos vectoriales en esta fase.

### Archivos generados

```
data/processed/embeddings/<model_name_sanitizado>/
├── embeddings_metadata.json   # metadatos de cada chunk (sin el vector)
├── embeddings.npy               # matriz NumPy (n_chunks, dimension)
└── manifest.json                # resumen del modelo, dimensión y cantidad
```

### Ejemplo de manifest

```json
{
  "model": "intfloat/multilingual-e5-small",
  "dimension": 384,
  "chunk_count": 363,
  "chunk_source": "data/processed/chunks/all_chunks.json",
  "metadata_file": "embeddings_metadata.json",
  "vectors_file": "embeddings.npy"
}
```

## Componentes

| Componente | Ubicación | Responsabilidad |
|---|---|---|
| `EmbeddingGenerator` | `src/rag/embeddings/embedding_generator.py` | Cargar el modelo, generar embeddings para texto o chunks. |
| `save_embeddings` / `load_embeddings` | `src/rag/embeddings/persistence.py` | Persistir y cargar metadatos + vectores. |
| `generate_embeddings.py` | `scripts/ingestion/generate_embeddings.py` | Script CLI que genera embeddings para todo el corpus. |

## Uso

### Generar embeddings para todos los chunks

```bash
$env:PYTHONPATH = "src"
.venv_chunking\Scripts\python.exe scripts/ingestion/generate_embeddings.py
```

### Cargar embeddings desde otro script

```python
from pathlib import Path
from rag.embeddings import load_embeddings

output_dir = Path("data/processed/embeddings/intfloat_multilingual-e5-small")
metadata, vectors = load_embeddings(output_dir)
print(vectors.shape)  # (363, 384)
```

## Consideraciones de rendimiento

- El modelo se carga una sola vez por instancia de `EmbeddingGenerator` (lazy-loading).
- La generación por batch utiliza `embed_documents`, que internamente optimiza el paso por el modelo.
- En CPU, generar 363 embeddings de ~100 palabras tarda unos pocos minutos la primera vez; posteriores ejecuciones son más rápidas porque el modelo ya está cacheado localmente.

## Pruebas

- `tests/rag/test_embeddings.py` cubre:
  - Generación de embeddings individuales y por batch.
  - Enriquecimiento de chunks con vectores.
  - Persistencia y carga roundtrip.
  - Validación de dimensiones consistentes.
  - Manejo de entradas vacías y archivos faltantes.

## Próximos pasos

La siguiente fase (S1-04 / Fase 5) integrará estos embeddings con un retriever híbrido (búsqueda vectorial + filtros por macrodominio, nivel funcional y patología) y un pipeline RAG completo.

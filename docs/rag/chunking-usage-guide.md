# Guía de Uso — Chunking SeniorVital RAG

## Requisitos

- Python 3.12+
- Entorno virtual con dependencias de `requirements_chunking.txt`
- Modelo de embeddings local descargado automáticamente por HuggingFace (`intfloat/multilingual-e5-small`)

## Instalación

```bash
# Crear entorno virtual
python -m venv .venv_chunking

# Activar (Windows PowerShell)
.venv_chunking\Scripts\Activate.ps1

# Instalar dependencias
python -m pip install -r requirements_chunking.txt
```

No se requiere API key para ejecutar el chunking. El modelo se descarga una sola vez desde HuggingFace Hub.

## Ejecutar el chunking

Desde la raíz del proyecto:

```bash
# Windows PowerShell
$env:PYTHONPATH = "src"
.venv_chunking\Scripts\python.exe scripts/indexing/run_chunking.py
```

O con Bash:

```bash
export PYTHONPATH=src
.venv_chunking/bin/python scripts/indexing/run_chunking.py
```

## Qué genera

- `data/processed/chunks/<documento>.chunks.json` — chunks por documento.
- `data/processed/chunks/all_chunks.json` — todos los chunks consolidados.
- `data/processed/chunking_stats.json` — estadísticas del proceso.

## Añadir nuevos documentos a la KB

1. Colocar el archivo `.md` en `data/knowledge_base/`.
2. Actualizar el mapeo de macrodominios en `scripts/indexing/inventory_documents.py` (`MACRODOMAIN_MAP`).
3. Volver a ejecutar:
   - `scripts/indexing/inventory_documents.py` para actualizar el inventario.
   - `scripts/indexing/run_chunking.py` para regenerar los chunks.

## Ajustar parámetros

Editar `src/knowledge/chunking/chunking_orchestrator.py` o pasar parámetros al instanciar las clases:

| Parámetro | Descripción | Valor por defecto |
|---|---|---|
| `model_name` | Modelo de embeddings HuggingFace | `intfloat/multilingual-e5-small` |
| `breakpoint_threshold_type` | Criterio de segmentación semántica | `percentile` |
| `breakpoint_threshold_amount` | Percentil para corte semántico | `85` |
| `chunk_size` | Tamaño objetivo del fallback recursivo | `700` caracteres |
| `chunk_overlap` | Solapamiento del fallback | `80` caracteres |
| `min_chunk_size` | Tamaño mínimo aceptable | `500` caracteres |
| `max_chunk_size` | Tamaño máximo antes de forzar fallback | `800` caracteres |

## Solución de problemas comunes

### El chunking es lento

- La primera ejecución descarga el modelo (~400 MB). Ejecuciones posteriores usan cache.
- Considere usar `breakpoint_threshold_amount=90` para generar menos chunks por documento.

### Chunks demasiado pequeños

- Aumentar `breakpoint_threshold_amount` para que el `SemanticChunker` corte menos veces.
- Ajustar `min_chunk_size` y `merge_small_chunks` en el orquestador.

### Chunks demasiado grandes

- Disminuir `max_chunk_size`.
- Verificar que el fallback recursivo esté activo en `_post_process`.

### Documentos con encabezados no se detectan

- El preprocesador detecta encabezados Markdown (`#`, `##`, etc.). Si un documento usa otro formato, se procesará como semántico.

## Generar embeddings

Una vez generados los chunks, ejecutar:

```bash
# Windows PowerShell
$env:PYTHONPATH = "src"
.venv_chunking\Scripts\python.exe scripts/ingestion/generate_embeddings.py
```

O con Bash:

```bash
export PYTHONPATH=src
.venv_chunking/bin/python scripts/ingestion/generate_embeddings.py
```

### Qué genera

- `data/processed/embeddings/<modelo>/embeddings_metadata.json` — metadatos de cada chunk.
- `data/processed/embeddings/<modelo>/embeddings.npy` — matriz NumPy con los vectores.
- `data/processed/embeddings/<modelo>/manifest.json` — resumen del modelo, dimensión y cantidad de chunks.

## Pruebas

```bash
$env:PYTHONPATH = "src"
.venv_chunking\Scripts\python.exe -m pytest tests/rag/test_chunking.py tests/rag/test_embeddings.py -v -m "not slow"
```

## Próximos pasos

- Integrar con retriever híbrido y pipeline RAG: Fase 5 del plan.

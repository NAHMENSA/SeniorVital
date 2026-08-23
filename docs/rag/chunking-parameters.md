# Parámetros de Chunking — SeniorVital RAG

## Parámetros Generales

| Parámetro | Valor | Descripción |
|---|---|---|
| `chunk_size` | 1500 | Tamaño objetivo de chunk en caracteres (aproximadamente). |
| `chunk_overlap` | 200 | Solapamiento entre chunks consecutivos en caracteres. |
| `min_chunk_size` | 200 | Tamaño mínimo aceptable de chunk en caracteres. |
| `max_chunk_size` | 3000 | Tamaño máximo aceptable de chunk en caracteres antes de forzar fallback. |
| `embedding_model` | `text-embedding-3-small` | Modelo de embeddings para `SemanticChunker`. |
| `breakpoint_threshold_type` | `percentile` | Criterio de segmentación semántica. |

## Parámetros por Estrategia

### Chunking Semántico (`SemanticChunker`)

| Parámetro | Valor | Justificación |
|---|---|---|
| `embeddings` | `OpenAIEmbeddings(model="text-embedding-3-small")` | Buen balance entre calidad y costo. |
| `breakpoint_threshold_type` | `percentile` | Útil cuando hay variabilidad en longitud de párrafos. |
| `breakpoint_threshold_amount` | 80 | Percentil alto para generar chunks más grandes y coherentes. |
| `number_of_chunks` | `None` | Dejar que el algoritmo determine la cantidad según el contenido. |

### Chunking Estructural (`MarkdownHeaderTextSplitter`)

| Parámetro | Valor | Justificación |
|---|---|---|
| `headers_to_split_on` | `[("#", "Header 1"), ("##", "Header 2"), ("###", "Header 3")]` | Captura tres niveles de jerarquía del documento principal. |
| `strip_headers` | `False` | Preservar los encabezados en el contenido del chunk para contexto. |

### Chunking de Respaldo (`RecursiveCharacterTextSplitter`)

| Parámetro | Valor | Justificación |
|---|---|---|
| `chunk_size` | 1500 | Tamaño objetivo en caracteres. |
| `chunk_overlap` | 200 | Solapamiento para preservar contexto entre chunks. |
| `separators` | `["\n\n", "\n", ". ", " ", ""]` | Prioriza separar por párrafos, luego oraciones. |

## Selección de Estrategia por Tipo de Documento

| Condición del Documento | Estrategia Seleccionada | Parámetros Aplicados |
|---|---|---|
| `has_markdown_headers == true` | Estructural | `MarkdownHeaderTextSplitter` con 3 niveles de headers. |
| `has_markdown_headers == false` y `word_count >= 500` | Semántica | `SemanticChunker` con `percentile=80`. |
| `has_markdown_headers == false` y `word_count < 500` | Respaldo recursivo | `RecursiveCharacterTextSplitter` con 1500/200. |
| Chunks generados exceden `max_chunk_size` | Respaldo recursivo | Aplicar a chunks demasiado grandes. |

## Ajustes por Entorno

### Desarrollo

- Usar `text-embedding-3-small` para reducir costos.
- Límite de tokens bajo para pruebas rápidas.
- Logging detallado del proceso.

### Producción

- Evaluar `text-embedding-3-large` si la calidad de recuperación lo justifica.
- Ajustar `breakpoint_threshold_amount` según resultados de evaluación.
- Considerar cacheo de embeddings para documentos ya procesados.

## Variables de Entorno

| Variable | Requerida | Descripción |
|---|---|---|
| `OPENAI_API_KEY` | Sí (para chunking semántico) | API key de OpenAI para generar embeddings. |
| `CHUNKING_LOG_LEVEL` | No | Nivel de logging (default: `INFO`). |

## Notas

- Los valores están en **caracteres** porque los documentos son en español y el tokenizador puede variar. Como referencia aproximada, 1500 caracteres ≈ 300-500 tokens.
- El valor de `breakpoint_threshold_amount` debe validarse en la Fase 3 con pruebas comparativas.

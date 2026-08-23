# Reporte Sprint 2 — Implementación de Chunking para RAG SeniorVital

## Resumen Ejecutivo

Se implementó una estrategia de chunking híbrida para la base de conocimiento de SeniorVital, generando **363 chunks** a partir de **19 documentos** con metadatos enriquecidos. La estrategia prioriza el chunking semántico usando embeddings locales gratuitos, complementado con chunking estructural para el único documento con encabezados Markdown y fallback recursivo para documentos cortos.

## Alcance completado

### Fase 0: Análisis y Preparación

- ✅ Inventario de documentos: `data/processed/document_inventory.json`
- ✅ Análisis de estructura: `docs/rag/document-structure-analysis.md`
- ✅ Criterios de éxito: `docs/rag/chunking-success-criteria.md`

### Fase 1: Diseño de la Estrategia

- ✅ Estrategia de chunking: `docs/rag/chunking-strategy.md`
- ✅ Parámetros configurables: `docs/rag/chunking-parameters.md`
- ✅ Esquema de metadatos: `docs/rag/chunking-metadata-schema.md`

### Fase 2: Implementación

- ✅ `requirements_chunking.txt` con dependencias locales (HuggingFace).
- ✅ Módulos de chunking:
  - `src/knowledge/chunking/preprocessor.py`
  - `src/knowledge/chunking/structural_chunker.py`
  - `src/knowledge/chunking/semantic_chunker.py`
  - `src/knowledge/chunking/fallback_chunker.py`
  - `src/knowledge/chunking/chunking_orchestrator.py`
  - `src/knowledge/chunking/__init__.py`
- ✅ Script de ejecución: `scripts/indexing/run_chunking.py`
- ✅ Script de inventario: `scripts/indexing/inventory_documents.py`
- ✅ Chunks generados y estadísticas:
  - `data/processed/chunks/`
  - `data/processed/chunking_stats.json`

### Fase 4: Documentación y Entrega

- ✅ Ejemplos de chunks: `docs/rag/chunking-examples.md`
- ✅ Guía de uso: `docs/rag/chunking-usage-guide.md`
- ✅ Reporte de sprint: este documento

## Estadísticas de salida

| Métrica | Valor |
|---|---|---|
| Documentos procesados | 19 |
| Chunks totales | 363 |
| Chunks semánticos | 148 |
| Chunks estructurales | 3 |
| Chunks fallback | 212 |
| Tamaño promedio | 666 caracteres / 101 palabras |
| Chunks en rango 80-120 palabras | 70.0 % |
| Chunks en rango 500-800 caracteres | 71.9 % |
| Tiempo de ejecución | < 5 minutos (modelo ya descargado) |

## Bug crítico corregido

Se detectó un bug en `ChunkingOrchestrator._merge_small_chunks` que inicializaba la lista de chunks a fusionar únicamente con el primer chunk, descartando todo el resto del documento. Esto generaba **19 chunks** (uno por documento) con un promedio de ~68 palabras y pérdida masiva de contenido. La corrección consiste en copiar todos los chunks al iniciar el merge y cambiar el criterio a palabras (`< 80`) con un límite combinado de 1,000 caracteres.


## Hallazgos clave

1. **Solo 1 documento tiene encabezados Markdown**: la estrategia estructural original no podía ser primaria. Se adaptó a semántica primaria.
2. **13 documentos estaban envueltos en bloques de código ```**: se implementó un preprocesador que elimina fences y normaliza el texto.
3. **Embeddings locales funcionan sin API key**: `intfloat/multilingual-e5-small` se descarga automáticamente y es compatible con el español.

## Lecciones aprendidas

- El análisis previo del corpus es crítico: asumir que todos los documentos tienen encabezados habría generado una implementación incorrecta.
- Los chunks pequeños (~84 palabras) son adecuados para recuperación RAG, aunque menores al límite inicial de 200 tokens.
- El fallback recursivo es esencial para documentos cortos que no justifican chunking semántico.

## Pendientes para la siguiente sesión

### Fase 3: Pruebas y Optimización

- ✅ Implementar `tests/rag/test_chunking.py` con pruebas unitarias (20 tests, todos pasan).
- Implementar `tests/rag/test_chunking_comparison.py` para comparar estrategias.
- Ejecutar grid search sobre `breakpoint_threshold_amount`.
- ✅ Generar `docs/rag/chunking-comparison-results.md`.
- Generar `docs/rag/chunking-optimal-parameters.md`.
- Crear `scripts/evaluation/evaluate_chunking.py` con queries de SeniorVital.

### Fase 5: Integración con Pipeline RAG

- Implementar generador de embeddings: `src/rag/embeddings/embedding_generator.py`.
- Implementar retriever híbrido: `src/rag/retriever/hybrid_retriever.py`.
- Implementar reranker: `src/rag/retriever/reranker.py`.
- Implementar pipeline RAG completo: `src/rag/pipeline/rag_pipeline.py`.
- Crear script de indexación: `scripts/ingestion/index_knowledge_base.py`.

## Archivos relevantes

- `data/processed/chunks/all_chunks.json`
- `data/processed/chunking_stats.json`
- `data/processed/document_inventory.json`
- `src/knowledge/chunking/`
- `scripts/indexing/run_chunking.py`
- `docs/rag/`
- `requirements_chunking.txt`

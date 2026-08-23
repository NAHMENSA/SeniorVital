# Task Plan: SeniorVital RAG — Chunking y Embeddings

## Goal

Implementar las fases S1-02 (chunking) y S1-03 (generación de embeddings) para la base de conocimiento de SeniorVital, generando chunks con metadatos, representaciones vectoriales y tests, documentando las decisiones para su uso dentro de la pipeline RAG.

## Current Phase

S1-06 completado. Framework de evaluación RAG implementado (métricas, runner, tests). Evaluación parcial ejecutada (5/30 queries).

## Phases

### Phase 1: Fase 0 — Análisis y Preparación

- [x] Inventariar documentos en `data/knowledge_base/`
- [x] Analizar estructura semántica de cada documento y macrodominio
- [x] Identificar patrones que requieran tratamiento especial
- [x] Definir criterios de éxito para la segmentación
- [x] Generar `data/processed/document_inventory.json`
- **Status:** complete

### Phase 2: Fase 1 — Diseño de la Estrategia de Chunking

- [x] Diseñar estrategia híbrida (MarkdownHeaderTextSplitter + SemanticChunker)
- [x] Definir esquema de metadatos completo por chunk
- [x] Definir estrategias para casos especiales (tablas, listas, notas contextuales)
- [x] Crear documentación en `docs/rag/`
- **Status:** complete

### Phase 3: Fase 2 — Implementación del Chunking

- [x] Crear `requirements_chunking.txt` (usando embeddings locales HuggingFace)
- [x] Implementar `StructuralChunker` en `src/knowledge/chunking/structural_chunker.py`
- [x] Implementar `SemanticChunker` en `src/knowledge/chunking/semantic_chunker.py`
- [x] Implementar `FallbackChunker` en `src/knowledge/chunking/fallback_chunker.py`
- [x] Implementar `ChunkingOrchestrator` en `src/knowledge/chunking/chunking_orchestrator.py`
- [x] Crear script `scripts/indexing/run_chunking.py`
- [x] Ejecutar chunking y generar chunks en `data/processed/chunks/`
- **Status:** complete

### Phase 4: Fase 3 — Pruebas y Optimización de Chunking

- [x] Crear `tests/rag/test_chunking.py` con pruebas unitarias (20 tests)
- [x] Ejecutar pruebas y documentar resultados
- [x] Generar `docs/rag/chunking-comparison-results.md`
- [ ] Crear `tests/rag/test_chunking_comparison.py` con pruebas comparativas
- [ ] Generar `docs/rag/chunking-optimal-parameters.md` (grid search de `breakpoint_threshold_amount`)
- **Status:** mostly complete

### Phase 5: Fase 4 — Documentación y Entrega de Chunking

- [x] Actualizar `docs/rag/chunking-strategy.md` (creado en Fase 1, actualizado con resultados)
- [x] Crear `docs/rag/chunking-examples.md`
- [x] Crear `docs/rag/chunking-usage-guide.md`
- [x] Crear `docs/reports/sprint-2-chunking-report.md`
- **Status:** complete

### Phase 6: S1-03 — Generación de Embeddings

- [x] Crear `src/rag/embeddings/embedding_generator.py` (`EmbeddingGenerator`)
- [x] Crear `src/rag/embeddings/persistence.py` (`save_embeddings` / `load_embeddings`, JSON + NumPy)
- [x] Crear `src/rag/embeddings/__init__.py`
- [x] Crear `scripts/ingestion/generate_embeddings.py`
- [x] Crear `tests/rag/test_embeddings.py` (12 tests)
- [x] Ejecutar generación de embeddings para 363 chunks
- [x] Completar `docs/rag/embeddings-strategy.md`
- [x] Crear `docs/reports/sprint-3-embeddings-report.md`
- **Status:** complete

### Phase 7: S1-04 — Vector Store & Retriever

- [x] Instalar ChromaDB en `.venv_chunking`
- [x] Implementar `src/rag/vector_store/chroma_store.py` (`SeniorVitalVectorStore`)
- [x] Crear `src/rag/vector_store/__init__.py`
- [x] Implementar `src/rag/retriever/retriever.py` (`SeniorVitalRetriever`)
- [x] Crear `scripts/ingestion/index_knowledge_base.py`
- [x] Crear `tests/rag/test_vector_store.py` (20 tests)
- [x] Ejecutar indexación: 363 chunks en ChromaDB
- [x] Validar búsqueda con 3 queries
- [x] Completar `docs/rag/vector-database.md` y `docs/rag/retrieval-pipeline.md`
- [x] Crear `docs/reports/sprint-4-vector-store-report.md`
- [x] Fix: `tests/rag/conftest.py` path corregido
- [x] Fix: `IncludeEnum` removido (ChromaDB 1.5.x)
- **Status:** complete

### Phase 8: S1-05 — Pipeline RAG Completo

- [x] Crear `src/rag/__init__.py` (package init)
- [x] Crear `src/rag/generation/__init__.py` con exports
- [x] Crear `src/rag/pipeline/__init__.py`
- [x] Implementar `src/rag/generation/ollama_client.py` (`OllamaClient`)
- [x] Implementar `src/rag/generation/prompt_builder.py` (`PromptBuilder`, 6 agentes)
- [x] Implementar `src/rag/generation/response_parser.py` (`ResponseParser`)
- [x] Implementar `src/rag/generation/generator.py` (`RAGGenerator`)
- [x] Implementar `src/rag/pipeline/query_processor.py` (`QueryProcessor`)
- [x] Implementar `src/rag/pipeline/context_assembler.py` (`ContextAssembler`)
- [x] Implementar `src/rag/pipeline/query_pipeline.py` (`SeniorVitalRAGPipeline`)
- [x] Crear tests: test_ollama_client, test_prompt_builder, test_response_parser, test_query_processor, test_context_assembler, test_generator, test_rag_pipeline
- [x] 123/123 tests pasando (suite RAG completa)
- [x] Fix: ContextAssembler truncación con presupuesto negativo
- [x] Fix: rag.generation.__init__.py exports
- [x] Fix: pytest-asyncio instalado en .venv_chunking
- [x] Completar `docs/rag/pipeline-architecture.md`
- [x] Crear `docs/reports/sprint-5-rag-pipeline-report.md`
- **Status:** complete

### Phase 10: S1-06 — Evaluación de Recuperación y Calidad

- [x] Crear query set con ground truth (`data/evaluation/test_queries.json`, 30 queries)
- [x] Implementar métricas de recuperación (`src/rag/evaluation/metrics.py`)
- [x] Implementar métricas de calidad (`src/rag/evaluation/quality.py`)
- [x] Crear runner de evaluación (`src/rag/evaluation/runner.py`)
- [x] Crear script CLI (`scripts/evaluation/run_evaluation.py`)
- [x] Tests del framework de evaluación (`tests/rag/test_evaluation.py`, 42 tests)
- [x] Ejecutar evaluación parcial (5/30 queries due to Ollama latency)
- [x] Documentar resultados en `docs/evaluation/`
- [x] Crear informe consolidado en `docs/rag/rag-evaluation.md`
- **Status:** complete
- **Note:** Evaluación completa (30 queries) requiere Ollama con timeout extendido (~300s/query)

## Key Questions

1. ✅ Se encontraron 19 documentos (no 18); mapeo a macrodominios en `data/processed/document_inventory.json`.
2. ✅ Solo 1 documento (`DOCUMENTO DE CONOCIMIENTO SENIORVITAL.md`) tiene encabezados Markdown; la estrategia se adaptó a semántico primario.
3. ✅ No se requiere `OPENAI_API_KEY`; se usaron embeddings locales gratuitos (`intfloat/multilingual-e5-small` vía HuggingFace).
4. ✅ El chunking generó chunks promedio de ~84 palabras (~556 caracteres), adecuados para recuperación RAG.

## Decisions Made

| Decision | Rationale |
|----------|-----------|
| Chunking híbrido (semántico + estructural + recursivo) | La mayoría de los documentos son texto plano o están en bloques de código; el chunking semántico es el más robusto, el estructural se usa para el documento con encabezados, y el recursivo actúa como fallback. |
| SemanticChunker como estrategia primaria | Agrupa párrafos por similitud semántica, lo cual funciona para los 18 documentos sin encabezados claros. |
| MarkdownHeaderTextSplitter como estrategia secundaria | Solo `DOCUMENTO DE CONOCIMIENTO SENIORVITAL.md` tiene encabezados Markdown claros; se usa chunking estructural para preservar su jerarquía. |
| Fallback con RecursiveCharacterTextSplitter | Garantiza que documentos pequeños, sin estructura o con secciones demasiado grandes también sean procesados. |
| Metadatos enriquecidos por chunk | Necesario para que el retriever filtre por agente, macrodominio, nivel funcional y patología. |
| Embeddings locales gratuitos (HuggingFace) | No requiere `OPENAI_API_KEY`; alinea con filosofía local-first de SeniorVital. |
| ChromaDB como vector store local | pgvector requiere compilar extensión en Windows; ChromaDB es pip install y funciona directamente. |
| Interfaz modular SeniorVitalVectorStore | Diseñada para ser reemplazable (pgvector futuro) sin cambiar el retriever ni scripts. |
| OllamaClient con fallback localhost→127.0.0.1 | Patrón existente en routines-ai-service, robusto ante cambios de configuración. |
| QueryProcessor por keywords | Simple, sin dependencias externas, 6 dominios bien definidos con 17 keywords c/u. |
| System prompts por agente | Cada agente tiene rol, expertise y formato de respuesta único en español latinoamericano. |
| ContextAssembler con truncación por tokens | Ventana de 4096 de phi3:mini requiere gestión inteligente del contexto. |

## Errors Encountered

| Error | Attempt | Resolution |
|-------|---------|------------|
| `conftest.py` path build `tests/src` en vez de `src/` | 1 | Corregido: 3 niveles de `dirname` en vez de 2 |
| ChromaDB 1.5.x: `IncludeEnum` no exportado | 1 | Usar strings (`"documents"`, `"metadatas"`, `"distances"`) en `include=` |
| `ContextAssembler` retornaba lista vacía con chunk grande | 1 | Siempre incluir al menos el primer chunk truncado |
| `rag.generation.__init__.py` sin exports | 1 | Agregados OllamaClient, PromptBuilder, ResponseParser, RAGGenerator |
| `pytest-asyncio` no reconocido | 1 | Instalado en `.venv_chunking` |

## Notes

- Este plan cubre Fases 0-4 (S1-02) y S1-03 en esta sesión. La Fase 5 (integración completa con retriever híbrido y pipeline RAG) queda como siguiente paso.
- La estructura de directorios debe respetar `directorioSeniorVital.txt`.
- Los documentos con tablas deben convertirse a texto estructurado antes de chunking para no perder información.
- **Hallazgo de Fase 0:** Solo 1 documento tiene encabezados Markdown. Se adapta la estrategia: semántico primario, estructural secundario, recursivo fallback.

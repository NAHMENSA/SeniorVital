# Sprint S1-05 — Pipeline RAG Completo

**Fecha**: 2026-08-22
**Estado**: COMPLETADO

## Resumen

Implementación del pipeline RAG completo: query → procesamiento → recuperación → contexto → generación con LLM.

## Archivos creados

### Código — `src/rag/generation/`

| Archivo | Descripción |
|---|---|
| `__init__.py` | Package init con exports |
| `ollama_client.py` | Cliente HTTP async para Ollama (patrón routines-ai-service) |
| `prompt_builder.py` | 6 plantillas de system prompt por agente + formateo de contexto |
| `response_parser.py` | Limpieza, extracción de warnings, parseo JSON |
| `generator.py` | Orquesta prompt→Ollama→parseo |

### Código — `src/rag/pipeline/`

| Archivo | Descripción |
|---|---|
| `__init__.py` | Package init |
| `query_processor.py` | Normalización, detección de macrodominio por keywords |
| `context_assembler.py` | Deduplicación, truncación por ventana de tokens |
| `query_pipeline.py` | `SeniorVitalRAGPipeline` — clase orquestadora principal |

### Código — raíz

| Archivo | Descripción |
|---|---|
| `src/rag/__init__.py` | Package init del paquete RAG |

### Tests

| Archivo | Tests |
|---|---|
| `tests/rag/test_ollama_client.py` | 11 tests (init, URLs, generate, health check) |
| `tests/rag/test_prompt_builder.py` | 12 tests (system prompts, build, context format) |
| `tests/rag/test_response_parser.py` | 10 tests (parse, clean, warnings, JSON) |
| `tests/rag/test_query_processor.py` | 14 tests (normalize, detect, process) |
| `tests/rag/test_context_assembler.py` | 11 tests (dedup, truncate, format) |
| `tests/rag/test_generator.py` | 4 tests (generate, mock Ollama) |
| `tests/rag/test_rag_pipeline.py` | 8 tests (integración pipeline completo) |

**Total nuevos tests**: 70
**Suite RAG completa**: 123 tests (todos pasando)

### Documentación

| Archivo | Contenido |
|---|---|
| `docs/rag/pipeline-architecture.md` | Arquitectura, flujo, componentes, uso |
| `docs/reports/sprint-5-rag-pipeline-report.md` | Este reporte |

## Bugs corregidos

| Bug | Fix |
|---|---|
| `ContextAssembler` retornaba lista vacía cuando el primer chunk excedía el presupuesto | Ahora siempre incluye al menos el primer chunk truncado |
| `rag.generation.__init__.py` no exportaba clases | Agregados exports de OllamaClient, PromptBuilder, ResponseParser, RAGGenerator |
| `pytest-asyncio` no instalado en `.venv_chunking` | Instalado `pytest-asyncio==1.4.0` |

## Decisiones técnicas

| Decisión | Rationale |
|---|---|
| Mantener `intfloat/multilingual-e5-small` | Ya integrado, 363 chunks indexados, funciona bien |
| OllamaClient con fallback localhost→127.0.0.1 | Patrón existente en routines-ai-service |
| QueryProcessor por keywords | Simple, sin dependencias externas, 6 dominios bien definidos |
| ContextAssembler con truncación por tokens | Ventana de 4096 de phi3:mini requiere gestión inteligente |
| System prompts por agente | Cada agente tiene rol, expertise y formato de respuesta único |

## Criterios de aceptación cumplidos

- [x] El sistema recibe una consulta y genera su representación vectorial
- [x] La consulta recupera información relevante desde ChromaDB
- [x] El contexto recuperado es utilizado por el LLM para generar la respuesta
- [x] El pipeline puede ejecutarse de principio a fin (mock Ollama en tests)
- [x] Las respuestas utilizan información de la base de conocimiento
- [x] Código y documentación disponibles en el repositorio

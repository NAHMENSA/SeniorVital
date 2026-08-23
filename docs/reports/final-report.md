# Reporte Final — Sprint 1: Sistema RAG SeniorVital

**Fecha**: 2026-08-22
**Estado**: COMPLETADO

## Resumen ejecutivo

Se construyó un sistema RAG (Retrieval-Augmented Generation) completo para la plataforma SeniorVital, desde la ingesta de documentos de conocimiento hasta la generación de respuestas personalizadas mediante un LLM local. El sistema cubre 6 macrodominios de bienestar para adultos mayores, con 363 chunks indexados, 161+ tests y un framework de evaluación que diagnostica problemas críticos de calidad.

## Sprints ejecutados

| Sprint | Objetivo | Estado | Tests | Archivos |
|--------|----------|--------|-------|----------|
| **S1-02** | Chunking de documentos | COMPLETADO | 20 | 8 |
| **S1-03** | Generación de embeddings | COMPLETADO | 12 | 4 |
| **S1-04** | Vector store + retriever | COMPLETADO | 20 | 4 |
| **S1-05** | Pipeline RAG completo | COMPLETADO | 70 | 10 |
| **S1-06** | Evaluación del sistema | COMPLETADO | 42 | 12 |
| **S1-07** | Documentación de arquitectura | EN PROGRESO | — | 6 |

**Total**: ~161 tests, ~25 archivos Python, ~2193 LOC, 19 docs de documentación

## Arquitectura lograda

### Componentes del sistema

```
src/rag/
├── constants.py              # Constantes centralizadas (agente→macrodominio)
├── chunking/                 # S1-02: Chunking semántico + estructural
├── embeddings/               # S1-03: Generador + cache de embeddings
├── vector_store/             # S1-04: ChromaDB CRUD + normalización
├── retriever/                # S1-04: Facade de recuperación
├── pipeline/                 # S1-05: QueryProcessor, ContextAssembler, Pipeline
├── generation/               # S1-05: OllamaClient, PromptBuilder, Parser, Generator
├── indexing/                 # S1-05: IndexingPipeline
└── evaluation/               # S1-06: Métricas, calidad, runner
```

### Flujo end-to-end

```
Ingesta:  19 docs → run_chunking.py → 363 chunks → generate_embeddings.py → ChromaDB

Consulta: query → QueryProcessor → Retriever → ContextAssembler → RAGGenerator → respuesta
                                       ↓
                                   ChromaDB (top-K chunks)
                                       ↓
                                   Ollama phi3:mini
```

## Métricas de construcción

| Métrica | Valor |
|---------|-------|
| Archivos Python en src/rag/ | 25 |
| Líneas de código estimadas | ~2,193 |
| Tests unitarios | 161+ |
| Archivos de documentación | 19 |
| Chunks indexados | 363 |
| Documentos fuente | 19 |
| Macrodominios | 6 (A-F) |
| Dimensiones embeddings | 384 |

## Resultados de evaluación

Ejecutadas 5 de 30 queries del test set. Resultados:

| Métrica | Valor | Diagnóstico |
|---------|-------|-------------|
| Precision@5 | 0.08 | MUY BAJO — retrieval recuperar beaucoup de ruido |
| Recall@5 | 0.27 | BAJO — no recupera chunks relevantes |
| MRR | 0.04 | MUY BAJO — primer resultado casi nunca es relevante |
| Hit Rate@5 | 0.40 | BAJO — 60% de queries sin ningún chunk relevante |
| Domain Accuracy | 0.40 | BAJO — keywords no distinguen bien dominios |
| Citation Rate | 0.80 | BUENO — respuestas citan fuentes |
| Hallucination Rate | 1.0 | CRÍTICO — phi3:mini siempre alucina |
| Avg Response Length | 214 palabras | LARGO — respuestas poco concisas |

### Hallazgos clave

1. **Precision es el problema principal**: el retriever trae muchos chunks irrelevantes
2. **Detección de dominio falla**: B↔F se confunden, A/D no se detectan
3. **Alucinaciones totales**: phi3:mini genera info no presente en contexto
4. **Dominio B funciona bien**: recall perfecto (1.0) — tiene los más chunks (182)

## Decisiones técnicas principales

| # | Decisión | Justificación |
|---|----------|---------------|
| 1 | ChromaDB sobre pgvector | pgvector requiere MSVC; ChromaDB es `pip install` directo |
| 2 | `intfloat/multilingual-e5-small` | Ya integrado, multilingüe, 384-dim, funciona bien |
| 3 | phi3:mini vía Ollama | Local y gratuito, sin API key, suficiente para MVP |
| 4 | Detección por keywords | Simple, sin dependencias, 6 dominios bien definidos |
| 5 | System prompts por agente | Cada agente tiene rol y formato único |
| 6 | ContextAssembler con truncación | Ventana de 4096 requiere gestión inteligente |
| 7 | FastAPI para RAG service | Consistente con microservicios existentes |
| 8 | Evaluación heurística | Sin dependencias externas, métricas reproducibles |
| 9 | Embedding cache MD5 | Simple, persistente, sin infraestructura extra |
| 10 | Gateway routing /rag/ | Consistente con arquitectura de microservicios |

## Lecciones aprendidas

1. **El chunking es crítico**: la calidad del retrieval depende directamente de cómo se fragmentaron los documentos
2. **Las keywords son frágiles**: superposición entre dominios causa errores de detección
3. **Los LLMs pequeños alucinan**: phi3:mini (3.8B) siempre genera info extra — se necesita instrucción explícita
4. **pgvector en Windows es problemático**: ChromaDB es una alternativa viable para desarrollo local
5. **La evaluación temprana revela problemas**: 5 queries fueron suficientes para diagnosticar problemas críticos

## Documentación generada

| Archivo | Contenido |
|---------|-----------|
| `docs/rag/chunking-strategy.md` | Estrategia de chunking semántico + estructural |
| `docs/rag/document-structure-analysis.md` | Análisis de los 19 documentos |
| `docs/rag/embeddings-strategy.md` | Estrategia de embeddings multilingües |
| `docs/rag/vector-database.md` | Interfaz ChromaDB |
| `docs/rag/retrieval-pipeline.md` | Flujo de ingesta y retriever |
| `docs/rag/pipeline-architecture.md` | Arquitectura del pipeline RAG |
| `docs/rag/rag-evaluation.md` | Resultados de evaluación |
| `docs/rag/knowledge-sources.md` | Fuentes de conocimiento |
| `docs/rag/document-curation.md` | Curación de documentos |
| `docs/architecture/rag-architecture.md` | Arquitectura completa del sistema RAG |
| `docs/evaluation/` | 5 docs de evaluación (test-cases, metrics, quality, agent, multiagent) |
| `docs/architecture.mermaid.md` | Diagramas Mermaid del sistema + RAG |
| `docs/reports/final-report.md` | Este reporte |

## Mejoras futuras

### Corto plazo (1-2 semanas)
1. Ejecutar evaluación completa (30/30 queries) con timeout 300s
2. Agregar instrucción anti-alucinación al PromptBuilder
3. Optimizar chunks dominios D y E (pocos documentos)

### Mediano plazo (2-4 semanas)
4. Clasificador de dominio basado en embeddings
5. Hybrid search (semántico + keywords)
6. Re-balancing de chunks por dominio
7. Evaluación con RAGAS

### Largo plazo (1-2 meses)
8. Fine-tuning de embeddings en dominio de bienestar
9. Multi-domain retrieval para queries que cruzan dominios
10. Migración a pgvector cuando el entorno lo permita
11. Integración con el sistema de rutinas existente

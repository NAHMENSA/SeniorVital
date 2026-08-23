# Pipeline RAG — Arquitectura

## Flujo completo

```
Usuario
  │
  ▼
SeniorVitalRAGPipeline.process_query(query, agent_name=?, macrodomain=?)
  │
  ├─ 1. QueryProcessor.process()
  │     → normaliza texto
  │     → detecta macrodominio (A-F) por keywords
  │     → resuelve agente ↔ macrodominio
  │
  ├─ 2. Retriever.retrieve[_for_agent / _with_filters]()
  │     → SeniorVitalVectorStore.search()
  │     → ChromaDB: embedding query → top-K chunks con metadatos
  │
  ├─ 3. ContextAssembler.assemble()
  │     → deduplica chunks
  │     → trunca por ventana de tokens (4096)
  │     → formatea contexto legible
  │
  ├─ 4. RAGGenerator.generate()
  │     ├─ PromptBuilder.build()
  │     │   → system prompt del agente + user prompt con contexto
  │     ├─ OllamaClient.generate()
  │     │   → POST http://localhost:11434/api/generate (phi3:mini)
  │     └─ ResponseParser.parse()
  │         → extrae answer, warnings, sources
  │
  ▼
Respuesta estructurada
  {
    "answer": str,
    "sources": [...],
    "agent": str,
    "macrodomain": str,
    "warnings": [...],
    "query_info": {...}
  }
```

## Componentes

### `src/rag/pipeline/query_processor.py` — QueryProcessor
- Normalización: lowercase, colapsa whitespace
- Detección de macrodominio por keywords (17 keywords × 6 dominios)
- Resolución automática agente ↔ macrodominio

### `src/rag/pipeline/context_assembler.py` — ContextAssembler
- Deduplicación por contenido (first 200 chars)
- Truncación por presupuesto de tokens (4096 - 300 overhead)
- Incluye siempre al menos el primer chunk (truncado si es necesario)

### `src/rag/generation/ollama_client.py` — OllamaClient
- HTTP async via `httpx` (patrón de `routines-ai-service`)
- Fallback: localhost → 127.0.0.1
- Soporte streaming y no-streaming
- Health check contra `/api/tags`

### `src/rag/generation/prompt_builder.py` — PromptBuilder
- 6 system prompts especializados por agente
- Formatea contexto recuperado con fuentes
- Instrucciones de respuesta (basado en evidencia, citar fuentes, advertencias)

### `src/rag/generation/response_parser.py` — ResponseParser
- Limpieza de markdown fences
- Extracción de advertencias de seguridad (regex)
- Parseo de JSON embebido en respuestas

### `src/rag/generation/generator.py` — RAGGenerator
- Orquesta: PromptBuilder → OllamaClient → ResponseParser

### `src/rag/pipeline/query_pipeline.py` — SeniorVitalRAGPipeline
- Clase principal: `process_query()` orquesta todo el flujo
- `health_check()` verifica Ollama + vector store
- Inyección de dependencias para testing

## Tecnologías y modelos

| Capa | Tecnología | Propósito |
|------|-----------|-----------|
| **Vector Store** | ChromaDB (PersistentClient) | Búsqueda por cosine similarity, persistencia local |
| **Embeddings** | `intfloat/multilingual-e5-small` (384-dim) | Representación vectorial multilingüe |
| **LLM** | Ollama `phi3:mini` (3.8B params) | Generación de respuestas en español LATAM |
| **HTTP Client** | httpx (async) | Comunicación con Ollama API |
| **Framework** | FastAPI + Pydantic | Servicio HTTP con validación automática |

## Decisiones técnicas

| Decisión | Alternativa descartada | Justificación |
|----------|----------------------|---------------|
| ChromaDB sobre pgvector | pgvector requiere MSVC en Windows | ChromaDB funciona directamente con `pip install` |
| Keywords para detección de dominio | Clasificador basado en embeddings | Simple, sin dependencias, 6 dominios bien definidos |
| Truncación por tokens | Lost-in-the-middle | Ventana de 4096 de phi3:mini requiere gestión inteligente |
| System prompts por agente | Prompt único genérico | Cada agente tiene expertise y formato único |

## Datos y estadísticas

| Métrica | Valor |
|---------|-------|
| Documentos fuente | 19 archivos Markdown |
| Chunks totales | 363 |
| Tamaño promedio chunk | ~101 palabras (~666 caracteres) |
| Dimensión embeddings | 384 |
| Macrodominios | 6 (A-F) |
| Chunks por dominio | A:35, B:182, C:23, D:9, E:13, F:101 |

## Limitaciones conocidas

- **Precision@5 baja (0.08)**: Solo 8% de chunks recuperados son relevantes
- **Detección de dominio imperfecta (40%)**: Keywords se superponen entre dominios
- **Alucinaciones (100%)**: phi3:mini genera info no presente en contexto
- **Latencia alta (100-500s/query)**: Ollama lento en hardware limitado

## Uso

```python
from rag.pipeline import SeniorVitalRAGPipeline

pipeline = SeniorVitalRAGPipeline(persist_directory="data/vector_store")

# Query automática (detecta agente)
result = await pipeline.process_query("¿Qué ejercicios de fuerza son seguros?")

# Query dirigida a un agente
result = await pipeline.process_query(
    "¿Cuáles son los criterios de sarcopenia?",
    agent_name="Physio-Evaluator",
)

# Query con filtros
result = await pipeline.process_query(
    "dieta para diabeticos",
    macrodomain="E",
    filters={"level": "principiante"},
)
```

## Datos

- 363 chunks indexados en ChromaDB
- 6 macrodominios: A (Physio), B (Exercise), C (Context), D (Safety), E (Nutri), F (Mind)
- Modelo embeddings: `intfloat/multilingual-e5-small` (384-dim)
- LLM: `phi3:mini` via Ollama (local, gratuito)

# Arquitectura de SeniorVital — Diagrama Mermaid

Este archivo contiene el diagrama de arquitectura del sistema en formato
[Mermaid](https://mermaid.js.org/). Puedes previsualizarlo en:

- GitHub (renderizado automático en `.md`).
- [Mermaid Live Editor](https://mermaid.live/).
- Editores con soporte Mermaid (VS Code + extensión).

## Contexto: estilo de despliegue

SeniorVital usa una **arquitectura de microservicios** con un **API Gateway** como
punto único de entrada. La comunicación es:

- **Síncrona (REST)**: el frontend siempre habla con el gateway (puerto 8000), que
  enruta cada petición al microservicio correspondiente según el prefijo de la URL.
- **Asíncrona (eventos)**: los servicios publican eventos en la tabla
  `event_queue` de PostgreSQL (en lugar de Redis). Los workers de fondo los
  consumen para replicación, análisis preventivo y notificaciones.
- **IA local**: el servicio de rutinas se comunica con Ollama (`phi3:mini`) vía
  HTTP REST en `localhost:11434`, con streaming (SSE) para progreso en tiempo real.

## Diagrama de componentes

```mermaid
graph TD
    subgraph Frontend["Frontend (React 18 + Vite + TypeScript)"]
        SPA["SPA — Rutas /login /routine /habits /progress /caregiver /admin"]
        OFFLINE["Cola offline (Zustand + localStorage)"]
        SSE["Cliente SSE — generateRoutineStream"]
    end

    subgraph Gateway["API Gateway (FastAPI) — puerto 8000"]
        PROXY["Proxy REST (httpx)"]
        STREAM["Proxy SSE (StreamingResponse)"]
        STATIC["Estáticos del frontend (frontend/dist)"]
    end

    subgraph Services["Microservicios (FastAPI)"]
        AUTH["Auth & Profile (8001)"]
        CAT["Catalog (8002)"]
        AI["Routines AI (8003)"]
        TRK["Tracking (8004)"]
        DASH["Dashboard (8005)"]
        NOTIF["Notification (8006)"]
        RAG["RAG Service (8007)"]
    end

    subgraph Data["Datos"]
        PG[("PostgreSQL<br/>seniorvital<br/>15 tablas + event_queue")]
        DUCK[("DuckDB<br/>analítica offline")]
        CHROMA[("ChromaDB<br/>RAG embeddings<br/>363 chunks")]
    end

    subgraph External["Externos"]
        OLLAMA["Ollama<br/>phi3:mini (11434)"]
        PUSH["Web Push API<br/>(navegador)"]
    end

    SPA -->|"fetch/api()  Bearer JWT"| PROXY
    SSE -->|"POST /routines/generate-stream"| STREAM

    PROXY -->|"/auth /caregiver /admin"| AUTH
    PROXY -->|"/catalog /storage"| CAT
    PROXY -->|"/routines"| AI
    PROXY -->|"/tracking /habits"| TRK
    PROXY -->|"/dashboard"| DASH
    PROXY -->|"/notify"| NOTIF
    PROXY -->|"/rag"| RAG

    STREAM --> AI

    AI -->|"POST /api/generate (stream)"| OLLAMA
    AI -->|"INSERT routines + evento"| PG
    RAG -->|"search embeddings"| CHROMA
    RAG -->|"POST /api/generate"| OLLAMA
    TRK -->|"INSERT tracking + evento"| PG
    AUTH --> PG
    CAT --> PG
    DASH -->|"consultas de progreso"| PG
    DASH -->|"lectura analítica"| DUCK
    NOTIF -->|"vapid payload"| PUSH
    NOTIF --> PG

    DUCK -.->|"replicator.py (cada 1s)"| PG
```

## Diagrama de flujo de datos (generación de rutina)

Flujo completo desde que el usuario pide la rutina hasta que la recibe:

```mermaid
sequenceDiagram
    participant U as Usuario (senior)
    participant F as Frontend (React)
    participant G as Gateway (8000)
    participant R as Routines AI (8003)
    participant O as Ollama (phi3:mini)
    participant D as PostgreSQL
    participant W as Workers

    U->>F: Abre /routine
    F->>G: GET /routines/today?user_id=X
    G->>R: Proxy REST
    R->>D: ¿Hay rutina activa para hoy?
    alt Rutina ya existe
        D-->>R: rutina cacheada (generated_by)
        R-->>F: 200 + rutina
    else No existe
        R->>R: build_prompt(health_profile, preferences, ejercicios seguros)
        R->>O: POST /api/generate (streaming, format=json)
        O-->>R: tokens JSON acumulados
        R->>R: limpiar + parsear JSON + map_exercises
        R->>D: INSERT routines (generated_by='ollama')
        R->>D: publish evento rutina-generada
        R-->>F: SSE events: progress → complete
    end
    F->>F: Muestra rutina (mensaje origen IA/fallback)
    U->>F: Completa series (RPE, descanso)
    F->>G: POST /tracking/record
    G->>R: Proxy → Tracking (8004)
    R-->>F: 200
    D->>W: Eventos en event_queue
    W->>W: replicator → DuckDB, preventivo, weekly
```

## Diagrama de infraestructura (despliegue)

Estado actual del despliegue local (no contenedorizado aún):

```mermaid
graph LR
    subgraph Host["Host local"]
        P["Python 3.12+ (uvicorn --reload)"]
        N["Node 18+ (Vite dev server :5173)"]
        S["Shell scripts start_all / stop_all"]
    end
    subgraph Infra["Infraestructura"]
        PGX["PostgreSQL 16+ (5432)"]
        OL["Ollama service (11434)"]
    end

    N -->|"proxy /api → :8000"| P
    P -->|"pool asyncpg"| PGX
    P -->|"httpx REST"| OL
    S --> P
```

> **Nota**: aún no hay Docker/docker-compose ni CI/CD (los archivos `.github/workflows`
> de `node_modules` son de dependencias de terceros, no del proyecto). Esto queda
> documentado como *pendiente de definir* en la sección de mejoras.

## Diagrama de flujo RAG (consulta de conocimiento)

Flujo completo de una consulta RAG desde el usuario hasta la respuesta generada:

```mermaid
sequenceDiagram
    participant U as Usuario
    participant G as Gateway (8000)
    participant R as RAG Service (8007)
    participant QP as QueryProcessor
    participant RET as Retriever
    participant C as ChromaDB
    participant CA as ContextAssembler
    participant GEN as RAGGenerator
    participant P as PromptBuilder
    participant O as Ollama (phi3:mini)

    U->>G: POST /rag/query {"query": "¿Qué ejercicios de fuerza son seguros?", "k": 5}
    G->>R: Proxy /rag/query

    Note over QP: 1. Preprocesamiento
    R->>QP: process(query)
    QP->>QP: normalizar (lowercase, collapse whitespace)
    QP->>QP: detectar dominio por keywords
    QP-->>R: {normalized, detected_domain: "B", agent: "Exercise Architect"}

    Note over RET: 2. Recuperación
    R->>RET: retrieve(query, k=5, filters)
    RET->>C: embedding query → cosine similarity
    C-->>RET: top-5 chunks con metadatos y distancias
    RET-->>R: [{chunk_id, content, metadata, distance}]

    Note over CA: 3. Ensamblaje de contexto
    R->>CA: assemble(chunks)
    CA->>CA: deduplicar (first-200 chars key)
    CA->>CA: truncar a ≤4096 tokens
    CA-->>R: contexto formateado con fuentes

    Note over GEN: 4. Generación
    R->>GEN: generate(query, context, agent)
    GEN->>P: build(query, context, "Exercise Architect")
    P-->>GEN: (system_prompt_es, user_prompt)
    GEN->>O: POST /api/generate (phi3:mini)
    O-->>GEN: respuesta generada (streaming)
    GEN->>GEN: ResponseParser.parse()
    GEN-->>R: {answer, sources, warnings}

    R-->>G: 200 + {answer, sources, agent, macrodomain, warnings, query_info}
    G-->>U: Respuesta estructurada
```

## Diagrama de ingesta RAG (indexación de documentos)

Proceso de indexación del conocimiento en el vector store:

```mermaid
graph LR
    KB["knowledge_base/<br/>19 docs .md"] -->|"run_chunking.py"| CHUNKS["chunks/<br/>363 chunks + metadatos"]
    CHUNKS -->|"generate_embeddings.py"| EMB["embeddings/<br/>363 × 384 matrix"]
    CHUNKS -->|"index_knowledge_base.py"| VS[("ChromaDB<br/>vector_store/")]
    EMB -->|"index_knowledge_base.py"| VS

    style KB fill:#e1f5fe
    style VS fill:#c8e6c9
```

### Descripción de la ingesta

1. **Documentos fuente**: 19 archivos Markdown en `data/knowledge_base/`
2. **Chunking**: `scripts/indexing/run_chunking.py` separa en fragmentos de ~100 palabras con metadatos
3. **Embeddings**: `scripts/ingestion/generate_embeddings.py` genera representaciones vectoriales (384-dim)
4. **Indexación**: `scripts/ingestion/index_knowledge_base.py` inserta en ChromaDB
5. **Pipeline automatizado**: `IndexingPipeline` orquesta chunks → embeddings → vector store

# SeniorVital

<p align="center">
  <img src="storage/img/SeniorVital_new.png" alt="" width="50%">
</p>

<p align="center">
  <strong>SeniorVital — Plataforma Inteligente de Bienestar para Adultos Mayores</strong>
</p>

<p align="center">
  <strong>Plataforma Inteligente de Bienestar para Adultos Mayores</strong><br>
  <em>IA local con Ollama, coach conversacional y sistema multiagente para un envejecimiento activo.</em>
</p>

<p align="center">
  <a href="#inicio-rápido">Inicio Rápido</a> &bull;
  <a href="#características-principales">Características</a> &bull;
  <a href="#sincronización-offline">Sincronización Offline</a> &bull;
  <a href="#tecnologías-utilizadas">Tecnologías</a> &bull;
  <a href="#arquitectura-del-sistema">Arquitectura</a> &bull;
  <a href="#pipeline-de-conocimiento-y-rag">Pipeline RAG</a> &bull;
  <a href="#agente-wellness-y-coach-conversacional">Agentes</a> &bull;
  <a href="#sistema-multiagente">Multiagente</a> &bull;
  <a href="#modelo-de-base-de-datos">Base de Datos</a> &bull;
  <a href="#guía-de-uso--api">Guía de Uso / API</a> &bull;
  <a href="#puesta-en-marcha-y-demo">Demo</a> &bull;
  <a href="#pruebas">Pruebas</a> &bull;
  <a href="#documentación">Documentación</a> &bull;
  <a href="#contribución">Contribución</a> &bull;
  <a href="#licencia">Licencia</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white" alt="Python 3.12+" />
  <img src="https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white" alt="FastAPI 0.115+" />
  <img src="https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black" alt="React 18" />
  <img src="https://img.shields.io/badge/TypeScript-5.3-3178C6?logo=typescript&logoColor=white" alt="TypeScript 5.3" />
  <img src="https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white" alt="PostgreSQL 16" />
  <img src="https://img.shields.io/badge/Vite-4-646CFF?logo=vite&logoColor=white" alt="Vite 4" />
  <img src="https://img.shields.io/badge/Ollama-Local_AI-FF6B35?logo=ollama&logoColor=white" alt="Ollama Local AI" />
  <img src="https://img.shields.io/badge/ChromaDB-Vector_Store-FFB13E?logo=chromadb&logoColor=black" alt="ChromaDB Vector Store" />
</p>

---

> **seniorvital** — _plataforma de bienestar_: salud y calidad de vida para adultos mayores, impulsada por inteligencia artificial local.

SeniorVital es una plataforma digital integral disenada especificamente para promover el bienestar fisico y mejorar la calidad de vida de los adultos mayores. Combina tecnologia de vanguardia con **inteligencia artificial local** para ofrecer una experiencia personalizada, accesible y segura que empodera a los seniors en su proceso de envejecimiento activo.

El sistema cuenta con tres capas de inteligencia:

1. **Generacion de rutinas**: Ejercicios personalizados con IA (modelo local `phi3:mini` via Ollama) adaptados al perfil de salud y restricciones medicas.
2. **Coach conversacional**: Agente de bienestar con razonamiento ReAct, memoria conversacional y 8 herramientas especializadas.
3. **Sistema multiagente**: Un Orchestrator clasifica la intencion del usuario y delega a agentes especializados (nutricion, bienestar general), con validacion centralizada de seguridad y trazabilidad completa.
4. **Base de conocimiento RAG**: Pipeline de Retrieval-Augmented Generation con 363 chunks en 6 dominios del bienestar para adultos mayores, consultable por los agentes especializados.

```mermaid
flowchart TD
    subgraph RAG["Pipeline RAG (Base de Conocimiento)"]
        DOCS["19 documentos<br/>6 macrodominios A-F"]
        CHROMA["ChromaDB<br/>363 chunks"]
        EMBED["Embeddings<br/>multilingual-e5-small"]
        DOCS --> CHROMA --> EMBED
    end

    subgraph Capa1["Capa 1 — Generacion de Rutinas"]
        OLLAMA["Ollama phi3:mini"]
        RTN["Rutinas personalizadas<br/>perfil de salud + restricciones"]
        OLLAMA --> RTN
    end

    subgraph Capa2["Capa 2 — Coach Conversacional"]
        COACH["WellnessCoachAgent"]
        REACT["Razonamiento ReAct<br/>max 3 iteraciones"]
        TOOLS["8 herramientas<br/>exercise_catalog, rag_search,<br/>safety_check, ..."]
        COACH --> REACT --> TOOLS
    end

    subgraph Capa3["Capa 3 — Sistema Multiagente"]
        ORCH["OrchestratorAgent<br/>IntentClassifier"]
        NUTRI["NutritionAgent"]
        MOTIV["MotivationAgent"]
        ANALYTICS["AnalyticsAgent"]
        SAFETY["SafetyGuardian"]
        ORCH --> NUTRI
        ORCH --> MOTIV
        ORCH --> ANALYTICS
        ORCH --> SAFETY
    end

    EMBED -->|"alimenta transversalmente"| Capa1
    EMBED -->|"alimenta transversalmente"| Capa2
    EMBED -->|"alimenta transversalmente"| Capa3

    RTN -->|"fallback"| COACH
    COACH -->|"delegacion"| ORCH
    ORCH -->|"rag_search"| EMBED

    classDef rag fill:#10B981,stroke:#047857,color:#FFFFFF
    classDef capa1 fill:#F97316,stroke:#C2410C,color:#FFFFFF
    classDef capa2 fill:#3B82F6,stroke:#1E40AF,color:#FFFFFF
    classDef capa3 fill:#8B5CF6,stroke:#6D28D9,color:#FFFFFF

    class DOCS,CHROMA,EMBED rag
    class OLLAMA,RTN capa1
    class COACH,REACT,TOOLS capa2
    class ORCH,NUTRI,MOTIV,ANALYTICS,SAFETY capa3
```

Las tres capas de inteligencia de SeniorVital se organizan jerarquicamente: la **Capa 1** genera rutinas personalizadas usando IA local (Ollama), la **Capa 2** ofrece un coach conversacional con razonamiento ReAct y 8 herramientas, y la **Capa 3** coordina agentes especializados via un Orchestrator central. Todas las capas se alimentan del **Pipeline RAG** (363 chunks en 6 dominios), que actua como la base de conocimiento transversal del sistema.

**Público objetivo**

- **Adultos mayores**: usuarios principales que realizan las rutinas y registran su progreso.
- **Cuidadores y familiares**: supervisan el bienestar, reciben alertas y reportes.
- **Administradores / profesionales de salud**: gestionan usuarios y analizan metricas globales.

## Inicio Rápido

### Prerrequisitos

- **Python 3.12+**
- **Node.js 18+** (para el frontend)
- **PostgreSQL 16+** corriendo en el puerto 5432
- **Ollama** corriendo en el puerto 11434, con el modelo `phi3:mini`

### Pasos

1. **Clonar el repositorio**

   ```bash
   git clone <repo-url> seniorvital
   cd seniorvital
   ```

2. **Instalar dependencias del backend** (todos los servicios)

   ```bash
   pip install -r auth-profile-service/requirements.txt
   pip install -r catalog-service/requirements.txt
   pip install -r routines-ai-service/requirements.txt
   pip install -r tracking-service/requirements.txt
   pip install -r dashboard-service/requirements.txt
   pip install -r notification-service/requirements.txt
   pip install -r gateway/requirements.txt
   pip install duckdb pywebpush pytest httpx aiofiles
   ```

3. **Instalar dependencias del Pipeline RAG** (opcional, para knowledge base)

   ```bash
   pip install -r requirements_chunking.txt
   # Incluye: chromadb, langchain, sentence-transformers, langchain-huggingface
   ```

4. **Instalar dependencias del frontend**

   ```bash
   cd frontend && npm install && cd ..
   ```

4. **Inicializar la base de datos**

   - Crear la base `seniorvital` en PostgreSQL.
   - Ejecutar `init_db.sql` en pgAdmin (crea el esquema completo).
   - Ejecutar `scripts/migrations.sql` (columnas y tablas adicionales).

   > Alternativamente, el esquema se auto-aplica al arrancar cada servicio
   > (`CREATE TABLE IF NOT EXISTS` + `ALTER TABLE ADD COLUMN IF NOT EXISTS`).

5. **Configurar variables de entorno**

   ```bash
   cp .env.example .env
   # Editar según sea necesario (DATABASE_URL, JWT_SECRET, claves VAPID, OLLAMA_URL…)
   ```

6. **Descargar el modelo de IA**

   ```bash
   ollama pull phi3:mini
   ```

7. **Indexar la base de conocimiento** (opcional, para RAG)

   ```bash
   python -m src.rag.indexing.pipeline
   ```

### Variables de entorno (`.env`)

| Variable | Descripcion | Ejemplo |
|----------|-------------|---------|
| `DATABASE_URL` | Conexion a PostgreSQL | `postgresql://postgres:pass@localhost:5432/seniorvital` |
| `OLLAMA_URL` | URL del servicio de Ollama | `http://localhost:11434` |
| `OLLAMA_MODEL` | Modelo de IA a usar | `phi3:mini` |
| `OLLAMA_TIMEOUT` | Timeout de generacion (segundos) | `600` |
| `JWT_SECRET` | Clave de firma de tokens JWT | *(aleatoria)* |
| `VAPID_PUBLIC_KEY` / `VAPID_PRIVATE_KEY` | Claves Web Push | *(generadas con pywebpush)* |
| `VAPID_CLAIM_EMAIL` | Email de contacto para VAPID | `admin@seniorvital.com` |
| `USE_REACTORED_AGENT` | Activar WellnessAgent refactorizado | `true` / `false` |
| `USE_ORCHESTRATOR_AGENT` | Activar sistema multiagente | `true` / `false` |
| `DATA_CLIENT_MODE` | Modo de clientes de datos | `local` / `gcp` |
| `VECTOR_STORE_DIR` | Directorio del vector store | `data/vector_store` |

## Características Principales

### Para Adultos Mayores (Seniors)

- **Rutinas personalizadas con IA**: ejercicios generados segun perfil de salud, edad, condicion fisica y restricciones medicas, con streaming en tiempo real (SSE) y mensaje informativo del origen de la rutina (IA / predeterminada).
- **Coach de bienestar**: conversacion natural en espanol sobre nutricion, ejercicio, habitos y bienestar emocional, con razonamiento ReAct y acceso a una base de conocimiento RAG.
- **Seguimiento de progreso**: visualizacion de racha de actividad, sesiones completadas y tendencia de esfuerzo percibido (RPE).
- **Registro de hábitos diarios**: control de hidratación y horas de sueño.
- **Escala de esfuerzo percibido (RPE)**: evaluación intuitiva del nivel de dificultad con emojis y colores.
- **Cronómetro y temporizador de descanso**: medición automática del tiempo de ejercicio y descanso entre series.
- **Onboarding guiado**: configuración inicial paso a paso del perfil de salud.

### Para Cuidadores

- **Vinculación con seniors**: conexión de cuidadores con adultos mayores para supervisión.
- **Dashboard de monitoreo**: vista consolidada del progreso de todos los pacientes vinculados.
- **Alertas automáticas**: notificaciones de fatiga alta (RPE ≥ 8) o inactividad prolongada (≥ 3 días).
- **Reportes periódicos**: análisis de 30 días con estadísticas y recomendaciones personalizadas.
- **Vista detallada por paciente**: acceso a progreso individual, calendario de actividad y tendencias.

### Para Administradores

- **Gestión de usuarios**: control de todos los usuarios de la plataforma.
- **Analíticas globales**: métricas agregadas de uso y engagement.
- **Semáforo de riesgo**: identificación visual de usuarios en riesgo (verde/amarillo/rojo).
- **Logs del sistema**: monitoreo de eventos y troubleshooting.

### Caracteristicas Tecnicas

- **Arquitectura de microservicios**: 8 servicios independientes para escalabilidad y mantenibilidad.
- **IA local con Ollama**: procesamiento de datos sin exposicion a internet.
- **Pipeline RAG**: base de conocimiento de bienestar indexada en ChromaDB (363 chunks, 6 dominios) consultable por agentes.
- **Sistema multiagente**: OrchestratorAgent con clasificacion de intencion, agentes especializados, y validacion centralizada de seguridad.
- **Sincronizacion offline**: funcionalidad sin conexion con cola de eventos.
- **Notificaciones Web Push**: alertas en tiempo real.
- **Accesibilidad WCAG 2.1 AA**: cumplimiento de estandares de accesibilidad.
- **Diseno responsive**: adaptado para moviles, tablets y desktop.

## Sincronización Offline

```mermaid
flowchart TD
    User["Usuario realiza accion<br/>(ejercicio, habito)"]
    Net{Conexion<br/>disponible?}

    Net -->|Si| Api["api() fetch con Bearer JWT"]
    Net -->|No| Queue["addToOfflineQueue()<br/>Zustand + localStorage"]

    Queue --> Persist["Persist: sv-offline-store<br/>{ id: UUID, path, method, body, created_at }"]
    Persist --> Wait["Esperando reconexion..."]

    User2["Nueva accion offline"]
    User2 --> Queue

    Recon{Reconexion<br/>detectada?}
    Wait --> Recon
    Recon -->|Si| Process["processOfflineQueue()"]
    Process --> Entry["Iterar entradas de la cola"]
    Entry --> Try["api(path, method, body)"]
    Try -->|Exito| Remove["remove(entry.id)"]
    Try -->|Fallo| Keep["Mantener en cola<br/>(reintentar despues)"]
    Remove --> Next["Siguiente entrada"]
    Next --> Entry

    Api --> Response["Respuesta del servidor"]
```

Este diagrama muestra el mecanismo de resiliencia del frontend: cuando no hay conexion, las acciones del usuario se serializan en `localStorage` via Zustand (`sv-offline-store`). Al reconectarse, `processOfflineQueue()` itera la cola y reintenta cada peticion. Las entradas exitosas se eliminan; las fallidas permanecen para el proximo ciclo. El`getOfflineQueueSize()` permite al frontend mostrar el numero de acciones pendientes.

## Tecnologías Utilizadas

> Extraidas de los archivos de configuracion del repositorio
> (`package.json`, `requirements.txt` de cada servicio, `pytest.ini`, `vite.config.ts`).

### Backend

| Tecnologia | Uso |
|------------|-----|
| **Python 3.12+** | Lenguaje principal de los servicios |
| **FastAPI >= 0.115** | Framework web (8 microservicios) |
| **Uvicorn** | Servidor ASGI |
| **asyncpg** | Driver asincrono de PostgreSQL |
| **PostgreSQL 16+** | Base de datos principal |
| **DuckDB** | Analitica offline (embebida, file-based) |
| **httpx** | Cliente HTTP (gateway proxy, llamadas a Ollama) |
| **Ollama** | Motor de IA local (modelo `phi3:mini`) |
| **passlib + bcrypt** | Hash de contrasenas |
| **python-jose** | Tokens JWT |
| **pywebpush** | Notificaciones Web Push (VAPID) |
| **pydantic v2** | Validacion de datos y modelos |
| **python-dotenv** | Configuracion por variables de entorno |

### Pipeline RAG y Knowledge

| Tecnologia | Uso |
|------------|-----|
| **ChromaDB >= 0.5** | Base de datos vectorial (persistencia local) |
| **sentence-transformers >= 3.0** | Generacion de embeddings (`intfloat/multilingual-e5-small`, 384d) |
| **langchain >= 0.3** | Framework RAG (chunking, pipeline, prompt management) |
| **langchain-huggingface** | Integracion HuggingFace para embeddings |
| **langchain-experimental** | SemanticChunker para chunking semantico |

### Clientes de Datos (Opcional)

| Tecnologia | Uso |
|------------|-----|
| **google-cloud-firestore >= 2.16** | Cliente Firestore (modo GCP) |
| **google-cloud-bigquery >= 3.25** | Cliente BigQuery (modo GCP) |

### Frontend

| Tecnología | Uso |
|------------|-----|
| **React 18** | Librería de UI |
| **TypeScript 5.3** | Tipado estático |
| **Vite 4** | Bundler / dev server |
| **React Router v6** | Enrutamiento (SPA) con lazy loading |
| **Zustand** | Estado global (auth + cola offline) |
| **@tanstack/react-query** | Cache de datos del servidor |
| **react-hook-form + zod** | Formularios y validación |
| **Tailwind CSS** | Estilos |
| **Recharts** | Gráficas de progreso |
| **Vitest + Testing Library** | Pruebas unitarias de frontend |

### Herramientas

- **Pytest** (con `pytest-asyncio`): pruebas unitarias e integración del backend.
- **Scripts PowerShell/Bash**: arranque y parada de todos los servicios.
- **Node.js 18+**: requerido para el frontend (npm).

## Arquitectura del Sistema

SeniorVital es un **monorepo** con **arquitectura de microservicios** y **API Gateway**:

- **Sincrono**: el frontend habla con el gateway (puerto 8000), que enruta por prefijo de URL al microservicio correspondiente.
- **Asincrono**: eventos en la tabla `event_queue` de PostgreSQL (en lugar de Redis), consumidos por workers de fondo.
- **IA local**: el servicio de rutinas se comunica con Ollama via REST con streaming SSE.
- **Multiagente**: el OrchestratorAgent clasifica intenciones y delega a agentes especializados via el patron Supervisor.

### Estructura de directorios

```
seniorvital/
├── auth-profile-service/   # Auth y gestion de perfiles (puerto 8001)
├── catalog-service/        # Catalogo de ejercicios y almacenamiento (8002)
├── routines-ai-service/    # Generacion de rutinas con IA / Ollama (8003)
├── tracking-service/       # Registro de series y eventos (8004)
├── dashboard-service/      # Progreso y analiticas (8005)
├── notification-service/   # Notificaciones Web Push (8006)
├── rag-service/            # Pipeline RAG (8007)
├── gateway/                # API Gateway / proxy / estaticos (8000)
├── seniorvital_shared/     # Libreria compartida (db, modelos, eventos)
├── src/                    # Codigo refactorizado (agentes, tools, RAG, orchestration)
│   ├── agents/             # WellnessCoachAgent, NutritionAgent
│   ├── tools/              # 8 herramientas del coach
│   ├── orchestration/      # OrchestratorAgent, protocolo, logging
│   ├── rag/                # Pipeline RAG completo
│   ├── memory/             # Memoria conversacional (PostgreSQL)
│   ├── clients/            # Adaptadores Firestore/BigQuery
│   └── services/           # LLMService, UserDataService
├── scripts/                # Workers y automatizacion (start/stop, replicador, etc.)
├── frontend/               # Aplicacion React/Vite/TypeScript
├── data/                   # Vector store (ChromaDB), DuckDB, embeddings, evaluacion
├── storage/                # Videos y fotos de progreso
├── tests/                  # Suite de pruebas pytest (301+ tests)
├── docs/                   # Documentacion tecnica y diagramas Mermaid
├── init_db.sql             # Esquema de base de datos (fuente de verdad)
└── .env.example            # Plantilla de variables de entorno
```

### Diagrama de arquitectura (Mermaid)

```mermaid
graph TD
    subgraph Frontend["Frontend (React 18 + Vite + TypeScript)"]
        SPA["SPA — /login /routine /habits /progress /caregiver /admin"]
        OFFLINE["Cola offline (Zustand + localStorage)"]
        SSE["Cliente SSE — generateRoutineStream"]
    end

    subgraph Gateway["API Gateway (FastAPI) — puerto 8000"]
        PROXY["Proxy REST (httpx)"]
        STREAM["Proxy SSE (StreamingResponse)"]
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

    subgraph Orchestrator["Capa Multiagente"]
        ORCH["OrchestratorAgent<br/>IntentClassifier + Router"]
        COACH["WellnessCoachAgent<br/>General + 8 tools"]
        NUTRI["NutritionAgent<br/>Nutricion + RAG + Safety"]
    end

    subgraph Data["Datos"]
        PG[("PostgreSQL<br/>16 tablas + event_queue")]
        DUCK[("DuckDB<br/>analitica offline")]
        CHROMA[("ChromaDB<br/>363 chunks<br/>6 dominios A-F")]
    end

    subgraph External["Externos"]
        OLLAMA["Ollama<br/>phi3:mini (11434)"]
        PUSH["Web Push API"]
    end

    SPA -->|"fetch/api()  Bearer JWT"| PROXY
    SSE -->|"POST /routines/generate-stream"| STREAM

    PROXY -->|"/auth /caregiver /admin"| AUTH
    PROXY -->|"/catalog /storage"| CAT
    PROXY -->|"/routines /chat"| AI
    PROXY -->|"/tracking /habits"| TRK
    PROXY -->|"/dashboard"| DASH
    PROXY -->|"/notify"| NOTIF
    PROXY -->|"/rag"| RAG

    STREAM --> AI
    AI -->|"POST /api/generate (stream)"| OLLAMA
    AI -->|"INSERT routines + evento"| PG
    AI -->|"USE_ORCHESTRATOR_AGENT=true"| ORCH
    ORCH -->|"delega"| COACH
    ORCH -->|"delega"| NUTRI
    COACH -->|"rag_search, safety_check, 6 mas"| OLLAMA
    NUTRI -->|"rag_search, safety_check"| OLLAMA
    RAG -->|"query → retrieve → generate"| CHROMA
    RAG -->|"generacion"| OLLAMA
    TRK -->|"INSERT tracking + evento"| PG
    AUTH --> PG
    CAT --> PG
    DASH -->|"consultas de progreso"| PG
    DASH -->|"lectura analitica"| DUCK
    NOTIF -->|"vapid payload"| PUSH
    NOTIF --> PG
    DUCK -.->|"replicator.py"| PG
```

```mermaid
flowchart TD
    subgraph Frontend["Frontend"]
        SPA["React 18 + Vite + TypeScript"]
    end

    subgraph Gateway["API Gateway"]
        PROXY["FastAPI :8000<br/>Proxy REST + SSE"]
    end

    subgraph Services["Microservicios"]
        direction LR
        AUTH["Auth :8001"]
        CAT["Catalog :8002"]
        AI["Routines AI :8003"]
        TRK["Tracking :8004"]
        DASH["Dashboard :8005"]
        NOTIF["Notification :8006"]
        RAG["RAG Service :8007"]
    end

    subgraph Orchestrator["Sistema Multiagente"]
        ORCH["OrchestratorAgent"]
        COACH["WellnessCoachAgent"]
        NUTRI["NutritionAgent"]
    end

    subgraph Data["Capa de Datos"]
        PG[("PostgreSQL")]
        DUCK[("DuckDB")]
        CHROMA[("ChromaDB")]
    end

    subgraph External["Servicios Externos"]
        OLLAMA["Ollama :11434"]
        PUSH["Web Push API"]
    end

    Usuario["Usuario"] --> SPA
    SPA -->|"JWT Bearer"| PROXY
    PROXY --> Services
    Services <-->|"delegacion"| Orchestrator
    Services --> Data
    Services --> External
    Orchestrator --> OLLAMA

    classDef frontend fill:#3B82F6,stroke:#1E40AF,color:#FFFFFF
    classDef gateway fill:#10B981,stroke:#047857,color:#FFFFFF
    classDef services fill:#F97316,stroke:#C2410C,color:#FFFFFF
    classDef multiagent fill:#8B5CF6,stroke:#6D28D9,color:#FFFFFF
    classDef data fill:#06B6D4,stroke:#0E7490,color:#FFFFFF
    classDef external fill:#6B7280,stroke:#374151,color:#FFFFFF

    class SPA frontend
    class PROXY gateway
    class AUTH,CAT,AI,TRK,DASH,NOTIF,RAG services
    class ORCH,COACH,NUTRI multiagent
    class PG,DUCK,CHROMA data
    class OLLAMA,PUSH external
```

Este diagrama de alto nivel muestra las 6 capas funcionales de SeniorVital y sus colores distintivos. A diferencia del diagrama detallado anterior (que muestra servicios individuales y rutas HTTP), esta vista se centra en la arquitectura por capas: el Frontend se comunica con el Gateway, que enruta a los Microservicios. Estos delegan tareas inteligentes al Sistema Multiagente, acceden a la Capa de Datos, y consumen Servicios Externos como Ollama y Web Push.

Version completa con diagrama de secuencia e infraestructura: **[docs/architecture.mermaid.md](docs/architecture.mermaid.md)**

### Tabla de servicios

| Servicio | Puerto | Descripcion |
|----------|--------|-------------|
| API Gateway | 8000 | Proxy/CORS router + estaticos del frontend |
| Auth & Profile | 8001 | Registro, login, perfiles, vinculos cuidador-senior, admin |
| Catalog | 8002 | Catalogo de ejercicios y almacenamiento de videos |
| Routines AI | 8003 | Generacion de rutinas con IA (Ollama) + coach conversacional + orquestador multiagente |
| Tracking | 8004 | Registro de series y habitos + publicacion de eventos |
| Dashboard | 8005 | Progreso, analiticas y proyecciones |
| Notification | 8006 | Notificaciones Web Push |
| RAG Service | 8007 | Pipeline de Retrieval-Augmented Generation |

## Pipeline de Conocimiento y RAG

SeniorVital incluye un pipeline de Retrieval-Augmented Generation (RAG) que permite a los agentes consultar una base de conocimiento especializada en bienestar para adultos mayores.

### Base de conocimiento

**19 documentos** en Markdown organizados en **6 macrodominios**:

| Dominio | Nombre | Chunks | Agente asignado |
|---------|--------|--------|-----------------|
| A | Fundamentos Fisiologicos | 35 | AnalyticsAgent (planeado) |
| B | Taxonomia del Ejercicio | 182 | AnalyticsAgent (planeado) |
| C | Contexto y Entorno | 23 | WellnessCoachAgent |
| D | Comorbilidades / Seguridad | 9 | SafetyGuardianAgent (planeado) |
| E | Nutricion | 13 | NutritionAgent |
| F | Bienestar Emocional | 101 | MotivationAgent (planeado) |
| **Total** | | **363** | |

**Fuentes**: OMS, SEGG, ACSM clinical guidelines, ESHI practical manuals, articulos cientificos, guias contextuales latinoamericanas.

### Estrategia de chunking

El sistema utiliza una estrategia **hibrida** con seleccion automatica:

```mermaid
flowchart TD
    Doc[Documento] --> HasHeaders{Tiene headers Markdown?}
    HasHeaders -->|Si| Structural["Structural Chunker<br/>(MarkdownHeaderTextSplitter)"]
    HasHeaders -->|No| ShortDoc{Menos de 500 palabras?}
    ShortDoc -->|Si| Fallback["Fallback Chunker<br/>(RecursiveCharacterTextSplitter)"]
    ShortDoc -->|No| Semantic["Semantic Chunker<br/>(basado en embeddings)"]
    
    Structural --> Post["Post-procesamiento<br/>Merge + enrichment"]
    Fallback --> Post
    Semantic --> Post
    
    Post --> ChromaDB[("ChromaDB")]
```

| Parametro | Valor |
|-----------|-------|
| Chunk minimo | 500 caracteres |
| Chunk maximo | 800 caracteres |
| Fallback chunk_size | 700 caracteres |
| Fallback overlap | 80 caracteres |
| Semantic breakpoint | Percentil 85 |
| Merge minimo | 80 palabras |
| Merge maximo | 1000 caracteres |

**Estadisticas de produccion**: Promedio de 665.8 caracteres y 101.2 palabras por chunk. 148 chunks semanticos, 212 de fallback, 3 estructurales.

> **Imagen recomendada**: Diagrama comparativo de los 3 estrategias de chunking con sus parametros.

### Modelo de embeddings

| Atributo | Valor |
|----------|-------|
| Modelo | `intfloat/multilingual-e5-small` |
| Dimension | 384 |
| Framework | sentence-transformers + langchain-huggingface |
| Dispositivo | CPU |
| Normalizacion | Si |
| Batch size | 32 |
| Costo | Gratuito, completamente local |

### Base de datos vectorial

| Atributo | Valor |
|----------|-------|
| Backend | ChromaDB (`PersistentClient`) |
| Coleccion | `seniorvital_kb` |
| Ruta de persistencia | `data/vector_store/` |
| Metrica de distancia | L2 (Euclidean) |
| Filtros metadata | macrodomain, agent, pathology, level, keywords |

**Diseno para evolucion**: La interfaz del vector store esta disenada para un futuro swap a pgvector.

### Flujo del pipeline RAG

```mermaid
sequenceDiagram
    participant Q as Query
    participant QP as QueryProcessor
    participant R as Retriever
    participant CA as ContextAssembler
    participant G as Generator
    participant L as LLM (phi3:mini)

    Q->>QP: Procesar consulta
    QP->>QP: Normalizar + detectar macrodominio
    QP->>R: retrieve(query, k=5, filters)
    R->>R: Busqueda vectorial en ChromaDB
    R-->>CA: 5 chunks recuperados
    CA->>CA: Deduplicar + truncar (3796 tokens)
    CA-->>G: Contexto ensamblado
    G->>L: system_prompt + context + query
    L-->>G: Respuesta generada
    G->>G: Limpiar + detectar advertencias
    G-->>Q: Respuesta final
```

### Metricas de evaluacion

| Metrica | Score |
|---------|-------|
| Precision@5 | 0.080 |
| Recall@5 | 0.267 |
| MRR | 0.400 |
| Hit Rate | 0.400 |
| Domain Accuracy | 0.400 |
| Keyword Coverage | 0.760 |
| Citation Rate | 0.800 |

> **Nota**: Estos resultados son con 5 queries de prueba. El pipeline RAG esta en fase de iteracion.

Documentacion detallada: **[docs/rag/](docs/rag/)**, **[docs/evaluation/](docs/evaluation/)**

<img src="storage/img/eva.png" width="20%"style="vertical-align: middle; margin-right: 10px;"> Agente Wellness y Coach Conversacional

El sistema incluye dos agentes de bienestar con roles diferentes:

<img src="storage/img/eva.png" width="20%"style="vertical-align: middle; margin-right: 10px;"> WellnessAgent (Generador de rutinas)

| Campo | Valor |
|-------|-------|
| Clase | `WellnessAgent` |
| Archivo | `src/agents/wellness/agent.py` |
| Rol | Generar rutinas de ejercicio personalizadas via Ollama |
| Tools | Ninguno (usa LLM directamente) |
| Estado | Implementado (Sprint 1-2) |

**Justificacion de refactorizacion**: La logica original estaba embebida en los HTTP route handlers de `routines-ai-service/main.py`. La refactorizacion extrae esta logica en una clase testable con dependency injection (LLMService, UserDataService, RoutineRepository), el dataclass `RoutineResult`, y manejo explicito de fallbacks.

<img src="storage/img/eva.png" width="20%"style="vertical-align: middle; margin-right: 10px;"> WellnessCoachAgent 2.0 (Conversacional)

| Campo | Valor |
|-------|-------|
| Clase | `WellnessCoachAgent` |
| Archivo | `src/agents/wellness/coach.py` |
| Rol | Conversaciones generales de bienestar con razonamiento ReAct |
| Tools | 8 herramientas especializadas |
| Memoria | PostgreSQL (`conversation_history`) |
| Estado | Implementado (Sprint 2) |

### Arquitectura interna del Coach

```mermaid
graph TD
    User["Mensaje del usuario"] --> Chat["WellnessCoachAgent.chat()"]
    
    Chat --> History["MemoryStore.get_history()"]
    Chat --> Profile["UserDataService.get_user_data()"]
    
    History --> Prompt["WellnessCoachPromptBuilder.build()"]
    Profile --> Prompt
    
    Prompt --> ReAct["ReActEngine.run()"]
    
    ReAct --> LLM1["LLM generate()"]
    LLM1 --> Parse["Parse JSON response"]
    
    Parse -->|action present| Tool["Tool.execute()"]
    Tool --> Observation["ToolResult"]
    Observation --> LLM1
    
    Parse -->|final_answer| Answer["Respuesta final"]
    
    ReAct --> Save["MemoryStore.add_message()"]
    Answer --> Save
    Save --> Response["Respuesta al usuario"]
```

### Herramientas del Coach (8 tools)

| Tool | Nombre | Descripcion | Args requeridos |
|------|--------|-------------|-----------------|
| ExerciseCatalogTool | `exercise_catalog` | Buscar ejercicios por nivel/keyword/contraindicaciones | (ninguno) |
| GenerateRoutineTool | `generate_routine` | Generar rutina diaria personalizada | `user_id` |
| GetHabitsTool | `get_habits` | Obtener registros de habitos (agua, sueno) | `user_id` |
| LogHabitTool | `log_habit` | Registrar habitos (agua, sueno) | `user_id`, `habit_type`, `value` |
| GetProgressTool | `get_progress` | Obtener insights y progreso semanal | `user_id` |
| GetRoutineTool | `get_routine` | Obtener rutina activa del dia | `user_id` |
| RAGSearchTool | `rag_search` | Consultar base de conocimiento RAG | `query` |
| SafetyCheckTool | `safety_check` | Verificar seguridad de actividad para perfil medico | `user_id`, `activity` |

### Patron ReAct (Reasoning + Acting)

El Coach utiliza un bucle ReAct con maximo 3 iteraciones:

1. **Observar**: Recibe el mensaje del usuario + historial + perfil
2. **Pensar**: El LLM genera un `thought` con su razonamiento
3. **Actuar**: Si necesita informacion, llama un tool con `action` + `action_input`
4. **Resultado**: El tool retorna un `ToolResult` que se inyecta como contexto
5. **Repetir** hasta obtener un `final_answer`

**Seguridad del bucle**: Si 2 tools consecutivos fallan, el bucle se aborta y retorna la ultima reflexion como respuesta.

### Memoria conversacional

| Aspecto | Detalle |
|---------|---------|
| Backend | PostgreSQL (`conversation_history` table) |
| Protocolo | `MemoryStore` (intercambiable) |
| Mensajes por contexto | 5 (configurable via `conversation_history_limit`) |
| Serializacion | JSON con `role`, `content`, `timestamp`, `metadata` |
| Degradacion graceful | Si falla la memoria, el agente funciona sin historial |

## Sistema Multiagente

El sistema multiagente utiliza el patron **Supervisor**: un OrchestratorAgent centraliza el routing, clasifica la intencion del usuario, delega al agente especializado apropiado, y valida la seguridad de las respuestas.

### Agentes implementados

| Agente | Dominio | Estado | Tools | Descripcion |
|--------|---------|--------|-------|-------------|
| <img src="storage/img/eva.png" width="20%"style="vertical-align: middle; margin-right: 10px;"> WellnessCoachAgent | General | Implementado | 8 tools | Conversaciones generales de bienestar |
| <img src="storage/img/eva.png" width="20%"style="vertical-align: middle; margin-right: 10px;"> NutritionAgent | Nutricion | Implementado | rag_search, safety_check | Consultas de nutricion y dieta |

### Agentes planeados

| Agente | Dominio | Estado | Tools | Descripcion |
|--------|---------|--------|-------|-------------|
| **AnalyticsAgent** | Progreso | Planeado | get_progress, get_habits, get_routine | Estadisticas y tendencias |
| **MotivationAgent** | Cognitivo | Planeado | rag_search, log_habit | Bienestar emocional |
| **SafetyGuardianAgent** | Seguridad | Planeado | safety_check, rag_search | Validacion transversal |

### OrchestratorAgent

| Campo | Valor |
|-------|-------|
| Clase | `OrchestratorAgent` |
| Archivo | `src/orchestration/router.py` |
| Patron | Supervisor |
| Feature flag | `USE_ORCHESTRATOR_AGENT=true` |

**Flujo del Orchestrator**:

```mermaid
flowchart TD
    Msg["Mensaje del usuario"] --> Route["OrchestratorAgent.route()"]
    Route --> Classify["IntentClassifier.classify()"]
    
    Classify --> Keywords{Match keywords?}
    Keywords -->|Si| Confidence{Confianza > 0.7?}
    Keywords -->|No| LLM["LLM classify()"]
    
    LLM --> Confidence
    Confidence -->|Si| Select["select_agent(domain)"]
    Confidence -->|No| Fallback["Fallback → WellnessCoachAgent"]
    
    Select --> Agent["Agente especializado"]
    Agent --> Handle["agent.handle(AgentRequest)"]
    Handle --> Safety{safety_level == critical?}
    Safety -->|Si| Block["Bloquear respuesta"]
    Safety -->|No| Return["Retornar AgentMessage"]
    
    Block --> Generic["Mensaje generico: Consulta a un profesional"]
    
    Agent -.->|excepcion| Fallback
    Fallback --> Handle2["WellnessCoachAgent.handle()"]
    Handle2 --> Return
```

```mermaid
flowchart TD
    User["Usuario"]

    subgraph Orchestrator["Orchestrator"]
        ORCH["OrchestratorAgent<br/>IntentClassifier + Router"]
    end

    subgraph Agents["Agentes Especializados"]
        COACH["WellnessCoachAgent<br/>General — 8 tools"]
        NUTRI["NutritionAgent<br/>Nutricion + dieta"]
        ANALYTICS["AnalyticsAgent<br/>Progreso y estadisticas"]
        MOTIV["MotivationAgent<br/>Bienestar emocional"]
        SAFETY["SafetyGuardianAgent<br/>Validacion transversal"]
    end

    subgraph Tools["Herramientas Externas"]
        OLLAMA["Ollama phi3:mini<br/>:11434"]
        RAG["rag_search<br/>Base de conocimiento RAG"]
        SAFETY_CHECK["safety_check<br/>Perfil medico"]
        CATALOG["exercise_catalog<br/>Catalogo de ejercicios"]
        HABITS["get_habits / log_habit<br/>Habitos diarios"]
        PROGRESS["get_progress / get_routine<br/>Progreso del usuario"]
    end

    subgraph Data["Fuentes de Datos"]
        PG[("PostgreSQL<br/>16 tablas")]
        CHROMA[("ChromaDB<br/>363 chunks — 6 dominios")]
        CONV[("conversation_history<br/>Memoria conversacional")]
    end

    User -->|"Mensaje"| ORCH
    ORCH -->|"delega dominio general"| COACH
    ORCH -->|"delega dominio nutricion"| NUTRI
    ORCH -->|"delega dominio progreso"| ANALYTICS
    ORCH -->|"delega dominio cognitivo"| MOTIV
    ORCH -->|"validacion seguridad"| SAFETY

    COACH -->|"consulta"| RAG
    COACH -->|"genera respuesta"| OLLAMA
    COACH -->|"busca ejercicios"| CATALOG
    COACH -->|"lee/escribe"| CONV

    NUTRI -->|"consulta nutricion"| RAG
    NUTRI -->|"genera recomendacion"| OLLAMA
    NUTRI -->|"valida perfil"| SAFETY_CHECK

    ANALYTICS -->|"lee metricas"| PG
    ANALYTICS -->|"consulta habitos"| HABITS
    ANALYTICS -->|"obtiene rutina"| PROGRESS

    MOTIV -->|"consulta bienestar"| RAG
    MOTIV -->|"registra habito"| HABITS

    SAFETY -->|"verifica restricciones"| SAFETY_CHECK
    SAFETY -->|"consulta contraindicaciones"| RAG

    RAG -->|"busca chunks"| CHROMA
    COACH -->|"guarda historial"| PG

    classDef orchestrator fill:#8B5CF6,stroke:#6D28D9,color:#FFFFFF
    classDef agent fill:#3B82F6,stroke:#1E40AF,color:#FFFFFF
    classDef tool fill:#F97316,stroke:#C2410C,color:#FFFFFF
    classDef data fill:#06B6D4,stroke:#0E7490,color:#FFFFFF

    class ORCH orchestrator
    class COACH,NUTRI,ANALYTICS,MOTIV,SAFETY agent
    class OLLAMA,RAG,SAFETY_CHECK,CATALOG,HABITS,PROGRESS tool
    class PG,CHROMA,CONV data
```

Este diagrama muestra la arquitectura completa del sistema multiagente. El **OrchestratorAgent** actua como punto central de entrada, clasificando la intencion del usuario y delegando al agente especializado correspondiente. Cada agente tiene acceso a herramientas externas (Ollama, RAG, safety_check) y fuentes de datos (PostgreSQL, ChromaDB, conversation_history) de acuerdo a su dominio de responsabilidad. Los agentes WellnessCoachAgent y NutritionAgent estan implementados; AnalyticsAgent, MotivationAgent y SafetyGuardianAgent estan planeados.

### Flujo de validacion de seguridad

La validacion de seguridad opera en 3 capas: el Orchestrator clasifica la intencion, el agente ejecuta herramientas de validacion, y el Orchestrator valida la respuesta final antes de retornarla al usuario.

```mermaid
sequenceDiagram
    participant U as Usuario
    participant O as OrchestratorAgent
    participant I as IntentClassifier
    participant A as Agente Especializado
    participant S as SafetyCheckTool
    participant DB as PostgreSQL

    U->>O: POST /chat { message }

    Note over O: 1. Clasificar intencion
    O->>I: classify(message)
    I-->>O: IntentResult(domain, confidence, safety_level)

    alt safety_level == "critical" (deteccion temprana)
        O-->>U: Mensaje generico: "Consulta a un profesional"
    else safety_level != "critical"
        Note over O: 2. Delegar a agente
        O->>A: handle(AgentRequest)

        Note over A: 3. Ejecutar tools (ReAct loop)
        A->>S: execute(user_id, activity)
        S->>DB: SELECT health_profile
        DB-->>S: { medical_restrictions, conditions }
        S->>DB: SELECT contraindications FROM exercises
        DB-->>S: contraindicaciones del ejercicio
        S-->>A: AgentResponse(safety_level)

        Note over A: 4. Generar respuesta
        A-->>O: AgentResponse(text, safety_level, tool_chain)

        alt safety_level == "critical" (validacion post-agente)
            O-->>U: Mensaje generico: "Consulta a un profesional"
        else safety_level == "warning"
            O-->>U: Respuesta con advertencia adjunta
        else safety_level == "safe"
            O-->>U: Respuesta completa
        end
    end
```

Este diagrama secuencial revela que la seguridad no es un checkpoint unico sino una cadena de 3 validaciones: (1) el Orchestrator detecta intenciones criticas antes de delegar, (2) el agente valida contra el perfil medico del usuario usando `SafetyCheckTool`, y (3) el Orchestrator re-valida la respuesta del agente antes de retornarla. Si cualquier capa detecta `critical`, la respuesta se bloquea y se retorna un mensaje generico sin informacion medica.

### Clasificacion de intencion

El IntentClassifier utiliza clasificacion hibrida (keywords + LLM):

| Dominio | Keywords ejemplo | Confianza minima |
|---------|-----------------|------------------|
| nutrition | comer, dieta, alimento, agua, nutricion | 0.7 |
| analytics | ejercicio, rutina, progreso, estadistica | 0.7 |
| motivation | triste, aburrido, motivacion, cognitivo | 0.7 |
| safety | peligro, riesgo, dolor, contraindicacion | 0.7 |

**Fast path**: Clasificacion por keywords (0ms de latencia).
**Slow path**: LLM fallback cuando keywords no alcanzan confianza (requiere llamada a Ollama).

### Protocolo de comunicacion

```python
# AgentMessage - mensaje estandar entre componentes
@dataclass
class AgentMessage:
    from_agent: str          # "user" | "orchestrator" | "agent_name"
    to_agent: str            # "orchestrator" | "agent_name" | "user"
    content: dict            # payload flexible
    message_type: str        # "query" | "response" | "delegation" | "alert"
    correlation_id: str      # UUID[:12], auto-generado
    parent_id: str           # correlation_id del padre
    timestamp: str           # ISO-8601 UTC

# AgentRequest - solicitud a un agente
@dataclass
class AgentRequest:
    message: str
    user_id: int
    user_profile: dict
    conversation_history: list[dict]
    context: dict  # intent, confidence, correlation_id, delegated_by

# AgentResponse - respuesta de un agente
@dataclass
class AgentResponse:
    text: str
    safety_level: str  # "safe" | "warning" | "critical"
    tool_chain: list[str]
    metadata: dict
```

### DelegateCallback

Protocolo inyectable para que agentes deleguen sin conocer al orchestrator:

```python
class DelegateCallback(Protocol):
    async def __call__(self, from_agent: str, to_agent: str, task: dict) -> dict: ...
```

### WorkflowEngine

Motor para flujos multi-paso con placeholders:

```python
steps = [
    WorkflowStep(agent="analytics", task_template={"message": "progress", "user_id": 1}),
    WorkflowStep(
        agent="nutrition",
        task_template={"message": "{prev.text}", "user_id": 1},
        condition="prev.safety_level != 'critical'",
    ),
]
engine = WorkflowEngine(orchestrator)
results = await engine.execute(steps, {"user_id": 1}, correlation_id="wf_001")
```
**Placeholders soportados**: `{prev.text}`, `{prev.safety_level}`, `{ctx.user_id}`, `{ctx.message}`.

### Trazabilidad y observabilidad

Cada evento de orquestacion se registra como JSON estructurado con `correlation_id`:

| Evento | Data | Descripcion |
|--------|------|-------------|
| `route_start` | user_id, message_preview | Inicio del routing |
| `intent_classified` | domain, confidence, method | Intencion clasificada |
| `agent_selected` | agent | Agente seleccionado |
| `delegation_start` | from_agent, to_agent | Inicio de delegacion |
| `delegation_end` | from_agent, to_agent, duration_ms, success | Fin de delegacion |
| `safety_check` | agent, level, blocked | Validacion de seguridad |
| `route_end` | agent, duration_ms | Fin del routing |
| `fallback_activated` | reason, fallback_agent | Activacion de fallback |

```bash
# Reconstruir flujo de una solicitud
grep "abc123def456" logs/orchestration.log | jq .
```

### Integracion con datos

El sistema incluye clientes duales para acceso a datos en modo local y GCP:

| Cliente | Modo local | Modo GCP | Uso |
|---------|-----------|----------|-----|
| `FirestoreClient` | PostgreSQL (asyncpg) | Firestore SDK | Perfiles, habitos, tracking |
| `BigQueryClient` | DuckDB (embebido) | BigQuery SDK | Analiticas, tendencias poblacionales |

**Configuracion**: `DATA_CLIENT_MODE=local|gcp` via variable de entorno. Los agentes reciben el cliente como dependency inyectada.

Documentacion detallada: **[docs/architecture/multiagent-architecture.md](docs/architecture/multiagent-architecture.md)**, **[docs/architecture/orchestration.md](docs/architecture/orchestration.md)**

## Modelo de Base de Datos

PostgreSQL (base `seniorvital`), esquema definido en `init_db.sql` y aplicado de forma idempotente por `seniorvital_shared/db.py`. **16 tablas** organizadas en cuatro grupos:

- **Dominio**: `users`, `caregiver_links`, `exercises`, `workout_sessions`, `workout_exercises`, `workout_sets`, `tracking`, `routines`, `projections`, `habits`.
- **Notificaciones**: `push_subscriptions`.
- **Infraestructura**: `event_queue`, `agent_queue`, `agent_insights`, `admin_logs`.
- **Conversacional**: `conversation_history`.

### Diagrama Entidad-Relación (Mermaid)

```mermaid
erDiagram
    USERS ||--o{ CAREGIVER_LINKS : "cuida (caregiver_user_id)"
    USERS ||--o{ CAREGIVER_LINKS : "es cuidado (senior_user_id)"
    USERS ||--o{ WORKOUT_SESSIONS : "tiene"
    USERS ||--o{ TRACKING : "registra"
    USERS ||--o{ ROUTINES : "recibe rutina"
    USERS ||--o{ PROJECTIONS : "tiene proyeccion"
    USERS ||--o{ HABITS : "registra habitos"
    USERS ||--o{ AGENT_INSIGHTS : "recibe insight"
    USERS ||--o{ CONVERSATION_HISTORY : "conversacion"
    USERS ||--o{ PUSH_SUBSCRIPTIONS : "suscripcion push"
    USERS ||--o{ ADMIN_LOGS : "acciones admin"

    WORKOUT_SESSIONS ||--o{ WORKOUT_EXERCISES : "contiene"
    EXERCISES ||--o{ WORKOUT_EXERCISES : "es usado en"
    WORKOUT_EXERCISES ||--o{ WORKOUT_SETS : "tiene series"
    EXERCISES ||--o{ TRACKING : "referenciado en"

    USERS {
        int id PK
        text email UK
        text password
        text role "senior | caregiver | admin"
        jsonb health_profile
        jsonb preferences
        jsonb profile
        int linked_senior_id FK
        boolean is_active
        text nombre_senior
        text nombre_cuidador
        timestamptz created_at
        timestamptz updated_at
    }

    ROUTINES {
        int id PK
        int user_id FK
        date date
        boolean active
        jsonb exercises
        text warmup
        timestamptz created_at
    }

    TRACKING {
        int id PK
        int user_id FK
        int exercise_id FK
        int sets
        int reps
        int rpe "1..10"
        text felt_difficulty
        timestamptz completed_at
    }

    WORKOUT_SESSIONS {
        int id PK
        int user_id FK
        date scheduled_date
        timestamptz started_at
        timestamptz completed_at
        text notes
    }

    WORKOUT_EXERCISES {
        int id PK
        int session_id FK
        int exercise_id FK
        int order_number
        int progression_level_used
        text notes
    }

    WORKOUT_SETS {
        int id PK
        int workout_exercise_id FK
        int set_number
        int reps
        int rpe "1..10"
        decimal weight_kg
        timestamptz completed_at
        int rest_duration_sec
    }

    EXERCISES {
        int id PK
        text name
        int level "1..4"
        text contraindications
        text video_url
        text description
    }

    HABITS {
        int id PK
        int user_id FK
        date date
        int water_intake_glasses
        decimal sleep_hours
    }

    CAREGIVER_LINKS {
        int id PK
        int caregiver_user_id FK
        int senior_user_id FK
        text status "active | inactive"
        timestamptz created_at
    }

    PROJECTIONS {
        int id PK
        int user_id FK
        date week_start
        text insight_text
        int estimated_level
        timestamptz created_at
    }

    AGENT_INSIGHTS {
        int id PK
        int user_id FK
        text insight_type
        text message
        jsonb metadata
        boolean displayed
        timestamptz generated_at
    }

    CONVERSATION_HISTORY {
        int id PK
        int user_id FK
        text role "user | assistant | system"
        text content
        jsonb metadata
        timestamptz created_at
    }

    PUSH_SUBSCRIPTIONS {
        text user_id PK
        text endpoint
        text p256dh
        text auth
    }

    EVENT_QUEUE {
        int id PK
        text stream_name
        jsonb payload
        boolean processed
        timestamptz created_at
        timestamptz processed_at
    }

    AGENT_QUEUE {
        int id PK
        text command_type
        jsonb payload
        text status "pending | completed | failed"
        timestamptz created_at
        timestamptz processed_at
        text error_message
    }

    ADMIN_LOGS {
        int id PK
        int admin_user_id FK
        text action
        int target_user_id FK
        jsonb details
        timestamptz created_at
    }
```

Diagrama ER completo con todas las tablas y relaciones: **[docs/database.mermaid.md](docs/database.mermaid.md)**

### Relaciones principales

| Relacion | Tipo |
|----------|------|
| `users` → `caregiver_links` | 1:N (cada lado) → M:N cuidadores ↔ seniors |
| `users` → `workout_sessions` / `tracking` / `routines` / `habits` / `projections` | 1:N |
| `workout_sessions` → `workout_exercises` → `workout_sets` | 1:N (jerarquia) |
| `exercises` → `workout_exercises` / `tracking` | 1:N |
| `users` → `conversation_history` | 1:N (memoria conversacional) |
| `users` → `push_subscriptions` | 1:1 (suscripcion Web Push) |
| `users` → `admin_logs` | 1:N (acciones de administrador) |
| `event_queue` | Independiente (procesado por workers) |
| `agent_queue` | Independiente (comandos del orchestrator) |

## Guía de Uso / API

### Ejecutar la aplicación

**Iniciar todos los servicios del backend:**

```powershell
# PowerShell
.\scripts\start_all.ps1
```

```bash
# Git Bash / WSL
bash scripts/start_all.sh
```

**Detener todos los servicios:**

```powershell
.\scripts\stop_all.ps1
```

```bash
bash scripts/stop_all.sh
```

**Ejecutar un único servicio:**

```bash
cd auth-profile-service
uvicorn main:app --port 8001 --reload
```

**Frontend en desarrollo (hot-reload):**

```bash
cd frontend && npm run dev
# http://localhost:5173 (proxy API → gateway :8000)
```

> En producción, el gateway sirve el frontend compilado (`frontend/dist`) en
> `http://localhost:8000`. Compílalo con `npm run build` en `frontend/`.

### Endpoints principales de la API

Todas las rutas pasan por el gateway (`http://localhost:8000`). Cada servicio expone documentación interactiva en `/docs`.

**Auth & Profile (8001)**

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/auth/register` | Registro de usuario |
| POST | `/auth/login` | Inicio de sesión (JWT) |
| POST | `/auth/refresh` | Renovar token |
| GET | `/auth/me` | Perfil del usuario autenticado |
| PUT | `/auth/profile` | Actualizar perfil |
| POST | `/auth/link-caregiver` | Vincular cuidador |
| GET | `/caregiver/seniors` | Seniors vinculados |
| GET | `/caregiver/alerts` | Alertas del cuidador |
| GET | `/caregiver/reports` | Reportes (30 días) |
| GET | `/caregiver/senior/{id}/progress` | Progreso de un senior |
| GET | `/admin/users` | Listar usuarios (admin) |
| PUT | `/admin/users/{id}/routine-override` | Anular rutina (admin) |

**Catalog (8002)**

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/catalog/exercises` | Listar ejercicios |
| POST | `/catalog/exercises` | Crear ejercicio |
| GET/PUT/DELETE | `/catalog/exercises/{id}` | Obtener/editar/eliminar |
| POST | `/catalog/exercises/{id}/video` | Subir video |
| GET | `/storage/videos/{filename}` | Servir video |

**Routines AI (8003)**

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| POST | `/routines/generate` | Generar rutina (sincrono, con fallback) |
| POST | `/routines/generate-stream` | Generar rutina con SSE (progreso en vivo) |
| GET | `/routines/today?user_id=X` | Rutina del dia |
| POST | `/chat` | Coach conversacional / Orchestrator multiagente |
| GET | `/ollama/status` | Estado del modelo de IA |

**RAG Service (8007)**

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| POST | `/rag/query` | Consulta RAG (retrieve + generate) |
| GET | `/rag/health` | Health check del pipeline |
| GET | `/rag/stats` | Estadisticas del vector store |

**Tracking (8004)**

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/tracking/record` | Registrar ejercicio completado |
| POST | `/tracking/batch` | Registrar lote de series |
| GET | `/habits/today` | Hábitos del día |
| POST | `/habits` | Registrar hábitos (agua/sueño) |

**Dashboard (8005)**

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/dashboard/progress/{user_id}` | Progreso completo |
| GET | `/dashboard/projection/{user_id}` | Proyección |
| GET | `/dashboard/insights/{user_id}` | Insights |

**Notification (8006)**

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/notify/subscribe` | Suscribir al Web Push |
| POST | `/notify/send` | Enviar notificacion |

### Flujo de notificaciones Web Push

```mermaid
sequenceDiagram
    participant F as Frontend
    participant GW as Gateway :8000
    participant NS as Notification Service :8006
    participant DB as PostgreSQL
    participant PW as preventive_worker.py
    participant WP as Web Push API
    participant B as Browser

    Note over F,B: 1. Suscripcion
    F->>GW: POST /notify/subscribe
    GW->>NS: /notify/subscribe
    NS->>DB: INSERT push_subscriptions (ON CONFLICT upsert)
    DB-->>NS: ok
    NS-->>F: { status: "subscribed" }

    Note over F,B: 2. Evento de fatiga alta (async)
    PW->>DB: SELECT event_queue WHERE stream=fatiga-alta
    DB-->>PW: payload { user_id, rpe, exercise }
    PW->>GW: POST /notify/send
    GW->>NS: /notify/send
    NS->>DB: SELECT push_subscriptions WHERE user_id
    DB-->>NS: { endpoint, p256dh, auth }
    NS->>NS: BackgroundTasks: send_push_notification()
    NS->>WP: pywebpush.webpush(payload, vapid_keys)
    WP-->>B: Push notification entregada

    alt WP retorna 410 Gone
        NS->>DB: DELETE push_subscriptions WHERE endpoint
        Note over NS: Suscripcion obsoleta eliminada
    end
```

El flujo de notificaciones cruza multiples procesos: el `preventive_worker` detecta el evento en `event_queue`, lo envia al notification-service via HTTP, y el servicio delega el envio real a `pywebpush` con claves VAPID. La limpieza automatica de suscripciones con error 410 (Gone) garantiza que el sistema no acumule suscripciones invalidas.

### Workers de fondo (`scripts/`)

| Script | Frecuencia | Función |
|--------|------------|---------|
| `replicator.py` | cada 1s | Replica eventos de PostgreSQL → DuckDB |
| `preventive_worker.py` | cada 2s | Procesa eventos de alta fatiga |
| `weekly_analysis.py` | semanal (manual) | Análisis semanal con IA |
| `daily_inactivity.py` | diaria | Detecta usuarios inactivos |

### Flujo de eventos asincronos

```mermaid
flowchart TD
    subgraph Productores
        TRK["Tracking Service<br/>POST /tracking/record"]
        RTN["Routines AI Service<br/>POST /routines/generate"]
        WA["weekly_analysis.py<br/>analisis semanal"]
        DI["daily_inactivity.py<br/>deteccion inactividad"]
    end

    subgraph Cola["event_queue (PostgreSQL)"]
        EQ[("event_queue<br/>stream_name + payload<br/>processed flag")]
    end

    subgraph Consumidores
        RE["replicator.py<br/>(cada 1s)"]
        PW["preventive_worker.py<br/>(cada 2s)"]
        WA2["weekly_analysis.py<br/>(semanal)"]
        DI2["daily_inactivity.py<br/>(diaria)"]
    end

    subgraph Destinos
        DUCK[("DuckDB<br/>analytics offline")]
        NOTIF["Notification Service<br/>:8006"]
        PROJ[("PostgreSQL<br/>projections table")]
    end

    TRK -->|"ejercicio-completado"| EQ
    TRK -->|"fatiga-alta (RPE >= 8)"| EQ
    RTN -->|"rutina-generada"| EQ
    WA -->|"recomendacion-ajuste"| EQ
    DI -->|"inactividad-detectada"| EQ

    EQ -->|"stream: ejercicio-completado"| RE
    EQ -->|"stream: fatiga-alta"| PW
    EQ -->|"stream: recomendacion-ajuste"| WA2
    EQ -->|"stream: inactividad-detectada"| DI2

    RE -->|"raw_events + weekly_progress"| DUCK
    PW -->|"HTTP POST /notify/send"| NOTIF
    WA2 -->|"INSERT projections"| PROJ
    DI2 -->|"re-inserta inactividad-detectada"| EQ
```

Este diagrama muestra el ciclo completo de eventos asincronos. Los productores insertan eventos en `event_queue` con un `stream_name` que identifica el tipo de evento. Los consumidores pollan la tabla cada N segundos, procesan los eventos correspondientes a su stream, y marcan `processed = TRUE` para evitar reprocesamiento. El replicator es el puente critico entre el PostgreSQL transaccional y el DuckDB analitico.

### Logica interna del replicator

```mermaid
flowchart TD
    Start["replicator.py<br/>Loop cada 1s"]
    Init["ensure_duckdb_schema()<br/>CREATE TABLE IF NOT EXISTS"]
    Select["SELECT event_queue<br/>WHERE stream = ejercicio-completado<br/>AND processed = FALSE<br/>LIMIT 100"]

    Init --> Select
    Start --> Init

    Select --> HasEvents{Hay eventos?}
    HasEvents -->|No| Sleep["Sleep 1s"]
    HasEvents -->|Si| Process["Para cada evento:"]
    Sleep --> Start

    Process --> Parse["Parse payload JSON<br/>{ user_id, exercise_id, rpe, ... }"]
    Parse --> InsertRaw["INSERT INTO DuckDB<br/>raw_events<br/>(event_id, user_id, event_type, payload)"]
    InsertRaw --> ComputeWeek["Calcular week_start<br/>(lunes de la semana actual)"]
    ComputeWeek --> UpsertWeekly["INSERT OR REPLACE<br/>weekly_progress<br/>(user_id, week_start, avg_rpe,<br/>total_exercises, streak_days, projected_level)"]
    UpsertWeekly --> Mark["UPDATE event_queue<br/>SET processed = TRUE,<br/>processed_at = NOW()<br/>WHERE id = event.id"]
    Mark --> Next["Siguiente evento"]
    Next --> Process

    Process -->|Exito| Next
    Process -->|Error| Skip["Log error, continuar<br/>(no marcar processed)"]
    Skip --> Next
```

El replicator ejecuta un patron de polling con procesamiento idempotente: si un evento falla (por ejemplo, error de DuckDB), no se marca como procesado y se reintentara en el proximo ciclo. La tabla `weekly_progress` usa INSERT OR REPLACE para mantener una unica fila por usuario-semana, calculando automaticamente el promedio de RPE, el total de ejercicios, la racha de dias, y el nivel proyectado.

## Puesta en Marcha y Demo

### Escenario de demo: "Evaluacion del sistema multiagente"

Esta demo demuestra las 3 capas de inteligencia del sistema: generacion de rutinas, coach conversacional, y routing multiagente.

### Pre-requisitos

- PostgreSQL corriendo en puerto 5432
- Ollama corriendo en puerto 11434 con `phi3:mini`
- Python 3.12+ con dependencias instaladas
- Base de datos `seniorvital` inicializada con `init_db.sql`

### Paso 1: Iniciar servicios

```powershell
.\scripts\start_all.ps1
```

Verificar que todos los servicios estan activos:

```powershell
# Verificar gateway
curl http://localhost:8000/docs

# Verificar Ollama
curl http://localhost:11434/api/tags
```

### Paso 2: Activar el sistema multiagente

Editar `routines-ai-service/.env` (o crear si no existe):

```env
USE_ORCHESTRATOR_AGENT=true
USE_REACTORED_AGENT=true
```

Reiniciar el servicio de rutinas:

```powershell
# Detener solo routines-ai
Stop-Process -Name "uvicorn" -Filter "*8003*" -Force -ErrorAction SilentlyContinue

# Reiniciar
cd routines-ai-service
uvicorn main:app --port 8003 --reload
```

### Paso 3: Query 1 — Nutricion (delega a NutritionAgent)

```bash
curl -X POST http://localhost:8000/chat `
  -H "Content-Type: application/json" `
  -d "{\"user_id\": 1, \"message\": \"¿Que debo comer hoy para mantener una dieta balanceada?\"}"
```

**Respuesta esperada**: NutritionAgent procesa la consulta usando `rag_search` para obtener conocimiento del dominio E (Nutricion), y retorna una recomendacion personalizada.

```json
{
  "user_id": 1,
  "response": "Para mantener una dieta balanceada, te recomiendo...",
  "agent": "nutrition",
  "safety_level": "safe"
}
```

### Paso 4: Query 2 — Bienestar general (delega a WellnessCoachAgent)

```bash
curl -X POST http://localhost:8000/chat `
  -H "Content-Type: application/json" `
  -d "{\"user_id\": 1, \"message\": \"¿Que ejercicios puedo hacer para mantenerme activo?\"}"
```

**Respuesta esperada**: WellnessCoachAgent procesa la consulta y puede usar `exercise_catalog` o `get_routine` para dar recomendaciones.

### Paso 5: Query 3 — Safety critical (bloqueado por Orchestrator)

```bash
curl -X POST http://localhost:8000/chat `
  -H "Content-Type: application/json" `
  -d "{\"user_id\": 1, \"message\": \"¿Puedo correr si tengo presion alta?\"}"
```

**Respuesta esperada**: El Orchestrator detecta `safety_level="critical"` y bloquea la respuesta original, retornando un mensaje generico de seguridad.

```json
{
  "user_id": 1,
  "response": "No puedo darte esa recomendación. Por favor, consulta con un profesional de la salud.",
  "agent": "nutrition",
  "safety_level": "critical"
}
```

### Paso 6: Observar trazabilidad

```powershell
# Ver logs de orquestacion
Get-Content logs/orchestration.log -Tail 20
```

Cada request genera eventos JSON con `correlation_id`, permitiendo reconstruir el flujo completo: `route_start -> intent_classified -> agent_selected -> delegation_start -> delegation_end -> route_end`.

### Paso 7: Ejecutar pruebas de integracion

```bash
pytest tests/integration/ -v
```

**17 tests** cubren: routing por dominio, safety blocking, fallback, workflow chaining, performance, y trazabilidad.

### Troubleshooting

| Problema | Solucion |
|----------|---------|
| `Connection refused` en Ollama | Verificar que Ollama esta corriendo: `ollama serve` |
| `USE_ORCHESTRATOR_AGENT` no funciona | Verificar que el servicio 8003 fue reiniciado despues del cambio |
| Respuestas vacias del LLM | Verificar modelo descargado: `ollama list` debe mostrar `phi3:mini` |
| Errores de conexion a DB | Verificar `DATABASE_URL` y que PostgreSQL esta en puerto 5432 |
| RAG no retorna resultados | Verificar que el vector store esta indexado: `GET /rag/stats` |

> **Imagen recomendada**: Captura de pantalla de los logs de orquestacion mostrando el flujo completo con correlation_id.

## Pruebas

### Backend (unitarias e integracion)

```bash
# Suite completa (301+ tests)
pytest tests/ --ignore=tests/rag -v

# Solo tests de integracion multiagente
pytest tests/integration/ -v

# Solo tests de orquestacion
pytest tests/orchestration/ -v
```

La suite cubre los 7 servicios: autenticacion, catalogo, generacion de rutinas,
tracking, dashboard, notificaciones y persistencia. Configuracion en `pytest.ini`
(`asyncio_mode = auto`, `testpaths = tests`).

### Cobertura por area

| Area | Directorio | Tests | Cobertura |
|------|-----------|-------|-----------|
| Auth & Profile | `tests/test_auth.py` | 9 | Registro, login, JWT, roles |
| Catalog | `tests/test_catalog.py` | 6 | CRUD ejercicios, video upload |
| Tracking | `tests/test_tracking.py` | 7 | Registro ejercicio, habitos, eventos |
| Dashboard | `tests/test_dashboard.py` | 3 | Proyecciones, insights |
| Notification | `tests/test_notification.py` | 3 | Subscribe, send |
| Persistence | `tests/test_persistence.py` | 4 | Health profile, caregiver links |
| Wellness Agent | `tests/agents/` | 53 | Coach, evaluation, scenarios, prompts |
| Orchestration | `tests/orchestration/` | 38 | Router, protocol, workflow, logging |
| Nutrition Agent | `tests/nutrition/` | 14 | Agent, adapter, prompts |
| Integration | `tests/integration/` | 17 | Multi-agent flow E2E |
| Tools | `tests/tools/` | 33 | 8 herramientas del coach |
| Clients | `tests/clients/` | 28 | Firestore, BigQuery, config |
| Memory | `tests/memory/` | 11 | PostgresMemoryStore |
| Services | `tests/services/` | 7 | LLM, UserData |
| Database | `tests/database/` | 4 | Repositories |

### Frontend (unitarias)

```bash
cd frontend
npm test          # vitest run
npm run test:watch  # modo watch
```

### Nota de cobertura

No existe aún configuración de cobertura ni CI/CD automatizado en el repositorio.
**Pendiente de definir.**

## Documentación

| Doc | Descripcion |
|-----|-------------|
| [docs/architecture.mermaid.md](docs/architecture.mermaid.md) | Versión completa con diagrama de secuencia e infraestructura |
| [docs/database.mermaid.md](docs/database.mermaid.md) | Diagrama ER completo con todas las tablas y relaciones |
| [docs/rag/](docs/rag/) | Documentacion detallada del pipeline RAG |
| [docs/evaluation/](docs/evaluation/) | Metricas y evaluacion del RAG |
| [docs/architecture/multiagent-architecture.md](docs/architecture/multiagent-architecture.md) | Arquitectura del sistema multiagente |
| [docs/architecture/orchestration.md](docs/architecture/orchestration.md) | Protocolo y flujo del Orchestrator |

## Contribución

Por el momento el proyecto no define un proceso formal de contribución. Guías básicas:

1. Haz un fork del repositorio.
2. Crea una rama descriptiva: `git checkout -b feature/mi-mejora`.
3. Realiza cambios siguiendo las convenciones del código existente.
4. Ejecuta las pruebas: `pytest tests/ -v` y `npm test`.
5. Envía un Pull Request con una descripción clara.

## Licencia

**Pendiente de definir.** El repositorio no incluye actualmente un archivo
`LICENSE` ni una declaración de licencia explícita. Antes de su uso comercial o
distribución, consulta con el equipo del proyecto.

---

**SeniorVital — Plataforma Inteligente de Bienestar para Adultos Mayores.**

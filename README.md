# SeniorVital

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-5.3-3178C6?logo=typescript&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-4-646CFF?logo=vite&logoColor=white)

**Plataforma Inteligente de Bienestar para Adultos Mayores**

## 📋 Descripción del Proyecto

SeniorVital es una plataforma digital integral diseñada específicamente para promover el bienestar físico y mejorar la calidad de vida de los adultos mayores. Combina tecnología de vanguardia con **inteligencia artificial local** para ofrecer una experiencia personalizada, accesible y segura que empodera a los seniors en su proceso de envejecimiento activo.

El sistema genera **rutinas de ejercicio personalizadas con IA** (modelo local `phi3:mini` vía Ollama) adaptadas al perfil de salud, restricciones médicas y objetivos de cada persona, y permite que **cuidadores y familiares** monitoreen el progreso en tiempo real.

### Público objetivo

- **Adultos mayores**: usuarios principales que realizan las rutinas y registran su progreso.
- **Cuidadores y familiares**: supervisan el bienestar, reciben alertas y reportes.
- **Administradores / profesionales de salud**: gestionan usuarios y analizan métricas globales.

---

## 📑 Tabla de Contenidos

1. [Descripción del Proyecto](#-descripción-del-proyecto)
2. [Características Principales](#-características-principales)
3. [Tecnologías Utilizadas](#-tecnologías-utilizadas)
4. [Arquitectura del Proyecto](#-arquitectura-del-proyecto)
5. [Modelo de Base de Datos](#-modelo-de-base-de-datos)
6. [Requisitos de Instalación](#-requisitos-de-instalación)
7. [Guía de Uso / API](#-guía-de-uso--api)
8. [Pruebas](#-pruebas)
9. [Contribución](#-contribución)
10. [Licencia](#-licencia)

---

## ✨ Características Principales

### Para Adultos Mayores (Seniors)
- **Rutinas personalizadas con IA**: ejercicios generados según perfil de salud, edad, condición física y restricciones médicas, con streaming en tiempo real (SSE) y mensaje informativo del origen de la rutina (IA / predeterminada).
- **Seguimiento de progreso**: visualización de racha de actividad, sesiones completadas y tendencia de esfuerzo percibido (RPE).
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

### Características Técnicas
- **Arquitectura de microservicios**: 7 servicios independientes para escalabilidad y mantenibilidad.
- **IA local con Ollama**: procesamiento de datos sin exposición a internet.
- **Sincronización offline**: funcionalidad sin conexión con cola de eventos.
- **Notificaciones Web Push**: alertas en tiempo real.
- **Accesibilidad WCAG 2.1 AA**: cumplimiento de estándares de accesibilidad.
- **Diseño responsive**: adaptado para móviles, tablets y desktop.

---

## 🛠️ Tecnologías Utilizadas

> Extraídas de los archivos de configuración del repositorio
> (`package.json`, `requirements.txt` de cada servicio, `pytest.ini`, `vite.config.ts`).

### Backend
| Tecnología | Uso |
|------------|-----|
| **Python 3.12+** | Lenguaje principal de los servicios |
| **FastAPI ≥ 0.115** | Framework web (7 microservicios) |
| **Uvicorn** | Servidor ASGI |
| **asyncpg** | Driver asíncrono de PostgreSQL |
| **PostgreSQL 16+** | Base de datos principal |
| **DuckDB** | Analítica offline (embebida, file-based) |
| **httpx** | Cliente HTTP (gateway proxy, llamadas a Ollama) |
| **Ollama** | Motor de IA local (modelo `phi3:mini`) |
| **passlib + bcrypt** | Hash de contraseñas |
| **python-jose** | Tokens JWT |
| **pywebpush** | Notificaciones Web Push (VAPID) |
| **pydantic v2** | Validación de datos y modelos |
| **python-dotenv** | Configuración por variables de entorno |

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

---

## 🏗️ Arquitectura del Proyecto

SeniorVital es un **monorepo** con **arquitectura de microservicios** y **API Gateway**:

- **Síncrono**: el frontend habla con el gateway (puerto 8000), que enruta por prefijo de URL al microservicio correspondiente.
- **Asíncrono**: eventos en la tabla `event_queue` de PostgreSQL (en lugar de Redis), consumidos por workers de fondo.
- **IA local**: el servicio de rutinas se comunica con Ollama vía REST con streaming SSE.

### Estructura de directorios

```
seniorvital/
├── auth-profile-service/   # Auth y gestión de perfiles (puerto 8001)
├── catalog-service/        # Catálogo de ejercicios y almacenamiento (8002)
├── routines-ai-service/    # Generación de rutinas con IA / Ollama (8003)
├── tracking-service/       # Registro de series y eventos (8004)
├── dashboard-service/      # Progreso y analíticas (8005)
├── notification-service/   # Notificaciones Web Push (8006)
├── gateway/                # API Gateway / proxy / estáticos (8000)
├── seniorvital_shared/     # Librería compartida (db, modelos, eventos)
├── scripts/                # Workers y automatización (start/stop, replicador, etc.)
├── frontend/               # Aplicación React/Vite/TypeScript
├── storage/                # Videos y fotos de progreso
├── tests/                  # Suite de pruebas pytest
├── docs/                   # Documentación técnica y diagramas Mermaid
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
    end

    subgraph Data["Datos"]
        PG[("PostgreSQL<br/>15 tablas + event_queue")]
        DUCK[("DuckDB<br/>analítica offline")]
    end

    subgraph External["Externos"]
        OLLAMA["Ollama<br/>phi3:mini (11434)"]
        PUSH["Web Push API"]
    end

    SPA -->|"fetch/api()  Bearer JWT"| PROXY
    SSE -->|"POST /routines/generate-stream"| STREAM

    PROXY -->|"/auth /caregiver /admin"| AUTH
    PROXY -->|"/catalog /storage"| CAT
    PROXY -->|"/routines"| AI
    PROXY -->|"/tracking /habits"| TRK
    PROXY -->|"/dashboard"| DASH
    PROXY -->|"/notify"| NOTIF

    STREAM --> AI
    AI -->|"POST /api/generate (stream)"| OLLAMA
    AI -->|"INSERT routines + evento"| PG
    TRK -->|"INSERT tracking + evento"| PG
    AUTH --> PG
    CAT --> PG
    DASH -->|"consultas de progreso"| PG
    DASH -->|"lectura analítica"| DUCK
    NOTIF -->|"vapid payload"| PUSH
    NOTIF --> PG
    DUCK -.->|"replicator.py"| PG
```

Versión completa con diagrama de secuencia e infraestructura: **[docs/architecture.mermaid.md](docs/architecture.mermaid.md)**

### Tabla de servicios

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| API Gateway | 8000 | Proxy/CORS router + estáticos del frontend |
| Auth & Profile | 8001 | Registro, login, perfiles, vínculos cuidador-senior, admin |
| Catalog | 8002 | Catálogo de ejercicios y almacenamiento de videos |
| Routines AI | 8003 | Generación de rutinas con IA (Ollama) + fallback |
| Tracking | 8004 | Registro de series y hábitos + publicación de eventos |
| Dashboard | 8005 | Progreso, analíticas y proyecciones |
| Notification | 8006 | Notificaciones Web Push |

---

## 🗄️ Modelo de Base de Datos

PostgreSQL (base `seniorvital`), esquema definido en `init_db.sql` y aplicado de forma idempotente por `seniorvital_shared/db.py`. **15 tablas** organizadas en tres grupos:

- **Dominio**: `users`, `caregiver_links`, `exercises`, `workout_sessions`, `workout_exercises`, `workout_sets`, `tracking`, `routines`, `projections`, `habits`.
- **Notificaciones**: `push_subscriptions`.
- **Infraestructura**: `event_queue`, `agent_queue`, `agent_insights`, `admin_logs`.

### Diagrama Entidad-Relación (Mermaid)

```mermaid
erDiagram
    USERS ||--o{ CAREGIVER_LINKS : "cuida (caregiver_user_id)"
    USERS ||--o{ CAREGIVER_LINKS : "es cuidado (senior_user_id)"
    USERS ||--o{ WORKOUT_SESSIONS : "tiene"
    USERS ||--o{ TRACKING : "registra"
    USERS ||--o{ ROUTINES : "recibe rutina"
    USERS ||--o{ PROJECTIONS : "tiene proyección"
    USERS ||--o{ HABITS : "registra hábitos"
    USERS ||--o{ AGENT_INSIGHTS : "recibe insight"

    WORKOUT_SESSIONS ||--o{ WORKOUT_EXERCISES : "contiene"
    EXERCISES ||--o{ WORKOUT_EXERCISES : "es usado en"
    WORKOUT_EXERCISES ||--o{ WORKOUT_SETS : "tiene series"
    EXERCISES ||--o{ TRACKING : "referenciado en"

    USERS {
        int id PK
        text email UK
        text role "senior | caregiver | admin"
        jsonb health_profile
        jsonb preferences
        text nombre_senior
        text nombre_cuidador
    }

    ROUTINES {
        int id PK
        int user_id FK
        date date
        jsonb exercises
        text generated_by "ollama | fallback"
    }

    TRACKING {
        int id PK
        int user_id FK
        int exercise_id FK
        int sets
        int reps
        int rpe "1..10"
    }

    WORKOUT_SESSIONS {
        int id PK
        int user_id FK
        date scheduled_date
    }

    WORKOUT_EXERCISES {
        int id PK
        int session_id FK
        int exercise_id FK
        int order_number
    }

    WORKOUT_SETS {
        int id PK
        int workout_exercise_id FK
        int set_number
        int reps
        int rpe "1..10"
    }

    EXERCISES {
        int id PK
        text name
        int level "1..4"
        text contraindications
    }

    HABITS {
        int id PK
        int user_id FK
        date date
        int water_intake_glasses
        decimal sleep_hours
    }
```

Diagrama ER completo con todas las tablas y relaciones: **[docs/database.mermaid.md](docs/database.mermaid.md)**

### Relaciones principales

| Relación | Tipo |
|----------|------|
| `users` → `caregiver_links` | 1:N (cada lado) → M:N cuidadores ↔ seniors |
| `users` → `workout_sessions` / `tracking` / `routines` / `habits` / `projections` | 1:N |
| `workout_sessions` → `workout_exercises` → `workout_sets` | 1:N (jerarquía) |
| `exercises` → `workout_exercises` / `tracking` | 1:N |

---

## 🚀 Requisitos de Instalación

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

3. **Instalar dependencias del frontend**
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

### Variables de entorno (`.env`)

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `DATABASE_URL` | Conexión a PostgreSQL | `postgresql://postgres:pass@localhost:5432/seniorvital` |
| `OLLAMA_URL` | URL del servicio de Ollama | `http://localhost:11434` |
| `OLLAMA_MODEL` | Modelo de IA a usar | `phi3:mini` |
| `OLLAMA_TIMEOUT` | Timeout de generación (segundos) | `600` |
| `JWT_SECRET` | Clave de firma de tokens JWT | *(aleatoria)* |
| `VAPID_PUBLIC_KEY` / `VAPID_PRIVATE_KEY` | Claves Web Push | *(generadas con pywebpush)* |
| `VAPID_CLAIM_EMAIL` | Email de contacto para VAPID | `admin@example.com` |

---

## 🧑‍💻 Guía de Uso / API

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

#### Auth & Profile (8001)
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

#### Catalog (8002)
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/catalog/exercises` | Listar ejercicios |
| POST | `/catalog/exercises` | Crear ejercicio |
| GET/PUT/DELETE | `/catalog/exercises/{id}` | Obtener/editar/eliminar |
| POST | `/catalog/exercises/{id}/video` | Subir video |
| GET | `/storage/videos/{filename}` | Servir video |

#### Routines AI (8003)
| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/routines/generate` | Generar rutina (síncrono, con fallback) |
| POST | `/routines/generate-stream` | Generar rutina con SSE (progreso en vivo) |
| GET | `/routines/today?user_id=X` | Rutina del día |
| GET | `/ollama/status` | Estado del modelo de IA |

#### Tracking (8004)
| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/tracking/record` | Registrar ejercicio completado |
| POST | `/tracking/batch` | Registrar lote de series |
| GET | `/habits/today` | Hábitos del día |
| POST | `/habits` | Registrar hábitos (agua/sueño) |

#### Dashboard (8005)
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/dashboard/progress/{user_id}` | Progreso completo |
| GET | `/dashboard/projection/{user_id}` | Proyección |
| GET | `/dashboard/insights/{user_id}` | Insights |

#### Notification (8006)
| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/notify/subscribe` | Suscribir al Web Push |
| POST | `/notify/send` | Enviar notificación |

### Workers de fondo (`scripts/`)

| Script | Frecuencia | Función |
|--------|------------|---------|
| `replicator.py` | cada 1s | Replica eventos de PostgreSQL → DuckDB |
| `preventive_worker.py` | cada 2s | Procesa eventos de alta fatiga |
| `weekly_analysis.py` | semanal (manual) | Análisis semanal con IA |
| `daily_inactivity.py` | diaria | Detecta usuarios inactivos |

---

## 🧪 Pruebas

### Backend (unitarias e integración)

```bash
pytest tests/ -v
```

La suite cubre los 7 servicios: autenticación, catálogo, generación de rutinas,
tracking, dashboard, notificaciones y persistencia. Configuración en `pytest.ini`
(`asyncio_mode = auto`, `testpaths = tests`).

### Frontend (unitarias)

```bash
cd frontend
npm test          # vitest run
npm run test:watch  # modo watch
```

### Nota de cobertura

No existe aún configuración de cobertura ni CI/CD automatizado en el repositorio.
**Pendiente de definir.**

---

## 🤝 Contribución

Por el momento el proyecto no define un proceso formal de contribución. Guías básicas:

1. Haz un fork del repositorio.
2. Crea una rama descriptiva: `git checkout -b feature/mi-mejora`.
3. Realiza cambios siguiendo las convenciones del código existente.
4. Ejecuta las pruebas: `pytest tests/ -v` y `npm test`.
5. Envía un Pull Request con una descripción clara.

---

## 📄 Licencia

**Pendiente de definir.** El repositorio no incluye actualmente un archivo
`LICENSE` ni una declaración de licencia explícita. Antes de su uso comercial o
distribución, consulta con el equipo del proyecto.

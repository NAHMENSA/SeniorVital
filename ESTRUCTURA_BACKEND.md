# Arquitectura de SeniorVital — Mapa Completo del Proyecto

Sistema backend de microservicios para el bienestar de adultos mayores.
Stack: FastAPI, PostgreSQL asíncrono (asyncpg + JSONB), autenticación JWT, IA local con Ollama (phi3:mini), DuckDB para analítica.

---

## 1. Árbol de Directorios

```
E:\SeniorVital-master\
│
├── .env                          # Variables de entorno (local, excluido de VCS)
├── .env.example                  # Plantilla de variables de entorno
├── .gitignore                    # Exclusiones de VCS (basura local, cachés, prompts)
├── AGENTS.md                     # Configuración para OpenCode
├── README.md                     # Documentación principal del proyecto
├── SDD.md                        # System Design Document (fuente de verdad del diseño)
├── ESTRUCTURA_BACKEND.md         # Este documento
├── ESTRUCTURA_FRONTEND.md        # Estructura del frontend
├── ESTRUCTURA_PROYECTO.md        # Visión general del proyecto
├── GUIA_DESARROLLO.md            # Guía de desarrollo
├── arquitectura_seniorvital.md   # Guía de arquitectura para exposiciones
├── REQUISITOS_FUNCIONALES.md     # Lista de requisitos por microservicio
├── PLAN_REFACTORIZACION.md       # Plan de refactorización
├── init_db.sql                   # Script de inicialización del esquema PostgreSQL
├── pytest.ini                    # Configuración de pytest
├── requirements.txt              # Dependencias globales del proyecto
├── package.json                  # Scripts raíz (npm) para frontend/backend
│
├───auth-profile-service/         # [8001] Autenticación y perfiles
│       main.py                   #   Aplicación FastAPI completa
│       requirements.txt          #   Dependencias del servicio
│
├───catalog-service/              # [8002] Catálogo de ejercicios y videos
│       main.py
│       requirements.txt
│
├───dashboard-service/            # [8005] Dashboard y analítica
│       main.py
│       requirements.txt
│
├───gateway/                      # [8000] API Gateway (proxy inverso + estáticos)
│       main.py
│       requirements.txt
│
├───notification-service/         # [8006] Notificaciones Web Push
│       main.py
│       requirements.txt
│
├───routines-ai-service/          # [8003] Generación de rutinas con IA
│       main.py
│       requirements.txt
│
├───tracking-service/             # [8004] Tracking de ejercicios, hábitos y eventos
│       main.py
│       requirements.txt
│
├───scripts/                      # Automatización y workers background
│       daily_inactivity.py       #   Detección de inactividad (≥3 días)
│       fix_db.sql                #   Recreación completa del esquema (sincronizado con init_db.sql)
│       migrations.sql            #   Migraciones de esquema BD
│       preventive_worker.py      #   Consumidor de eventos fatiga-alta
│       quick_check.py            #   Chequeo rápido de integración vía gateway
│       replicator.py             #   Replicación PostgreSQL → DuckDB
│       smoke_test.py             #   Smoke tests de todos los servicios
│       start_all.ps1             #   Inicio de servicios (PowerShell)
│       start_all.sh              #   Inicio de servicios (Bash)
│       stop_all.ps1              #   Parada de servicios (PowerShell)
│       stop_all.sh               #   Parada de servicios (Bash)
│       verify_integration.py     #   Verificación frontend-backend
│       weekly_analysis.py        #   Análisis semanal con IA
│
├───seniorvital_shared/           # Librería compartida entre servicios
│       __init__.py               #   Exportaciones públicas
│       db.py                     #   Pool de conexiones + esquema (SCHEMA_SQL, init_db)
│       events.py                 #   Publicación de eventos asíncronos
│       models.py                 #   Modelos Pydantic (HealthProfile)
│
├───frontend/                     # Aplicación SPA (React + Vite + TypeScript)
│       (ver ESTRUCTURA_FRONTEND.md para detalle completo)
│
├───docs/                         # Documentación técnica y diagramas
│       architecture.mermaid.md   #   Diagramas Mermaid de arquitectura
│       database.mermaid.md       #   Diagrama Mermaid de base de datos
│
├───storage/                      # Almacenamiento local de archivos
│   ├───progress-photos/          #   Fotos de progreso (reservado)
│   └───videos/                   #   Videos de ejercicios subidos
│
├───tests/                        # Suite de pruebas pytest
│       __init__.py               #   Paquete de tests
│       conftest.py               #   Fixtures compartidos
│       test_auth.py              #   Tests de autenticación
│       test_catalog.py           #   Tests de catálogo
│       test_dashboard.py         #   Tests de dashboard
│       test_db_conn.py           #   Verificación de conexión BD
│       test_notification.py      #   Tests de notificaciones
│       test_persistence.py       #   Tests de persistencia
│       test_routines.py          #   Tests de rutinas IA
│       test_tracking.py          #   Tests de tracking
│
└───logs/                         # Logs de servicios y PIDs (creado en tiempo de ejecución)
```

---

## 2. Descripción de Carpetas

### 2.1 `auth-profile-service/` — Autenticación y Perfiles (puerto 8001)

| Atributo | Valor |
|----------|-------|
| **Responsabilidad** | Registro, login, refresh JWT, gestión de perfiles, roles, vinculación cuidador-senior y endpoints de administración |
| **Tecnologías clave** | FastAPI, passlib[bcrypt], python-jose, Pydantic[EmailStr] |
| **Independencia** | Servicio independiente, comparte pool de BD vía `seniorvital_shared` |

**Archivos:**
- `main.py` — Aplicación FastAPI completa: modelos Pydantic (`RegisterRequest`, `LoginRequest`, `ProfileUpdate`, `LinkCaregiverRequest`), endpoints REST, lógica de bcrypt y JWT, ciclo de vida del pool.
- `requirements.txt` — fastapi, uvicorn, asyncpg, passlib[bcrypt], python-jose[cryptography], pydantic[email], python-dotenv, httpx.

### 2.2 `catalog-service/` — Catálogo de Ejercicios (puerto 8002)

| Atributo | Valor |
|----------|-------|
| **Responsabilidad** | CRUD de ejercicios, subida y servicio de videos |
| **Tecnologías clave** | FastAPI, aiofiles, python-multipart, almacenamiento local |
| **Independencia** | Servicio independiente; sirve archivos estáticos vía `/storage/videos/` |

**Archivos:**
- `main.py` — CRUD completo (`GET/POST/PUT/DELETE /catalog/exercises`), subida de video (`POST /catalog/exercises/{id}/video`), servidor de archivos (`GET /storage/videos/{filename}`).
- `requirements.txt` — fastapi, uvicorn, asyncpg, pydantic, python-dotenv, python-multipart, aiofiles, httpx.

### 2.3 `routines-ai-service/` — Rutinas con IA (puerto 8003)

| Atributo | Valor |
|----------|-------|
| **Responsabilidad** | Generar rutinas de ejercicio personalizadas usando Ollama, con streaming SSE y fallback |
| **Tecnologías clave** | FastAPI, httpx (cliente Ollama), phi3:mini, SSE |
| **Independencia** | Servicio independiente; requiere Ollama en `localhost:11434` |

**Archivos:**
- `main.py` — Endpoints `POST /routines/generate` (síncrono), `POST /routines/generate-stream` (SSE con progreso en vivo), `GET /routines/today`, `GET /ollama/status`. Funciones `call_ollama()`, `call_ollama_stream()`, `build_prompt()` (perfil + preferencias + ejercicios seguros).
- `requirements.txt` — fastapi, uvicorn, asyncpg, pydantic, python-dotenv, httpx.

### 2.4 `tracking-service/` — Tracking de Ejercicios y Hábitos (puerto 8004)

| Atributo | Valor |
|----------|-------|
| **Responsabilidad** | Registrar ejercicios completados, hábitos diarios y publicar eventos asíncronos |
| **Tecnologías clave** | FastAPI, asyncpg, event_queue (PostgreSQL) |
| **Independencia** | Servicio independiente; publica eventos en tabla compartida |

**Archivos:**
- `main.py` — Endpoint `POST /tracking/record` (registro individual con eventos `ejercicio-completado` y `fatiga-alta`), `POST /tracking/batch` (lote en transacción), `GET /habits/today` y `POST /habits` (agua y sueño). Modelos `TrackEntry` y `BatchTrackRequest`. Normaliza `exercise_id` inexistente a NULL (evita violación de FK con rutinas de IA).
- `requirements.txt` — fastapi, uvicorn, asyncpg, pydantic, python-dotenv, httpx.

### 2.5 `dashboard-service/` — Dashboard y Analítica (puerto 8005)

| Atributo | Valor |
|----------|-------|
| **Responsabilidad** | Consultas agregadas de progreso, proyecciones e insights |
| **Tecnologías clave** | FastAPI, asyncpg, DuckDB |
| **Independencia** | Servicio independiente; lee de PostgreSQL y DuckDB |

**Archivos:**
- `main.py` — `GET /dashboard/progress/{user_id}` (calendario semanal, tendencia RPE, racha, sesiones totales e históricas), `GET /dashboard/projection/{user_id}`, `GET /dashboard/insights/{user_id}`.
- `requirements.txt` — fastapi, uvicorn, asyncpg, pydantic, python-dotenv, duckdb, httpx.

### 2.6 `notification-service/` — Notificaciones Push (puerto 8006)

| Atributo | Valor |
|----------|-------|
| **Responsabilidad** | Gestionar suscripciones Web Push y enviar notificaciones |
| **Tecnologías clave** | FastAPI, pywebpush, VAPID, BackgroundTasks |
| **Independencia** | Servicio independiente; tabla `push_subscriptions` propia |

**Archivos:**
- `main.py` — `POST /notify/subscribe` (upsert de suscripción), `POST /notify/send` (envío como background task), función `send_push_notification()` con manejo de errores 410 Gone.
- `requirements.txt` — fastapi, uvicorn, asyncpg, pydantic, python-dotenv, pywebpush, httpx.

### 2.7 `gateway/` — API Gateway (puerto 8000)

| Atributo | Valor |
|----------|-------|
| **Responsabilidad** | Proxy inverso que rutea peticiones al microservicio correcto + sirve el frontend compilado |
| **Tecnologías clave** | FastAPI, httpx, CORSMiddleware, StreamingResponse (SSE) |
| **Independencia** | Servicio frontal único; punto de entrada para todos los clientes |

**Archivos:**
- `main.py` — Mapa de rutas (`ROUTES`), `proxy_request()` que reenvía al destino, `_proxy_stream()` para streaming SSE, ruta comodín `/{path:path}` (API proxy o SPA), CORS para `localhost:5173`/`localhost:8000`, timeout de cliente 600s, distinción de errores 502/504, montaje de estáticos de `frontend/dist/`.

### 2.8 `seniorvital_shared/` — Librería Compartida

| Atributo | Valor |
|----------|-------|
| **Responsabilidad** | Pool de conexiones PostgreSQL, esquema idempotente, modelos de dominio, publicación de eventos |
| **Uso** | Paquete Python importado por todos los servicios (vía `PYTHONPATH` a la raíz) |
| **Dependencia clave** | asyncpg, pydantic |

**Archivos:**
- `__init__.py` — Exporta `get_pool`, `init_pool`, `close_pool`, `init_db`, `HealthProfile`, `publish_event`.
- `db.py` — Pool singleton con sistema de `owner`. Además define `SCHEMA_SQL` (CREATE TABLE IF NOT EXISTS + ALTER ADD COLUMN IF NOT EXISTS de las 15 tablas) y `init_db()`. Funciones: `init_pool(min_size, max_size, owner)`, `close_pool(owner)`, `get_pool()`, `_get_dsn()` (desde `DATABASE_URL`).
- `models.py` — `HealthProfile` (Pydantic): edad, peso, altura, nivel fitness, metas, restricciones médicas (9 valores permitidos), equipo, horario preferido.
- `events.py` — `publish_event(stream_name, payload)`: inserta en `event_queue`.

### 2.9 `scripts/` — Automatización y Workers

| Atributo | Valor |
|----------|-------|
| **Responsabilidad** | Workers background, scripts de inicio/parada, migraciones, chequeos y smoke tests |
| **Ejecución** | Procesos independientes (workers bucle infinito) o programados (cron) |

**Archivos:**

| Archivo | Tipo | Función |
|---------|------|---------|
| `replicator.py` | Worker (loop 1s) | Lee `ejercicio-completado` de `event_queue`, replica en DuckDB (`raw_events`, `weekly_progress`), marca `processed=true`. |
| `preventive_worker.py` | Worker (loop 2s) | Lee `fatiga-alta` de `event_queue`, loggea alerta, notifica vía notification-service. |
| `weekly_analysis.py` | Programado (lunes 2AM) | Lee DuckDB, llama Ollama para insights, guarda en `projections`, publica `recomendacion-ajuste`. |
| `daily_inactivity.py` | Programado (diario) | Detecta seniors sin tracking en 3+ días, publica `inactividad-detectada`. |
| `quick_check.py` | Manual | Chequeo rápido de integración vía gateway (frontend HTML, rutas SPA, register/login, catálogo, docs). |
| `smoke_test.py` | Manual | Smoke tests por servicio (auth 8001, catalog 8002, routines 8003, tracking 8004, dashboard 8005, notification 8006). |
| `verify_integration.py` | Manual | Verifica que el gateway sirva el frontend y proxye la API correctamente. |
| `fix_db.sql` | SQL | Recrea el esquema completo (DROP + CREATE de las 15 tablas), sincronizado con `init_db.sql`. |
| `start_all.ps1` | Script PowerShell | Inicia los 7 servicios con uvicorn, construye el frontend si no existe `dist/`, guarda PIDs. |
| `start_all.sh` | Script Bash | Equivalente a start_all.ps1. |
| `stop_all.ps1` | Script PowerShell | Detiene servicios por PID, limpia puertos 8000-8006. |
| `stop_all.sh` | Script Bash | Equivalente a stop_all.ps1. |
| `migrations.sql` | SQL | Migraciones ad-hoc (columnas y tablas adicionales). |

### 2.10 `tests/` — Suite de Pruebas

| Atributo | Valor |
|----------|-------|
| **Framework** | pytest 9.x con pytest-asyncio (asyncio_mode=auto) |
| **Cobertura** | 35 tests, 9 archivos de test |
| **Infraestructura** | `init_database` (sesión, recrea esquema con fix_db.sql), `auto_init_pool` (por test), `cleanup` (TRUNCATE de 15 tablas), `load_service_app` (carga dinámica) |

**Archivos:**

| Archivo | Tests | Cobertura |
|---------|-------|-----------|
| `conftest.py` | Fixtures | — |
| `test_auth.py` | 5 | AC-AUTH-01 al 05 |
| `test_catalog.py` | 6 | CRUD + video |
| `test_dashboard.py` | 3 | Progreso, proyección, insights |
| `test_db_conn.py` | 1 | Conexión a la BD |
| `test_notification.py` | 3 | AC-NOT-01, AC-NOT-02 |
| `test_persistence.py` | 4 | AC-PERS-01, 02, 03 |
| `test_routines.py` | 3 | Rutinas IA |
| `test_tracking.py` | 7 | Tracking individual, sin exercise_id, fatiga alta, lote, hábitos |

> El `conftest.py` ejecuta `fix_db.sql` (DROP + CREATE) al inicio de la sesión, por lo que los tests requieren PostgreSQL accesible. Los helpers locales `get_pg_*.py` (recuperación de credenciales) están excluidos del VCS.

### 2.11 `frontend/` — Aplicación SPA

Frontend React 18 + Vite 4 + TypeScript. Consume la API a través del gateway (puerto 8000) y en desarrollo usa el proxy de Vite (puerto 5173 → 8000). Ver **ESTRUCTURA_FRONTEND.md** para el detalle completo.

### 2.12 `storage/` — Almacenamiento Local

| Subcarpeta | Propósito |
|------------|-----------|
| `videos/` | Videos de ejercicios subidos vía catalog-service (archivos .mp4 con nombre UUID) |
| `progress-photos/` | Fotos de progreso (reservado para uso futuro) |

### 2.13 `logs/` — Logs de Servicios

Creado en tiempo de ejecución por `start_all.ps1`/`start_all.sh`. Contiene archivos `.pid` y logs de cada servicio.

### 2.14 Archivos de Configuración Raíz

| Archivo | Propósito |
|---------|-----------|
| `.env` | Variables de entorno locales (no versionado) |
| `.env.example` | Plantilla con valores por defecto |
| `pytest.ini` | `asyncio_mode = auto`, `testpaths = tests` |
| `requirements.txt` | Dependencias globales del proyecto |
| `init_db.sql` | Esquema completo PostgreSQL (15 tablas, índices, triggers) |
| `package.json` | Scripts raíz: `install:frontend`, `build:frontend`, `dev:frontend`, `dev:backend`, `test:frontend` |
| `SDD.md` | System Design Document — fuente de verdad del diseño |
| `AGENTS.md` | Configuración para OpenCode (asistente de desarrollo) |

---

## 3. Descripción Detallada de Cada Archivo

### 3.1 `seniorvital_shared/db.py`

**Funcionalidad:** Pool de conexiones a PostgreSQL singleton con sistema de propietario (owner) y esquema idempotente.

- `init_pool(min_size=2, max_size=10, owner="default")` — Crea el pool si no existe, asigna un owner.
- `close_pool(owner="default")` — Cierra el pool solo si el owner coincide (protección contra cierres accidentales).
- `get_pool()` — Retorna el pool existente o lo inicializa.
- `_get_dsn()` — Construye la cadena desde `DATABASE_URL`.
- `SCHEMA_SQL` — Constante con el DDL de las 15 tablas (CREATE TABLE IF NOT EXISTS + ALTER ADD COLUMN IF NOT EXISTS para BD antiguas).
- `init_db()` — Ejecuta `SCHEMA_SQL` (lo llaman los servicios en su `lifespan`).

**Conexiones:** Importado por todos los microservicios, `tests/conftest.py`, scripts. Depende de `asyncpg`, `os`. Variable de entorno: `DATABASE_URL`.

### 3.2 `seniorvital_shared/models.py`

**Funcionalidad:** Modelo `HealthProfile` (Pydantic BaseModel) que valida el perfil de salud de un adulto mayor:

| Campo | Tipo | Validación |
|-------|------|------------|
| `age` | int | 60 ≤ age ≤ 120 |
| `weight_kg` | float | 30 ≤ weight ≤ 200 |
| `height_cm` | float | 100 ≤ height ≤ 250 |
| `fitness_level` | str | `^(principiante\|intermedio\|avanzado)$` |
| `goals` | List[str] | default [] |
| `medical_restrictions` | List[str] | Solo valores permitidos (9) |
| `equipment` | List[str] | defaults to [] |
| `preferred_schedule` | Optional[str] | Sin restricción |

**Valores permitidos para `medical_restrictions` (constante `VALID_MEDICAL_RESTRICTIONS`):**
`artrosis_rodilla`, `osteoporosis`, `hipertension`, `hipertensión`, `artritis`, `dolor_articular`, `prótesis`, `diabetes`, `cardiopatia`.

**Conexiones:** Usado por `auth-profile-service` (validación en register/profile update) y `tests`.

### 3.3 `seniorvital_shared/events.py`

**Funcionalidad:** Publicación de eventos asíncronos. `publish_event(stream_name, payload)` inserta una fila en `event_queue` con el stream name y el payload serializado a JSON.

**Conexiones:** Usado por `routines-ai-service`, `tracking-service`, scripts. Depende de `db.py` para el pool.

### 3.4 `seniorvital_shared/__init__.py`

**Funcionalidad:** Exporta `get_pool`, `init_pool`, `close_pool`, `init_db`, `HealthProfile`, `publish_event`.

### 3.5 `auth-profile-service/main.py`

**Funcionalidad:** Microservicio completo de autenticación y perfiles.

**Constantes:**
- `JWT_SECRET`: desde variable de entorno, con fallback.
- `JWT_ALG = "HS256"`, `JWT_EXPIRY = timedelta(days=7)`, `REFRESH_EXPIRY`.
- `security = HTTPBearer()`: esquema de seguridad Bearer token.

**Funciones auxiliares:**

| Función | Descripción |
|---------|-------------|
| `create_token(user_id)` | Genera JWT con sub=user_id, exp=now+7d, firmado con HS256 |
| `create_refresh_token(user_id)` | Genera token de refresh con expiración propia |
| `verify_token(credentials)` | Decodifica y valida JWT; raise 401 si inválido |
| `get_current_user(payload)` | Obtiene registro completo de BD desde el sub del token |
| `lifespan(app)` | Inicializa pool, ejecuta `init_db()`, cierra pool al final |

**Modelos Pydantic:**

| Clase | Campos | Uso |
|-------|--------|-----|
| `RegisterRequest` | email: EmailStr, password: str, role: str="senior", profile: Optional[dict] | POST /auth/register |
| `LoginRequest` | email: EmailStr, password: str | POST /auth/login |
| `ProfileUpdate` | profile: dict | PUT /auth/profile |
| `LinkCaregiverRequest` | caregiver_email: EmailStr | POST /auth/link-caregiver |

**Endpoints REST:**

| Método | Ruta | Función | Validaciones Clave |
|--------|------|---------|-------------------|
| POST | `/auth/register` | `register()` | role en (senior,caregiver,admin), email único, profile válido, bcrypt hash, constraint `check_nombres` |
| POST | `/auth/login` | `login()` | bcrypt verify, devuelve access + refresh token |
| POST | `/auth/refresh` | `refresh()` | Valida refresh token, emite nuevos tokens |
| GET | `/auth/me` | `get_me()` | Requiere token Bearer |
| PUT | `/auth/profile` | `update_profile()` | Solo senior/admin, HealthProfile validation |
| POST | `/auth/link-caregiver` | `link_caregiver()` | Solo senior, máx 3 caregivers, caregiver único |
| GET | `/caregiver/seniors` | `list_seniors()` | Seniors vinculados al cuidador |
| POST | `/caregiver/link` | `link()` | Vinculación cuidador-senior |
| GET | `/caregiver/alerts` | `get_alerts()` | Alertas del cuidador |
| GET | `/caregiver/reports` | `get_reports()` | Reporte de 30 días |
| GET | `/caregiver/senior/{id}/progress` | `get_senior_progress()` | Progreso de un senior vinculado |
| GET | `/admin/users` | `list_users()` | Listar usuarios (admin) |
| PUT | `/admin/users/{id}/routine-override` | `override_routine()` | Anular rutina (admin) |

**Conexiones:**
- `seniorvital_shared`: `get_pool`, `init_pool`, `close_pool`, `init_db`, `HealthProfile`
- `passlib.hash.bcrypt`, `jose.jwt`, `jose.JWTError`, `fastapi.security.HTTPBearer`

### 3.6 `catalog-service/main.py`

**Funcionalidad:** CRUD de ejercicios + subida y servicio de videos.

**Modelos:** `ExerciseCreate` (name, level 1-4, contraindications[], video_url?) y `ExerciseUpdate` (todos opcionales).

**Endpoints:**

| Método | Ruta | Función |
|--------|------|---------|
| GET | `/catalog/exercises` | `list_exercises()` — filtros por level y name (ILIKE) |
| POST | `/catalog/exercises` | `create_exercise()` — valida level 1-4, HTTP 201 |
| GET | `/catalog/exercises/{id}` | `get_exercise()` — HTTP 404 si no existe |
| PUT | `/catalog/exercises/{id}` | `update_exercise()` — actualización parcial |
| DELETE | `/catalog/exercises/{id}` | `delete_exercise()` — HTTP 404 si no existe |
| POST | `/catalog/exercises/{id}/video` | `upload_video()` — MP4, max 50MB, guarda en storage/videos/ |
| GET | `/storage/videos/{filename}` | `serve_video()` — FileResponse video/mp4 |

**Conexiones:** `seniorvital_shared` (pool), `aiofiles` (escritura asíncrona), `uuid` (nombres únicos), almacenamiento en `storage/videos/`.

### 3.7 `routines-ai-service/main.py`

**Funcionalidad:** Generación de rutinas personalizadas usando Ollama (phi3:mini), con streaming y fallback.

**Componentes clave:**

| Elemento | Descripción |
|----------|-------------|
| `OLLAMA_URL` | `http://localhost:11434` (configurable vía env) |
| `OLLAMA_MODEL` | `phi3:mini` |
| `OLLAMA_TIMEOUT` | 600 s |
| `DEFAULT_ROUTINE` | Rutina de fallback: 3 ejercicios + 1 warmup |
| `GenerateRequest` | user_id + force (bool) |
| `call_ollama(prompt)` | Cliente HTTP asíncrono a Ollama `/api/generate` |
| `call_ollama_stream(prompt)` | Streaming de tokens con httpx `client.stream` |
| `build_prompt(profile, health_profile, preferences, safe_exercises)` | Prompt con perfil completo + ejercicios seguros |
| `map_exercises(exercises)` | Normaliza el formato BD → formato frontend |
| `_clean_ollama_response(text)` | Extrae JSON válido (quita fences, comentarios, comas finales) |

**Flujo de `POST /routines/generate`:**
1. Obtener usuario de BD → 404 si no existe
2. Si `force=false` y ya hay rutina activa para hoy, retornarla (con `generated_by` persistido)
3. Construir prompt con perfil de salud, preferencias y ejercicios seguros
4. Llamar a Ollama; si falla (timeout/conexión/JSON inválido) usar `DEFAULT_ROUTINE` con `generated_by='fallback'`
5. Insertar en tabla `routines` (con `generated_by='ollama'` o `'fallback'`)
6. Publicar evento `rutina-generada`
7. Retornar rutina con `llm_available`, `llm_model`, `llm_error`, `generated_by`

**Flujo de `POST /routines/generate-stream`:**
1. Igual obtención de datos; emite eventos SSE: `progress` (5 pasos) → `complete` (rutina) → `error`.
2. El gateway lo proxya con `StreamingResponse` y timeout de 600s.
3. Si ya existe rutina para hoy, emite `complete` con la cacheada.

**Conexiones:** Ollama `POST /api/generate` con httpx; `seniorvital_shared` (pool + `publish_event`); tablas `users`, `exercises`, `routines`, `event_queue`.

### 3.8 `tracking-service/main.py`

**Funcionalidad:** Registro de ejercicios completados y hábitos diarios con publicación de eventos.

**Modelos:** `TrackEntry` (user_id, exercise_id, sets, reps, rpe?, felt_difficulty?, completed_at?) y `BatchTrackRequest` (lista de TrackEntry).

**Flujo de `POST /tracking/record`:**
1. Verificar si `exercise_id` existe en `exercises`; si no, usar `NULL` (normalización FK, evita fallos con rutinas generadas por IA).
2. Insertar en tabla `tracking`.
3. Publicar evento `ejercicio-completado`.
4. Si rpe >= 8, publicar evento `fatiga-alta`.
5. Todo en una sola transacción PostgreSQL.

**Flujo de `POST /tracking/batch`:** Mismo comportamiento, iterando sobre cada entrada.

**Endpoints de hábitos:** `GET /habits/today` (consulta del día) y `POST /habits` (upsert de agua y sueño).

**Conexiones:** `seniorvital_shared` (pool); tablas `tracking`, `habits`, `event_queue`; FK `tracking.user_id → users.id`, `tracking.exercise_id → exercises.id`.

### 3.9 `dashboard-service/main.py`

**Funcionalidad:** Consultas de progreso, proyecciones e insights.

**Endpoints:**

| Ruta | Función | Lógica |
|------|---------|--------|
| `GET /dashboard/progress/{user_id}` | `get_progress()` | Calendario semanal de reps, tendencia RPE, racha de días consecutivos, `sessions_this_week` (7 días), `total_sessions` (histórico) |
| `GET /dashboard/projection/{user_id}` | `get_projection()` | Última fila de `projections` ordenada por week_start DESC |
| `GET /dashboard/insights/{user_id}` | `get_insights()` | Historial de insights |

**Cálculo de racha:** Itera hacia atrás desde hoy contando días con al menos un registro en tracking (DISTINCT por `completed_at::date`).

**Conexiones:** `seniorvital_shared` (pool), tablas `users`, `tracking`, `projections`.

### 3.10 `notification-service/main.py`

**Funcionalidad:** Suscripción y envío de notificaciones Web Push.

**Modelos:** `SubscribeRequest` (user_id, subscription) y `SendNotificationRequest` (user_id, title, body).

**Componentes:**

| Elemento | Descripción |
|----------|-------------|
| `VAPID_PUBLIC_KEY` / `VAPID_PRIVATE_KEY` | Claves VAPID para Web Push |
| `VAPID_CLAIM_EMAIL` | Email para el claim sub de VAPID |
| `subscribe()` | Upsert en `push_subscriptions` |
| `send_push_notification()` | Busca suscripción, envía vía pywebpush, elimina si 410 Gone |
| `send_notification()` | Encola la función como BackgroundTask de FastAPI |

**Conexiones:** `pywebpush.webpush`; `seniorvital_shared` (pool); tabla `push_subscriptions`.

### 3.11 `gateway/main.py`

**Funcionalidad:** Proxy inverso que reenvía peticiones al microservicio correcto y sirve el frontend compilado.

**Mapa de rutas:**

| Prefijo | Destino |
|---------|---------|
| `/auth/` | `http://localhost:8001` |
| `/caregiver/` | `http://localhost:8001` |
| `/admin/` | `http://localhost:8001` |
| `/catalog/` | `http://localhost:8002` |
| `/routines/` | `http://localhost:8003` |
| `/tracking/` | `http://localhost:8004` |
| `/habits` | `http://localhost:8004` |
| `/dashboard/` | `http://localhost:8005` |
| `/notify/` | `http://localhost:8006` |
| `/storage/` | `http://localhost:8002` |

**Flujo de `proxy_request()`:**
1. Identificar prefijo en ROUTES.
2. Construir URL destino y reenviar método, body, headers y query params.
3. Devolver la respuesta del microservicio (normalizando no-JSON a `{"detail": ...}`).
4. HTTP 502 si el servicio no responde; HTTP 504 si hay timeout (con sugerencia del endpoint streaming).

**Flujo de `_proxy_stream()`:** Proxya SSE `/routines/generate-stream` con `StreamingResponse` y `httpx.stream` (timeout 600s), reenviando chunks sin bufferizar.

**Estáticos y SPA:** En producción monta `/assets` y sirve `index.html` para cualquier ruta no-API (SPA fallback).

**Conexiones:** `httpx.AsyncClient`, `CORSMiddleware`, `StaticFiles`/`FileResponse`.

### 3.12 `scripts/replicator.py`

**Funcionalidad:** Bucle infinito (1s) que replica eventos `ejercicio-completado` desde PostgreSQL a DuckDB.

**Flujo:** `ensure_duckdb_schema()` (tablas `raw_events` y `weekly_progress`) → `process_events()` (consulta `event_queue` con `stream_name='ejercicio-completado'`, `processed=FALSE`, LIMIT 100) → inserta en `raw_events`, actualiza `weekly_progress` (INSERT OR REPLACE), marca `processed=TRUE`. Si DuckDB falla, no marca como procesado (reintento).

**Conexiones:** asyncpg (PostgreSQL), duckdb, `seniorvital_analytics.duckdb`.

### 3.13 `scripts/preventive_worker.py`

**Funcionalidad:** Bucle infinito (2s) que procesa eventos `fatiga-alta`.

**Flujo:** Consulta `event_queue` (`stream_name='fatiga-alta'`, `processed=FALSE`, LIMIT 50) → loggea alerta → notifica vía `POST http://localhost:8006/notify/send` → marca como procesado.

### 3.14 `scripts/weekly_analysis.py`

**Funcionalidad:** Análisis semanal (ejecución única, diseñado para cron los lunes 2AM).

**Flujo:** Conecta DuckDB, obtiene usuarios con datos en `weekly_progress` → por cada usuario calcula promedio semanal y llama Ollama para generar insight → guarda en `projections` (PostgreSQL) → publica `recomendacion-ajuste`.

**Conexiones:** asyncpg (PostgreSQL), duckdb, httpx (Ollama).

### 3.15 `scripts/daily_inactivity.py`

**Funcionalidad:** Detección diaria de inactividad (ejecución única).

**Flujo:** Busca seniors sin registros en `tracking` en los últimos 3 días → por cada inactivo publica `inactividad-detectada`.

### 3.16 `scripts/quick_check.py` y `scripts/smoke_test.py`

- `quick_check.py` — Verifica vía gateway (8000): HTML del frontend, rutas SPA, register/login, `/catalog/exercises`, `/docs`, `/auth/me` con token.
- `smoke_test.py` — Verifica cada servicio por su puerto directo (8001-8006): registro, login, CRUD de catálogo, rutinas, tracking, dashboard, notificaciones.

### 3.17 `tests/conftest.py`

**Funcionalidad:** Configuración compartida de pytest.

| Elemento | Descripción |
|----------|-------------|
| `load_service_app(name)` | Carga dinámicamente el `main.py` de un servicio y retorna `app` |
| `init_database` (fixture de sesión) | DROP SCHEMA, ejecuta `scripts/fix_db.sql`, cierra pool |
| `auto_init_pool` (fixture autouse) | Inicializa pool BD con owner="test" antes de cada test |
| `cleanup` (fixture autouse) | TRUNCATE de las 15 tablas después de cada test |

**Conexiones:** Usado por todos los test files. Fija `DATABASE_URL` y carga `.env`.

---

## 4. Mapa de Relaciones y Vínculos

### 4.1 Diagrama de Arquitectura General

```
┌──────────────┐     ┌────────────────────────────────────────────────────────────┐
│   Cliente    │     │                    API Gateway (:8000)                     │
│  (React SPA) │────▶│  Proxy REST + Proxy SSE (streaming) + estáticos frontend   │
└──────────────┘     └──┬───────┬───────┬───────┬───────┬───────┬───────┬──────────┘
                        │       │       │       │       │       │       │
              ┌─────────┤       │       │       │       │       │       ├──────────┐
              ▼         ▼       ▼       ▼       ▼       ▼       ▼       ▼
        ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌─────────┐ ┌────────┐ ┌────────┐
        │ Auth   │ │Catalog │ │Routines│ │Tracking│ │Dashboard│ │ Notif. │ │Storage │
        │ :8001  │ │ :8002  │ │ :8003  │ │ :8004  │ │ :8005   │ │ :8006  │ │ :8002  │
        └───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘ └───┬─────┘ └───┬────┘ └────────┘
            │          │          │          │          │           │
            └──────────┼──────────┼──────────┼──────────┼───────────┘
                       │          │          │          │
              ┌────────▼──────────▼──────────▼──────────▼──────────┐
              │                PostgreSQL (:5432)                  │
              │  users, tracking, routines, exercises, habits,     │
              │  projections, caregiver_links, workout_*,          │
              │  push_subscriptions, event_queue, agent_*,         │
              │  admin_logs                                        │
              └────────┬──────────┬──────────┬─────────────────────┘
                       │          │          │
                       ▼          ▼          ▼
                 ┌─────────┐ ┌────────┐ ┌────────────┐
                 │DuckDB   │ │ Ollama │ │  Workers   │
                 │analytics│ │:11434  │ │replicator  │
                 └─────────┘ └────────┘ │preventive  │
                                        │weekly_an.  │
                                        │daily_inact.│
                                        └────────────┘
```

### 4.2 Flujo de Autenticación (JWT + bcrypt)

```
┌──────────┐     ┌──────────────────┐     ┌──────────────┐     ┌────────────┐
│ Cliente  │     │  Auth Service    │     │  passlib     │     │ PostgreSQL │
│          │     │    (:8001)       │     │  (bcrypt)    │     │            │
└────┬─────┘     └────────┬─────────┘     └──────┬───────┘     └─────┬──────┘
     │                    │                      │                   │
     │ POST /auth/register│                      │                   │
     │ {email,password,   │                      │                   │
     │  role,nombre_*}    │                      │                   │
     │───────────────────▶│                      │                   │
     │                    │  bcrypt.hash(pw)     │                   │
     │                    │─────────────────────▶│                   │
     │                    │◀─────────────────────│                   │
     │                    │  "$2b$12$..."        │                   │
     │                    │                      │                   │
     │                    │  INSERT INTO users   │                   │
     │                    │─────────────────────────────────────────▶│
     │  {id, email, role} │                      │                   │
     │◀───────────────────│                      │                   │
     │                    │                      │                   │
     │ POST /auth/login   │                      │                   │
     │ {email,password}   │                      │                   │
     │───────────────────▶│                      │                   │
     │                    │  SELECT * FROM users │                   │
     │                    │  WHERE email=...     │                   │
     │                    │─────────────────────────────────────────▶│
     │                    │◀─────────────────────────────────────────│
     │                    │  {id, password_hash, ...}                │
     │                    │                      │                   │
     │                    │  bcrypt.verify(pw,   │                   │
     │                    │    password_hash)    │                   │
     │                    │─────────────────────▶│                   │
     │                    │◀─────────────────────│                   │
     │                    │  True                │                   │
     │                    │                      │                   │
     │                    │  create_token(id)    │                   │
     │                    │  jwt.encode(...HS256)│                   │
     │ {access_token,     │                      │                   │
     │  refresh_token}    │                      │                   │
     │◀───────────────────│                      │                   │
     │                    │                      │                   │
     │ GET /auth/me       │                      │                   │
     │ Authorization:     │                      │                   │
     │ Bearer <token>     │                      │                   │
     │───────────────────▶│  jwt.decode(token)   │                   │
     │                    │  → {sub: user_id}    │                   │
     │                    │  SELECT * FROM users │                   │
     │                    │─────────────────────────────────────────▶│
     │                    │◀─────────────────────────────────────────│
     │ {id,email,role,    │                      │                   │
     │  profile,health...}│                      │                   │
     │◀───────────────────│                      │                   │
```

### 4.3 Comunicación entre Microservicios

| Origen | Destino | Método | Propósito |
|--------|---------|--------|-----------|
| Gateway (:8000) | Auth (:8001) | Proxy | Ruteo de `/auth/*`, `/caregiver/*`, `/admin/*` |
| Gateway (:8000) | Catalog (:8002) | Proxy | Ruteo de `/catalog/*` y `/storage/*` |
| Gateway (:8000) | Routines (:8003) | Proxy | Ruteo de `/routines/*` + streaming SSE |
| Gateway (:8000) | Tracking (:8004) | Proxy | Ruteo de `/tracking/*` y `/habits*` |
| Gateway (:8000) | Dashboard (:8005) | Proxy | Ruteo de `/dashboard/*` |
| Gateway (:8000) | Notification (:8006) | Proxy | Ruteo de `/notify/*` |
| Routines (:8003) | Ollama (:11434) | HTTP POST | Generación de rutinas (streaming) |
| Preventive Worker | Notification (:8006) | HTTP POST | Alerta de fatiga alta |
| Weekly Analysis | Ollama (:11434) | HTTP POST | Generación de insights |
| Tracking (:8004) | event_queue (PG) | INSERT | Publicación de eventos |
| Routines (:8003) | event_queue (PG) | INSERT | Publicación de eventos |
| Replicator | event_queue (PG) | SELECT/UPDATE | Consumo de eventos |
| Preventive Worker | event_queue (PG) | SELECT/UPDATE | Consumo de eventos |
| Replicator | DuckDB | INSERT | Replicación analítica |
| Weekly Analysis | DuckDB | SELECT | Consulta analítica |

### 4.4 Eventos Asíncronos (tabla `event_queue`)

```
┌────────────────────────────────────────────────────────────────────┐
│                      event_queue (PostgreSQL)                      │
│  id SERIAL | stream_name TEXT | payload JSONB | processed BOOL     │
│  created_at | processed_at                                         │
└────────────────────────────────────────────────────────────────────┘

Productores:
  tracking-service ───▶ "ejercicio-completado" ──▶ replicator (DuckDB)
  tracking-service ───▶ "fatiga-alta" ───────────▶ preventive_worker
  routines-ai-service ▶ "rutina-generada" ──────── (sin consumidor)
  daily_inactivity.py ▶ "inactividad-detectada" ── (sin consumidor)
  weekly_analysis.py ─▶ "recomendacion-ajuste" ── (sin consumidor)
```

### 4.5 Tabla de Referencia Cruzada de Archivos

| Archivo | Importa de | Es importado por |
|---------|-----------|-----------------|
| `seniorvital_shared/db.py` | asyncpg, os | Todos los servicios, tests |
| `seniorvital_shared/models.py` | pydantic | auth-profile-service, tests |
| `seniorvital_shared/events.py` | json, .db | routines-ai-service, tracking-service, scripts |
| `seniorvital_shared/__init__.py` | .db, .models, .events | Todos |
| `auth-profile-service/main.py` | seniorvital_shared, passlib, jose | tests/conftest (load_service_app) |
| `catalog-service/main.py` | seniorvital_shared, aiofiles | tests/conftest |
| `routines-ai-service/main.py` | seniorvital_shared, httpx | tests/conftest |
| `tracking-service/main.py` | seniorvital_shared | tests/conftest |
| `dashboard-service/main.py` | seniorvital_shared | tests/conftest |
| `notification-service/main.py` | seniorvital_shared, pywebpush | tests/conftest |
| `gateway/main.py` | httpx, fastapi.middleware.cors | — |
| `tests/conftest.py` | seniorvital_shared, importlib | tests/test_*.py |

### 4.6 Esquema de Base de Datos (PostgreSQL + JSONB)

```
┌─────────────────┐       ┌──────────────────┐       ┌──────────────────┐
│     users       │       │    tracking      │       │    routines      │
├─────────────────┤       ├──────────────────┤       ├──────────────────┤
│ id SERIAL (PK)  │◄──────┤ user_id (FK)     │       │ user_id (FK)     │◄──────┐
│ email TEXT UNQ  │       │ exercise_id FK   │       │ date DATE        │       │
│ role TEXT       │       │ sets INT         │       │ exercises JSONB  │       │
│ profile JSONB   │       │ reps INT         │       │ warmup TEXT      │       │
│ password TEXT   │       │ rpe INT (1-10)   │       │ active BOOL      │       │
│ nombre_senior   │       │ felt_difficulty  │       │ generated_by TEXT│       │
│ nombre_cuidador │       │ completed_at     │       │ created_at       │       │
│ health_profile  │       └──────────────────┘       └──────────────────┘       │
│ preferences     │         ┌──────────────────┐      ┌──────────────────┐      │
│ linked_senior_id│         │  exercises       │      │  projections     │      │
│ is_active       │         ├──────────────────┤      ├──────────────────┤      │
│ created_at      │         │ id SERIAL (PK)   │      │ user_id (FK)     │◄─────┘
│ updated_at      │         │ name TEXT        │      │ week_start DATE  │
└─────────────────┘         │ level INT (1-4)  │      │ insight_text TEXT│
        │                   │ contraindications│      │ estimated_level  │
        │◄──────────────────│ video_url TEXT   │      └──────────────────┘
        │   (linked_senior_id) └──────────────────┘
        │
        │         ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
        │         │  caregiver_links │   │    habits        │   │push_subscriptions │
        │         ├──────────────────┤   ├──────────────────┤   ├──────────────────┤
        │         │ caregiver_user_id│   │ user_id (FK)     │   │ user_id TEXT (PK)│
        │         │ senior_user_id   │   │ date DATE        │   │ endpoint TEXT    │
        │         │ status           │   │ water_intake_gl. │   │ p256dh TEXT      │
        │         └──────────────────┘   │ sleep_hours      │   │ auth TEXT        │
        │                                └──────────────────┘   └──────────────────┘
        │
        │         ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
        │         │ workout_sessions │   │ workout_exercises│   │ workout_sets     │
        │         ├──────────────────┤   ├──────────────────┤   ├──────────────────┤
        │         │ user_id (FK)     │──▶│ session_id (FK)  │──▶│ workout_exercise_│
        │         │ scheduled_date   │   │ exercise_id (FK) │   │ id (FK)          │
        │         │ started_at       │   │ order_number     │   │ set_number, reps │
        │         │ completed_at     │   │ progression_lvl  │   │ weight_kg, rpe   │
        │         └──────────────────┘   └──────────────────┘   │ rest_duration_sec│
        │                                                     └──────────────────┘
        │         ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
        │         │  event_queue     │   │  agent_queue     │   │  agent_insights  │
        │         ├──────────────────┤   ├──────────────────┤   ├──────────────────┤
        │         │ stream_name TEXT │   │ command_type TEXT│   │ user_id (FK)     │
        │         │ payload JSONB    │   │ payload JSONB    │   │ insight_type     │
        │         │ processed BOOL   │   │ status           │   │ message TEXT     │
        │         │ created_at       │   │ error_message    │   │ displayed BOOL   │
        │         └──────────────────┘   └──────────────────┘   └──────────────────┘
        │         ┌──────────────────┐
        │         │  admin_logs      │
        │         ├──────────────────┤
        │         │ admin_user_id FK │
        │         │ action TEXT      │
        │         │ target_user_id FK│
        │         │ details JSONB    │
        │         └──────────────────┘
```

### 4.7 Interacción con Ollama

```
┌──────────────────────┐       ┌──────────────────┐       ┌──────────────┐
│ routines-ai-service  │──────▶│   Ollama Server  │◀──────│weekly_analysis│
│ (:8003)              │ HTTP  │   (:11434)       │ HTTP  │   (.py)      │
│                      │ POST  │                  │ POST  │              │
│ POST /routines/      │──────▶│ POST /api/       │◀──────│              │
│ generate             │       │ generate         │       │              │
│ POST /routines/      │──────▶│ (stream)         │       │ Prompt de    │
│ generate-stream (SSE)│       │                  │       │ análisis     │
│                      │       │ Modelo:          │       │ semanal      │
│ Prompt construido    │       │ phi3:mini        │       │              │
│ con perfil de salud  │       │ format=json      │       │ Fallback:    │
│ + preferencias       │       │ num_predict=600  │       │ insight por  │
│ + ejercicios seguros │       │ temperature=0.2  │       │ defecto      │
│                      │       │                  │       │              │
│ Fallback:            │       │ Respuesta:       │       │              │
│ DEFAULT_ROUTINE      │       │ JSON con rutina  │       │              │
│ si Ollama no responde│       │ o insight        │       │              │
└──────────────────────┘       └──────────────────┘       └──────────────┘
```

### 4.8 Pipeline de Pruebas

```
tests/conftest.py
│
├── init_database (sesión) — DROP SCHEMA + fix_db.sql (15 tablas)
│
├── load_service_app("auth-profile-service")  →  test_auth.py (5)
├── load_service_app("catalog-service")       →  test_catalog.py (6)
├── load_service_app("dashboard-service")     →  test_dashboard.py (3)
├── load_service_app("notification-service")  →  test_notification.py (3)
├── load_service_app("routines-ai-service")   →  test_routines.py (3)
├── load_service_app("tracking-service")      →  test_tracking.py (7)
│
├── auto_init_pool (autouse)
│   └── init_pool(owner="test") → get_pool() para BD real
│
├── cleanup (autouse)
│   └── TRUNCATE de las 15 tablas RESTART IDENTITY CASCADE
│
└── test_persistence.py (4) + test_db_conn.py (1)
    └── usan seniorvital_shared.HealthProfile + get_pool() directamente
```

---

## 5. Resumen de Puertos y Servicios

| Puerto | Servicio | Tecnología | Dependencia Externa |
|--------|----------|-----------|-------------------|
| 8000 | API Gateway | FastAPI + httpx + StreamingResponse | — |
| 8001 | Auth Profile | FastAPI + bcrypt + JWT | PostgreSQL |
| 8002 | Catalog | FastAPI + aiofiles | PostgreSQL, filesystem |
| 8003 | Routines AI | FastAPI + httpx + SSE | PostgreSQL, Ollama |
| 8004 | Tracking | FastAPI + asyncpg | PostgreSQL |
| 8005 | Dashboard | FastAPI + asyncpg | PostgreSQL, DuckDB |
| 8006 | Notification | FastAPI + pywebpush | PostgreSQL |
| 5432 | PostgreSQL | asyncpg | — |
| 11434 | Ollama | httpx | Modelo phi3:mini |

---

## 6. Variables de Entorno (`.env`)

| Variable | Default | Usada por |
|----------|---------|-----------|
| `DATABASE_URL` | `postgresql://postgres:...@localhost:5432/seniorvital` | Todos los servicios y scripts |
| `OLLAMA_URL` | `http://localhost:11434` | routines-ai-service, weekly_analysis |
| `OLLAMA_MODEL` | `phi3:mini` | routines-ai-service |
| `OLLAMA_TIMEOUT` | `600` | routines-ai-service |
| `JWT_SECRET` | *(configurable)* | auth-profile-service |
| `VAPID_PUBLIC_KEY` | *(configurable)* | notification-service |
| `VAPID_PRIVATE_KEY` | *(configurable)* | notification-service |
| `VAPID_CLAIM_EMAIL` | *(configurable)* | notification-service |

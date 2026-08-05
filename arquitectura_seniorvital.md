# Arquitectura de SeniorVital

Guía de exposición del desarrollo full stack. Explica cómo está construida la plataforma, qué decisiones se tomaron y por qué.

---

## 1. Resumen ejecutivo

**SeniorVital** es una plataforma web para el bienestar de adultos mayores que combina:

- Una **aplicación de ejercicios** guiada, accesible y sencilla (pensada para usuarios no técnicos).
- **Inteligencia artificial local** (modelo `phi3:mini` vía Ollama) que genera una rutina de ejercicios **personalizada** según el perfil de salud, edad, objetivos y restricciones médicas de cada persona.
- **Monitoreo de progreso**: registro de series completadas, percepción de esfuerzo (RPE), hábitos de agua y sueño, y dashboards para cuidadores y administradores.

La plataforma es **full stack**, con un frontend en React/TypeScript y un backend compuesto por microservicios en Python (FastAPI) que hablan con PostgreSQL.

---

## 2. Arquitectura general

SeniorVital usa una arquitectura **microservicios con API Gateway**, dividida en dos dominios de comunicación:

- **Sincrónico (request/response)**: el frontend habla siempre con un único punto de entrada (el gateway), que redirige cada petición al microservicio correspondiente según el prefijo de la URL.
- **Asíncrono (eventos)**: los servicios publican eventos en una tabla `event_queue` de PostgreSQL (en lugar de Redis). Workers de fondo (replicador, preventivo, análisis semanal) los consumen.

### Diagrama de componentes

```
┌──────────────┐   HTTP/SSE (JSON)   ┌──────────────────────┐
│   Frontend   │────────────────────►│  API Gateway (8000)   │
│  React + Vite│◄────────────────────│  proxy + estáticos    │
└──────────────┘                     └──────────┬───────────┘
                                                │ enruta por prefijo de URL
        ┌──────────┬──────────┬──────────┬──────┴───────┬───────────┬───────────┐
        ▼          ▼          ▼          ▼              ▼           ▼           ▼
  Auth/Profile  Catalog   Routines-AI  Tracking     Dashboard   Notifications
    (8001)      (8002)      (8003)     (8004)         (8005)       (8006)
    usuarios     ejercicios  Ollama     series/hábitos  analítica    Web Push
        │          │          │          │              │            │
        └──────────┴──────────┴──────────┴──────────────┴────────────┘
                                    │
                               PostgreSQL
                           (15 tablas + event_queue)

   Ollama phi3:mini (11434) ◄────────── Routines-AI (8003) — IA local
```

### Tabla de servicios

| Servicio | Puerto | Responsabilidad |
|----------|--------|-----------------|
| Gateway | 8000 | Proxy de API, sirve el frontend compilado, streaming SSE |
| Auth/Profile | 8001 | Registro/login JWT, perfiles senior/cuidador/admin, vínculos |
| Catalog | 8002 | Catálogo de ejercicios y almacenamiento de videos |
| Routines-AI | 8003 | Generación de rutinas con Ollama + fallback |
| Tracking | 8004 | Registro de series y hábitos; publica eventos |
| Dashboard | 8005 | Consultas de progreso y analítica |
| Notification | 8006 | Notificaciones Web Push |

---

## 3. Frontend

- **Framework**: React 18 + Vite 4 + TypeScript 5.3.
- **Estado**: `zustand` (auth y cola offline) + `@tanstack/react-query` (cache de datos del servidor, con `staleTime` de 5 minutos).
- **Formularios**: `react-hook-form` + `zod` (validación de tipos en el cliente).
- **Estilos**: Tailwind CSS con componentes de accesibilidad propios (`AccessibleButton`, `RpeScale`, `RestTimer`, `TrafficLight`).
- **Gráficas**: Recharts (progreso).
- **Accesibilidad**: pantallas optimizadas para adultos mayores — botones grandes (touch targets ≥ 56px), textos aumentados, emojis, anuncios de voz y vibración.
- **Routing**: React Router con lazy loading por página y rutas protegidas por rol (`senior`, `caregiver`, `admin`).

### Flujo principal de usuario (senior)

```
Login → HealthProfileOnboarding (edad, salud, objetivos)
     → /routine   (rutina del día generada por IA)
     → /habits    (agua, sueño)
     → /progress  (gráficas de progreso)
```

En el frontend, todas las llamadas pasan por un helper `api()` (`services/api.ts`) que agrega el token JWT automáticamente, reintenta con el token de refresh ante un 401, y mantiene una **cola offline** (`offlineStore`) para reintentar registros cuando hay red.

---

## 4. Backend

> Corrección respecto a la plantilla genérica: el backend **no** usa Node.js/Express ni MySQL. Está construido en **Python 3.12 con FastAPI**, con **asyncpg** (pool de conexiones) y **PostgreSQL**.

Cada microservicio comparte una estructura común:

- **`main.py`**: define la app FastAPI, los endpoints (rutas) y la lógica de negocio (controladores ligeros).
- **`seniorvital_shared/db.py`**: biblioteca compartida con el **pool de conexiones** singleton y el **esquema de base de datos** (`SCHEMA_SQL`). Todos los servicios ejecutan `init_db()` al arrancar (CREATE IF NOT EXISTS + ALTER ADD COLUMN IF NOT EXISTS), garantizando un esquema consistente sin migraciones manuales.
- **`gateway/main.py`**: tabla `ROUTES` que mapea prefijos de URL a servicios:

```python
ROUTES = {
    "/auth/":     "http://localhost:8001",
    "/catalog/":  "http://localhost:8002",
    "/routines/": "http://localhost:8003",
    "/tracking/": "http://localhost:8004",
    "/habits":    "http://localhost:8004",
    "/dashboard/": "http://localhost:8005",
    "/notify/":   "http://localhost:8006",
}
```

El gateway reenvía la petición con `httpx`, normaliza errores a JSON y distingue **502** (servicio caído) de **504** (timeout).

### Conexión a base de datos

```python
import asyncpg
pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=10)
```

Cada microservicio usa `asyncpg` (postgres driver asíncrono) sobre el puerto 5432, con `async with pool.acquire() as conn:` para ejecutar consultas parametrizadas (seguras frente a inyección SQL).

---

## 5. Integración con IA (Ollama phi3:mini)

### Comunicación backend ↔ Ollama

El servicio `routines-ai-service` (8003) se comunica con Ollama por **HTTP REST** en `http://localhost:11434` mediante el endpoint `/api/generate`:

```python
payload = {
    "model": "phi3:mini",
    "prompt": prompt,
    "stream": True,          # streaming de tokens
    "format": "json",        # forzar salida JSON
    "options": {
        "num_predict": 600,
        "temperature": 0.2,  # baja = salida determinista
        "top_p": 0.9,
        "num_ctx": 4096,
    },
}
```

- **Streaming**: `client.stream("POST", ...)` y se leen líneas a medida que el modelo las genera (`aiter_lines`).
- **Timeout**: `OLLAMA_TIMEOUT = 600` segundos — la generación en CPU pura de `phi3:mini` es lenta (puede tardar 1 a 5 minutos).
- **Health check**: el endpoint `/ollama/status` consulta `/api/tags` (ligero) en lugar de generar texto, para verificar disponibilidad en milisegundos.

### Qué datos del usuario se envían al modelo

El prompt se construye con `build_prompt()` a partir del perfil de salud (`health_profile`), el perfil (`profile`) y las preferencias:

- Edad, nivel de condición física.
- Objetivos (p. ej. "mejorar equilibrio").
- Equipo disponible, condiciones médicas, medicamentos.
- Restricciones y contraindicaciones.
- Horarios de sueño y duración preferida de la rutina.
- Ejercicios favoritos y a evitar.
- Catálogo de ejercicios **seguros** (sin contraindicaciones) para que el modelo responda usando IDs válidos.

> El prompt es la parte más importante: pide explícitamente **solo JSON válido** con estructura `{exercises: [...], warmup: [...]}`.

### Procesamiento de la respuesta

1. `call_ollama()` acumula y **limpia** la respuesta (quita bloques ```json, comentarios `//` y comas finales) con `_clean_ollama_response()`.
2. Se parsea con `json.loads`. Si falla el parseo, se marca `llm_available = False`.
3. `map_exercises()` normaliza el formato BD → formato esperado por el frontend (`reps_per_set`, `rest_duration_sec`, `order_number`, etc.).
4. La rutina se **persiste** en la tabla `routines` con `generated_by = 'ollama'`:

```sql
INSERT INTO routines (user_id, date, exercises, warmup, generated_by)
VALUES ($1, CURRENT_DATE, '[...JSON...]', '...', 'ollama');
```

5. Se publica el evento `rutina-generada` en `event_queue` para notificaciones/replicación.
6. La respuesta API incluye `generated_by: 'ollama' | 'fallback'`, `llm_available`, `llm_model` y `llm_error`.

### Manejo de fallback

Si Ollama **no responde** (timeout, error de conexión, JSON inválido), el servicio usa `DEFAULT_ROUTINE` (una rutina genérica de 3 ejercicios suaves: caminata, estiramiento, respiración) y la guarda con `generated_by = 'fallback'`. El frontend muestra:

- Con IA: *"Rutina generada con IA (Ollama phi3:mini)"*.
- Fallback: *"Rutina predeterminada (IA no disponible)"*.

---

## 6. Interacción entre servicios: flujo completo de una rutina

Flujo desde que el usuario pide la rutina hasta que la recibe:

```
1. Frontend  GET /routines/today?user_id=X     (¿ya hay rutina para hoy?)
       │
       ▼
2. Gateway   /routines/ → 8003   (proxy)
       │
       ▼
3. Routines-AI  ¿Existe rutina activa para hoy?
       │
       ├─ SÍ  → responde 200 con la rutina cacheada (generated_by persistido)
       │
       └─ NO  → construye prompt (perfil + ejercicios seguros)
              → POST http://localhost:11434/api/generate  (streaming)
              → acumula tokens, limpia y parsea JSON
              → INSERT en routines + evento rutina-generada en event_queue
              → responde la rutina
       │
       ▼
4. Gateway   reenvía la respuesta (JSON o SSE streaming)
       │
       ▼
5. Frontend  muestra la rutina; usuario completa series
       │
       ▼
6. Tracking  POST /tracking/record  (sets, RPE, dificultad)
              → INSERT en tracking + evento ejercicio-completado
       │
       ▼
7. Workers   replicator.py → DuckDB (analítica offline)
              preventive_worker.py → alertas de alta fatiga
              weekly_analysis.py → análisis semanal con IA
       │
       ▼
8. Dashboard GET /dashboard/progress/X → gráficas de progreso
```

### Streaming con SSE

La generación con Ollama tarda **1–5 minutos**. Para no dejar al usuario con una pantalla en blanco o un timeout del proxy, se implementó **Server-Sent Events (SSE)**:

- El servicio 8003 expone `POST /routines/generate-stream` que emite eventos `progress`, `complete` y `error`.
- El gateway detecta la ruta (`/routines/generate-stream`) y usa `StreamingResponse` con un proxy de chunks vía `httpx` (`_proxy_stream`), timeout de 600 s.
- El frontend (`generateRoutineStream`) parsea los eventos SSE y muestra el progreso ("Enviando prompt a Ollama…", "Generando rutina…"), con **reintentos automáticos** (hasta 2) si el timeout ocurre.
- Los timeouts del proxy de Vite en desarrollo también se aumentaron a 600 s.

---

## 7. Base de datos

PostgreSQL (puerto 5432), base `seniorvital`. Esquema creado idempotentemente por `seniorvital_shared/db.py`. Tablas principales:

| Tabla | Descripción | Relaciones clave |
|-------|-------------|------------------|
| `users` | Usuarios (senior, caregiver, admin). `health_profile` y `preferences` en JSONB | — |
| `caregiver_links` | Vínculo cuidador ↔ senior | `caregiver_user_id`, `senior_user_id` → `users` |
| `exercises` | Catálogo de ejercicios (nivel 1–4, contraindicaciones) | — |
| `workout_sessions` | Cabecera de sesión de entrenamiento | `user_id` → `users` |
| `workout_exercises` | Ejercicios dentro de una sesión | `session_id` → `workout_sessions`, `exercise_id` → `exercises` |
| `workout_sets` | Series individuales (reps, RPE 1–10, descanso) | `workout_exercise_id` → `workout_exercises` |
| `tracking` | Registro de ejercicios completados (usado por dashboard) | `user_id` → `users`, `exercise_id` → `exercises` |
| `routines` | Rutinas diarias generadas por IA | `user_id` → `users` |
| `habits` | Hábitos diarios (agua en vasos, horas de sueño) | `user_id` → `users`, UNIQUE(user_id, date) |
| `projections` | Insights y proyecciones semanales | `user_id` → `users` |
| `push_subscriptions` | Suscripciones Web Push | `user_id` (PK) |
| `event_queue` | Cola de eventos asíncronos (replicación) | `stream_name`, `processed` |
| `agent_queue` / `agent_insights` | Comandos e insights de los agentes IA | `user_id` → `users` |
| `admin_logs` | Auditoría de acciones de administradores | `admin_user_id` → `users` |

### Diagrama de relaciones (núcleo)

```
users 1 ──── N caregiver_links ──── 1 users
  │
  ├── N workout_sessions 1 ── N workout_exercises N ── 1 exercises
  │                             │
  │                             └── N workout_sets
  │
  ├── N tracking (exercise_id → exercises)
  ├── N routines   (rutina diaria, exercises JSONB)
  ├── N habits     (agua, sueño por día)
  └── N projections / agent_insights
```

Dos decisiones de diseño notables:

- **JSONB para datos flexibles**: `health_profile`, `preferences`, y los `exercises` de cada rutina se guardan como JSON, porque su forma varía y evita joins complejos.
- **La tabla `routines` guarda la lista completa de ejercicios en JSONB** (no normalizada con `workout_sessions`). `workout_sessions`/`workout_exercises`/`workout_sets` corresponden a la sesión en vivo cuando el usuario entrena, mientras `tracking` es el registro agregado que alimenta el dashboard.

---

## 8. Consideraciones de rendimiento y escalabilidad

- **LLM en CPU es el cuello de botella**: `phi3:mini` en CPU pura tarda 1–5 min por rutina. Mitigaciones:
  - **Streaming SSE** para feedback en tiempo real y evitar timeouts del proxy.
  - **Timeout ampliado (600 s)** en servicio, gateway y proxy de Vite.
  - **Health check ligero** (`/api/tags`) para no confundir "modelo lento" con "servicio caído".
  - Parámetros `num_predict: 600`, `temperature: 0.2` para respuestas cortas y deterministas.
- **Cache por día**: `GET /routines/today` devuelve la rutina ya guardada (no se regenera salvo `force=true`), evitando llamadas repetidas a Ollama. Frontend cachea con React Query (5 min).
- **Manejo de errores**: gateway distingue 502/504; normaliza cualquier respuesta no-JSON a `{"detail": ...}`; el frontend reintenta (con backoff simple) y mantiene una **cola offline** en `localStorage` para registros fallidos.
- **Tolerancia a fallos de IA**: fallback a rutina predeterminada + indicador `generated_by` para que el usuario sepa el origen.
- **Normalización de datos externos**: si Ollama devuelve un `exercise_id` que no existe en el catálogo, `tracking-service` lo registra como `NULL` (en lugar de fallar por FK) — evita perder el registro del ejercicio completado.
- **Escalado**: los microservicios son stateless (la sesión está en la BD), por lo que pueden escalarse horizontalmente detrás del gateway. La generación de IA es el único recurso intensivo; la cola de eventos permite procesar la analítica por fuera del request.
- **Analítica**: `replicator.py` copia eventos a **DuckDB** (embebido, file-based) para consultas de analítica sin cargar el OLTP.

---

## 9. Próximos pasos y mejoras potenciales

- **Rendimiento de IA**: usar un modelo más liviano o GPU para reducir la generación a segundos en lugar de minutos.
- **Seed del catálogo de ejercicios**: la tabla `exercises` está vacía; poblar con ejercicios reales para que Ollama genere rutinas con IDs válidos y el tracking mantenga integridad referencial.
- **Autenticación con roles**: ya existe el modelo de roles (senior/caregiver/admin); extender con gestión de sesiones, revocación de tokens y refresh con rotación.
- **Notificaciones**: Web Push ya está esbozado (`notification-service`, `push_subscriptions`); completar campañas (recordatorios de rutina, alertas de inactividad que ya detecta `daily_inactivity.py`).
- **Replicación PostgreSQL → DuckDB**: robustecer el `replicator.py` para tolerancia a fallos y reinicio seguro.
- **Observabilidad**: métricas (Prometheus), logs centralizados y tracing entre servicios.
- **Despliegue**: contenedores Docker + docker-compose, CI/CD, y entorno de producción con HTTPS.
- **Test de carga** sobre el gateway y el flujo de streaming con múltiples usuarios.

# Data Integrations — Integración de Datos y Servicios

## Resumen

Capa de abstracción de datos que permite a los agentes acceder a fuentes de datos locales (PostgreSQL, DuckDB) en desarrollo y servicios GCP (Firestore, BigQuery) en producción, sin cambiar el código de los agentes.

## Arquitectura

```
Agentes (WellnessCoach, Nutrition)
  │
  ├── FirestoreClient (user data)
  │     ├── LocalFirestoreAdapter → PostgreSQL (asyncpg)
  │     └── GCPFirestoreAdapter → Firestore SDK
  │
  └── BigQueryClient (analytics)
        ├── LocalBigQueryAdapter → DuckDB
        └── GCPBigQueryAdapter → BigQuery SDK
```

## Clientes

### FirestoreClient

Acceso a datos de usuario (perfil, salud, hábitos, tracking, rutinas).

| Método | Retorna | Fuente (local) | Fuente (GCP) |
|--------|---------|----------------|--------------|
| `get_user_profile(user_id)` | `dict` | PostgreSQL `users.profile` | Firestore `users/{id}` |
| `get_user_health(user_id)` | `dict` | PostgreSQL `users.health_profile` | Firestore `users/{id}` |
| `get_user_habits(user_id, days)` | `list[dict]` | PostgreSQL `habits` | Firestore `users/{id}/habits` |
| `get_user_tracking(user_id, weeks)` | `list[dict]` | PostgreSQL `tracking` | Firestore `users/{id}/tracking` |
| `get_user_routine(user_id)` | `dict|None` | PostgreSQL `routines` | Firestore `users/{id}/routines` |

### BigQueryClient

Acceso a analytics y tendencias.

| Método | Retorna | Fuente (local) | Fuente (GCP) |
|--------|---------|----------------|--------------|
| `get_weekly_progress(user_id, weeks)` | `list[dict]` | DuckDB `weekly_progress` | BigQuery `weekly_progress` |
| `get_activity_summary(user_id)` | `dict` | DuckDB `raw_events` | BigQuery `tracking` |
| `get_population_trends(condition)` | `list[dict]` | `[]` (no disponible) | BigQuery `population_analytics` |

## Configuración

### Variables de entorno

```bash
# Modo de operación: "local" o "gcp"
DATA_CLIENT_MODE=local

# GCP (requerido para modo gcp)
GCP_PROJECT_ID=tu-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
BIGQUERY_DATASET=seniorvital
FIRESTORE_COLLECTION_USERS=users
FIRESTORE_COLLECTION_HABITS=habits
```

### Modo local (desarrollo)

```python
from src.clients import FirestoreClient, BigQueryClient

firestore = FirestoreClient(mode="local", pool=asyncpg_pool)
bigquery = BigQueryClient(mode="local")

# Los clientes funcionan igual independientemente del modo
profile = await firestore.get_user_profile(user_id=1)
```

### Modo GCP (producción)

```python
from src.clients import FirestoreClient, BigQueryClient, GCPConfig

config = GCPConfig(mode="gcp")
firestore = FirestoreClient(mode="gcp", config=config)
bigquery = BigQueryClient(mode="gcp", config=config)
```

## Integración con Agentes

### WellnessCoachAgent

```python
coach = WellnessCoachAgent(
    llm=llm,
    user_data=user_data,
    tools=tools,
    firestore_client=FirestoreClient(mode="local", pool=pool),
)

# En _get_user_profile(), automáticamente:
# - Consulta PostgreSQL para perfil base
# - Si firestore_client existe, agrega recent_habits y recent_tracking_count
```

### NutritionAgent

```python
nutrition = NutritionAgent(
    llm=llm,
    user_data=user_data,
    tools=[rag_search, safety_check],
    firestore_client=FirestoreClient(mode="local", pool=pool),
)

# En _get_user_profile(), automáticamente:
# - Consulta PostgreSQL para perfil base
# - Si firestore_client existe, agrega recent_habits, weight, height
```

## Manejo de Errores

Todos los métodos de los clientes retornan datos vacíos en caso de error:

```python
# Nunca lanzan excepciones
profile = await firestore.get_user_profile(user_id=1)  # {} si falla
habits = await firestore.get_user_habits(user_id=1)     # [] si falla
```

Los errores se loguean con `logger.warning()` para debugging.

### Fallback chain

```
Firestore/GCP error → log warning → return empty dict/list
Agent continues with available data (PostgreSQL)
```

## Seguridad

- **Sin credenciales en código**: Todas las credenciales están en variables de entorno
- **GOOGLE_APPLICATION_CREDENTIALS**: Nunca se lee directamente, se pasa al SDK de GCP
- **Service account JSON**: No debe commitearse al repositorio (agregado a .gitignore)
- **Modo local por defecto**: `DATA_CLIENT_MODE=local` — no necesita credenciales GCP

## Dependencias

### Requeridas (ya instaladas)

- `asyncpg` — PostgreSQL driver
- `duckdb` — Analytics embebido

### Opcionales (para modo GCP)

- `google-cloud-firestore>=2.16.0` — Firestore SDK
- `google-cloud-bigquery>=3.25.0` — BigQuery SDK

```bash
# Instalar solo si se necesita modo GCP
pip install google-cloud-firestore google-cloud-bigquery
```

## Diagrama de Datos

```
PostgreSQL (14 tables)
├── users (profile JSONB, health_profile JSONB, preferences JSONB)
├── tracking (sets, reps, rpe, completed_at)
├── habits (water_intake_glasses, sleep_hours)
├── routines (exercises JSONB, warmup)
├── projections (weekly insights)
├── exercises (catalog)
├── conversation_history (chat messages)
└── event_queue (async events)

DuckDB (analytics)
├── raw_events (replicated from PostgreSQL)
└── weekly_progress (aggregated insights)

ChromaDB (RAG vectors)
├── wellness_domain (363 chunks, 6 macrodominios)
└── nutrition_domain (13 chunks, domain E)
```

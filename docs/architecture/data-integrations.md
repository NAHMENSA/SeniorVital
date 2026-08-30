# Data Integrations — Acceso a Datos del Sistema Multiagente

> **Issue**: S3-05 (#21) — Integrar el sistema multiagente con datos y servicios
> **Módulos**: `src/clients/` (Firestore, BigQuery), wiring en `routines-ai-service/main.py`

## 1. Modelo de acceso (dual-mode)

Los agentes no conocen el backend subyacente: dependen de protocolos
(`FirestoreClientProtocol`, `BigQueryClientProtocol` en `src/clients/base.py`).

| Modo | Firestore | BigQuery |
|---|---|---|
| `DATA_CLIENT_MODE=local` (dev) | **PostgreSQL** (asyncpg pool) | **DuckDB** (archivo analítico read-only) |
| `DATA_CLIENT_MODE=gcp` (prod) | **Firestore** (SDK) | **BigQuery** (SDK) |

El switch lo decide `GCPConfig` (`src/clients/config.py`) leyendo
`DATA_CLIENT_MODE`; `FirestoreClient`/`BigQueryClient` (`src/clients/firestore_client.py`,
`bigquery_client.py`) implementan la interfaz unificada.

## 2. Matriz agente → fuente de datos

| Agente | Firestore (PG/Firestore) | BigQuery (DuckDB/BigQuery) | Métodos usados |
|---|---|---|---|
| **WellnessCoachAgent** | hábitos + tracking | activity_summary + weekly_insights | `get_user_habits`, `get_user_tracking`; `get_activity_summary`, `get_weekly_progress` |
| **NutritionAgent** | hábitos + salud (peso/altura) | weekly_insights | `get_user_habits`, `get_user_health`; `get_weekly_progress` |
| OrchestratorAgent | — (no consulta datos) | — | solo routing |

El enriquecimiento ocurre en `_get_user_profile()` de cada agente: los datos
ingresan al prompt como parte del perfil (sin modificar system_prompts).

## 3. Inyección

`routines-ai-service/main.py` — helper `_get_data_clients()` crea los dos
clientes según `DATA_CLIENT_MODE` y los inyecta en `WellnessCoachAgent`
(fallback) y `NutritionAgent` (especializado):

```python
firestore_client, bigquery_client = await _get_data_clients()
agent = WellnessCoachAgent(llm=..., firestore_client=firestore_client,
                           bigquery_client=bigquery_client)
```

Si la creación falla, el client se degrada a `None` (el agente sigue
operando sin enriquecimiento).

## 4. Variables de entorno

Definidas en `.env.template` (sin valores reales):

| Variable | Descripción | Default |
|---|---|---|
| `DATA_CLIENT_MODE` | `local` o `gcp` | `local` |
| `GCP_PROJECT_ID` | Proyecto GCP (modo gcp) | — |
| `GOOGLE_APPLICATION_CREDENTIALS` | Ruta del service account JSON (modo gcp) | — |
| `BIGQUERY_DATASET` | Dataset BigQuery | `seniorvital` |
| `FIRESTORE_COLLECTION_USERS` | Colección users | `users` |
| `FIRESTORE_COLLECTION_HABITS` | Colección habits | `habits` |
| `DUCKDB_PATH` | Ruta DuckDB (modo local) | `seniorvital_analytics.duckdb` |

> **Seguridad**: no existen credenciales en el repositorio. `.env*` está en
> `.gitignore` excepto `.env.example`/`.env.template` (placeholders).

## 5. Manejo de errores

Todos los métodos de los adaptadores **retornan vacíos ante fallos** (nunca
levantan):

- `get_user_profile` → `{}` · `get_user_habits` → `[]` · `get_user_routine` → `None`
- `get_weekly_progress` → `[]` · `get_activity_summary` → `{}` · `get_population_trends` → `[]`

El fallo se registra con `logger.warning`. Los agentes envuelven el
enriquecimiento en try/except adicional: un timeout de Firestore no rompe la
conversación.

## 6. Dependencias externas

En `requirements.txt`:

- `google-cloud-firestore>=2.16.0` (modo gcp)
- `google-cloud-bigquery>=3.25.0` (modo gcp)
- `duckdb>=1.0.0` (modo local / BigQuery adapter)

## 7. Responsabilidad por agente

- **WellnessCoachAgent** (general): contextualiza conversación con hábitos y
  progreso reciente.
- **NutritionAgent** (especializado): solo Datos nutricionales relevantes
  (hábitos, peso/altura, insights semanales) — consistentes con su dominio.
- **OrchestratorAgent**: no accede directamente a datos (desacoplamiento).

## 8. Evidencia

`tests/integration/test_s3_data_integration.py` (mockeado, sin BD real):

- Perfil de coach enriquecido con hábitos (Firestore/PG) y métricas (BigQuery/DuckDB).
- Perfil nutricional con insights semanales.
- `chat()` E2E con clientes inyectados.
- Regresión sin clientes y degradación ante fallos.

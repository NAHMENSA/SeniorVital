# AnalyticsAgent

Agente especializado en estadisticas de progreso, tendencias de ejercicio y analisis de datos del usuario.

## Responsabilidad

Procesar consultas sobre progreso personal, estadisticas de ejercicio, habitos y tendencias. Puede ejecutar queries SQL contra DuckDB para obtener datos agregados.

## Arquitectura

| Aspecto | Detalle |
|---------|---------|
| **Dominio** | A (Physio-Evaluator) + B (Exercise Architect) — 217 chunks |
| **Tools** | `get_progress`, `get_habits`, `get_routine`, `query_analytics` |
| **Estado** | Disenado, no implementado |
| **Delegado desde** | OrchestratorAgent via IntentClassifier |

## Flujo

```
Usuario -> OrchestratorAgent -> IntentClassifier (dominio=analytics)
  -> AnalyticsAgent -> get_progress(user_id, period)
  -> query_analytics(SQL)
  -> Respuesta con estadisticas y graficos
```

## Tools

### get_progress

Obtiene metricas de progreso del usuario para un periodo dado.

- **Fuente**: PostgreSQL `tracking` table
- **Metricas**: sesiones completadas, minutos totales, ejercicios realizados
- **Periodo**: 7d, 30d, 90d, custom

### get_habits

Obtiene habitos diarios del usuario.

- **Fuente**: PostgreSQL `habits` table
- **Metricas**: agua (vasos), sueno (horas), peso

### get_routine

Obtiene la rutina actual del usuario.

- **Fuente**: PostgreSQL `routines` + `workout_exercises` tables
- **Retorna**: lista de ejercicios con sets, reps, descanso

### query_analytics

Ejecuta queries SQL personalizadas contra DuckDB.

- **Modo**: Solo SELECT (no DDL/DML)
- **DuckDB path**: `data/seniorvital.duckdb`
- **Tablas**: replicas de PostgreSQL via replicator.py

## Conocimiento

Los dominios A y B cubren:
- **A (Physio-Evaluator)**: Ejercicios de fisioterapia, evaluacion funcional, rango de movimiento
- **B (Exercise Architect)**: Diseno de rutinas, progresion de carga, periodizacion

## Implementacion futura

Para implementar este agente:
1. Crear `src/agents/analytics/agent.py` con clase `AnalyticsAgent`
2. Integrar con `seniorvital_shared/db.py` para queries PostgreSQL
3. Integrar con DuckDB para analytics agregados
4. Registrar en `src/orchestration/router.py` mappings
5. Agregar tests en `tests/analytics/`

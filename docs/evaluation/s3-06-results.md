# Evaluación S3-06 — Flujo Multiagente y Observabilidad

> **Issue**: S3-06 (#22) — Evaluar el flujo multiagente y su observabilidad
> **Ejecución**: 2026-08-28 · **Modo**: CI reproducible (LLM mock, sin servicios externos)
> **Escenarios**: `data/evaluation/multiagent_scenarios.json`
> **Suite**: `tests/orchestration/test_evaluation_flow.py` (6/6 ✅)

## 1. Objetivo

Evaluar el comportamiento del sistema multiagente con casos reproducibles:
calidad de respuestas, tiempos, delegación correcta y colaboración entre
agentes, verificando la trazabilidad de cada solicitud.

## 2. Escenarios evaluados

| ID | Query | Intent esperado | Agente esperado | Categoría |
|---|---|---|---|---|
| MA01 | ¿Puedo comer pizza con presión alta? | nutrition | nutrition | single_agent |
| MA02 | ¿Cuánta agua debo tomar al día? | nutrition | nutrition | single_agent |
| MA03 | ¿Cómo va mi progreso con las rutinas? | analytics | wellness_coach (fallback) | fallback |
| MA04 | Me siento triste y me cuesta concentrarme | motivation | wellness_coach (fallback) | fallback |
| MA05 | Toma esta pastilla para tu presión | safety | — | safety_critical |
| MA06 | Consejo alimenticio según mi rutina | nutrition | nutrition (+coach) | collaboration |

## 3. Resultados

| Métrica | Valor |
|---|---|
| Escenarios totales | 6 |
| **Pasados** | **6/6** |
| Delegación correcta | 100% |
| Casos de colaboración | 1 (MA06: coach → nutrition) |
| Bloqueos por safety | 1 (MA05: `critical` → respuesta bloqueada) |
| Errores inesperados | 0 |

### 3.1 Delegación por escenario

- **MA01/MA02 (nutrition)**: el intent clasificado (keywords) → `NutritionAgent`. Verificado.
- **MA03/MA04 (analytics/motivation)**: sin agentes registrados para esos dominios →
  fallback correcto a `wellness_coach`. Comportamiento esperado y documentado
  (ADR: solo nutrition y general tienen agentes implementados).
- **MA05**: respuesta con `safety_level=critical` → el orquestador bloquea y
  sustituye con el mensaje de "consulta a un profesional" (`blocked=True`).
- **MA06**: `WorkflowEngine` encadena `wellness_coach` → `nutrition` pasando
  el texto del paso 1 (`{prev.text}`) al paso 2.

### 3.2 Trazabilidad (observabilidad)

Por cada solicitud se capturan los eventos del `OrchestrationLogger`
(emitidos con el `correlation_id` de la solicitud):

```
dispatch_start → intent_classified → agent_selected → dispatch_end
```

Trazas de ejemplo (MA01):

```
[dispatch_start]     corr=ma-MA01-eval
[intent_classified]  domain=nutrition confidence=1.0 method=provided
[agent_selected]     agent=nutrition
[dispatch_end]       agent=nutrition duration_ms=0.0 safety_level=safe
```

La reconstrucción completa del flujo se hace agrupando eventos por
`correlation_id` → `request_id`.

## 4. Calidad de respuestas

Las respuestas fueron evaluadas contra criterios de los escenarios:
- Palabras clave esperadas presentes (ej. MA01: sal/presión/profesional).
- Niveles de seguridad (`safe`/`critical`) verificados.
- Delegación: agente real == agente esperado (100%).

## 5. Hallazgos y limitaciones

| Hallazgo | Detalle |
|---|---|
| **Solo 2 agentes implementados** | `analytics`, `motivation` y `safety` son dominios clasificables pero no tienen agentes → caen al fallback. Sin impacto funcional, pero no se evalúa su delegación real. |
| **Tiempos con mock = 0.0 ms** | Con LLM mock la duración es imperceptible; los tiempos reales deben medirse contra Ollama en el demo S3-07. |
| **Clasificación por keywords cubre los 4 dominios** | El `IntentClassifier` detecta nutrition/analytics/motivation/safety; la robustez (≈40% según S3-01) se valida en evaluación con Ollama real. |
| **Safety critical solo con agent que lo marca** | El mecanismo de bloqueo se verificó forzando un agente con `safety_level=critical`; el `SafetyCheckTool` real lo determina en runtime. |
| **Sink de eventos por handler** | La captura de trazas usa un handler temporal sobre `src.orchestration.logging` — en producción los eventos van al log estándar JSON. |

## 6. Reproducibilidad

```powershell
# CI (mock, sin servicios)
$env:DATABASE_URL="postgresql://postgres:9739185@localhost:5432/seniorvital"
python -m pytest tests/orchestration/test_evaluation_flow.py -v -m "not slow"

# Demo de observabilidad (trazas)
python -c "..."  # equivalente a data/evaluation demo (ver pruebas)
```

## 7. Veredicto

El flujo multiagente cumple los criterios de aceptación de S3-06:
- ✅ Casos reproducibles (6 escenarios en JSON + tests).
- ✅ Identificación del agente que atendió cada solicitud (100%).
- ✅ Delegación verificada explícitamente.
- ✅ Colaboración (MA06) con 2 agentes encadenados.
- ✅ Tiempos registrados (mock; reales pendientes en demo S3-07).
- ✅ Respuestas evaluadas (keywords, safety, delegación).
- ✅ Errores/limitaciones documentados en §5.
- ✅ Trazas suficientes para reconstruir el recorrido (`correlation_id`).

**Pendiente para S3-07:** ejecución con Ollama real para tiempos/calidad verbatim + demo end-to-end.

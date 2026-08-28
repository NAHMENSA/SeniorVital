# Interaction Protocol — Comunicación y Delegación entre Agentes

> **Issue**: S3-04 (#20) — Implementar comunicación y delegación entre agentes
> **Módulo**: `src/orchestration/dispatch.py` + `src/orchestration/router.py`
> **Mecanismo**: síncrono con timeouts (llamadas a métodos async; el handler del LLM tiene timeout en `LLMService`)

## 1. Alcance

Define el protocolo formal de mensajería entre el Orchestrator Agent (S3-02)
y los agentes especializados (S3-03), cubriendo:

- Formato de mensajes de solicitud/respuesta.
- Contexto que acompaña cada solicitud.
- Delegación y retorno de resultados.
- Colaboración multi-agente (`WorkflowEngine`).
- Trazabilidad de delegaciones (`OrchestrationLogger`).
- Nota de evolución hacia MCP/A2A.

## 2. Formato de Mensajes

### 2.1 DispatchRequest (solicitud)

Definido en `DispatchRequest` (`src/orchestration/dispatch.py`):

| Campo | Tipo | Descripción |
|---|---|---|
| `request_id` | `str` (autogenerado) | Identificador único de la solicitud |
| `user_id` | `int` | ID del usuario |
| `message` | `str` | Mensaje del usuario |
| `intent` | `str` | Dominio de intención (vacío → se clasifica) |
| `payload` | `dict` | Datos adicionales (macrodominio, filtros, etc.) |
| `context` | `dict` | `user_profile`, `from_agent` y datos de contexto |
| `conversation_history` | `list[dict]` | Historial reciente |
| `correlation_id` | `str` | ID de correlación (trazabilidad) |

### 2.2 DispatchResponse (respuesta)

| Campo | Tipo | Descripción |
|---|---|---|
| `request_id` | `str` | Idéntico a la solicitud |
| `text` | `str` | Respuesta textual |
| `agent` | `str` | Agente que respondió |
| `intent` | `str` | Dominio atendido |
| `safety_level` | `str` | `safe` \| `warning` \| `critical` |
| `tool_chain` | `list[str]` | Tools ejecutadas |
| `blocked` | `bool` | `True` si safety critical la bloqueó |
| `duration_ms` | `float` | Tiempo total del despacho |
| `metadata` | `dict` | `correlation_id` y extras |

### 2.3 Conversores

- `request_to_agent_message(request) -> AgentMessage` — al protocolo wire (S3-02).
- `response_from_agent_message(message) -> DispatchResponse` — desde `AgentMessage`.
- `response_to_dispatch_response(response, ...) -> DispatchResponse` — desde `AgentResponse`.

## 3. Mecanismo de Delegación y Retorno

### 3.1 Entry point: `orchestrator.dispatch(request)`

```python
async def dispatch(self, request: DispatchRequest) -> DispatchResponse:
    # 1. Correlation id (request.correlation_id or request.request_id)
    # 2. Guard anti-ciclo (correlation_id activo → OrchestrationError)
    # 3. Intent: provisto o clasificado (IntentClassifier)
    # 4. select_agent(intent) → agente destino
    # 5. AgentRequest con contexto completo → agent.handle(request)
    # 6. Safety: critical → respuesta bloqueada
    # 7. dispatch_start / dispatch_end (logs) → DispatchResponse
```

### 3.2 Delegación directa (legado S3-02)

`route()` y `delegate()` del `OrchestratorAgent` continúan disponibles y
comparten el mismo código de selección, safety y logging.

## 4. Colaboración Multiagente

`WorkflowEngine` (`src/orchestration/protocol.py`) encadena pasos:

```python
steps = [
    WorkflowStep(agent="wellness_coach", task_template={"message": "¿Cómo va mi progreso?", "user_id": 1}, step_id="coach"),
    WorkflowStep(agent="nutrition", task_template={"message": "Consejo para: {prev.text}", "user_id": 1}, step_id="nutri"),
]
results = await engine.execute(steps, {"user_id": 1}, correlation_id="...")
```

### Placeholders soportados
- `{prev.text}` — texto del paso anterior
- `{prev.safety_level}` — safety del paso anterior
- `{ctx.user_id}`, `{ctx.message}` — contexto inicial

### Condiciones
- `condition="prev.safety_level != 'critical'"` — salta el paso si no se cumple.

## 5. Trazabilidad

`OrchestrationLogger` emite eventos JSON por `correlation_id`:
`route_start`, `intent_classified`, `agent_selected`, `delegation_start`,
`delegation_end`, `safety_check`, `route_end`, `fallback_activated`,
`workflow_step`, `dispatch_start`, `dispatch_end`.

La cadena completa de una solicitud se reconstruye agrupando eventos por
`correlation_id` → `request_id`.

## 6. Anti-Ciclos

`dispatch()` mantiene `_active_correlations` (set de correlations en curso):
- Reentrada con el mismo `correlation_id` → `OrchestrationError("Delegation cycle detected")`.
- El diseño estructural impide ciclos agentes→orquestador (los agentes no
  tienen referencia al orquestador; usan `DelegateCallback` si lo necesitan).

## 7. Caso de Colaboración Verificado (S3-04)

Escenario: `wellness_coach` → `nutrition` (real agents, mock LLM):

```
Usuario: "¿Cómo va mi progreso esta semana?"
→ coach: "Has completado tus rutinas de la semana. Buenos progresos."
→ nutrition({prev.text}): "Dame un consejo alimenticio para esta rutina: ..."
→ respuesta nutricional contextualizada
```

Evidencia: `tests/integration/test_s3_collaboration.py` (66/66 tests).

## 8. Evolución hacia MCP y A2A (nota arquitectónica)

La arquitectura actual usa comunicación síncrona método-a-método con
protocolos Python (`Agent`, `Tool`, `Orchestrator`). Para interoperar con
ecosistemas externos:

- **MCP (Model Context Protocol)** — exponer las 8 wellness tools como
  recursos/heatmaps MCP reutilizables por cualquier cliente (sin tocar el
  `Tool` Protocol en ejecución). Directorio reservado:
  `src/orchestration/communication/mcp/`.
- **A2A (Agent-to-Agent)** — desacoplar `AgentMessage` (ya portable como JSON)
  hacia un transporte HTTP/async cuando los agentes se vuelvan servicios
  independientes. Directorio reservado:
  `src/orchestration/communication/a2a/`.

> **Decisión**: S3-04 NO implementa MCP/A2A (fuera de alcance según la issue #20);
> solo deja la nota y los placeholders. Ambas evoluciones preservan
> `DispatchRequest`/`DispatchResponse` como contrato de nivel de aplicación.

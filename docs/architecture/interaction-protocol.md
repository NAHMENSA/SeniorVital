# Interaction Protocol — Comunicación Inter-Agente

## Resumen

Define el protocolo de comunicación entre el OrchestratorAgent y los agentes especializados del sistema multiagente de SeniorVital.

## Arquitectura

```
User ──► OrchestratorAgent.route()
           │
           ├─ correlation_id = uuid4()[:12]  ← auto-generado
           ├─ IntentClassifier.classify()
           ├─ _select_agent()
           ├─ agent.handle(AgentRequest)
           │     └─ agent puede llamar delegate_callback(target, task)
           │           └─ OrchestratorAgent.delegate()
           │                 ├─ safety validation
           │                 ├─ structured logging
           │                 └─ agent.handle()
           ├─ safety validation
           └─ return AgentMessage(correlation_id=...)
```

## Tipos de Mensaje

### AgentMessage

```python
@dataclass
class AgentMessage:
    from_agent: str          # "user" | "orchestrator" | "agent_name"
    to_agent: str            # "orchestrator" | "agent_name" | "user"
    content: dict            # payload flexible
    message_type: str        # "query" | "response" | "delegation" | "alert"
    correlation_id: str      # uuid4[:12], auto-generado
    parent_id: str           # correlation_id del padre (para delegaciones anidadas)
    timestamp: str           # ISO-8601, auto-generado
```

### AgentRequest (interno)

```python
@dataclass
class AgentRequest:
    message: str
    user_id: int
    user_profile: dict
    conversation_history: list[Message]
    context: dict  # intent, confidence, correlation_id, delegated_by
```

### AgentResponse (interno)

```python
@dataclass
class AgentResponse:
    text: str
    safety_level: str  # "safe" | "warning" | "critical"
    tool_chain: list[str]
    metadata: dict
```

## Flujo de Routing

1. **User envía mensaje** → `OrchestratorAgent.route(AgentMessage)`
2. **Se genera correlation_id** si no existe
3. **IntentClassifier** clasifica el dominio (keyword → LLM)
4. **_select_agent()** selecciona agente por dominio
5. **agent.handle(AgentRequest)** ejecuta el agente
6. **Safety validation** bloquea respuestas críticas
7. **Se retorna AgentMessage** con correlation_id preservado

## Flujo de Delegación

1. **Agente necesita ayuda** → llama `delegate_callback(from, to, task)`
2. **OrchestratorAgent.delegate()** busca el agente destino
3. **Se loguea** delegation_start con correlation_id
4. **agent.handle(AgentRequest)** ejecuta el agente destino
5. **Safety validation** bloquea respuestas críticas
6. **Se loguea** delegation_end con timing y resultado
7. **Se retorna dict** con text, safety_level, tool_chain, metadata

## DelegateCallback

Protocolo inyectable para que agentes deleguen sin conocer al orchestrator:

```python
class DelegateCallback(Protocol):
    async def __call__(self, from_agent: str, to_agent: str, task: dict) -> dict: ...
```

**Uso en agente:**

```python
class MyAgent:
    def __init__(self, delegate_callback: DelegateCallback):
        self._delegate = delegate_callback

    async def process(self, user_id, message):
        result = await self._delegate(
            from_agent="analytics",
            to_agent="nutrition",
            task={"message": "restricciones diabetes", "user_id": user_id}
        )
        return result
```

## WorkflowEngine

Motor para flujos multi-paso:

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

**Placeholders soportados:**
- `{prev.text}` → texto de la respuesta del paso anterior
- `{prev.safety_level}` → nivel de seguridad del paso anterior
- `{ctx.user_id}` → user_id del contexto inicial
- `{ctx.message}` → message del contexto inicial

## Trazabilidad

### OrchestrationLogger

Cada evento incluye:

```json
{
  "timestamp": "2026-08-24T23:00:00Z",
  "correlation_id": "abc123def456",
  "event": "route_start",
  "data": {"user_id": 1, "message_preview": "¿Qué debo comer?"}
}
```

**Eventos disponibles:**

| Evento | Data | Descripción |
|--------|------|-------------|
| `route_start` | user_id, message_preview | Inicio del routing |
| `intent_classified` | domain, confidence, method | Intención clasificada |
| `agent_selected` | agent | Agente seleccionado |
| `delegation_start` | from_agent, to_agent, parent_id | Inicio de delegación |
| `delegation_end` | from_agent, to_agent, duration_ms, success, safety_level | Fin de delegación |
| `safety_check` | agent, level, blocked | Validación de seguridad |
| `route_end` | agent, duration_ms | Fin del routing |
| `fallback_activated` | reason, fallback_agent | Activación de fallback |
| `workflow_step` | step_index, agent, skipped | Paso de workflow |

### Reconstrucción de flujo

Para reconstruir el flujo de una solicitud:

```bash
# Buscar todos los eventos de un correlation_id
grep "abc123def456" logs/orchestration.log | jq .

# Secuencia esperada:
# route_start → intent_classified → agent_selected → delegation_start → delegation_end → route_end
```

## Safety Validation

Tanto `route()` como `delegate()` validan `safety_level`:

- **"safe"**: respuesta permitida
- **"warning"**: respuesta permitida con log
- **"critical"**: respuesta bloqueada, se retorna mensaje genérico de "consulta a un profesional"

## Nota Técnica: Evolución hacia Estándares

### MCP (Model Context Protocol)

**Estado actual:** Tools hardcoded por agente (RAGSearchTool, SafetyCheckTool, etc.)

**Evolución MCP:** Los agentes podrían exponer sus tools como recursos descubribles vía MCP servers. Un agente podría preguntar "¿qué tools tiene disponible nutrition?" y descubrir `rag_search` dinámicamente.

**Impacto:** Desacoplaría la definición de tools del código del agente. Los tools serían registrados en un registry central y descubiertos por nombre/capacidad.

### A2A (Agent-to-Agent)

**Estado actual:** Hub-and-spoke — todos los mensajes pasan por el Orchestrator.

**Evolución A2A:** Agentes con "agent cards" que describen sus capacidades. Un agente podría enviar un mensaje directamente a otro sin intermediario, usando el protocolo A2A de Google.

**Impacto:** Permitiría comunicación directa entre agentes (ej. NutritionAgent → SafetyGuardianAgent) con descubrimiento automático. Reduciría la carga del orchestrator pero增加aría la complejidad de trazabilidad.

### Recomendación

Mantener el patrón Supervisor actual (hub-and-spoke) para la v1.0. Evaluar MCP/A2A cuando:
- Hayan 5+ agentes especializados
- Los agentes necesiten descubrir tools dinámicamente
- Se requiera comunicación directa agente-agente sin intermediario

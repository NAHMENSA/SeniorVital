# OrchestratorAgent

Agente central que actua como router y coordinador de todos los agentes especializados.

## Responsabilidad

Recibir todas las solicitudes del usuario, clasificar la intencion, delegar al agente apropiado, validar la seguridad de la respuesta, y retornar el resultado final.

## Arquitectura

| Aspecto | Detalle |
|---------|---------|
| **Dominio** | Todos (no especializado) |
| **Tools** | Ninguno (usa LLM para clasificar intencion) |
| **Estado** | Implementado (Sprint 3) |
| **Ubicacion** | `src/orchestration/router.py` |

## Componentes

### OrchestratorAgent

Clase principal que implementa `AgentProtocol`.

```python
class OrchestratorAgent:
    def __init__(self):
        self.classifier = IntentClassifier()
        self.agents = {}  # domain -> agent mapping

    async def handle(self, message: AgentMessage) -> AgentMessage:
        # 1. Clasificar intencion
        intent = self.classifier.classify(message.content)

        # 2. Seleccionar agente destino
        agent = self.agents.get(intent.domain, self.default_agent)

        # 3. Delegar
        response = await agent.handle(message)

        # 4. Validar seguridad
        if response.safety_level == "critical":
            return self.block_response(message)

        return response
```

### IntentClassifier

Clasificador de intenciones basado en keywords con threshold de confianza.

| Dominio | Keywords ejemplo | Threshold |
|---------|------------------|-----------|
| nutrition | dieta, comer, alimento, hidratacion, nutricion | 0.7 |
| analytics | progreso, estadisticas, tendencia, datos, reporte | 0.7 |
| motivation | animo, motivacion, animar, fuerza, animo | 0.7 |
| safety | dolor, emergencia, peligro, herida, mareo | 0.7 |

**Comportamiento:**
- Si `confidence >= threshold`: delega al agente del dominio
- Si `confidence < threshold`: fallback a WellnessCoachAgent
- Si `safety_level == "critical"` en la respuesta: bloquea y retorna mensaje generico

## Flujo completo

```
1. POST /chat { user_id, message }
2. OrchestratorAgent.handle(message)
3. IntentClassifier.classify(message)
   -> IntentResult(domain, confidence, safety_level)
4. Si safety_level == "critical" -> bloquear inmediatamente
5. Seleccionar agente: agents[domain] o default
6. agent.handle(message_with_context)
7. Validar respuesta del agente
   -> Si safety_level == "critical" -> bloquear
8. OrchestrationLogger.log(correlation_id, eventos)
9. Retornar AgentMessage al usuario
```

## Logging

Cada request genera eventos JSON con `correlation_id` para trazabilidad completa.

**Eventos**: `route_start`, `intent_classified`, `agent_selected`, `delegation_start`, `delegation_end`, `route_end`, `safety_blocked`, `fallback_triggered`, `error`

**Archivo**: `logs/orchestration.log`

## Workflow Engine

Para flujos multi-paso (futuro), el Orchestrator usa `WorkflowEngine`:

```python
steps = [
    WorkflowStep(agent="nutrition", action="rag_search"),
    WorkflowStep(agent="analytics", action="get_progress"),
    WorkflowStep(agent="coach", action="synthesize"),
]
result = await workflow_engine.execute(steps, context)
```

## Registro de agentes

El Orchestrator mapea dominios a agentes:

| Dominio | Agente | Estado |
|---------|--------|--------|
| nutrition | NutritionAgent | Disenado |
| analytics | AnalyticsAgent | Disenado |
| motivation | MotivationAgent | Disenado |
| safety | SafetyGuardian | Pendiente |
| general | WellnessCoachAgent | Implementado |

## Referencias

- `src/orchestration/router.py` — implementacion
- `src/orchestration/protocol.py` — WorkflowStep, WorkflowEngine
- `src/orchestration/logging.py` — OrchestrationLogger
- `docs/architecture/multiagent-architecture.md` — diagrama completo

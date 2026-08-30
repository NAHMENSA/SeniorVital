# NutritionAgent

Agente especializado en consultas de nutrición, dieta, hidratación y cuidado del adulto mayor.

> **Estado**: Implementado (S3-03). Es el agente especializado del equipo,
> asignado según la issue S3-01 (#17) — ver ADR-2 en
> `docs/architecture/multiagent-system.md`.

## Responsabilidad

Procesar preguntas del usuario sobre alimentación, planificación de comidas,
restricciones dietéticas y recomendaciones de hidratación. Utiliza RAG para
fundamentar respuestas con conocimiento del dominio E (Nutri-Buddy).

**Límites del dominio:** el agente NO responde consultas de análisis de
progreso, motivación/cognitivo ni seguridad transversal — esos dominios
pertenecen a otros agentes (Analytics, Motivation, SafetyGuardian). Su
`can_handle` solo acepta el dominio `nutrition` con confianza ≥ 0.5.

## Arquitectura

| Aspecto | Detalle |
|---------|---------|
| **Dominio** | E (Nutri-Buddy) — 13 chunks en ChromaDB |
| **Tools** | `rag_search`, `safety_check` |
| **Estado** | Implementado — `src/agents/nutrition/agent.py` |
| **Adapter** | `NutritionAgentAdapter` — `src/agents/nutrition/adapter.py` |
| **Prompt** | `SYSTEM_PROMPT_BASE` + `REACT_FORMAT_INSTRUCTIONS` — `src/agents/nutrition/prompts.py` |
| **Reutiliza** | ReActEngine, MemoryStore, LLMService, UserDataService (Sprints 1-2) |
| **Registrado como** | `"nutrition"` en el OrchestratorAgent (S3-02) |

## Entradas y Salidas

| Dirección | Contrato | Detalle |
|-----------|----------|---------|
| **Entrada** | `agent.chat(user_id: int, message: str) -> str` | Uso directo |
| **Entrada** | `agent.process(request: AgentRequest) -> str` | Entry point S3-03 (delega en `chat`) |
| **Entrada** | `adapter.handle(request: AgentRequest) -> AgentResponse` | Contrato Agent Protocol (usado por el Orchestrator) |
| **Salida** | `str` | Respuesta en español |
| **Salida** | `AgentResponse(text, safety_level="safe", tool_chain, metadata)` | Al orquestador |

## Flujo

```
Usuario -> OrchestratorAgent -> IntentClassifier (dominio=nutrition)
  -> NutritionAgentAdapter.handle(AgentRequest)
  -> NutritionAgent.chat / process
  -> historial (PostgresMemoryStore) + perfil (UserDataService)
  -> NutritionPromptBuilder.build() -> ReActEngine.run()
  -> rag_search(knowledge_base, query) / safety_check(response)
  -> Respuesta personalizada (agente → orquestador → usuario)
```

## Prompt Especializado

`SYSTEM_PROMPT_BASE` (definido en `src/agents/nutrition/prompts.py`) delimita:

1. NUTRICIÓN: recomendaciones para adultos mayores (60+).
2. SEGURIDAD: considera restricciones médicas (diabetes, hipertensión, colesterol, renales).
3. PROFESIONAL: no da planes dietéticos sin recomendar consulta profesional.
4. EMPATÍA: tono cálido y comprensivo.
5. IDIOMA: responde SIEMPRE en español.
6. FORMATO: responde SOLO con JSON válido (formato ReAct).
7. LÍMITES: no sustituye la consulta con un nutricionista o médico.

## Tools

### rag_search
Busca en la base de conocimiento del dominio E (Nutri-Buddy) chunks relevantes para la consulta.

- **Knowledge base**: `data/knowledge/domains/E_nutri_buddy/`
- **Embeddings**: `intfloat/multilingual-e5-small` (384d)
- **Vector store**: ChromaDB en `data/vector_store/`
- **Retrieval**: Top-3 chunks, cosine similarity
- **Sin pipeline RAG**: retorna "RAG pipeline not available" (fallback seguro)

### safety_check
Valida que la respuesta no contenga recomendaciones médicas sin disclaimer.

- Retorna mensaje de seguridad con warnings/restricciones del usuario
- Si `critical`: OrchestratorAgent bloquea la respuesta y retorna mensaje genérico

## Capacidades y limitaciones

**Capacidades:**
- Conversación con memoria (PostgresMemoryStore, `conversation_history`).
- Razonamiento ReAct (máx. 3 iteraciones, umbral de 2 fallos).
- Responde SOLO en su dominio; `can_handle` filtra otras intenciones.
- Registrado en el OrchestratorAgent — invocable vía `POST /chat` con `USE_ORCHESTRATOR_AGENT=true`.

**Limitaciones:**
- Llama a Ollama (`phi3:mini`): sigue el formato ReAct de forma poco confiable (~40% fallo con prompts largos).
- Requiere el servicio `rag-service` activo para `rag_search`; sin él el tool devuelve error controlado.
- `safety_check` interno no está implementado como re-evaluación por LLM; la validación transversal la ejecuta el Orchestrator.
- No sustituye a un nutricionista o médico (regla 7 del prompt).

## Evidencia de ejecución

Tests arranquen en `tests/nutrition/test_nutrition_agent.py` + `tests/agents/`:

```powershell
$env:DATABASE_URL="postgresql://postgres:9739185@localhost:5432/seniorvital"
python -m pytest tests/nutrition tests/agents -v -m "not slow"
```

Caso de uso end-to-end (con servicios corriendo y `USE_ORCHESTRATOR_AGENT=true`):

```powershell
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" `
  -d '{"user_id": 1, "message": "¿Puedo comer pizza con presión alta?"}'
# -> {"response": "...", "agent": "nutrition", "safety_level": "safe|critical"}
```

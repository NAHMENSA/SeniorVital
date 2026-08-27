# Flujos de Orquestación — SeniorVital Multi-Agent

## Visión general

Este documento define los flujos de comunicación y delegación entre agentes en el sistema multiagente de SeniorVital. Cada flujo incluye diagrama Mermaid y descripción detallada.

## Flujo 1: Happy Path — Consulta simple

El usuario hace una consulta que corresponde a un solo dominio.

```mermaid
sequenceDiagram
    participant U as Usuario
    participant GW as API Gateway
    participant O as OrchestratorAgent
    participant I as IntentClassifier
    participant A as Agente destino
    participant T as Tools
    participant L as LLM (phi3:mini)

    U->>GW: POST /chat {user_id: 1, message: "¿Qué debo comer hoy?"}
    GW->>O: AgentMessage(to="orchestrator", type="query")

    O->>I: classify(message)
    I->>L: "Clasifica: ¿Qué debo comer hoy?"
    L-->>I: {domain: "nutrition", confidence: 0.92}
    I-->>O: IntentResult(domain="nutrition", confidence=0.92)

    O->>O: select_agent("nutrition") → NutritionAgent
    O->>A: handle(AgentRequest(message, user_id, profile, history))

    loop ReAct (max 3 iteraciones)
        A->>L: system_prompt + user_prompt
        L-->>A: {thought: "...", action: "rag_search", action_input: {query: "dieta adultos mayores"}}
        A->>T: execute("rag_search", {query: "..."})
        T-->>A: ToolResult(success=True, data={chunks: [...]})
        A->>L: context + tool_result
    end

    L-->>A: {thought: "...", final_answer: "Para adultos mayores, se recomienda..."}
    A-->>O: AgentResponse(text="Para adultos mayores...", safety_level="safe", tool_chain=["rag_search"])

    O->>O: validate_safety(response) → safe
    O-->>GW: AgentMessage(content={response: "Para adultos mayores..."})
    GW-->>U: 200 OK {response: "Para adultos mayores..."}
```

### Pasos clave
1. IntentClassifier identifica dominio "nutrition" con confianza 0.92
2. Orchestrator selecciona NutritionAgent
3. NutritionAgent usa `rag_search` para obtener conocimiento del dominio E
4. Orchestrator valida que la respuesta es segura
5. Respuesta enviada al usuario

---

## Flujo 2: Safety Override — Respuesta insegura

El agente genera una respuesta que el Orchestrator detecta como insegura.

```mermaid
sequenceDiagram
    participant U as Usuario
    participant O as OrchestratorAgent
    participant A as MotivationAgent
    participant S as SafetyGuardianAgent
    participant L as LLM

    U->>O: "¿Puedo correr si tengo presión alta?"
    O->>O: classify → domain: "safety"
    O->>O: select_agent("safety") → SafetyGuardianAgent

    Note over O,S: El Orchestrator delega directamente al SafetyGuardian

    O->>S: handle(message, user_profile={hipertensión: true})
    S->>L: ReAct → safety_check(activity="correr", restrictions=["hipertensión"])
    L-->>S: {safe: false, level: "critical", reason: "hipertensión contraindica"}
    S-->>O: AgentResponse(safety_level="critical", text="No se recomienda correr...")

    O->>O: safety_level == "critical" → Bloquear
    O-->>U: "No puedo darte esa recomendación. Consulta a tu médico."
```

### Pasos clave
1. SafetyGuardianAgent detecta que "correr" es inseguro para hipertensión
2. Retorna `safety_level="critical"`
3. Orchestrator bloquea la respuesta original
4. Genera respuesta de fallback genérica

---

## Flujo 3: Multi-agente — Delegación cruzada

Una consulta requiere información de múltiples dominios.

```mermaid
sequenceDiagram
    participant U as Usuario
    participant O as OrchestratorAgent
    participant N as NutritionAgent
    participant A as AnalyticsAgent
    participant S as SafetyGuardianAgent
    participant L as LLM

    U->>O: "¿Cómo voy con mis ejercicios y qué debo comer?"

    O->>O: classify → domain: "analytics+nutrition" (multi-domain)

    par Delegación paralela
        O->>A: handle("¿Cómo voy con mis ejercicios?")
        A-->>O: AgentResponse(text="Has completado 12 sesiones...", safety_level="safe")
    and
        O->>N: handle("¿Qué debo comer?")
        N-->>O: AgentResponse(text="Una dieta balanceada incluye...", safety_level="safe")
    end

    O->>O: merge_responses(response_analytics, response_nutrition)
    O->>S: validate(merged_response, user_profile)
    S-->>O: SafetyResult(level="safe")

    O-->>U: Respuesta combinada de analytics + nutrición
```

### Pasos clave
1. IntentClassifier detecta consulta multi-dominio
2. Orchestrator delega en paralelo a AnalyticsAgent y NutritionAgent
3. Combina las respuestas
4. SafetyGuardian valida la respuesta combinada

---

## Flujo 4: Error — Agente no disponible

El agente seleccionado falla o no está disponible.

```mermaid
sequenceDiagram
    participant U as Usuario
    participant O as OrchestratorAgent
    participant A as NutritionAgent
    participant F as WellnessCoachAgent (fallback)
    participant L as LLM

    U->>O: "¿Qué debo comer?"
    O->>O: classify → domain: "nutrition"
    O->>A: handle(message, ...)

    alt Agente falla (timeout/error)
        A-->>O: ERROR: Connection timeout
        O->>O: fallback_agent("nutrition") → WellnessCoachAgent
        O->>F: handle(message, ...)
        F-->>O: AgentResponse(text="No tengo información específica...", safety_level="safe")
        O-->>U: Respuesta de fallback
    else Agente no existe
        O->>O: No agent for domain "unknown"
        O-->>U: "Lo siento, no puedo ayudar con eso."
    end
```

### Pasos clave
1. NutritionAgent falla (timeout, error de LLM, etc.)
2. Orchestrator detecta el error
3. Selecciona WellnessCoachAgent como fallback
4. Respuesta de fallback (menos especializada pero funcional)

---

## Flujo 5: Conversación multi-turno

El usuario mantiene una conversación con contexto.

```mermaid
sequenceDiagram
    participant U as Usuario
    participant O as OrchestratorAgent
    participant M as MemoryStore
    participant A as Agente destino
    participant L as LLM

    U->>O: Turn 1: "¿Qué ejercicios puedo hacer?"
    O->>A: handle(message, history=[])
    A-->>O: AgentResponse(text="Puedes hacer caminata...")
    O->>M: add_message(user, "¿Qué ejercicios...")
    O->>M: add_message(assistant, "Puedes hacer caminata...")
    O-->>U: "Puedes hacer caminata..."

    U->>O: Turn 2: "¿Y para dormir mejor?"
    O->>M: get_history(user_id, limit=5)
    M-->>O: [turn1_user, turn1_assistant]
    O->>A: handle(message, history=[turn1...])
    A-->>O: AgentResponse(text="Para mejorar el sueño...")
    O->>M: add_message(user, "¿Y para dormir mejor?")
    O->>M: add_message(assistant, "Para mejorar el sueño...")
    O-->>U: "Para mejorar el sueño..."
```

### Pasos clave
1. Cada turno se persiste en MemoryStore (PostgreSQL)
2. El historial se incluye en el prompt del agente
3. El agente mantiene contexto conversacional
4. Límite: últimos 5 mensajes en el contexto

---

## Flujo 6: Intent Classification — Detalle del router

Cómo el IntentClassifier decide qué agente usar.

```mermaid
flowchart TD
    Start[Mensaje del usuario] → Extract[Extraer keywords]
    Extract → Match{Match con dominios?}
    
    Match -->|Dominio único| Single[Agente único]
    Match -->|Multi-dominio| Multi[Delegación paralela]
    Match -->|Sin match| General[WellnessCoachAgent]
    
    Single --> Conf{Confianza > 0.7?}
    Conf -->|Sí| Route[Enrutar a agente]
    Conf -->|No| General
    
    Multi --> Route1[Enrutar a Agente 1]
    Multi --> Route2[Enrutar a Agente 2]
    Multi --> Merge[Combinar respuestas]
    
    Route --> Agent[Agente destino]
    Route1 --> Merge
    Route2 --> Merge
    General --> CoachAgent[WellnessCoachAgent]
    Merge --> SafetyCheck[Validar safety]
    SafetyCheck --> Response[Respuesta al usuario]
    Agent --> SafetyCheck
    CoachAgent --> SafetyCheck
```

### Reglas de routing

| Condición | Agente destino | Confianza mínima |
|-----------|---------------|-----------------|
| Keywords nutrición (comer, dieta, alimento, agua) | NutritionAgent | 0.7 |
| Keywords ejercicio (ejercicio, rutina, entrenar) | AnalyticsAgent | 0.7 |
| Keywords progreso (progreso, estadística, avance) | AnalyticsAgent | 0.7 |
| Keywords emocional (triste, aburrido, motivación) | MotivationAgent | 0.7 |
| Keywords seguridad (peligro, riesgo, seguro) | SafetyGuardianAgent | 0.8 |
| Multi-dominio | Múltiples agentes | 0.6 |
| Sin match claro | WellnessCoachAgent | N/A (fallback) |

---

## Matriz de delegación

| Origen → Destino | Orchestrator | Coach | Nutrition | Analytics | Motivation | Safety |
|-------------------|:-----------:|:-----:|:---------:|:---------:|:----------:|:------:|
| **Orchestrator** | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Coach** | — | — | — | — | — | ✓ |
| **Nutrition** | — | — | — | — | — | ✓ |
| **Analytics** | — | — | — | — | — | ✓ |
| **Motivation** | — | — | — | — | — | ✓ |
| **Safety** | — | — | — | — | — | — |

**Lectura**: Las filas indican quién puede delegar a quién. Solo el Orchestrator puede delegar a todos los agentes. Los agentes especializados solo pueden solicitar validación a SafetyGuardian.

---

## Manejo de errores

### Categorías de error

| Categoría | Ejemplo | Acción |
|-----------|---------|--------|
| **Timeout LLM** | Ollama no responde en 600s | Fallback a WellnessCoachAgent |
| **Tool fallida** | rag_search sin resultados | Agente intenta sin tool (respuesta directa) |
| **Safety critical** | Actividad peligrosa detectada | Bloquear respuesta + fallback genérico |
| **Agente no encontrado** | Dominio "unknown" | WellnessCoachAgent |
| **Conexión perdida** | PostgreSQL caído | Continuar sin memoria |

### Circuit Breaker (futuro)

```
Si agente falla 3 veces consecutivas:
  → Marcar agente como "degraded"
  → Todas las consultas van a WellnessCoachAgent
  → Reintentar cada 5 minutos
  → Marcar como "healthy" tras 2 éxitos consecutivos
```

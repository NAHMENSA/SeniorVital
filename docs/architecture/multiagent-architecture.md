# Arquitectura Multiagente — SeniorVital Wellness Platform

## Visión general

El sistema multiagente de SeniorVital coordina múltiples agentes especializados para responder consultas de bienestar de adultos mayores. Un **Orchestrator Agent** centraliza el routing de consultas, delega a agentes especializados, y valida la seguridad de las respuestas antes de enviarlas al usuario.

El sistema evoluciona el WellnessCoachAgent monolítico (Sprint 2) hacia una arquitectura modular donde cada agente domina un área específica del bienestar, compartiendo tools y memoria a través de PostgreSQL.

## Diagrama de arquitectura

```mermaid
graph TB
    subgraph External["Entrada"]
        User["Usuario / Frontend"]
        GW["API Gateway :8000"]
    end

    subgraph OrchestratorLayer["Capa de Orquestación"]
        Orchestrator["OrchestratorAgent<br/>Router + Coordinador"]
        IntentClassifier["IntentClassifier<br/>Clasificación vía LLM"]
    end

    subgraph AgentLayer["Agentes Especializados"]
        Coach["WellnessCoachAgent<br/>Conversacional general"]
        Nutrition["NutritionAgent<br/>Nutrición y dieta"]
        Analytics["AnalyticsAgent<br/>Progreso y estadísticas"]
        Motivation["MotivationAgent<br/>Bienestar cognitivo-emocional"]
        Safety["SafetyGuardianAgent<br/>Validación de seguridad"]
    end

    subgraph ToolLayer["Capa de Herramientas"]
        Tools["8 Wellness Tools<br/>exercise_catalog, generate_routine,<br/>get_habits, log_habit, get_progress,<br/>get_routine, rag_search, safety_check"]
    end

    subgraph DataLayer["Capa de Datos"]
        PG[("PostgreSQL<br/>conversation_history<br/>users, routines, habits")]
        ChromaDB[("ChromaDB<br/>363 chunks<br/>6 dominios A-F")]
    end

    subgraph LLM["IA Local"]
        Ollama["Ollama<br/>phi3:mini<br/>localhost:11434"]
    end

    User -->|"POST /chat"| GW
    GW -->|"Proxy"| Orchestrator
    Orchestrator --> IntentClassifier
    IntentClassifier -->|"clasifica intención"| Orchestrator

    Orchestrator -->|"delega"| Coach
    Orchestrator -->|"delega"| Nutrition
    Orchestrator -->|"delega"| Analytics
    Orchestrator -->|"delega"| Motivation
    Orchestrator -->|"valida safety"| Safety

    Coach --> Tools
    Nutrition -->|"rag_search, safety_check"| Tools
    Analytics -->|"get_progress, get_habits, get_routine"| Tools
    Motivation -->|"rag_search, log_habit"| Tools
    Safety -->|"safety_check, rag_search"| Tools

    Tools --> PG
    Tools --> ChromaDB

    Coach --> Ollama
    Nutrition --> Ollama
    Analytics --> Ollama
    Motivation --> Ollama
    Safety --> Ollama
    IntentClassifier --> Ollama
```

## Patrón de orquestación: Supervisor

### Definición

El patrón **Supervisor** utiliza un agente central (Orchestrator) que:
1. Recibe todas las solicitudes del usuario
2. Clasifica la intención usando el LLM
3. Delega al agente especializado apropiado
4. Valida la respuesta antes de retornarla
5. Gestiona errores y fallbacks

### Justificación

| Criterio | Supervisor | Jerárquico | Secuencial | Enjambre |
|----------|-----------|-----------|-----------|---------|
| Punto de entrada único | ✓ | ✓ | ✓ | ✗ |
| Routing por intención | ✓ | ✓ | ✗ | ✗ |
| Seguridad centralizada | ✓ | ✓ | ✗ | ✗ |
| Simpleza para phi3:mini | ✓ | ✗ | ✓ | ✗ |
| Escalabilidad futura | ✓ | ✓ | ✗ | ✓ |
| Complejidad de implementación | Baja | Alta | Baja | Muy alta |

**Decisión**: Supervisor es el patrón óptimo porque:
- La plataforma tiene un único punto de entrada (POST /chat)
- Los dominios son claros y disjuntos (nutrición, ejercicio, seguridad, cognitivo)
- La validación de seguridad debe ser centralizada (no delegada a cada agente)
- phi3:mini tiene capacidades limitadas; la simpleza reduce puntos de fallo
- Es coherente con el `Orchestrator` Protocol ya definido en `src/orchestration/__init__.py`

**Por qué no los otros:**
- **Jerárquico**: No hay necesidad de múltiples niveles de gestión (Orchestrator → Manager → Worker). Un solo nivel de delegación es suficiente.
- **Secuencial**: Las consultas necesitan routing a diferentes agentes, no procesamiento lineal en cadena.
- **Enjambre (Swarm)**: Auto-organización innecesaria para este alcance. Los agentes no necesitan descubrir ni negociar entre sí.

## Definición de roles y responsabilidades

### OrchestratorAgent

| Aspecto | Detalle |
|---------|---------|
| **Responsabilidad** | Router central + coordinador de flujo |
| **Dominio** | Todos (no especializado en ninguno) |
| **Tools** | Ninguno (usa LLM para clasificar intención) |
| **Entrada** | `AgentMessage` del usuario vía API Gateway |
| **Salida** | `AgentMessage` con respuesta del agente destino |
| **Seguridad** | Valida nivel de safety de la respuesta antes de retornar |

**Flujo interno:**
1. Recibe mensaje del usuario
2. `IntentClassifier` clasifica intención (dominio + confianza)
3. Selecciona agente destino basado en dominio
4. Delega con contexto (perfil usuario, historial, tools disponibles)
5. Recibe respuesta del agente
6. Verifica nivel de seguridad (delega a SafetyGuardian si es necesario)
7. Retorna respuesta al usuario

### WellnessCoachAgent

| Aspecto | Detalle |
|---------|---------|
| **Responsabilidad** | Conversaciones generales de bienestar |
| **Dominio** | General (cuando no hay dominio específico) |
| **Tools** | 8 tools completos |
| **Entrada** | Mensaje + perfil usuario + historial |
| **Salida** | Respuesta textual con reasoning ReAct |
| **Estado** | Implementado (Sprint 2) |

### NutritionAgent

| Aspecto | Detalle |
|---------|---------|
| **Responsabilidad** | Consultas sobre nutrición, dieta, hidratación |
| **Dominio** | E (Nutri-Buddy) — 13 chunks |
| **Tools** | `rag_search`, `safety_check` |
| **Entrada** | Mensaje + perfil usuario |
| **Salida** | Recomendación nutricional personalizada |
| **Conocimiento** | Base de conocimiento dominio E |

### AnalyticsAgent

| Aspecto | Detalle |
|---------|---------|
| **Responsabilidad** | Progreso, estadísticas, tendencias de ejercicio |
| **Dominio** | A (Physio-Evaluator) + B (Exercise Architect) — 217 chunks |
| **Tools** | `get_progress`, `get_habits`, `get_routine` |
| **Entrada** | Mensaje + user_id |
| **Salida** | Resumen de progreso con datos reales |
| **Conocimiento** | Datos de PostgreSQL + conocimiento dominios A-B |

### MotivationAgent

| Aspecto | Detalle |
|---------|---------|
| **Responsabilidad** | Bienestar cognitivo-emocional, motivación |
| **Dominio** | F (Mind & Soul) — 101 chunks |
| **Tools** | `rag_search`, `log_habit` |
| **Entrada** | Mensaje + perfil usuario |
| **Salida** | Actividad cognitiva/emocional recomendada |
| **Conocimiento** | Base de conocimiento dominio F |

### SafetyGuardianAgent

| Aspecto | Detalle |
|---------|---------|
| **Responsabilidad** | Validación de seguridad transversal |
| **Dominio** | D (Safety Guardian) — 9 chunks |
| **Tools** | `safety_check`, `rag_search` |
| **Entrada** | Respuesta de otro agente + perfil usuario |
| **Salida** | Nivel de seguridad (safe/warning/critical) + versión segura |
| **Comportamiento** | Cross-cutting: validado por el Orchestrator después de cada respuesta |

## Flujo de comunicación y delegación

### Flujo normal (Happy path)

```mermaid
sequenceDiagram
    participant U as Usuario
    participant O as Orchestrator
    participant I as IntentClassifier
    participant A as Agente destino
    participant T as Tools
    participant L as LLM

    U->>O: POST /chat {user_id, message}
    O->>I: classify(message)
    I->>L: Prompt: "Clasifica: {message}"
    L-->>I: {domain: "nutrition", confidence: 0.9}
    I-->>O: IntentResult

    O->>O: select_agent(domain)
    O->>A: handle(message, user_profile, history)
    
    loop ReAct (max 3 iteraciones)
        A->>L: system_prompt + user_prompt
        L-->>A: {thought, action, action_input}
        A->>T: execute(action, action_input)
        T-->>A: ToolResult
        A->>L: context + tool_result
    end
    
    L-->>A: {final_answer: "..."}
    A-->>O: AgentResponse(text, safety_level)

    alt safety_level == "critical"
        O->>O: Bloquear + fallback
        O-->>U: "Consulta a un profesional"
    else safety_level == "safe"
        O-->>U: Respuesta del agente
    end
```

### Flujo de error (fallback)

```mermaid
sequenceDiagram
    participant U as Usuario
    participant O as Orchestrator
    participant A as Agente destino
    participant L as LLM

    U->>O: POST /chat {user_id, message}
    O->>O: classify → domain: "nutrition"
    O->>A: handle(message, ...)
    
    alt Agente falla
        A-->>O: AgentResponse(error="timeout")
        O->>O: Fallback a WellnessCoachAgent
        O->>O: WellnessCoachAgent.handle(message, ...)
        O-->>U: Respuesta de fallback
    else Sin agente para dominio
        O->>O: No agent for domain "unknown"
        O-->>U: "No puedo ayudar con eso"
    end
```

### Flujo multi-agente (delegación cruzada)

```mermaid
sequenceDiagram
    participant U as Usuario
    participant O as Orchestrator
    participant N as NutritionAgent
    participant S as SafetyGuardian
    participant L as LLM

    U->>O: POST /chat "¿Puedo comerpizza con presión alta?"
    O->>N: handle(message, ...)
    N->>L: ReAct → rag_search(dominio E)
    L-->>N: Recomendación nutricional
    N-->>O: AgentResponse(text, safety_level="warning")

    O->>S: validate(response, user_profile)
    S->>L: Evalúa safety
    L-->>S: {level: "critical", reason: "hipertensión"}
    S-->>O: SafetyResult(level="critical")

    O->>O: Bloquear respuesta original
    O-->>U: "Consulta a tu médico antes de cambiar tu dieta"
```

## Tools por agente

| Tool | Coach | Nutrition | Analytics | Motivation | Safety |
|------|:-----:|:---------:|:---------:|:----------:|:------:|
| exercise_catalog | ✓ | — | — | — | — |
| generate_routine | ✓ | — | — | — | — |
| get_habits | ✓ | — | ✓ | — | — |
| log_habit | ✓ | — | — | ✓ | — |
| get_progress | ✓ | — | ✓ | — | — |
| get_routine | ✓ | — | ✓ | — | — |
| rag_search | ✓ | ✓ | — | ✓ | ✓ |
| safety_check | ✓ | ✓ | — | — | ✓ |

## Restricciones y limitaciones

### Técnicas
- **phi3:mini (3.8B)**: No sigue confiablemente formato ReAct (~40% falla en tool calling). Prompts deben ser cortos (<200 tokens).
- **Un solo modelo LLM**: Todos los agentes comparten phi3:mini. No hay recursos para múltiples modelos.
- **Sin streaming entre agentes**: Comunicación síncrona via method calls, no event-driven.

### De dominio
- **RAG con precision@5 = 0.08**: Solo 8% de chunks recuperados son relevantes. La calidad de respuestas RAG depende de la precisión del retrieval.
- **Detección de dominio por keywords (40% accuracy)**: El IntentClassifier necesita mejora futura con embeddings.

### Operacionales
- **Una sesión por usuario**: Sin TTL en memoria conversacional.
- **Sin evaluación completa**: Solo 7/20 escenarios evaluados contra Ollama real.
- **Mock data en evaluación**: Tools fallan con datos mock (user_id incorrecto).

## Sprint 3 — Cadena de issues

| Issue | Título | Relación con arquitectura |
|-------|--------|--------------------------|
| S3-01 | Diseñar arquitectura multiagente | **Este documento** |
| S3-02 | Implementar OrchestratorAgent | Implementa capa de orquestación |
| S3-03 | Implementar agente especializado | Implementa uno de los agentes (Nutrition/Analytics/Motivation) |
| S3-04 | Comunicación y delegación entre agentes | Implementa AgentMessage + routing |
| S3-05 | Integrar con datos y servicios | Conecta agentes a PostgreSQL + RAG |
| S3-06 | Evaluar flujo multiagente | Pruebas de integración + observabilidad |
| S3-07 | Documentar Sprint 3 + demo | Documentación final + demostración |

# Arquitectura de Agentes — SeniorVital

## Interfaz base: Agent Protocol

Todos los agentes del sistema implementan un Protocol común que define el contrato de comunicación.

```python
from typing import Protocol, Any
from dataclasses import dataclass

@dataclass
class AgentRequest:
    """Solicitud entrante a un agente."""
    message: str
    user_id: int
    user_profile: dict
    conversation_history: list
    context: dict = field(default_factory=dict)

@dataclass
class AgentResponse:
    """Respuesta saliente de un agente."""
    text: str
    safety_level: str  # "safe" | "warning" | "critical"
    tool_chain: list[str]
    metadata: dict = field(default_factory=dict)

class Agent(Protocol):
    """Contrato base para todos los agentes del sistema."""
    
    name: str
    domain: str
    description: str
    
    async def handle(self, request: AgentRequest) -> AgentResponse:
        """Procesa una solicitud y retorna una respuesta."""
        ...
    
    def can_handle(self, intent: str, confidence: float) -> bool:
        """Determina si este agente puede manejar la intención dada."""
        ...
```

## WellnessCoachAgent — Implementado

### Especificación

| Campo | Valor |
|-------|-------|
| **Clase** | `WellnessCoachAgent` |
| **Archivo** | `src/agents/wellness/coach.py` |
| **Nombre** | `"wellness_coach"` |
| **Dominio** | `"general"` |
| **Estado** | Implementado (Sprint 2) |

### Dependencias

```
WellnessCoachAgent
├── LLMService (Ollama phi3:mini)
├── UserDataService (perfil usuario)
├── list[Tool] (8 tools)
├── MemoryStore (PostgreSQL, opcional)
├── WellnessConfig
├── WellnessCoachPromptBuilder
└── ReActEngine
```

### Tools asignados

| Tool | Propósito |
|------|-----------|
| `exercise_catalog` | Buscar ejercicios por nivel/keyword/contraindicaciones |
| `generate_routine` | Generar rutina diaria personalizada |
| `get_habits` | Obtener registros de hábitos (agua, sueño) |
| `log_habit` | Registrar hábito (agua, sueño) |
| `get_progress` | Obtener insights y progreso semanal |
| `get_routine` | Obtener rutina activa del día |
| `rag_search` | Consultar base de conocimiento |
| `safety_check` | Verificar seguridad de actividad |

### Prompt especializado

```
Eres el Wellness Coach de SeniorVital, un coach de bienestar para adultos mayores.

## REGLAS
1. SEGURIDAD: Si hay duda sobre salud, recomienda consultar a un profesional.
2. EMPATÍA: Habla como un amigo que se preocupa. Tono cálido y motivacional.
3. IDIOMA: Responde SIEMPRE en español.
4. FORMATO: Responde SOLO con JSON válido.
5. LÍMITES: No des diagnósticos médicos.

## FORMATO
{"thought": "tu razonamiento", "final_answer": "tu respuesta"}
{"thought": "tu razonamiento", "action": "tool_name", "action_input": {"param": "valor"}}
```

### Comportamiento

- Clasificación de intención: No aplica (agente general, maneja todo lo que Orchestrator delega)
- Fallback: Si falla, Orchestrator retorna mensaje de error genérico
- Safety: Verifica `safety_check` antes de recomendaciones de ejercicio

---

## NutritionAgent — Propuesto (S3-03)

### Especificación

| Campo | Valor |
|-------|-------|
| **Clase** | `NutritionAgent` |
| **Archivo** | `src/agents/wellness/nutrition.py` |
| **Nombre** | `"nutrition"` |
| **Dominio** | `"E"` (Nutri-Buddy) |
| **Chunks** | 13 |
| **Estado** | Propuesto |

### Dependencias

```
NutritionAgent
├── LLMService (Ollama phi3:mini)
├── UserDataService (perfil usuario)
├── list[Tool]: [rag_search, safety_check]
├── MemoryStore (PostgreSQL, opcional)
├── WellnessConfig
└── WellnessCoachPromptBuilder (adaptado)
```

### Tools asignados

| Tool | Propósito |
|------|-----------|
| `rag_search` | Consultar conocimiento nutricional (dominio E) |
| `safety_check` | Verificar restricciones médicas para dieta |

### Prompt especializado

```
Eres el asistente de nutrición de SeniorVital, especializado en dietas para adultos mayores.

## REGLAS
1. Nutrición para adultos mayores (60+ años)
2. Considera restricciones médicas (diabetes, hipertensión, colesterol)
3. Recomendaciones prácticas y accesibles
4. No des planes dietéticos sin consultar a un profesional
5. Responde en español

## FORMATO
{"thought": "tu razonamiento", "final_answer": "tu respuesta"}
{"thought": "tu razonamiento", "action": "rag_search", "action_input": {"query": "..."}}
```

### Intenciones que maneja

- "¿Qué debo comer?"
- "¿Cuánta agua debo tomar?"
- "¿Es bueno comer [alimento]?"
- "Necesito una dieta para [condición]"
- "¿Cuántas calorías debo consumir?"

---

## AnalyticsAgent — Propuesto

### Especificación

| Campo | Valor |
|-------|-------|
| **Clase** | `AnalyticsAgent` |
| **Archivo** | `src/agents/wellness/analytics.py` |
| **Nombre** | `"analytics"` |
| **Dominio** | `"A+B"` (Physio-Evaluator + Exercise Architect) |
| **Chunks** | 217 |
| **Estado** | Propuesto |

### Dependencias

```
AnalyticsAgent
├── LLMService (Ollama phi3:mini)
├── UserDataService (perfil usuario)
├── list[Tool]: [get_progress, get_habits, get_routine]
├── WellnessConfig
└── AnalyticsPromptBuilder (nuevo)
```

### Tools asignados

| Tool | Propósito |
|------|-----------|
| `get_progress` | Obtener insights, actividad semanal, sesiones totales |
| `get_habits` | Obtener registros de hábitos para análisis |
| `get_routine` | Obtener rutina activa para comparar con progreso |

### Prompt especializado

```
Eres el analista de bienestar de SeniorVital, especializado en progreso y estadísticas de ejercicio.

## REGLAS
1. Usa datos reales del usuario (no inventes estadísticas)
2. Presenta datos de forma clara y visual (listas, porcentajes)
3. Compara con metas y tendencias previas
4. Sé motivador pero realista
5. Responde en español

## FORMATO
{"thought": "tu razonamiento", "final_answer": "tu respuesta"}
{"thought": "tu razonamiento", "action": "get_progress", "action_input": {"user_id": 1}}
```

### Intenciones que maneja

- "¿Cómo voy con mis ejercicios?"
- "¿Cuántos ejercicios he hecho esta semana?"
- "Muéstrame mi progreso"
- "¿He mejorado este mes?"
- "¿Cuál es mi rutina de hoy?"

---

## MotivationAgent — Propuesto

### Especificación

| Campo | Valor |
|-------|-------|
| **Clase** | `MotivationAgent` |
| **Archivo** | `src/agents/wellness/motivation.py` |
| **Nombre** | `"motivation"` |
| **Dominio** | `"F"` (Mind & Soul) |
| **Chunks** | 101 |
| **Estado** | Propuesto |

### Dependencias

```
MotivationAgent
├── LLMService (Ollama phi3:mini)
├── UserDataService (perfil usuario)
├── list[Tool]: [rag_search, log_habit]
├── MemoryStore (PostgreSQL, opcional)
├── WellnessConfig
└── MotivationPromptBuilder (nuevo)
```

### Tools asignados

| Tool | Propósito |
|------|-----------|
| `rag_search` | Consultar conocimiento cognitivo-emocional (dominio F) |
| `log_habit` | Registrar actividad cognitiva completada |

### Prompt especializado

```
Eres el coach de bienestar emocional y cognitivo de SeniorVital.

## REGLAS
1. Enfócate en estimulación cognitiva y bienestar emocional
2. Recomienda actividades apropiadas para la edad
3. Sé cálido y motivador
4. Considera el contexto social y emocional del usuario
5. Responde en español

## FORMATO
{"thought": "tu razonamiento", "final_answer": "tu respuesta"}
{"thought": "tu razonamiento", "action": "rag_search", "action_input": {"query": "..."}}
```

### Intenciones que maneja

- "Me siento triste/aburrido"
- "Necesito actividad mental"
- "¿Qué juegos puedo hacer?"
- "Cómo mantener mi mente activa"
- "Ejercicios de memoria"

---

## SafetyGuardianAgent — Propuesto (Cross-cutting)

### Especificación

| Campo | Valor |
|-------|-------|
| **Clase** | `SafetyGuardianAgent` |
| **Archivo** | `src/agents/wellness/safety_guardian.py` |
| **Nombre** | `"safety_guardian"` |
| **Dominio** | `"D"` (Safety Guardian) |
| **Chunks** | 9 |
| **Estado** | Propuesto |
| **Rol** | Validación transversal (no es agente de routing) |

### Dependencias

```
SafetyGuardianAgent
├── LLMService (Ollama phi3:mini)
├── UserDataService (perfil usuario)
├── list[Tool]: [safety_check, rag_search]
├── WellnessConfig
└── SafetyPromptBuilder (nuevo)
```

### Tools asignados

| Tool | Propósito |
|------|-----------|
| `safety_check` | Verificar si actividad es segura para perfil médico |
| `rag_search` | Consultar conocimiento de seguridad (dominio D) |

### Prompt especializado

```
Eres el guardián de seguridad de SeniorVital. Tu ÚNICO trabajo es evaluar si una respuesta es segura.

## REGLAS
1. Evalúa si la actividad recomendada es segura para el perfil médico del usuario
2. Detecta riesgos: caídas, sobreesfuerzo, contraindicaciones médicas
3. Si hay riesgo, clasifica como "warning" o "critical"
4. Nunca recomiendes actividad física sin verificar restricciones
5. Responde en español

## FORMATO DE SALIDA
{"safe": true/false, "level": "safe|warning|critical", "reason": "explicación"}
```

### Comportamiento

- No es invocado directamente por el Orchestrator para routing
- Es invocado por el Orchestrator DESPUÉS de recibir respuesta de otro agente
- Validación post-hoc: revisa la respuesta antes de enviarla al usuario
- Si `level == "critical"`: bloquea la respuesta y genera fallback

---

## Mapeo de dominios RAG → Agentes

| Dominio RAG | Macrodominio | Chunks | Agente asignado |
|-------------|-------------|--------|-----------------|
| Physio-Evaluator | A | 35 | AnalyticsAgent |
| Exercise Architect | B | 182 | AnalyticsAgent |
| Context-Adaptor | C | 23 | WellnessCoachAgent (general) |
| Safety Guardian | D | 9 | SafetyGuardianAgent |
| Nutri-Buddy | E | 13 | NutritionAgent |
| Mind & Soul | F | 101 | MotivationAgent |

## Evolución desde Sprint 2

| Componente | Sprint 2 | Sprint 3 |
|------------|---------|---------|
| WellnessCoachAgent | Agente único con todos los tools | Agente general + 4 especializados |
| Tool calling | 8 tools en un agente | Subconjuntos por agente |
| Safety | Integrado en WellnessCoachAgent | SafetyGuardianAgent transversal |
| Routing | No existe (todo va al coach) | OrchestratorAgent con IntentClassifier |
| Memoria | Una conversación por usuario | Memoria compartida + contexto inter-agentes |

# NutritionAgent

Agente especializado en consultas de nutricion, dieta, hidratacion y cuidado del adulto mayor.

## Responsabilidad

Procesar preguntas del usuario sobre alimentacion, planificacion de comidas, restricciones dieteticas y recomendaciones de hidratacion. Utiliza RAG para fundamentar respuestas con conocimiento del dominio E (Nutri-Buddy).

## Arquitectura

| Aspecto | Detalle |
|---------|---------|
| **Dominio** | E (Nutri-Buddy) — 13 chunks en ChromaDB |
| **Tools** | `rag_search`, `safety_check` |
| **Estado** | Disenado, no implementado |
| **Delegado desde** | OrchestratorAgent via IntentClassifier |

## Flujo

```
Usuario -> OrchestratorAgent -> IntentClassifier (dominio=nutrition)
  -> NutritionAgent -> rag_search(knowledge_base, query)
  -> safety_check(response)
  -> Respuesta personalizada
```

## Tools

### rag_search

Busca en la base de conocimiento del dominio E (Nutri-Buddy) chunks relevantes para la consulta del usuario.

- **Knowledge base**: `data/knowledge/domains/E_nutri_buddy/`
- **Embeddings**: `intfloat/multilingual-e5-small` (384d)
- **Vector store**: ChromaDB en `data/vector_store/`
- **Retrieval**: Top-3 chunks, cosine similarity

### safety_check

Valida que la respuesta no contenga recomendaciones medicas sin disclaimer.

- Retorna `safety_level`: `safe` | `warning` | `critical`
- Si `critical`: OrchestratorAgent bloquea la respuesta y retorna mensaje generico

## Conocimiento

El dominio E cubre:
- Planificacion de comidas para adultos mayores
- Restricciones dieteticas (diabetes, hipertension, colesterol alto)
- Hidratacion y recomendaciones de consumo de agua
- Suplementacion vitaminica
- Alimentos ricos en calcio, fibra, proteinas

## Implementacion futura

Para implementar este agente:
1. Crear `src/agents/nutrition/agent.py` con clase `NutritionAgent`
2. Implementar interfaz `AgentProtocol` (handle, get_capabilities)
3. Registrar en `src/orchestration/router.py` mappings
4. Agregar tests en `tests/nutrition/`

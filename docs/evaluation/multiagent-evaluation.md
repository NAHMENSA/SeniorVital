# Evaluación Multi-agente

## Queries multi-dominio

Se identificaron 2 queries que involucran múltiples dominios:

| Query | Dominios esperados | Dominio detectado | Resultado |
|-------|-------------------|-------------------|-----------|
| "¿Puede una persona con diabetes hacer ejercicio?" | B + D | B | Parcial — recuperó chunks de B, no de D |
| "¿Qué alimentos son ricos en calcio para osteoporosis?" | E + A | E | Parcial — recuperó chunks de E, no de A |

## Análisis

### Problema de routing

El pipeline actual solo detecta **un** dominio por query. Cuando una query involucra múltiples dominios:

1. Solo se recupera del dominio detectado
2. Los chunks del dominio secundario se pierden
3. La respuesta es incompleta

### Ejemplo: "diabetes y ejercicio"

- **Dominio detectado**: B (Ejercicio)
- **Chunks recuperados**: Solo de dominio B
- **Faltan**: Chunks de dominio D (Seguridad clínica) que mencionan precauciones específicas para diabetes
- **Resultado**: La respuesta menciona ejercicio pero omite precauciones clínicas

### Estrategia actual vs ideal

| Aspecto | Actual | Ideal |
|---------|--------|-------|
| Routing | 1 dominio por query | Múltiples dominios |
| Recuperación | Filtro por 1 macrodominio | Búsqueda híbrida |
| Contexto | Solo chunks del dominio detectado | Chunks de todos los dominios relevantes |

## Recomendaciones

1. **Detección multi-dominio**: Modificar QueryProcessor para detectar múltiples dominios
2. **Búsqueda híbrida**: Buscar en todos los dominios y rankear por relevancia
3. **Fusión de resultados**: Combinar resultados de múltiples dominios antes de generar
4. **Prompt multi-agente**: Modificar PromptBuilder para incluir contexto de múltiples agentes

# Evaluación por Agente

## Rendimiento por agente

| Agente | Dominio | Precision@5 | Recall@5 | Keyword Coverage | Detección |
|--------|---------|-------------|----------|------------------|-----------|
| Nutri-Buddy | E | 0.200 | 0.333 | 0.800 | ❌ No detectado |
| Physio-Evaluator | A | 0.000 | 0.000 | 1.000 | ✅ Detectado |
| Exercise Architect | B | 0.200 | 1.000 | 0.750 | ✅ Detectado |
| Context-Adaptor | C | — | — | — | No evaluado |
| Safety Guardian | D | 0.000 | 0.000 | 0.750 | ❌ Detectado como B |
| Mind & Soul | F | 0.000 | 0.000 | 0.500 | ❌ Detectado como B |

## Análisis por agente

### Exercise Architect (B) — Mejor rendimiento

- **Precision**: 0.200 (mejor de todos)
- **Recall**: 1.000 (encontró todos los relevantes)
- **Detección**: Correcta en 100% de las queries
- **Razón**: Dominio con más chunks (182), mejor cobertura semántica

### Nutri-Buddy (E) — Rendimiento medio

- **Precision**: 0.200
- **Recall**: 0.333
- **Detección**: Falló — el pipeline detectó dominio E como no detectado
- **Razón**: Dominio pequeño (13 chunks), pero la respuesta fue correcta

### Physio-Evaluator (A) — Recall bajo

- **Precision**: 0.000
- **Recall**: 0.000
- **Detección**: Correcta
- **Razón**: Los chunks recuperados no coinciden con los ground truth (distancia semántica)

### Safety Guardian (D) — Confusión de dominio

- **Precision**: 0.000
- **Recall**: 0.000
- **Detección**: Incorrecta (detectado como B)
- **Razón**: Dominio muy pequeño (9 chunks), se confunde con B por keywords compartidas

### Mind & Soul (F) — Peor rendimiento

- **Precision**: 0.000
- **Recall**: 0.000
- **Detección**: Incorrecta (detectado como B)
- **Razón**: 101 chunks pero keywords genéricas que se superponen con B

## Problemas transversales

1. **Confusión B↔F**: Ambos dominios comparten keywords de ejercicio y bienestar
2. **Dominios pequeños (D, E)**: Con pocos chunks, la recuperación es menos precisa
3. **Detección por keywords es frágil**: El QueryProcessor usa overlap de keywords que se superpone entre dominios

## Recomendaciones

1. **Mejorar detección de dominio**: Usar embeddings en vez de keywords para clasificación
2. **Agregar contexto al query**: Incluir el nombre del agente en la consulta al vector store
3. **Re-balancear chunks**: Los dominios D y E tienen muy pocos chunks (9 y 13)
4. **Agregar chunks sintéticos**: Para dominios pequeños, generar chunks adicionales

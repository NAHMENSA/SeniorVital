# Informe de Evaluación RAG — SeniorVital

## Resumen ejecutivo

Se evaluó el pipeline RAG de SeniorVital con 5 consultas representativas (de 30 planificadas). El sistema muestra **fortalezas en generación de respuestas** pero **limitaciones significativas en recuperación y detección de dominio**.

## Métricas principales

| Métrica | Valor | Estado |
|---------|-------| |
| Precision@5 | 0.080 | 🔴 Crítico |
| Recall@5 | 0.267 | 🟡 Bajo |
| MRR | 0.400 | 🟡 Medio |
| Hit Rate | 0.400 | 🟡 Medio |
| Domain Accuracy | 0.400 | 🟡 Bajo |
| Keyword Coverage | 0.760 | 🟢 Bueno |
| Citation Rate | 0.800 | 🟢 Bueno |
| Hallucination Rate | 1.000 | 🔴 Crítico |

## Fortalezas

1. **Keyword coverage alto (76%)**: Las respuestas contienen la información clave esperada
2. **Citas frecuentes (80%)**: El LLM referencia fuentes correctamente
3. **Pipeline funcional**: El sistema completo opera end-to-end
4. **Dominio B fuerte**: Recall perfecto (100%) para queries de ejercicio

## Limitaciones

### 1. Recuperación pobre (Precision@5 = 0.08)

**Problema**: Solo 8% de los chunks recuperados son relevantes.

**Causa raíz**: Los embeddings `intfloat/multilingual-e5-small` no capturan bien la relevancia semántica en este dominio específico. Los chunks recuperados son topicalmente relacionados pero no contienen la información específica buscada.

**Mejora propuesta**:
- Re-entrenar embeddings con fine-tuning en el dominio de bienestar
- Usar hybrid search (keywords + semántica)
- Aumentar k y filtrar por relevancia

### 2. Detección de dominio incorrecta (40%)

**Problema**: El QueryProcessor usa overlap de keywords que se superpone entre dominios.

**Causa raíz**: Keywords como "ejercicio", "fuerza", "equilibrio" aparecen en múltiples dominios (A, B, D, F).

**Mejora propuesta**:
- Usar un clasificador basado en embeddings en vez de keywords
- Agregar contexto del agente al query
- Implementar detección multi-dominio

### 3. Alucinaciones (100%)

**Problema**: Todas las respuestas contienen información no sustentada por el contexto.

**Causa raíz**: phi3:mini genera información general del entrenamiento que no está en los chunks recuperados.

**Mejora propuesta**:
- Agregar instrucción estricta de "solo usar información del contexto"
- Implementar verificación post-generación
- Usar RAGAS faithfulness score

### 4. Dominios pequeños (D=9, E=13 chunks)

**Problema**: Con pocos chunks, la recuperación es menos precisa.

**Mejora propuesta**:
- Generar chunks sintéticos para dominios pequeños
- Re-chunkear documentos existentes con mayor granularidad
- Agregar más documentos fuente

## Top 5 queries exitosas

1. **B01** (Ejercicio aeróbico): Recall=1.0, respuesta precisa sobre 150 min/semana
2. **E01** (Alimentos recomendados): Keyword coverage=0.8, respuesta completa
3. **A03** (Osteoporosis): Keyword coverage=1.0, detección correcta
4. **D01** (Diabetes y ejercicio): Keyword coverage=0.75, respuesta útil
5. **F01** (Memoria): Keyword coverage=0.5, intento razonable

## Top 5 queries problemáticas

1. **F01** (Memoria): No encontró chunks de dominio F, dice "no hay ejercicios específicos"
2. **A03** (Osteoporosis): Precision=0, los chunks recuperados no son los ground truth
3. **D01** (Diabetes): Dominio detectado incorrectamente (B en vez de D)
4. **B04** (Equilibrio): No ejecutada (timeout)
5. **E03** (Calorías): No ejecutada (timeout)

## Recomendaciones prioritarias

### Corto plazo (1-2 semanas)

1. **Aumentar timeout de Ollama**: Configurar 300s en vez de 60s
2. **Ejecutar evaluación completa**: Correr las 30 queries para tener datos robustos
3. **Agregar instrucción anti-alucinación** al PromptBuilder

### Mediano plazo (2-4 semanas)

4. **Mejorar detección de dominio**: Implementar clasificador basado en embeddings
5. **Hybrid search**: Combinar búsqueda semántica con keywords
6. **Re-balancear chunks**: Agregar contenido a dominios D y E

### Largo plazo (1-2 meses)

7. **Fine-tuning de embeddings**: Entrenar en el dominio de bienestar
8. **RAGAS evaluation**: Implementar métricas con framework RAGAS
9. **Multi-domain retrieval**: Soporte para queries multi-dominio

## Archivos de evidencia

- `data/evaluation/test_queries.json` — Query set con ground truth
- `data/evaluation/results/raw_results.json` — Resultados crudos por query
- `data/evaluation/results/metrics_summary.json` — Métricas computadas
- `tests/rag/test_evaluation.py` — Tests del framework de evaluación
- `scripts/evaluation/run_evaluation.py` — Script de ejecución

## Conclusión

El pipeline RAG de SeniorVital es **funcional pero no producción-ready**. La recuperación y detección de dominio necesitan mejoras significativas antes de desplegar. Las respuestas generadas son útiles pero contienen alucinaciones que deben mitigarse.

La evaluación demuestra que el sistema tiene una **base sólida** (pipeline completo, 363 chunks, 6 agentes) pero requiere **optimización del retrieval** y **mejora de la detección de dominio** para alcanzar calidad de producción.

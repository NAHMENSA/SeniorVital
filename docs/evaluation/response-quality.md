# Calidad de Respuestas

## Métricas implementadas

### Keyword Coverage

Porcentaje de palabras clave esperadas que aparecen en la respuesta.

```
keyword_coverage = |keywords_en_respuesta| / |keywords_esperadas|
```

### Citation Check

Verifica si la respuesta referencia fuentes (patrones: [1], "fuente", "según").

### Hallucination Flag

Detecta oraciones que contienen palabras no presentes en el contexto recuperado.

### Answer Length Stats

Estadísticas descriptivas: min, max, media, mediana, desviación estándar.

## Resultados (muestra de 5 queries)

| Métrica | Valor |
|---------|-------|
| Keyword Coverage | 0.760 |
| Citation Rate | 0.800 |
| Hallucination Rate | 1.000 |
| Answer Length (avg) | 214 palabras |

## Análisis cualitativo

### Casos exitosos

**E01 (Nutrición)**: La respuesta incluye verduras, frutas, cereales, proteína, lácteos. Cita la fuente correctamente.

**B01 (Ejercicio)**: Respuesta precisa sobre 150 minutos semanales. Referencia múltiples fuentes.

### Casos problemáticos

**D01 (Diabetes + Ejercicio)**: El pipeline recuperó chunks de dominio B en vez de D. La respuesta es correcta pero el dominio detectado es incorrecto.

**F01 (Memoria)**: El pipeline no encontró chunks de dominio F. La respuesta dice "no hay ejercicios específicos de memoria mencionados" — cuando sí existen en el dominio F.

### Problemas identificados

1. **Alta tasa de alucinación (100%)**: Todas las respuestas contienen información no sustentada por el contexto
2. **Citas frecuentes (80%)**: La mayoría de respuestas referencian fuentes correctamente
3. **Keywords bien cubiertas (76%)**: Las respuestas incluyen la información clave
4. **Respuestas largas (214 palabras promedio)**: Podrían ser más concisas

## Recomendaciones

1. **Mejorar detección de dominio**: El QueryProcessor confunde dominios con keywords superpuestas
2. **Aumentar relevancia de chunks**: Precision@5 es muy baja (0.08)
3. **Reducir alucinaciones**: El LLM genera información no presente en el contexto
4. **Agregar validación de fuentes**: Verificar que las respuestas solo usen información del contexto

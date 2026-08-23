# Métricas de Recuperación

## Métricas implementadas

### Precision@k

Fracción de los k resultados recuperados que son relevantes.

```
precision@k = |relevantes en top-k| / k
```

**Rango**: [0.0, 1.0]. 1.0 = todos los top-k son relevantes.

### Recall@k

Fracción de los ítems relevantes que fueron encontrados en top-k.

```
recall@k = |relevantes en top-k| / |relevantes totales|
```

**Rango**: [0.0, 1.0]. 1.0 = se encontraron todos los relevantes.

### MRR (Mean Reciprocal Rank)

Inverso del rank del primer resultado relevante.

```
MRR = 1/rank_del_primer_relevante
```

**Rango**: [0.0, 1.0]. 1.0 = el primer resultado es relevante.

### Hit Rate

Porcentaje de queries que tienen al menos 1 resultado relevante en top-k.

```
hit_rate = |queries_con_hit| / |total_queries|
```

### Macrodomain Accuracy

Precisión de detección del macrodominio correcto.

```
accuracy = |detecciones_correctas| / |total_queries|
```

## Resultados (muestra de 5 queries)

| Métrica | Valor | Interpretación |
|---------|-------|----------------|
| Precision@5 | 0.080 | Solo 8% de los top-5 son relevantes |
| Recall@5 | 0.267 | Se recuperó 27% de los relevantes |
| MRR | 0.400 | El relevante suele estar en posiciones 2-3 |
| Hit Rate | 0.400 | 40% de queries tienen al menos 1 relevante |
| Domain Accuracy | 0.400 | 40% de detecciones de dominio son correctas |

## Análisis por dominio

| Dominio | Precision | Recall | Keyword Coverage |
|---------|-----------|--------|------------------|
| A (Fisiología) | 0.000 | 0.000 | 1.000 |
| B (Ejercicio) | 0.200 | 1.000 | 0.750 |
| D (Seguridad) | 0.000 | 0.000 | 0.750 |
| E (Nutrición) | 0.200 | 0.333 | 0.800 |
| F (Cognitivo) | 0.000 | 0.000 | 0.500 |

## Observaciones clave

1. **Precision muy baja**: El pipeline recupera muchos chunks no relevantes junto con los relevantes
2. **Recall variable**: Dom B tiene recall perfecto (1.0), pero A, D, F tienen recall 0
3. **Detección de dominio pobre**: Solo 40% de accuracy — el QueryProcessor confunde dominios
4. **Buen keyword coverage**: Las respuestas contienen las palabras clave esperadas (76%)

## Limitaciones de la muestra

- Solo 5 de 30 queries ejecutadas (Ollama muy lento: ~100-500s/query)
- Necesita ejecución completa para conclusiones robustas

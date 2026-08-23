# Resultados de Comparación de Chunking — SeniorVital RAG

## Objetivo

Comparar las distintas iteraciones de la estrategia de chunking híbrida para validar que el corpus queda correctamente segmentado para el sistema RAG.

## Versiones comparadas

| Versión | Descripción |
|---|---|
| v0 (bug) | `_merge_small_chunks` inicializaba la lista de merge solo con el primer chunk, descartando el resto de cada documento. |
| v1 (merge conservador) | Merge con límite de 800 caracteres y criterio mixto (chars + palabras). |
| v2 (merge por palabras) | Merge basado en palabras (`< 80`), límite combinado de 1,000 caracteres, con absorción final hacia atrás. |

## Métricas

| Métrica | v0 (bug) | v1 (800 chars) | v2 (1,000 chars) |
|---|---:|---:|---:|
| Documentos procesados | 19 | 19 | 19 |
| Chunks totales | 19 | 417 | 363 |
| Chunks semánticos | 185 | 185 | 148 |
| Chunks fallback | 229 | 229 | 212 |
| Chunks estructurales | 3 | 3 | 3 |
| Palabras promedio | ~68 | 88.1 | 101.2 |
| Caracteres promedio | - | 579.3 | 665.8 |
| Chunks 80-120 palabras | 0 % | 65.9 % | 70.0 % |
| Chunks < 80 palabras | 100 % | 28.5 % | 13.8 % |
| Chunks > 120 palabras | 0 % | 5.5 % | 16.3 % |
| Cobertura de contenido | Pérdida masiva | Completa | Completa |

## Conclusiones

- **v0**: Inusable. Todo el contenido se condensaba en un único chunk por documento, perdiendo la mayoría del corpus.
- **v1**: Redujo drásticamente los chunks pequeños, pero quedaron 119 fragmentos por debajo de 80 palabras (28.5 %). El límite de 800 caracteres era demasiado estricto para absorber pequeños fragmentos semánticos.
- **v2**: Distribución más centrada en el rango objetivo de 80-120 palabras (70.0 %). El promedio de 101 palabras está en el centro del rango objetivo. El costo es un ligero aumento de chunks > 120 palabras (16.3 %), aceptable porque aún están lejos del límite de 2,000 tokens por chunk.

## Recomendación

La versión **v2** es la configuración actual recomendada. La mejora clave fue:

1. Inicializar el merge con **todos** los chunks, no solo el primero.
2. Usar el **número de palabras** (`< 80`) como principal criterio de merge.
3. Permitir combinaciones de hasta **1,000 caracteres** para absorver fragmentos pequeños sin romper límites semánticos.
4. Añadir un **paso de absorción hacia atrás** para el último chunk si queda pequeño.

## Archivos relevantes

- `src/knowledge/chunking/chunking_orchestrator.py` — lógica de merge.
- `data/processed/chunking_stats.json` — estadísticas de la versión v2.
- `data/processed/chunks/all_chunks.json` — chunks generados con la versión v2.
- `tests/rag/test_chunking.py` — pruebas unitarias que validan el merge y el pipeline.

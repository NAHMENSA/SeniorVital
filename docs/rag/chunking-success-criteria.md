# Criterios de Éxito para la Segmentación — SeniorVital RAG

## Objetivo

Definir criterios medibles para evaluar la calidad del chunking aplicado a la base de conocimiento de SeniorVital, garantizando que los chunks sean útiles para la posterior generación de embeddings y recuperación en el sistema RAG.

## Criterios de Calidad

### 1. Coherencia Semántica

- Cada chunk debe contener información temáticamente relacionada.
- No se deben cortar frases, procedimientos o recomendaciones a la mitad.
- Ejemplo negativo: un chunk que termine con "Coma de 8 a 10 onzas de" y el siguiente comience con "pescados y mariscos por semana".

### 2. Preservación de Contexto

- Los chunks deben conservar el contexto necesario para ser interpretados por el LLM.
- Las rutinas de ejercicio deben mantenerse completas: descripción, repeticiones, series y precauciones deben viajar juntas.
- Las progresiones de ejercicios (básico → intermedio → avanzado) no deben separarse.

### 3. Tamaño Adecuado

- Cada chunk debe tener entre **200 y 2.000 tokens** (aproximadamente).
- El límite superior se fija en **2.000 tokens** para dejar espacio al contexto del LLM generador.
- El límite inferior se fija en **200 tokens** para evitar chunks con información insuficiente.

### 4. Metadatos Completos

Cada chunk debe incluir obligatoriamente:

| Metadato | Descripción | Ejemplo |
|---|---|---|
| `document_name` | Nombre del documento fuente | `DOCUMENTO DE CONOCIMIENTO SENIORVITAL.md` |
| `macrodomain` | Letra del macrodominio (A-F) | `B` |
| `section_path` | Jerarquía de secciones (cuando aplique) | `Taxonomía del ejercicio > Fuerza` |
| `chunk_type` | Tipo de chunk generado | `semantic`, `structural`, `fallback` |
| `chunk_index` | Índice secuencial dentro del documento | `3` |
| `source_path` | Ruta relativa del documento fuente | `data/knowledge_base/...` |

### 5. Cobertura Completa

- Todo el contenido textual de cada documento debe quedar representado en al menos un chunk.
- No deben quedar párrafos, tablas ni listas sin procesar.

### 6. Manejo de Casos Especiales

| Caso | Criterio de Éxito |
|---|---|
| Tablas Markdown | Convertir a representación textual antes de chunking; no perder filas ni columnas. |
| Bloques de código | Eliminar fences ``` y tratar el contenido como texto plano. |
| Documentos muy cortos (< 500 palabras) | Generar al menos un chunk coherente; si es muy corto, fallback recursivo. |
| Documentos muy largos (> 5.000 palabras) | Dividir en múltiples chunks semánticos sin perder coherencia. |
| Documento con encabezados | Preservar jerarquía de secciones mediante `MarkdownHeaderTextSplitter`. |

## Métricas Cuantitativas

| Métrica | Umbral Mínimo | Objetivo |
|---|---|---|
| Cobertura de documentos | 100% procesados | 100% |
| Chunks dentro de rango de tokens (200-2000) | ≥ 80% | ≥ 90% |
| Chunks con metadatos completos | 100% | 100% |
| Tiempo de procesamiento de toda la KB | < 10 minutos | < 5 minutos |
| Pruebas unitarias que pasan | ≥ 80% cobertura | ≥ 90% cobertura |

## Criterios de Validación Manual

- Revisar al menos 5 chunks por macrodominio.
- Verificar que las preguntas de ejemplo encuentren respuesta en los chunks recuperados:
  - "¿Qué ejercicios de fuerza son seguros para un adulto mayor con osteoporosis?"
  - "¿Cómo adaptar una rutina para alguien con diabetes tipo 2?"
  - "¿Qué ejercicios de equilibrio se pueden hacer en casa?"
  - "¿Cuáles son las recomendaciones nutricionales para hipertensos?"

## Proceso de Evaluación

1. Ejecutar el chunking sobre toda la KB.
2. Generar estadísticas de chunks (`data/processed/chunking_stats.json`).
3. Revisar chunks manualmente para validar coherencia y contexto.
4. Ejecutar pruebas unitarias (`pytest tests/rag/test_chunking.py -v`).
5. Documentar resultados en `docs/rag/chunking-comparison-results.md`.

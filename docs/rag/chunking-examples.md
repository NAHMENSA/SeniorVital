# Ejemplos de Chunks Generados — SeniorVital RAG

## Resumen del corpus chunkado

| Métrica | Valor |
|---|---|
| Documentos procesados | 19 |
| Chunks generados | 424 |
| Chunks semánticos | 403 |
| Chunks estructurales | 7 |
| Chunks de fallback | 14 |
| Tamaño promedio | ~556 caracteres / ~84 palabras |

## Ejemplo 1: Chunk estructural con tabla convertida

**Archivo:** `DOCUMENTO DE CONOCIMIENTO SENIORVITAL.md`

```json
{
  "chunk_id": "c2462331-3e55-45d6-94dd-c1dd5877de91",
  "document_name": "DOCUMENTO DE CONOCIMIENTO SENIORVITAL.md",
  "source_path": "data/knowledge_base/DOCUMENTO DE CONOCIMIENTO SENIORVITAL.md",
  "macrodomain": "B",
  "macrodomain_name": "Taxonomía del ejercicio",
  "section_path": "Base de Rutinas de Ejercicios y Recomendaciones para Adultos Mayores > 1. PRINCIPIOS FUNDAMENTALES Y SEGURIDAD",
  "chunk_type": "structural",
  "chunk_index": 1,
  "total_chunks": 15,
  "char_count": 2040,
  "word_count": 288,
  "has_markdown_headers": true,
  "pathology": "osteoporosis",
  "keywords": ["fuerza", "equilibrio", "aeróbico", "seguridad"],
  "content": "## **Base de Rutinas... Tabla: Tipo de actividad, Frecuencia..."
}
```

**Observación:** la tabla Markdown fue convertida a texto estructurado antes de chunking, preservando filas y columnas.

## Ejemplo 2: Chunk semántico de texto plano

**Archivo:** `WEB-GUIA-MAYORES-version-publicacion.md`

```json
{
  "chunk_id": "...",
  "document_name": "WEB-GUIA-MAYORES-version-publicacion.md",
  "macrodomain": "F",
  "macrodomain_name": "Estimulación cognitiva y bienestar emocional",
  "section_path": "",
  "chunk_type": "semantic",
  "chunk_index": 0,
  "total_chunks": 131,
  "keywords": ["fuerza", "equilibrio", "aeróbico"],
  "content": "El ejercicio físico ayuda a mantenernos mejor..."
}
```

## Ejemplo 3: Chunk de fallback (documento corto)

**Archivo:** `Exercising Outdoors_ Safety Tips for Older Adults.md`

```json
{
  "chunk_id": "...",
  "document_name": "Exercising Outdoors_ Safety Tips for Older Adults.md",
  "macrodomain": "C",
  "macrodomain_name": "Contexto y entorno",
  "chunk_type": "fallback",
  "chunk_index": 0,
  "total_chunks": 2,
  "keywords": ["seguridad"],
  "content": "..."
}
```

## Distribución por macrodominio

| Macrodominio | Chunks |
|---|---|
| A (Fundamentos fisiológicos y patologías) | 44 |
| B (Taxonomía del ejercicio) | 200 |
| C (Contexto y entorno) | 24 |
| D (Comorbilidades y seguridad clínica) | 9 |
| E (Nutrición y metabolismo) | 16 |
| F (Estimulación cognitiva y bienestar emocional) | 131 |

## Preservación de contexto

- Las rutinas de ejercicio se mantienen dentro de un mismo chunk cuando la coherencia semántica lo permite.
- Las progresiones de ejercicios (básico → avanzado) no se cortan artificialmente por el solapamiento de 200 caracteres.
- Los metadatos de `section_path` permiten al retriever filtrar por sección cuando corresponde.

## Notas sobre calidad

- El chunking semántico genera chunks más pequeños (~84 palabras) de lo esperado inicialmente (~1500 caracteres).
- Esto es beneficioso para la recuperación: chunks pequeños y coherentes mejoran la precisión del retriever.
- Para generación de respuestas largas, se recomienda recuperar varios chunks top-k y concatenarlos en el contexto del LLM.

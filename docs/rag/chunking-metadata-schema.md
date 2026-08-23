# Esquema de Metadatos de Chunks — SeniorVital RAG

## Propósito

Cada chunk generado debe llevar metadatos enriquecidos que permitan al retriever filtrar, rankear y contextualizar la información recuperada según el agente, el macrodominio, el nivel funcional y la patología del usuario.

## Esquema de Metadatos

| Campo | Tipo | Obligatoriedad | Descripción |
|---|---|---|---|
| `chunk_id` | `string` | Sí | Identificador único del chunk (UUID o hash). |
| `document_name` | `string` | Sí | Nombre del archivo fuente. |
| `source_path` | `string` | Sí | Ruta relativa del documento dentro del repositorio. |
| `macrodomain` | `string` | Sí | Letra del macrodominio (`A`, `B`, `C`, `D`, `E`, `F`). |
| `macrodomain_name` | `string` | Sí | Nombre descriptivo del macrodominio. |
| `section_path` | `string` | Condicional | Jerarquía de encabezados cuando aplica (ej: `Base de Rutinas > Perfil 1`). |
| `chunk_type` | `string` | Sí | Tipo de chunk generado: `semantic`, `structural` o `fallback`. |
| `chunk_index` | `integer` | Sí | Índice secuencial del chunk dentro del documento. |
| `total_chunks` | `integer` | Sí | Total de chunks generados para el documento. |
| `char_count` | `integer` | Sí | Número de caracteres del contenido del chunk. |
| `word_count` | `integer` | Sí | Número aproximado de palabras del chunk. |
| `has_markdown_headers` | `boolean` | Sí | Indica si el documento fuente tenía encabezados Markdown. |
| `level` | `string` | Opcional | Nivel funcional del contenido: `Frágil`, `Activo`, `Muy Activo`. |
| `pathology` | `string` | Opcional | Patología asociada si se detecta en el texto (ej: `osteoporosis`, `diabetes`). |
| `keywords` | `list[string]` | Opcional | Palabras clave extraídas del chunk. |

## Ejemplo de Chunk con Metadatos

```json
{
  "chunk_id": "doc-001-semantic-0003",
  "document_name": "WEB-GUIA-MAYORES-version-publicacion.md",
  "source_path": "data/knowledge_base/WEB-GUIA-MAYORES-version-publicacion.md",
  "macrodomain": "F",
  "macrodomain_name": "Estimulación cognitiva y bienestar emocional",
  "section_path": "",
  "chunk_type": "semantic",
  "chunk_index": 3,
  "total_chunks": 12,
  "char_count": 1480,
  "word_count": 235,
  "has_markdown_headers": false,
  "level": null,
  "pathology": null,
  "keywords": ["equilibrio", "caídas", "fortalecimiento", "adultos mayores"]
}
```

## Reglas de Asignación

### `chunk_type`

- `semantic`: generado por `SemanticChunker`.
- `structural`: generado por `MarkdownHeaderTextSplitter`.
- `fallback`: generado por `RecursiveCharacterTextSplitter` como respaldo.

### `macrodomain`

Se asigna según el mapeo definido en `scripts/indexing/inventory_documents.py`:

- `A`: Fundamentos fisiológicos y patologías
- `B`: Taxonomía del ejercicio
- `C`: Contexto y entorno
- `D`: Comorbilidades y seguridad clínica
- `E`: Nutrición y metabolismo
- `F`: Estimulación cognitiva y bienestar emocional

### `section_path`

- Solo se incluye cuando el chunk proviene de `MarkdownHeaderTextSplitter`.
- Formato: `Header 1 > Header 2 > Header 3`.
- Para chunks semánticos o de fallback, se deja como cadena vacía.

### `level` y `pathology`

- Campos opcionales que se pueden completar en etapas posteriores mediante NLP o reglas simples.
- `level` se puede inferir del contenido si menciona perfiles funcionales.
- `pathology` se puede inferir si el texto menciona condiciones como osteoporosis, diabetes, artritis, etc.

## Almacenamiento

Los chunks se guardan en formato JSON en `data/processed/chunks/` con la siguiente estructura:

```
data/processed/chunks/
├── <document_name>.chunks.json
└── all_chunks.json
```

Cada archivo `.chunks.json` contiene una lista de objetos chunk con el esquema anterior.

## Integración con Pipeline RAG

En fases posteriores, estos metadatos se utilizarán para:

- Filtrar chunks por macrodominio antes de la generación de embeddings.
- Enriquecer el prompt del LLM con contexto sobre el origen del chunk.
- Mejorar la evaluación de recuperación segmentando métricas por dominio.

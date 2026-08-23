# Análisis de Estructura de Documentos — SeniorVital RAG

## Resumen Ejecutivo

Se analizaron **19 documentos** en `data/knowledge_base/` con un total de **36.005 palabras** y **236.989 caracteres**. El corpus está compuesto principalmente por texto plano y documentos envueltos en bloques de código Markdown, lo cual afecta directamente la estrategia de chunking seleccionada.

| Métrica | Valor |
|---|---|
| Documentos totales | 19 |
| Palabras totales | 36.005 |
| Caracteres totales | 236.989 |
| Documentos con encabezados Markdown | 1 |
| Documentos envueltos en bloques de código (```) | 13 |
| Documentos con tablas Markdown | 1 (aproximado) |

## Distribución por Macrodominio

| Macrodominio | Nombre | Documentos | Ejemplos representativos |
|---|---|---|---|
| A | Fundamentos fisiológicos y patologías | 4 | Sarcopenia y dinapenia, Movilidad articular, Osteoporosis, La diabetes |
| B | Taxonomía del ejercicio | 8 | Mejores ejercicios de fuerza, Los tres tipos de ejercicio, guia-ejercicio-mayores-segg |
| C | Contexto y entorno | 3 | Manual ejercicio persona mayor domicilio, Exercising Outdoors, Tips for Getting and Staying Active |
| D | Comorbilidades y seguridad clínica | 1 | Hacer ejercicio con enfermedades crónicas |
| E | Nutrición y metabolismo | 1 | Alimentación saludable para personas mayores |
| F | Estimulación cognitiva y bienestar emocional | 2 | WEB-GUIA-MAYORES, Gimnasia para mayores |

## Patrones Estructurales Detectados

### 1. Documentos con encabezados Markdown (1/19)

- `DOCUMENTO DE CONOCIMIENTO SENIORVITAL.md` es el único documento con estructura jerárquica clara usando `#`, `##`, `###`, `####`.
- Contiene 42 encabezados, incluyendo perfiles funcionales (`Frágil`, `Resiliente`), glosarios de ejercicios y rutinas por nivel.
- Incluye tablas Markdown (OMS, puntuaciones) y listas numeradas.
- **Estrategia recomendada:** `MarkdownHeaderTextSplitter` para preservar la jerarquía.

### 2. Documentos envueltos en bloques de código (13/19)

- El contenido está rodeado por fences ``` ```, lo que lo convierte en texto plano para los splitters Markdown.
- Ejemplos: `Alimentación saludable para personas mayores.md`, `La diabetes.md`, `Cómo frenar la osteoporosis...`.
- **Implicación:** Requiere preprocesamiento para eliminar fences antes de aplicar chunking semántico o recursivo.

### 3. Documentos de texto plano continuo (5/19)

- Texto sin encabezados ni fences, compuesto por párrafos extensos.
- Ejemplo: `WEB-GUIA-MAYORES-version-publicacion.md` (9.380 palabras, 873 líneas).
- **Implicación:** Requiere chunking semántico para agrupar párrafos temáticamente.

### 4. Documentos con tablas

- Solo `DOCUMENTO DE CONOCIMIENTO SENIORVITAL.md` presenta tablas Markdown detectables.
- Las tablas deben convertirse a texto estructurado antes de chunking para evitar pérdida de información.

### 5. Documentos con listas

- Las listas numeradas y con viñetas aparecen principalmente en `DOCUMENTO DE CONOCIMIENTO SENIORVITAL.md`.
- Documentos de texto plano contienen listas implícitas (párrafos que enumeran recomendaciones) pero no en sintaxis Markdown.

## Implicaciones para la Estrategia de Chunking

| Hallazgo | Decisión de Diseño |
|---|---|
| Solo 1 documento con encabezados Markdown | `SemanticChunker` como estrategia primaria. |
| 13 documentos en bloques de código | Preprocesamiento normalizador que elimina fences ```. |
| Texto plano extenso y continuo | `SemanticChunker` con `breakpoint_threshold_type=percentile` para agrupar párrafos. |
| Documento con encabezados jerárquicos | `MarkdownHeaderTextSplitter` como estrategia secundaria para ese documento específico. |
| Tablas y listas concentradas en un documento | Conversión a texto estructurado en el preprocesador. |
| Variabilidad de longitud (436 a 9.380 palabras) | Necesidad de fallback recursivo para documentos muy cortos o muy largos. |

## Recomendaciones

1. **Preprocesamiento obligatorio:** normalizar todos los documentos eliminando fences de código, tablas y espacios en blanco redundantes.
2. **Chunking semántico primario:** usar `SemanticChunker` de LangChain para la mayoría de los documentos.
3. **Chunking estructural condicional:** aplicar `MarkdownHeaderTextSplitter` solo cuando `has_markdown_headers` sea `true`.
4. **Fallback recursivo:** usar `RecursiveCharacterTextSplitter` cuando el chunking semántico genere chunks demasiado grandes o el documento sea muy corto.
5. **Metadatos enriquecidos:** cada chunk debe conservar `macrodomain`, `document_name`, `chunk_type`, `chunk_index` y `has_headers`.

## Archivo Fuente

- Inventario completo: `data/processed/document_inventory.json`
- Script generador: `scripts/indexing/inventory_documents.py`

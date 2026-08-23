# Curación de Documentos — Pipeline RAG

## Visión general

La curación de documentos es el proceso de preparar, limpiar y estructurar los documentos de conocimiento antes de indexarlos en el vector store. En SeniorVital, este proceso transforma 19 documentos Markdown en 363 chunks optimizados para recuperación semántica.

## Pipeline de curación

```
documentos fuente (data/knowledge_base/)
    │
    ▼
┌─────────────────────────────┐
│  1. Limpieza y validación   │ → Eliminar ruido, verificar formato
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│  2. Chunking                │ → Fragmentar en unidades semánticas
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│  3. Enriquecimiento         │ → Agregar metadatos (agente, dominio, keywords)
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│  4. Embedding generation    │ → Vectorizar cada chunk
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│  5. Indexación en ChromaDB  │ → Almacenar embeddings + metadatos
└─────────────────────────────┘
```

## Técnicas de preprocesamiento aplicadas

### Limpieza y normalización

| Técnica | Implementación | Justificación |
|---------|---------------|---------------|
| Eliminación de artefactos | `chunking/chunker.py` — limpieza de marcado HTML/Markdown | Los documentos tienen formato inconsistente |
| Normalización de texto | Lowercase, colapsar whitespace | Reducir variabilidad en embeddings |
| Detección de idioma | Español LATAM (mayoritariamente) | Mantener coherencia con el contexto de uso |

### Chunking semántico

El sistema usa un **chunking híbrido** que combina:

1. **Chunking semántico principal**: Fragmentación basada en similitud de embeddings entre oraciones consecutivas
2. **Chunking estructural**: Secciones con encabezados Markdown se procesan como unidades separadas
3. **Fallback recursivo**: Para documentos muy cortos, se usa chunking por tamaño fijo

**Configuración actual**:
- Tamaño mínimo chunk: ~50 caracteres
- Tamaño máximo chunk: ~2000 caracteres
- Promedio: ~101 palabras (~666 caracteres)

### Enriquecimiento de metadatos

Cada chunk recibe metadatos para facilitar el filtrado y routing:

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| `chunk_id` | Identificador único | `doc_001_chunk_005` |
| `document_name` | Nombre del documento fuente | `Sarcopenia y dinapenia` |
| `macrodomain` | Dominio funcional (A-F) | `A` |
| `agent` | Agente responsable | `Physio-Evaluator` |
| `keywords` | Palabras clave extraídas | `["sarcopenia", "fuerza"]` |
| `level` | Nivel funcional | `todos`, `activo`, `frágil` |
| `pathology` | Patología asociada | `Sarcopenia, Dinapenia` |
| `evidence_level` | Nivel de evidencia | `alta`, `media`, `baja` |

## Estrategias de compresión

Las siguientes técnicas están documentadas pero no todas se implementan actualmente:

| Técnica | Estado | Descripción |
|---------|--------|-------------|
| **Compresión extractiva** | Parcial | Selección de oraciones más relevantes por embeddings |
| **Compresión abstractiva** | No implementada | Resúmenes generados por LLM (futuro) |
| **Simplificación textual** | No implementada | Reducción de complejidad lingüística |
| **Eliminación de ruido** | Implementada | Limpieza de marcado HTML/Markdown |
| **Chunking semántico** | Implementada | Fragmentación por similitud de embeddings |
| **Estrategias híbridas** | Parcial | Combinación de semántico + estructural |

## Verificación de calidad

### Checks automáticos

```python
# Longitud de chunks
assert 50 <= len(chunk.content) <= 2000

# Presencia de metadatos
assert chunk.metadata.macrodomain in ["A", "B", "C", "D", "E", "F"]
assert chunk.metadata.agent in AGENT_TO_MACRODOMAIN

# Keywords no vacías
assert len(chunk.metadata.keywords) > 0
```

### Métricas de calidad

| Métrica | Valor actual | Objetivo |
|---------|-------------|----------|
| Promedio palabras/chunk | ~101 | 80-120 |
| Chunks sin keywords | ~5% | <2% |
| Distribución por dominio | 35-182 | Más equilibrado |
| Cobertura de documentos | 19/19 | 100% |

## Comandos de curación

```bash
# Ejecutar todo el pipeline de curación
python scripts/indexing/run_all.py

# Paso individual: chunking
python scripts/indexing/run_chunking.py

# Paso individual: embeddings
python scripts/ingestion/generate_embeddings.py

# Paso individual: indexación
python scripts/ingestion/index_knowledge_base.py

# Verificar resultados
python -c "import json; d=json.load(open('data/processed/chunks/all_chunks.json')); print(f'{len(d)} chunks')"
```

## Mejoras pendientes

1. **Re-balancear dominios D y E**: Agregar más documentos de nutrición y comorbilidades
2. **Reducir chunks vacíos de keywords**: Algunos chunks no tienen keywords extraídas
3. **Mejorar chunking semántico**: Ajustar umbrales para mejor coherencia
4. **Agregar validación post-chunking**: Verificar que cada chunk es autocontenida
5. **Implementar compresión abstractiva**: Resúmenes generados por LLM para dominios grandes

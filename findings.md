# Findings & Decisions — SeniorVital Chunking RAG

## Requirements

- Diseñar e implementar chunking híbrido (estructural + semántico) para la base de conocimiento de SeniorVital.
- Procesar los documentos de `data/knowledge_base/` y generar chunks en `data/processed/chunks/`.
- Preservar metadatos: documento, macrodominio, sección, nivel funcional, patología, tipo de chunk, índice.
- Incluir chunking de respaldo para documentos sin estructura clara.
- Documentar la estrategia, parámetros, ejemplos y guía de uso en `docs/rag/`.
- Escribir pruebas unitarias con cobertura > 80% en módulos de chunking.
- (Posterior) Integrar con embeddings, vector store, retriever híbrido, reranking y pipeline RAG.

## Research Findings

- El proyecto tiene 19 documentos Markdown en `data/knowledge_base/` organizados por macrodominios (A-F).
- La arquitectura define rutas: `src/knowledge/chunking/`, `scripts/indexing/`, `tests/rag/`, `docs/rag/`, `data/processed/`, `data/vector_store/`.
- No existen aún implementaciones de chunking; solo hay `.gitkeep` en `src/knowledge/chunking/`.
- La estrategia recomendada por el plan de trabajo es: `MarkdownHeaderTextSplitter` (estructural) + `SemanticChunker` (semántico) + `RecursiveCharacterTextSplitter` (fallback).
- **Hallazgo crítico:** Solo 1 de 19 documentos (`DOCUMENTO DE CONOCIMIENTO SENIORVITAL.md`) contiene encabezados Markdown. Los demás están en bloques de código (```) o como texto plano continuo, por lo que el chunking estructural no puede ser la estrategia primaria.
- Embeddings propuestos inicialmente: `text-embedding-3-small` (OpenAI). Decisión final: usar embeddings locales gratuitos `intfloat/multilingual-e5-small` vía HuggingFace para alinearse con filosofía local-first de SeniorVital.
- Vector store: ChromaDB (Fase 5). Reranker: `BAAI/bge-reranker-large` (Fase 5).

## Technical Decisions

| Decision | Rationale |
|----------|-----------|
| Usar LangChain como framework de chunking | `MarkdownHeaderTextSplitter` y `SemanticChunker` están disponibles en `langchain` y `langchain-experimental`. |
| Estrategia primaria: semántica | La mayoría de los documentos son texto plano o están envueltos en bloques de código; `SemanticChunker` agrupa párrafos por similitud semántica. |
| Estrategia secundaria: estructural | Solo `DOCUMENTO DE CONOCIMIENTO SENIORVITAL.md` tiene encabezados claros; se usa `MarkdownHeaderTextSplitter` para él. |
| Estrategia terciaria: recursiva con solapamiento | Fallback para documentos pequeños o sin estructura detectable, usando `RecursiveCharacterTextSplitter`. |
| Fallback: recursivo con solapamiento | Documentos con encabezados pobres o secciones gigantes se dividen por `RecursiveCharacterTextSplitter`. |
| Metadatos obligatorios por chunk | Necesarios para filtrado por agente y contexto clínico: `document_name`, `macrodomain`, `section_path`, `chunk_type`, `chunk_index`, `source_path`. |
| Conversión de tablas a texto | Las tablas Markdown se convierten a representación textual estructurada para evitar pérdida de información. |
| Preprocesamiento de bloques de código | Muchos documentos están envueltos en ``` ```; se normalizan eliminando fences y extrayendo el texto real. |
| Limitar chunk a ~1500-2000 tokens | Objetivo inicial; el chunking semántico generó chunks más pequeños (~84 palabras / ~556 caracteres), lo cual es adecuado para recuperación RAG. |
| Usar embeddings locales gratuitos (HuggingFace) | No requiere `OPENAI_API_KEY`; alineado con arquitectura local-first. Modelo elegido: `intfloat/multilingual-e5-small`. |

## Issues Encountered

| Issue | Resolution |
|-------|------------|
| Documentos sin encabezados Markdown | Adaptar estrategia: chunking semántico primario y estructural secundario. |
| Import de `HuggingFaceEmbeddings` en `langchain_community` está deprecated | Funciona correctamente; se puede migrar a `langchain-huggingface` en futuras iteraciones. |
| `MarkdownHeaderTextSplitter` devuelve headers con marcas HTML (`<mark>`) | Se conservan en `section_path`; no afectan la calidad del chunk. |

## Resources

- Archivo de arquitectura: `directorioSeniorVital.txt`
- Documentos fuente: `data/knowledge_base/*.md`
- Carpeta de implementación: `src/knowledge/chunking/`
- Carpeta de scripts: `scripts/indexing/`, `scripts/evaluation/`
- Carpeta de pruebas: `tests/rag/`
- Carpeta de documentación: `docs/rag/`, `docs/reports/`

## Visual/Browser Findings

- No aplica en esta tarea.

---

*Update this file after every 2 view/browser/search operations*

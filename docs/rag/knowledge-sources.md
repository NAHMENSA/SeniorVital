# Fuentes de Conocimiento — Base de Datos RAG

## Visión general

La base de conocimiento de SeniorVital alimenta el sistema RAG con información experta sobre bienestar para adultos mayores. Está compuesta por **19 documentos Markdown** organizados en **6 macrodominios funcionales** que mapean directamente con los agentes autónomos del sistema.

## Fuentes de los documentos

| Categoría | Fuentes | Cantidad |
|-----------|---------|----------|
| **Guías clínicas** | OMS, SEGG, ACSM | 4 documentos |
| **Manuales prácticos** | ESHI, manuales de ejercicio | 5 documentos |
| **Documentos técnicos** | Artículos científicos, guías de nutrición | 6 documentos |
| **Guias de adherencia** | Tips para actividad física, motivación | 4 documentos |

## Distribución por macrodominio

### Macrodominio A — Fundamentos Fisiológicos y Patologías

**Agente responsable**: Physio-Evaluator (Evaluación Física)
**Chunks**: 35 | **Documentos**: 4

| Documento | Descripción | Keywords |
|-----------|-------------|----------|
| Sarcopenia y dinapenia | Diferencia entre pérdida de masa y fuerza, criterios EWGSOP2, impacto funcional | sarcopenia, dinapenia, fuerza muscular, diagnóstico |
| Movilidad articular en adultos mayores | Pérdida de colágeno, rigidez fascial, ejercicios específicos | colágeno, fascia, rigidez, rango de movimiento |
| Cómo frenar la osteoporosis | Mecanotransducción, microimpactos, seguridad | osteoporosis, densidad ósea, mecanotransducción |
| La diabetes | Datos OMS, tipos, síntomas, prevención, ejercicio | diabetes tipo 2, hiperglucemia, insulina |

### Macrodominio B — Taxonomía del Ejercicio

**Agente responsable**: Exercise Architect (Prescripción de Ejercicio)
**Chunks**: 182 | **Documentos**: 8

| Documento | Descripción | Keywords |
|-----------|-------------|----------|
| Mejores ejercicios de fuerza para mayores de 60 | 9 ejercicios con progresiones y correcciones por patología | sentadilla, remo, banda elástica, zancada |
| Los tres tipos de ejercicio | Aeróbico (150 min), fortalecimiento, equilibrio | aeróbico, fortalecimiento, equilibrio |
| Guía de ejercicio para mayores SEGG | Ejercicios específicos de bíceps, tríceps, cadera, rodillas | bíceps, tríceps, flexión plantar, cadera |
| Entrenamiento en adultos mayores - guía completa | Recomendaciones OMS multicomponente, estructura de sesión | entrenamiento multicomponente, volumen, frecuencia |

### Macrodominio C — Contexto y Entorno

**Agente responsable**: Context-Adaptor (Entorno Latinoamericano)
**Chunks**: 23 | **Documentos**: 3

| Documento | Descripción | Keywords |
|-----------|-------------|----------|
| Manual de ejercicio persona mayor domicilio | Rutinas en casa con materiales caseros | ejercicios en casa, silla, botellas, espacio seguro |
| Exercising Outdoors - Safety Tips | Seguridad en exteriores, ropa, hidratación, clima | seguridad exterior, calor, frío, tránsito |
| Tips for Getting and Staying Active | Estrategias de adherencia, apoyo social | adherencia, motivación, grupo, barreras |

### Macrodominio D — Comorbilidades y Seguridad Clínica

**Agente responsable**: Safety Guardian (Seguridad y Salud)
**Chunks**: 9 | **Documentos**: 1

| Documento | Descripción | Keywords |
|-----------|-------------|----------|
| Hacer ejercicio con enfermedades crónicas | Recomendaciones para Alzheimer, Artritis, EPOC, Diabetes, Cardiopatías | Alzheimer, artritis, EPOC, diabetes, corazón |

### Macrodominio E — Nutrición y Metabolismo

**Agente responsable**: Nutri-Buddy (Nutrición)
**Chunks**: 13 | **Documentos**: 1

| Documento | Descripción | Keywords |
|-----------|-------------|----------|
| Alimentación saludable para personas mayores | Porciones, grupos alimenticios, adaptaciones LA | porciones, tazas, calorías, grupos alimenticios |

### Macrodominio F — Estimulación Cognitiva y Bienestar Emocional

**Agente responsable**: Mind & Soul (Cognitivo-Emocional)
**Chunks**: 101 | **Documentos**: 2

| Documento | Descripción | Keywords |
|-----------|-------------|----------|
| WEB-GUIA MAYORES - secciones finales | Ejercicios de memoria, gimnasia facial, relajación | memoria, estimulación cognitiva, relajación, Tai Chi |
| Gimnasia para mayores - guía oficial | Sesión completa con énfasis en coordinación | coordinación, ritmo, socialización, caídas |

## Mapeo agente → macrodominio

| Agente | Macrodominio | Chunks | Docs |
|--------|-------------|--------|------|
| Physio-Evaluator | A | 35 | 4 |
| Exercise Architect | B | 182 | 8 |
| Context-Adaptor | C | 23 | 3 |
| Safety Guardian | D | 9 | 1 |
| Nutri-Buddy | E | 13 | 1 |
| Mind & Soul | F | 101 | 2 |
| **Total** | **6** | **363** | **19** |

## Metadatos de chunks

Cada chunk indexado incluye los siguientes metadatos para filtrado y routing:

```json
{
  "chunk_id": "doc_001_chunk_005",
  "document_name": "Sarcopenia y dinapenia",
  "macrodomain": "A",
  "agent": "Physio-Evaluator",
  "keywords": ["sarcopenia", "dinapenia", "fuerza muscular"],
  "level": "todos",
  "pathology": "Sarcopenia, Dinapenia",
  "evidence_level": "alta"
}
```

## Adquisición de fuentes

Los documentos fueron compilados de:

1. **Organizaciones oficiales**: OMS, SEGG (Sociedad Española de Geriatría y Gerontología), ACSM (American College of Sports Medicine)
2. **Literatura científica**: Estudios sobre sarcopenia, osteoporosis, ejercicio en mayores
3. **Manuales prácticos**: Guías de ejercicio doméstico, nutrición, adherencia
4. **Adaptaciones regionales**: Contexto latinoamericano (vivienda, alimentación, familia)

## Mantenimiento

- **Agregar documentos**: Colocar en `data/knowledge_base/` con formato Markdown
- **Re-indexar**: Ejecutar `python scripts/indexing/run_all.py`
- **Verificar chunks**: Revisar `data/processed/chunks/all_chunks.json`

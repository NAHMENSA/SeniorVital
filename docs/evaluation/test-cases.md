# Conjunto de Consultas de Prueba

## Metodología

Se definieron 30 consultas representativas del dominio de bienestar para adultos mayores, cubriendo los 6 macrodominios del sistema RAG.

### Criterios de cobertura

- **5 consultas por macrodominio** (30 total)
- **3 categorías**: factual, procedural, comparative
- **3 niveles de dificultad**: fácil (40%), medio (40%), difícil (20%)
- **2 consultas multi-dominio**: "ejercicio con diabetes" (B+D), "nutrición para osteoporosis" (E+A)
- **2 consultas fuera de dominio**: para evaluar rechazo
- **2 consultas ambiguas**: para evaluar manejo de incertidumbre

### Distribución por dominio

| Dominio | Nombre | Consultas | Ejemplos |
|---------|--------|-----------|----------|
| A | Fundamentos fisiológicos | 5 | "¿Qué es la sarcopenia?", "¿Cómo se diagnostica?" |
| B | Taxonomía del ejercicio | 5 | "¿Cuánto ejercicio aeróbico?", "¿Ejercicios de equilibrio?" |
| C | Contexto y entorno | 5 | "¿Precauciones al aire libre?", "¿Ejercicio en casa?" |
| D | Seguridad clínica | 5 | "¿Diabetes y ejercicio?", "¿Contraindicaciones?" |
| E | Nutrición | 5 | "Alimentos recomendados", "¿Dieta para diabetes?" |
| F | Bienestar emocional | 5 | "Ejercicios de memoria", "Ejercicio y depresión" |

### Formato del query set

```json
{
  "id": "E01",
  "query": "¿Cuáles son los alimentos recomendados para personas mayores?",
  "expected_macrodomain": "E",
  "expected_agent": "Nutri-Buddy",
  "relevant_chunk_ids": ["54057e85-...", "5e81a0cc-...", "1a9c00c7-..."],
  "difficulty": "easy",
  "category": "factual",
  "expected_answer_keywords": ["verduras", "frutas", "cereales", "proteína", "lácteos"]
}
```

### Archivo

El query set completo se encuentra en: `data/evaluation/test_queries.json`

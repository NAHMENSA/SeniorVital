**Preparar los documentos para las siguientes etapas de procesamiento.**

**Técnicas de preprocesamiento y condensación de Documentos**

Para optimizar un documento antes de su fragmentación (_chunking_) en un sistema RAG, se pueden aplicar diversas técnicas de preprocesamiento y condensación. Estas se agrupan en seis categorías principales, cada una con un fundamento, pasos prácticos y un análisis de ventajas y limitaciones.

1.  **Compresión Extractiva (_Extractive Compression_)**

- **Fundamento teórico**: Esta técnica selecciona y extrae las oraciones o fragmentos más relevantes del documento original, preservando textualmente el contenido seleccionado. El objetivo es identificar las porciones con mayor densidad de información y descartar el resto. Modelos como **EXIT** (Context-Aware Extractive Compression) o **RECOMP** utilizan clasificadores para determinar la relevancia de cada oración en función de su contenido y contexto.
- **Pasos prácticos para aplicarla**:

1.  **Segmentación**: Dividir el documento en unidades atómicas (oraciones o párrafos cortos).
2.  **Vectorización**: Convertir cada unidad en una representación vectorial (embedding).
3.  **Puntuación de relevancia**: Aplicar un modelo de clasificación (entrenado o mediante _prompting_ a un LLM) para asignar una puntuación de relevancia a cada unidad.
4.  **Selección y filtrado**: Seleccionar las unidades con mayor puntuación, estableciendo un umbral (por ejemplo, mantener el top 30% de oraciones o un número fijo de tokens).
5.  **Reconstrucción**: Unir las unidades seleccionadas en el orden original para formar el documento condensado.

- **Ventajas**:
- **Alta fidelidad semántica**: Al no generar nuevo texto, se preserva exactamente el significado y la terminología original.
- **Control y predictibilidad**: El nivel de compresión es ajustable y el resultado es predecible.
- **Limitaciones**:
- **Ruptura de coherencia**: Al eliminar oraciones, se puede perder la fluidez y la conexión lógica entre ideas.
- **Dependencia del criterio de selección**: La calidad del resultado depende críticamente de la precisión del modelo que puntúa la relevancia.

1.  **Compresión Abstractiva (Abstractive Compression / Summarization)**

- **Fundamento teórico**: A diferencia de la extractiva, esta técnica **genera nuevo texto** que parafrasea y sintetiza la información de las fuentes. Utiliza modelos de lenguaje (LLMs) para comprender el contenido y producir un resumen coherente y condensado. Se puede considerar un proceso de _pre-recuperación_ que “reescribe” el contexto. Una estrategia avanzada es la **abstractiva extractiva previa** (_extractive-before-abstractive_), que primero extrae las partes más relevantes y luego las resume de forma abstractiva.
- **Pasos prácticos para aplicarla**:

1.  **Preparación**: Limpiar el texto y, opcionalmente, segmentarlo en secciones lógicas (capítulos, párrafos).
2.  **Diseño del _prompt_**: Crear una instrucción detallada para el LLM que especifique el objetivo (ej. “genera un resumen conciso de no más de 200 palabras, manteniendo los conceptos clave y la secuencia lógica”).
3.  **Generación**: Enviar el texto (o las secciones) al LLM junto con el _prompt_ para obtener el resumen.
4.  **Validación**: Revisar el resumen generado para asegurar que no contiene alucinaciones y que preserva el sentido original.

- **Ventajas**:
- **Alta densidad informativa**: Puede condensar información de manera muy eficiente, eliminando redundancias y reformulando ideas.
- **Mayor coherencia**: El texto resultante suele ser más fluido y legible que una simple extracción.
- **Limitaciones**:
- **Riesgo de alteración semántica**: Existe la posibilidad de que el modelo introduzca imprecisiones o “alucine” información no presente en el original.
- **Costo computacional**: Requiere el uso de LLMs, lo que implica un mayor costo y latencia.
- **Menor control**: Es más difícil controlar con precisión qué información se retiene y cuál se descarta.

1.  **Simplificación Textual (Text Simplification)**

- **Fundamento teórico**: Esta técnica busca reducir la complejidad lingüística del texto, haciéndolo más fácil de procesar, sin necesariamente acortarlo drásticamente. Esto incluye eliminar “ruido” gramatical (artículos, preposiciones, conjunciones, verbos auxiliares), normalizar palabras a su forma base (lematización) y reformular oraciones complejas en estructuras más simples.
- **Pasos prácticos para aplicarla**:

1.  **Análisis sintáctico**: Identificar y etiquetar los componentes gramaticales de las oraciones.
2.  **Eliminación de ruido**: Remover palabras y frases que no aportan significado sustancial (muletillas, redundancias).
3.  **Lematización/Stemming**: Reducir las palabras a su raíz o forma base.
4.  **Reformulación de oraciones**: Dividir oraciones complejas en otras más cortas y simples.
5.  **Reensamblaje**: Unir las oraciones simplificadas para formar el nuevo documento.

- **Ventajas**:
- **Reducción del vocabulario**: Disminuye la cantidad de tokens únicos, lo que puede mejorar la eficiencia de los embeddings.
- **Mayor claridad para el modelo**: El texto simplificado puede ser más fácil de procesar para los algoritmos de _chunking_ y recuperación.
- **Limitaciones**:
- **Pérdida de matices**: Al simplificar, se pueden perder sutilezas del lenguaje y el contexto.
- **Riesgo de ambigüedad**: La excesiva simplificación puede generar oraciones ambiguas o con significado alterado.

1.  **Eliminación de Ruido y Limpieza (Noise Reduction & Cleaning)**

- **Fundamento teórico**: Consiste en eliminar del documento todos los elementos que no aportan información relevante para el proceso de recuperación. Esto incluye, por ejemplo, metadatos irrelevantes, código de marcado (HTML, Markdown), elementos de navegación, pies de página, o texto repetitivo.
- **Pasos prácticos para aplicarla**:

1.  **Identificación**: Detectar y clasificar los diferentes tipos de “ruido” presentes en el documento (basado en reglas o mediante un modelo).
2.  **Extracción de contenido principal**: Aislar el cuerpo del texto, descartando elementos estructurales o de formato no esenciales.
3.  **Filtrado de duplicados**: Identificar y eliminar fragmentos de texto duplicados o casi duplicados dentro del documento.
4.  **Normalización**: Unificar formatos (fechas, unidades) y corregir errores tipográficos comunes.

- **Ventajas**:
- **Mejora de la calidad del embedding**: Al eliminar el ruido, los vectores resultantes representan mejor el contenido semántico relevante.
- **Reducción de tamaño**: Se reduce el número total de tokens a procesar.
- **Limitaciones**:
- **Riesgo de eliminar información útil**: Si las reglas de limpieza no son precisas, se podría descartar contenido valioso.
- **Dependencia del formato**: Las técnicas suelen ser específicas para cada tipo de documento (PDF, HTML, Word).

1.  **Fragmentación Semántica Inteligente (Semantic Chunking)**

- **Fundamento teórico**: Esta técnica no se centra en reducir el tamaño del documento completo, sino en optimizar cómo se divide en fragmentos para la recuperación. En lugar de usar reglas fijas (por ejemplo, 500 caracteres), el _chunking_ semántico analiza el significado del texto para determinar los límites de los fragmentos, agrupando oraciones o párrafos que tratan sobre un mismo tema. El objetivo es que cada fragmento sea una unidad de información coherente y autocontenida.
- **Pasos prácticos para aplicarla**:

1.  **Segmentación inicial**: Dividir el texto en oraciones.
2.  **Cálculo de embeddings**: Generar un vector para cada oración.
3.  **Cálculo de distancia semántica**: Medir la similitud (ej. distancia coseno) entre oraciones consecutivas.
4.  **Detección de quiebres**: Identificar puntos donde la similitud entre oraciones cae por debajo de un umbral, lo que indica un cambio de tema.
5.  **Formación de fragmentos**: Agrupar oraciones entre quiebres para formar los fragmentos finales.

- **Ventajas**:
- **Mayor precisión en la recuperación**: Al recuperar un fragmento, es más probable que todo su contenido sea relevante para la consulta.
- **Mejor comprensión por el LLM**: El modelo generador recibe contextos más coherentes y completos.
- **Limitaciones**:
- **Mayor costo computacional**: Calcular embeddings para cada oración y las distancias entre ellas es más costoso que un _chunking_ por tamaño fijo.
- **Complejidad de implementación**: Requiere un procesamiento más sofisticado y el ajuste de umbrales.

1.  **Estrategias Híbridas y de Optimización (Hybrid & Optimization Strategies)**

- **Fundamento teórico**: Combinan varias de las técnicas anteriores para obtener un mejor rendimiento. Un ejemplo común es la **compresión en tiempo de consulta** (_query-time compression_), donde se decide dinámicamente si se usa el fragmento original o una versión comprimida (extractiva o abstractiva) en función de la consulta. Otro enfoque es la **arquitectura de fragmentos padre-hijo** (_parent-child chunking_), donde se indexan fragmentos pequeños (hijos) para una recuperación precisa, pero se entregan al LLM fragmentos más grandes (padres) que contienen el contexto completo.
- **Pasos prácticos para aplicarla**:

1.  **Preprocesamiento**: Aplicar limpieza y, opcionalmente, simplificación al documento completo.
2.  **Fragmentación semántica**: Dividir el documento en fragmentos coherentes.
3.  **Generación de resúmenes (opcional)**: Para cada fragmento, generar un resumen breve (abstractivo o extractivo).
4.  **Indexación dual**: Indexar tanto los fragmentos originales como sus resúmenes (o fragmentos de diferente tamaño).
5.  **Enrutamiento dinámico**: Durante la recuperación, decidir qué versión del fragmento (original, resumida, padre, hijo) es más apropiada para la consulta.

- **Ventajas**:
- **Máxima flexibilidad y rendimiento**: Permite adaptar la estrategia a diferentes tipos de consultas y documentos.
- **Balance entre costo y precisión**: Se pueden usar representaciones más costosas (ej. fragmentos padres completos) solo cuando es necesario.
- **Limitaciones**:
- **Alta complejidad**: Requiere un diseño de sistema más sofisticado y un mantenimiento continuo.
- **Mayor latencia**: El proceso de decisión dinámica puede añadir latencia a la respuesta.

**Tabla Resumen de Técnicas**

| **Técnica** | **Objetivo Principal** | **Mecanismo** | **Mejor para** |
| --- | --- | --- | --- |
| **Compresión Extractiva** | Reducir tamaño seleccionando partes clave | Extrae y mantiene oraciones originales | Documentos donde la terminología exacta es crítica |
| **Compresión Abstractiva** | Reducir tamaño generando un resumen | Genera nuevo texto que sintetiza la información | Reducir drásticamente el tamaño manteniendo la coherencia |
| **Simplificación Textual** | Reducir complejidad lingüística | Simplifica gramática y vocabulario | Documentos con lenguaje complejo o técnico |
| **Eliminación de Ruido** | Mejorar calidad de la información | Filtra y elimina elementos no relevantes | Documentos con mucho formato o ruido (HTML, PDFs) |
| **Fragmentación Semántica** | Mejorar la coherencia de los fragmentos | Agrupa texto por similitud semántica | Cualquier documento donde la coherencia del fragmento sea clave |
| **Estrategias Híbridas** | Optimizar el balance entre costo, velocidad y precisión | Combina múltiples técnicas de forma dinámica | Sistemas RAG en producción con requisitos variables |
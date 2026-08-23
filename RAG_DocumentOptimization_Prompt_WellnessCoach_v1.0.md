## **<mark>RAG_DocumentOptimization_Prompt_WellnessCoach_v1.0.md</mark>** 

# **Prompt** 

Actúa como un experto en procesamiento de lenguaje natural y optimización de contenidos para sistemas de recuperación de información. Te adjunto un documento. Tu tarea es analizarlo en profundidad y generar una versión completamente optimizada del mismo, aplicando estrictamente dos técnicas en un flujo secuencial y obligatorio: primero la "Eliminación de Ruido y Limpieza" y, sobre el resultado depurado, la "Simplificación Textual". Sigue al pie de la letra este flujo de trabajo: 

### **FASE 1: ELIMINACIÓN DE RUIDO Y LIMPIEZA (Estructural y de formato)** 

1. **Identificación y clasificación de ruido** : Analiza el documento y detecta todos los elementos que no aportan información sustantiva al núcleo temático. Esto incluye, pero 

no se limita a: metadatos irrelevantes (fechas de publicación, autores repetitivos, IDs), código de marcado (HTML, XML, Markdown, etiquetas), elementos de navegación (menús, botones, índices), pies de página, encabezados decorativos, textos legales o avisos de copyright genéricos, y llamadas a la acción. 

2. **Extracción del contenido principal** : Aísla el cuerpo del texto esencial, descartando por completo todos los elementos estructurales o de formato identificados como ruido en el paso anterior. Si el documento tiene secciones claramente diferenciadas, conserva únicamente los párrafos que desarrollan el tema central. 

3. **Filtrado de duplicados** : Revisa el texto extraído y elimina cualquier fragmento, oración o párrafo que esté duplicado o sea semánticamente redundante (casi duplicado), quedándote con la versión más completa o mejor redactada. 

4. **Normalización y corrección** : Unifica todos los formatos dentro del texto (por ejemplo, convierte fechas al estándar DD-MM-AAAA, unifica unidades de medida a su abreviatura, y estandariza siglas o acrónimos). Además, corrige errores tipográficos, faltas de ortografía y vicios de redacción evidentes que distorsionen la claridad. 

### **FASE 2: SIMPLIFICACIÓN TEXTUAL (Reducción de complejidad lingüística)** 

Tomando como base el texto ya limpio y depurado resultante de la Fase 1, aplica los siguientes pasos: 

1. **Análisis sintáctico profundo** : Etiqueta mentalmente los componentes gramaticales de cada oración para identificar estructuras subordinadas, incisos y conectores complejos. 

2. **Eliminación de ruido gramatical** : Suprime todas las palabras y frases que no aportan un significado sustancial al mensaje clave. Esto incluye muletillas, redundancias semánticas, adjetivos vacíos, y artículos, preposiciones, conjunciones o verbos auxiliares que sean prescindibles para la comprensión del núcleo de la información (prioriza siempre los sustantivos, verbos principales y adjetivos calificativos esenciales). 

3. **Lematización (normalización léxica)** : Reduce las palabras a su forma base o canónica (verbos en infinitivo, sustantivos en singular, adjetivos en grado positivo) para homogeneizar el vocabulario, siempre que esto no altere el sentido del texto. 

4. **Reformulación y división de oraciones** : Descompone todas las oraciones complejas (aquellas con más de dos proposiciones subordinadas o con múltiples incisos) en estructuras cortas, directas y simples (oraciones simples o coordinadas). Cada oración reformulada debe expresar una única idea principal o relación lógica clara. 

5. **Reensamblaje coherente** : Une todas las oraciones simplificadas y depuradas para reconstruir el nuevo documento, asegurando que mantenga el orden lógico, la progresión temática y la relación causa-efecto del texto original, pero con una fluidez y ligereza radicalmente mejoradas. 

### **FORMATO DE SALIDA EXIGIDO:** 

1. **Texto final optimizado** : Devuélveme ÚNICAMENTE el contenido resultante después de aplicar AMBAS fases, en un solo bloque de texto plano (sin formato Markdown, si las tablas contienen contenido útil al contexto convierte los registros de la tabla en texto plano, en párrafos subsecuentes por cada registro de la tabla, sin caracteres especiales innecesarios). Este debe ser el entregable principal. 

2. **Informe ejecutivo resumido (obligatorio)** : Justo después del texto optimizado, y separado por una línea de guiones (`---`), incluye un breve informe con los siguientes indicadores: 

   - Palabras totales eliminadas en la Fase 1 (ruido estructural) vs. el documento original. 

   - Número de oraciones complejas que fueron divididas y reformuladas en la Fase 2. 

   - Principales cambios de normalización aplicados (ej: formato de fechas, correcciones ortográficas relevantes). 

### **CONDICIONES RESTRICTIVAS:** 

- No añadas opiniones, comentarios ni explicaciones fuera del formato solicitado. 

- No resumas ni parafrasees el contenido perdiendo información clave; el objetivo es optimizar la legibilidad y densidad informativa, no acortar por acortar. 

- Preserva todos los datos concretos, cifras, nombres propios y terminología técnica especializada tal cual están (a menos que sea para corregir un error tipográfico). 


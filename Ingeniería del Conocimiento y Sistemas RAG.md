# **<mark>Ingeniería del Conocimiento y Sistemas RAG</mark>** 

## **Índice** 

1. Introducción a la Ingeniería del Conocimiento 

<mark>2. Representación del Conocimiento</mark> 

<mark>3. Ontologías ligeras y taxonomías</mark> 

<mark>4. Introducción a los embeddings</mark> 

<mark>5. Estrategias de segmentación (chunking)</mark> 

<mark>6. Bases de datos vectoriales</mark> 

<mark>7. Arquitectura de sistemas RAG</mark> 

<mark>8. Recuperación de información y generación aumentada</mark> 

<mark>9. Evaluación de recuperación y calidad de respuestas</mark> 

- <mark>10.Diseño de conocimiento especializado para dominios específcos</mark> 

## **1. Introducción a la Ingeniería del Conocimiento** 

La **Ingeniería del Conocimiento** (Knowledge Engineering) es una disciplina dentro de la inteligencia artificial que se enfoca en la creación de sistemas capaces de adquirir, representar, manipular y utilizar conocimiento para resolver problemas complejos. 

Su objetivo fundamental es transformar conocimiento humano —frecuentemente tácito, disperso y no estructurado— en representaciones formales que puedan ser procesadas por sistemas computacionales. Este proceso involucra: 

- **Adquisición del conocimiento** : Extracción de expertise de expertos humanos, documentos y fuentes de datos. 

- **Representación** : Codificación del conocimiento en formatos estructurados (ontologías, reglas, redes semánticas). 

- **Razonamiento** : Aplicación de mecanismos lógicos o heurísticos para derivar nueva información. 

- **Validación** : Verificación de la corrección y consistencia del conocimiento 

- representado. 

Los ingenieros del conocimiento construyen ontologías basadas en conocimiento consensual sobre un dominio, permitiendo a un grupo de agentes (humanos o máquinas) compartir y utilizar ese conocimiento de manera consistente. 

### **<mark>Caso de uso: Sistema experto para diagnóstico médico</mark>** 

Un hospital implementa un sistema experto que asiste a médicos en el diagnóstico de enfermedades raras. El ingeniero del conocimiento trabaja con especialistas para documentar síntomas, factores de riesgo, pruebas diagnósticas y relaciones entre enfermedades, creando una base de conocimiento que el sistema utiliza para sugerir diagnósticos diferenciales. 

#### **Herramientas open-source recomendadas:** 

- **Protege** : Editor de ontologías y bases de conocimiento desarrollado por Stanford. Permite crear, visualizar y manipular ontologías en diversos formatos. 

- **Jena (Apache)** : Framework Java para construir aplicaciones semánticas, con soporte para RDF, OWL y SPARQL. 

- **KNIME** : Plataforma de análisis de datos que incluye nodos para minería de textos y extracción de conocimiento. 

## **2. Representación del Conocimiento** 

La **Representación del Conocimiento** es el subcampo de la IA que estudia cómo codificar conocimiento de manera que los sistemas computacionales puedan almacenarlo, razonar sobre él y utilizarlo para tomar decisiones. 

Los principales esquemas de representación incluyen: 



|**Esquema**|**Descripción**|**Ejemplo**|
|---|---|---|
|**Lógica proposicional**|Afrmaciones verdaderas/falsas|Llueve<br>Calle_mojada<br>→|
|**Lógica de primer**<br>**orden**|Cuantifcadores y predicados|∀<br>x (Humano(x)<br>→<br>Mortal(x))|
|**Redes semánticas**|Grafos con nodos (conceptos) y<br>aristas (relaciones)|"Is-a" (Perro<br>Mamífero)<br>→|
|**Marcos (Frames)**|Estructuras con slots y valores|Objeto: Auto, Slots: color, marca,<br>año|



|**Esquema**|**Descripción**|**Ejemplo**|
|---|---|---|
|**Reglas de producción**|Reglas IF-THEN|IF febre AND tos THEN<br>posible_gripe|
|**Ontologías**|Representación formal de un<br>dominio|Ver sección 3|



La representación del conocimiento debe equilibrar varios atributos: **expresividad** (capacidad de capturar matices), **eficiencia computacional** , **claridad** para humanos y **facilidad de mantenimiento** . 

### **Caso de uso: Sistema de recomendación de productos** 

Una plataforma de e-commerce representa el conocimiento sobre productos y preferencias de usuarios mediante una red semántica. Los nodos representan productos, categorías, atributos y usuarios; las aristas codifican relaciones como "comprado_con", "similar_a", "prefiere_categoría". Este grafo permite recomendar productos basados en similitud semántica y comportamiento de usuarios similares. 

#### **Herramientas open-source recomendadas:** 

- **Neo4j** : Base de datos de grafos nativa, ideal para redes semánticas y sistemas de recomendación. 

- **<mark>RDFlib</mark>** <mark>: Biblioteca Python para trabajar con RDF (Resource Description Framework).</mark> 

- **<mark>OWL API</mark>** <mark>: API Java para manipular ontologías en OWL (Web Ontology Language).</mark> 

## **3. Ontologías ligeras y taxonomías** 

### **Ontologías** 

Una **ontología** es una representación formal y explícita de un dominio de conocimiento, que describe conceptos relevantes, define sus propiedades y especifica las relaciones existentes entre ellos. Funciona como un "mapa conceptual" altamente estructurado que permite a los sistemas computacionales interpretar información de forma consistente. 

Por ejemplo, en una ontología médica: "un paciente es una persona", "una enfermedad puede afectar a un paciente", "un medicamento puede tratar una enfermedad". 

### **<mark>Ontologías ligeras</mark>** 

Las **ontologías ligeras** son versiones simplificadas que incluyen: 

- Un vocabulario controlado de términos del dominio. 

- <mark>Jerarquías de clases (taxonomías).</mark> 

- <mark>Relaciones básicas entre conceptos.</mark> 

- <mark>Menos axiomas y restricciones formales que las ontologías pesadas.</mark> 

Son más fáciles de construir, mantener y escalar, ideales para aplicaciones prácticas donde no se requiere razonamiento lógico complejo. 

### **Taxonomías** 

Una **taxonomía** es una clasificación jerárquica de conceptos donde cada nivel representa una generalización del nivel inferior (relación "es-un" o "tipo-de"). Por ejemplo: <mark>Animal → Vertebrado → Mamífero → Canino → Perro</mark> . 

Tanto las taxonomías como las ontologías describen un dominio de conocimiento con colecciones de entidades estructuradas en grupos o tipos. La diferencia clave es que las ontologías incluyen relaciones más ricas (no solo jerárquicas) y pueden incorporar reglas y restricciones. 

### **Caso de uso: Clasificación de productos en comercio electrónico** 

Una tienda online utiliza una taxonomía para categorizar productos: <mark>Electrónica → Computadoras → Laptops → Gaming Laptops</mark> . Además, una ontología ligera añade relaciones como "Laptop tiene componente Procesador", "Procesador fabricado_por Intel/AMD", permitiendo búsquedas semánticas como "laptops con procesador Intel de última generación". 

#### **Herramientas open-source recomendadas:** 

- **Protege** : El estándar de facto para crear y editar ontologías. 

- **TopBraid Composer Free Edition** : Entorno visual para desarrollo de ontologías RDF/OWL. 

- **<mark>VocBench</mark>** <mark>: Plataforma web para gestión colaborativa de tesauros y ontologías.</mark> 

- **SKOS (Simple Knowledge Organization System)** : Estándar W3C para representar taxonomías y tesauros en RDF. 

## **<mark>4. Introducción a los embeddings</mark>** 

Un **embedding** es una representación numérica de un objeto (texto, imagen, audio, etc.) como un vector de números en un espacio continuo de baja dimensión. Los embeddings transforman datos complejos y de alta dimensionalidad en vectores donde la **distancia entre vectores mide su relación semántica** : vectores cercanos indican alta similitud conceptual. 

### **Propiedades fundamentales** 

- **Dimensionalidad reducida** : Comprimen información en vectores de dimensión fija 

- (p.ej., 384, 768, 1536 dimensiones). 

- **Preservación semántica** : Palabras/conceptos similares ocupan regiones cercanas en el espacio vectorial. 

- **Relaciones composicionales** : Permiten operaciones algebraicas (p.ej., <mark>vector("Rey") - vector("Hombre") + vector("Mujer") ≈ vector("Reina")</mark> ). 

- **Transferencia** : Modelos pre-entrenados pueden adaptarse a nuevos dominios con poco ajuste. 

### **Tipos de embeddings** 

|**Tipo**|**Descripción**|**Ejemplos**|
|---|---|---|
|**Word embeddings**|Representan palabras individuales|Word2Vec, GloVe, FastText|
|**Sentence/Text**<br>**embeddings**|Representan frases o documentos<br>completos|SBERT, OpenAI embeddings,<br>Instructor|
|**Multimodal**|Representan imágenes, audio, etc.|CLIP (texto-imagen), ImageBind|



### **<mark>Caso de uso: Búsqueda semántica en documentos legales</mark>** 

Un bufete de abogados utiliza embeddings para buscar jurisprudencia relevante. En lugar de buscar por palabras clave exactas, el sistema convierte consultas y documentos a vectores; la búsqueda encuentra documentos semánticamente similares aunque usen terminología diferente (p.ej., "rescisión contractual" encuentra documentos sobre "terminación de contrato"). 

#### **<mark>Herramientas open-source recomendadas:</mark>** 

- **Sentence-Transformers** : Librería Python con modelos pre-entrenados para embeddings de oraciones (all-MiniLM-L6-v2, multi-qa-mpnet-base). 

- **<mark>FastText</mark>** <mark>: Embeddings de palabras de Facebook con soporte para subpalabras.</mark> 

- **<mark>Gensim</mark>** <mark>: Implementaciones de Word2Vec y Doc2Vec.</mark> 

- **Hugging Face Transformers** : Acceso a cientos de modelos de embeddings (BERT, RoBERTa, etc.). 

- **Instructor** : Modelo que permite instrucciones para adaptar embeddings al contexto. 

## **5. Estrategias de segmentación (chunking)** 

El **chunking** (fragmentación) es el proceso de dividir documentos extensos en segmentos más pequeños y manejables para su procesamiento. Es una etapa crítica en sistemas RAG porque determina qué información se recuperará y cómo se contextualizará. 

### **Estrategias principales** 

#### **1. Segmentación por tamaño fijo (Fixed-size chunking)** 

Divide el texto en fragmentos de un número fijo de caracteres o tokens. 

- **Ventajas** : Simple, predecible. 

- **Desventajas** : Puede cortar oraciones o conceptos por la mitad, perdiendo coherencia semántica. 

- **<mark>Mejora</mark>** <mark>: Usar</mark> **<mark>solapamiento (overlap)</mark>** <mark>entre fragmentos para preservar contexto.</mark> 

#### **2. Segmentación basada en estructura (Structural chunking)** 

Utiliza la estructura del documento: párrafos, oraciones, secciones, encabezados. 

- **Ventajas** : Respeta la organización natural del documento. 

- **<mark>Desventajas</mark>** <mark>: Tamaños muy variables.</mark> 

#### **3. Segmentación semántica (Semantic chunking)** 

Divide el texto en unidades de significado completo, identificando cambios de tema. 

- **<mark>Ventajas</mark>** <mark>: Fragmentos semánticamente coherentes.</mark> 

- **<mark>Desventajas</mark>** <mark>: Más compleja de implementar; puede requerir modelos de NLP.</mark> 

#### **4. Segmentación recursiva (Recursive chunking)** 

Aplica múltiples niveles de segmentación: primero por estructura, luego ajusta tamaños. 

- **Ventajas** : Flexible, combina lo mejor de otras estrategias. 

#### **5. Segmentación agéntica (Agentic chunking)** 

Utiliza agentes de IA que deciden dinámicamente cómo segmentar según el contenido y el contexto. 

Una buena estrategia de chunking busca un equilibrio entre **calidad de recuperación** (recordatorio/precisión) y **coherencia semántica** . 

### **Caso de uso: Chatbot de atención al cliente con manuales técnicos** 

Una empresa de telecomunicaciones tiene manuales de productos de cientos de páginas. Aplican segmentación: 

1. **Estructura** : Dividen por capítulos y secciones. 

<mark>2.</mark> **<mark>Tamaño</mark>** <mark>: Fragmentos de ~500 tokens con overlap de 100 tokens.</mark> 

3. **Semántica** : Aseguran que cada fragmento contenga información completa sobre un tema específico (ej., "configuración de router", "solución de problemas de conectividad"). 

#### **Herramientas open-source recomendadas:** 

- **LangChain** : Ofrece múltiples <mark>TextSplitters</mark> (RecursiveCharacterTextSplitter, SemanticChunker, etc.). 

- **<mark>LlamaIndex</mark>** <mark>: SentenceSplitter, SemanticSplitterNodeParser.</mark> 

- **<mark>Chonkie</mark>** <mark>: Librería Python especializada en chunking rápido y fexible.</mark> 

- **Unstructured** : Biblioteca para extraer y segmentar contenido de documentos PDF, HTML, etc. 

## **6. Bases de datos vectoriales** 

Una **base de datos vectorial** almacena y compara información como representaciones numéricas de alta dimensión (vectores), permitiendo a los sistemas de IA encontrar conceptos basados en **significado** , no solo en palabras clave. 

### **Características clave** 

- **Indexación eficiente** : Utilizan algoritmos ANN (Approximate Nearest Neighbor) como HNSW, IVF, o PQ para búsquedas rápidas a gran escala. 

- **Búsqueda por similitud** : Encuentran los vectores más cercanos a una consulta usando distancia coseno, Euclidiana o producto punto. 

- **Filtrado por metadatos** : Combinan búsqueda vectorial con filtros estructurados (ej., "documentos de 2024 con similitud > 0.8"). 

- **<mark>Escalabilidad</mark>** <mark>: Manejan miles de millones de vectores.</mark> 

### **Comparativa de bases de datos vectoriales open-source** 

|**Base de**<br>**datos**|**Características**|**Mejor para**|
|---|---|---|
|**Qdrant**|Escrita en Rust, alto rendimiento, soporte para fltros,<br>APIs REST/gRPC|Aplicaciones de baja latencia,<br>búsqueda fltrada|
|**Weaviate**|Escrita en Go, soporte para esquemas, integración<br>nativa con OpenAI/Cohere/HuggingFace|Sistemas con datos<br>estructurados y no<br>estructurados|
|**Milvus**|Diseñada para cargas de trabajo a escala de billones,<br>soporte GPU|Aplicaciones a gran escala,<br>investigación|
|**Chroma**|Ligera, local-frst, ideal para prototipos|Desarrollo rápido, notebooks,<br>LangChain|
|**pgvector**|Extensión de PostgreSQL para vectores|Equipos que ya usan<br>PostgreSQL|
|**OpenSearc**<br>**h**|Fork de Elasticsearch, combina BM25 y búsqueda<br>vectorial|Búsqueda híbrida, empresas<br>con ELK stack|



### **<mark>Caso de uso: Motor de recomendación de contenido</mark>** 

Una plataforma de streaming musical usa Qdrant para almacenar embeddings de canciones (generados a partir de letras, metadatos y características de audio). Cuando un usuario escucha una canción, el sistema busca canciones con vectores similares, ofreciendo recomendaciones personalizadas en tiempo real. 

#### **Herramientas open-source recomendadas:** 

- **Qdrant** : Alto rendimiento, soporte para filtrado y búsqueda híbrida. 

- **<mark>Weaviate</mark>** <mark>: Modular, fuerte comunidad.</mark> 

- **<mark>Milvus</mark>** <mark>: Ideal para datasets masivos.</mark> 

- **<mark>Chroma</mark>** <mark>: Para prototipado rápido y aplicaciones locales.</mark> 

- **<mark>pgvector</mark>** <mark>: Para quienes preferen PostgreSQL como base de datos principal.</mark> 

## **7. Arquitectura de sistemas Retrieval-Augmented Generation (RAG)** 

**Retrieval-Augmented Generation (RAG)** es un marco de trabajo híbrido que refuerza los modelos de lenguaje grande (LLMs) combinándolos con información recuperada de fuentes externas de conocimiento. Su objetivo es **mejorar la precisión, reducir alucinaciones y proporcionar respuestas basadas en hechos** . 

### **Arquitectura típica de un sistema RAG** 



<!-- Start of picture text -->
┌───────────────────────────────────────────────────────────┐<br>│                      FASE DE INDEXACIÓN                   │<br>├───────────────────────────────────────────────────────────┤<br>│ │<br>│   Documentos → [Chunking] → [Embedding] → [Vector DB]     │<br>│ │<br>└───────────────────────────────────────────────────────────┘<br>│<br>▼<br>┌───────────────────────────────────────────────────────────┐<br>│                      FASE DE CONSULTA                     │<br>├───────────────────────────────────────────────────────────┤<br>│ │<br>│      Consulta → [Embedding] → [Búsqueda vectorial]        │<br>│ │ │<br>│ ▼ │<br>│                  [Recuperación de chunks]                 │<br>│ │ │<br><!-- End of picture text -->



<!-- Start of picture text -->
│ ▼ │<br>│         [Prompt: Contexto + Consulta] → [LLM]             │<br>│ │ │<br>│ ▼ │<br>│                      [Respuesta fnal]                    │<br>│ │<br>└───────────────────────────────────────────────────────────┘<br><!-- End of picture text -->

### **Componentes principales** 

1. **Capa de ingestión** : Procesa documentos (extracción, limpieza, chunking, embedding, almacenamiento vectorial). 

2. **Capa de recuperación** : Convierte consultas a embeddings, busca chunks relevantes en la base vectorial. 

3. **Capa de reordenamiento (opcional)** : Re-ranking de resultados recuperados para mejorar relevancia. 

4. **Capa de generación** : Construye un prompt con el contexto recuperado y la consulta, lo envía al LLM. 

5. **Capa de respuesta** : Post-procesa y entrega la respuesta final, opcionalmente con citas. 

### **Variantes arquitectónicas** 

- **RAG básico** : Recuperación única + generación. 

- **<mark>RAG multiconsulta</mark>** <mark>: Genera múltiples consultas para cubrir diferentes aspectos.</mark> 

- **<mark>RAG híbrido</mark>** <mark>: Combina búsqueda vectorial y búsqueda por palabras clave (BM25).</mark> 

- **<mark>RAG multimodal</mark>** <mark>: Procesa y recupera texto, imágenes, audio.</mark> 

- **<mark>RAG agéntico</mark>** <mark>: Utiliza agentes especializados para diferentes tareas.</mark> 

### **Caso de uso: Asistente virtual para soporte técnico** 

Una empresa de software implementa un sistema RAG que: 

1. **Indexa** toda su documentación técnica, FAQs y tickets de soporte resueltos. 

<mark>2. Cuando un usuario hace una pregunta,</mark> **<mark>recupera</mark>** <mark>los fragmentos más relevantes.</mark> 

<mark>3. El LLM</mark> **<mark>genera</mark>** <mark>una respuesta personalizada citando las fuentes.</mark> 

4. El sistema incluye un **re-ranker** que prioriza documentos oficiales sobre foros comunitarios. 

#### **<mark>Herramientas open-source recomendadas:</mark>** 

- **LangChain** : Framework completo para construir pipelines RAG. 

- **<mark>LlamaIndex</mark>** <mark>: Especializado en indexación y recuperación de datos para LLMs.</mark> 

- **FlexRAG** : Framework open-source para investigación y prototipado, soporta RAG multimodal y basado en redes. 

- **<mark>FlashRAG</mark>** <mark>: Toolkit Python con 36 datasets y 23 algoritmos RAG pre-procesados.</mark> 

- **<mark>RAGnar</mark>** <mark>: Herramientas para fujos de trabajo RAG en R.</mark> 

## **8. Recuperación de información y generación aumentada** 

### **Recuperación de información** 

La recuperación en RAG va más allá de la búsqueda tradicional: 

- **Búsqueda vectorial** : Encuentra documentos por similitud semántica usando embeddings. 

- **<mark>Búsqueda por keywords</mark>** <mark>: BM25, TF-IDF para coincidencia exacta de términos.</mark> 

- **Búsqueda híbrida** : Combina ambos enfoques (p.ej., fusión recíproca de resultados). 

- **<mark>Recuperación por metadatos</mark>** <mark>: Filtra por fecha, autor, categoría, etc.</mark> 

### **Generación aumentada** 

La generación aumentada consiste en **enriquecer el prompt del LLM con el contexto recuperado** : 

Prompt = f""" <mark>Contexto: {chunks_recuperados}</mark> 

<mark>Pregunta: {consulta}</mark> 

<mark>Instrucción: Responde basándote EXCLUSIVAMENTE en el contexto proporcionado. Si la respuesta no está en el contexto, indica que no tienes información sufciente. """</mark> 

<mark>respuesta = LLM.generate(prompt)</mark> 

### **<mark>Técnicas avanzadas</mark>** 

|**Técnica**|**Descripción**|
|---|---|
|**Query transformation**|Reformular la consulta para mejorar recuperación|
|**HyDE (Hypothetical**<br>**Document Embeddings)**|Generar un documento hipotético y usar su embedding para<br>buscar|
|**Self-RAG**|El modelo refexiona sobre si necesita recuperar y si la<br>respuesta es adecuada|
|**Corrective RAG**|Valida y corrige la recuperación antes de generar|
|**Multi-hop RAG**|Realiza múltiples pasos de recuperación para preguntas<br>complejas|



### **<mark>Caso de uso: Investigación académica</mark>** 

Un investigador utiliza un sistema RAG para explorar la literatura científica: 

1. Formula una pregunta compleja sobre un tema interdisciplinario. 

<mark>2. El sistema transforma la pregunta en múltiples subconsultas.</mark> 

3. Recupera artículos de diferentes fuentes (arXiv, PubMed, repositorios institucionales). 

4. Genera un resumen sintetizado que integra información de múltiples fuentes con citas. 

#### **Herramientas open-source recomendadas:** 

- **Haystack** : Framework de deepset para pipelines de búsqueda y RAG. 

- **<mark>RAGatouille</mark>** <mark>: Implementación de técnicas avanzadas como ColBERT.</mark> 

- **BM25 (rank_bm25)** : Implementación Python de BM25 para búsqueda por keywords. 

- **<mark>Whoosh</mark>** <mark>: Motor de búsqueda de texto completo en Python.</mark> 

## **9. Evaluación de recuperación y calidad de respuestas** 

La evaluación es crítica para garantizar que un sistema RAG cumpla con los requisitos de calidad y precisión. 

### **Evaluación de la recuperación** 

Métricas para medir la calidad de los documentos recuperados: 

|**Métrica**|**Descripción**|
|---|---|
|**Precisión@k**|Proporción de documentos relevantes entre los k primeros<br>recuperados|
|**Recall@k**|Proporción de documentos relevantes totales que aparecen en<br>los k primeros|
|**MRR (Mean Reciprocal**<br>**Rank)**|Inverso del rango del primer documento relevante|
|**NDCG (Normalized**<br>**Discounted Cumulative**<br>**Gain)**|Considera la posición y relevancia graduada|
|**Hit Rate**|Porcentaje de consultas donde al menos un documento<br>relevante está en los k primeros|



### **<mark>Evaluación de la generación (calidad de respuestas)</mark>** 

|**Métrica**|**Descripción**|
|---|---|
|**Faithfulness / Fundamentación**|¿La respuesta está basada en hechos del contexto?|
|**Answer Relevance**|¿La respuesta responde directamente a la pregunta?|
|**Context Relevance**|¿El contexto recuperado es relevante para la pregunta?|
|**Coherencia**|¿La respuesta es lógica y bien estructurada?|
|**Utilidad**|¿La respuesta es práctica y accionable?|



### **<mark>Enfoques de evaluación</mark>** 

1. **Evaluación con ground truth** : Comparar respuestas con respuestas de referencia (costoso de crear). 

2. **LLM-as-a-Judge** : Usar un LLM para evaluar las respuestas. La "tríada RAG" de Microsoft evalúa recuperación, fundamentación y calidad. 

3. **Métricas automáticas** : BLEU, ROUGE, METEOR para similitud textual (limitadas para RAG). 

<mark>4.</mark> **<mark>Evaluación humana</mark>** <mark>: Gold standard, pero costosa y lenta.</mark> 

### **Caso de uso: Evaluación de un chatbot médico** 

Un sistema RAG para preguntas médicas se evalúa con: 

1. **Ground truth** : Un panel de médicos crea 500 preguntas con respuestas de referencia. 

<mark>2.</mark> **<mark>Métricas de recuperación</mark>** <mark>: Precisión@5 y Recall@10.</mark> 

<mark>3.</mark> **<mark>LLM-as-Judge</mark>** <mark>: Un modelo como GPT-4 evalúa fundamentación (0-10) y seguridad.</mark> 

4. **Evaluación humana** : Muestreo mensual con especialistas para validación continua. 

#### **Herramientas open-source recomendadas:** 

- **RAGAS** : Framework específico para evaluar pipelines RAG (faithfulness, answer 

- relevancy, context relevancy). 

- **<mark>DeepEval</mark>** <mark>: Framework de evaluación para LLMs y RAG con métricas integradas.</mark> 

- **<mark>TruLens</mark>** <mark>: Monitoreo y evaluación de aplicaciones LLM.</mark> 

- **LangSmith** : Plataforma de LangChain para depuración y evaluación (con plan gratuito). 

- **<mark>RAGChecker</mark>** <mark>: Herramienta de diagnóstico para sistemas RAG.</mark> 



## **10. Diseño de conocimiento especializado para dominios específicos** 

El diseño de conocimiento especializado adapta las técnicas de Ingeniería del Conocimiento y RAG a las necesidades particulares de un dominio, considerando su vocabulario, estructura de datos, requisitos de precisión y restricciones. 

### **Consideraciones por dominio** 

|**Dominio**|**Desafíos**|**Estrategias**|
|---|---|---|
|**Medicina/**<br>**Salud**|Terminología precisa, seguridad del<br>paciente, actualización constante|Ontologías médicas (SNOMED CT), fltros<br>por credenciales, validación humana|
|**Legal**|Lenguaje formal, precedentes,<br>confdencialidad|Embeddings legales especializados,<br>chunking por documentos, control de<br>acceso|
|**Finanzas**|Datos numéricos, regulaciones,<br>volatilidad|Integración con datos estructurados,<br>actualización en tiempo real|
|**Ingeniería**|Especifcaciones técnicas, estándares,<br>seguridad|Taxonomías de componentes, relaciones<br>jerárquicas|
|**Educación**|Diferentes niveles, pedagogía,<br>adaptabilidad|Segmentación por nivel educativo,<br>generación de explicaciones graduadas|



### **<mark>Proceso de diseño</mark>** 

1. **Análisis del dominio** : Identificar conceptos clave, relaciones, fuentes de 

conocimiento, usuarios y casos de uso. 

2. **Selección de representación** : Elegir entre ontologías, taxonomías, grafos de conocimiento o embeddings según necesidades. 

<mark>3.</mark> **<mark>Construcción de ontología/taxonomía</mark>** <mark>: Defnir clases, propiedades y relaciones.</mark> 

<mark>4.</mark> **<mark>Preparación de datos</mark>** <mark>: Limpieza, normalización, enriquecimiento con metadatos.</mark> 

<mark>5.</mark> **<mark>Selección de modelos</mark>** <mark>: Embeddings ajustados al dominio (fne-tuning).</mark> 

6. **Diseño de chunking** : Estrategias adaptadas a la estructura típica de documentos del dominio. 

7. **Configuración de recuperación** : Parámetros de búsqueda (k, umbral de similitud, filtros). 

<mark>8.</mark> **<mark>Personalización de prompts</mark>** <mark>: Instrucciones específcas del dominio para el LLM.</mark> 

<mark>9.</mark> **<mark>Evaluación continua</mark>** <mark>: Monitoreo y ajuste basado en feedback.</mark> 

### **<mark>Caso de uso: Sistema RAG para normativa de construcción</mark>** 

Una empresa de construcción implementa un sistema que: 

1. **Indexa** : Códigos de construcción, normativas municipales, manuales de seguridad. 

2. **Ontología** : Define relaciones entre tipos de edificación, materiales, requisitos estructurales y normativas aplicables. 

<mark>3.</mark> **<mark>Chunking</mark>** <mark>: Segmenta por artículos y secciones normativas, no por tamaño fjo.</mark> 

<mark>4.</mark> **<mark>Embeddings</mark>** <mark>: Modelo fne-tuneado con terminología de construcción.</mark> 

<mark>5.</mark> **<mark>Recuperación</mark>** <mark>: Búsqueda híbrida (vectorial + keywords para números de artículos).</mark> 

6. **Generación** : Respuestas que citan artículos específicos y advierten sobre 

interpretaciones. 

<mark>7.</mark> **<mark>Evaluación</mark>** <mark>: Validación por ingenieros civiles y arquitectos.</mark> 

#### **Herramientas open-source recomendadas:** 

- **Protege** : Para construir ontologías de dominio. 

- **<mark>Neo4j</mark>** <mark>: Para grafos de conocimiento con relaciones complejas.</mark> 

- **<mark>Haystack + domain-specifc embeddings</mark>** <mark>: Pipeline RAG adaptable.</mark> 

- **<mark>spaCy + custom NER</mark>** <mark>: Extracción de entidades específcas del dominio.</mark> 

- **<mark>MLfow</mark>** <mark>: Seguimiento de experimentos y versionado de modelos.</mark> 

- **<mark>DVC</mark>** <mark>: Control de versiones para datasets y pipelines de datos.</mark> 

## **Resumen y recomendaciones finales** 

|**Componente**|**Recomendación open-source**|
|---|---|
|Ontologías/Taxonomías|Protege, SKOS, VocBench|
|Embeddings|Sentence-Transformers, FastText, Hugging Face|
|Chunking|LangChain, LlamaIndex, Chonkie|
|Base de datos vectorial|Qdrant, Weaviate, Milvus, pgvector|
|Framework RAG|LangChain, LlamaIndex, FlexRAG, Haystack|
|Evaluación|RAGAS, DeepEval, TruLens|



La Ingeniería del Conocimiento y los sistemas RAG representan una convergencia poderosa entre la representación estructurada del conocimiento y la flexibilidad de los modelos generativos. El éxito de un sistema RAG depende de un diseño cuidadoso en cada etapa: desde la ontología que organiza el dominio, pasando por los embeddings que capturan semántica, hasta la arquitectura de recuperación y generación que produce respuestas precisas y fundamentadas. 

**Ontologías** , en el contexto de la Inteligencia Artificial y la Ingeniería del Conocimiento, son **representaciones formales y explícitas de un conjunto de conceptos dentro de un dominio específico, junto con las relaciones que existen entre ellos** . 

La definición más aceptada en el mundo académico es la de Tom Gruber: _"Una ontología_ . _es una especificación explícita y formal de una conceptualización compartida"_ 

Para entenderlo de forma sencilla: **piensa en una ontología como un "mapa conceptual" o un "diccionario inteligente"** de un área del saber (por ejemplo, la medicina, el derecho o la ingeniería). Pero a diferencia de un diccionario tradicional (que solo da definiciones), una ontología incluye **reglas lógicas** que permiten a las máquinas **razonar** y deducir nueva información a partir de los datos existentes. 

### **¿Qué componentes tiene una ontología?** 

Para que sea considerada una ontología formal, debe contener estos cinco elementos: 

1. **Clases (o Conceptos)** : Son los tipos de entidades del dominio. Ejemplo: _Paciente_ , _Enfermedad_ , _Medicamento_ . 

2. **Propiedades (o Atributos)** : Características que describen a las clases. Ejemplo: una _Enfermedad_ tiene _nombre_ , _síntomas_ y _nivel_de_gravedad_ . 

3. **Relaciones** : Cómo se conectan los conceptos entre sí. Van más allá de la jerarquía. Ejemplo: _Medicamento_ **trata** _Enfermedad_ ; _Paciente_ **presenta** _Síntoma_ . 

4. **Instancias (o Individuos)** : Son los objetos concretos que pertenecen a las clases. Ejemplo: _Juan Pérez_ es una instancia de _Paciente_ ; la _Aspirina_ es una instancia de _Medicamento_ . 

5. **Axiomas (o Reglas lógicas)** : Son afirmaciones que siempre deben cumplirse y permiten inferir conocimiento nuevo. Ejemplo: _Si un paciente tiene fiebre y tos, Y la fiebre dura más de 3 días, ENTONCES podría tener una infección respiratoria._ 

### **<mark>Ontología vs. Taxonomía (La diferencia clave)</mark>** 

Es muy común confundirlas, pero la diferencia es crucial: 

- Una **Taxonomía** es una jerarquía **simple y rígida** (relación de herencia "es-un"). Ejemplo: _Animal → Vertebrado → Mamífero → Canino → Perro_ . Solo dice "el perro es un mamífero". 

- Una **Ontología** es un **grafo rico y flexible** que incluye esa jerarquía, pero además añade relaciones complejas entre conceptos de diferentes ramas. Ejemplo: _Perro_ **tiene_raza** _Labrador_ , _Labrador_ **requiere_ejercicio** _Alto_ , y _Alto_ejercicio_ **previene** _Obesidad_canina_ . 

En resumen: **Toda ontología contiene taxonomías, pero no toda taxonomía es una ontología.** La ontología permite razonar; la taxonomía solo clasificar. 

### **Ejemplos del mundo real** 

- **Dominio Médico (SNOMED CT)** : Es una de las ontologías médicas más grandes del mundo. No solo clasifica "Neumonía", sino que la relaciona con "Infección pulmonar", "Causada por bacteria", "Presenta fiebre" y "Se trata con antibióticos". Esto permite que un historial clínico electrónico "entienda" que si un paciente tiene neumonía, automáticamente sabe que debe monitorizar su respiración. 

- **Dominio de Comercio Electrónico ( Schema.org )** : Es una ontología ligera usada por Google, Amazon y Shopify. Define que un _Producto_ tiene una _Marca_ , un _Precio_ , y una _Disponibilidad_ , y que una _Persona_ puede realizar una _Acción de Compra_ . Esto permite que los motores de búsqueda muestren tarjetas enriquecidas (precios, estrellas) directamente en los resultados. 

### **¿Para qué sirven en los sistemas RAG (Retrieval-Augmented Generation)?** 

Aunque los sistemas RAG modernos suelen depender mucho de _embeddings_ (vectores numéricos) y bases de datos vectoriales, las ontologías juegan un papel **estratégico** de alto nivel: 

1. **Mejoran la recuperación (Query Enhancement)** : Si el usuario pregunta _"Tratamiento para infección de oído"_ , la ontología sabe que "Amoxicilina" es un tipo de tratamiento y 

que "Otitis media" es el término médico exacto. El sistema enriquece la consulta con estos sinónimos y relaciones para buscar mejor. 

2. **Filtrado estructural** : Permiten a la base de datos vectorial filtrar por metadatos. Por 

ejemplo: _"Solo recupera documentos que pertenezcan a la clase 'Efectos Secundarios' y que tengan relación con 'Pacientes pediátricos'"_ . 

3. **Validación de respuestas** : Antes de que el LLM dé una respuesta, la ontología puede verificar que no esté contradiciendo una regla lógica del dominio (por ejemplo, que no recomiende un medicamento contraindicado para una condición específica). 

### **Herramientas y lenguajes para construir ontologías** 

- **Lenguajes estándar** : **OWL** (Web Ontology Language) y **RDFS** (RDF Schema), avalados por el W3C. 

- **Editores visuales** : **Protégé** (el más famoso, open-source, desarrollado por la Universidad de Stanford). 

- **Bases de datos de grafos** : **Neo4j** o **GraphDB** , que permiten almacenar y consultar ontologías usando **SPARQL** (el lenguaje de consulta para grafos de conocimiento). 

En definitiva, las ontologías son el "andamiaje lógico" que aporta **precisión, consistencia y capacidad de razonamiento** a los sistemas de IA, evitando que estos se comporten como simples "loro estocástico" y actuando más como un experto que realmente entiende las reglas de su campo. 


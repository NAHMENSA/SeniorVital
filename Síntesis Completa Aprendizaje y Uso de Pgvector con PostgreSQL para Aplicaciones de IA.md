# **Síntesis Completa: Aprendizaje y Uso de Pgvector con PostgreSQL para Aplicaciones de IA** 

**(Enfoque completamente local y gratuito con HuggingFaceEmbeddings)** 

## **Introducción: Postgres como Base de Datos Vectorial** 

PostgreSQL, combinado con la extensión **pgvector** , se posiciona como una solución completa para construir aplicaciones de inteligencia artificial. Esta aproximación permite a los desarrolladores utilizar sus conocimientos existentes de bases de datos relacionales para adentrarse en el mundo de la IA, sin necesidad de herramientas especializadas, costosas claves de API externas o equipos de investigación dedicados. La extensión pgvector transforma Postgres en una base de datos vectorial de alto rendimiento, manteniendo todas las ventajas de una base de datos relacional madura: cumplimiento ACID, recuperación puntual, joins, y confiabilidad probada. 

### **¿Qué son los Vectores y las Bases de Datos Vectoriales?** 

Los **vectores** son representaciones numéricas comprimidas de datos (texto, imágenes, audio) generadas por modelos de _embedding_ . Esencialmente, son listas de números flotantes que capturan el "significado" semántico del contenido original en un espacio multidimensional. Estos vectores permiten realizar búsquedas por similitud semántica, no solo por coincidencia de palabras clave. 

Las **bases de datos vectoriales** son sistemas especializados en almacenar y buscar estos vectores de manera eficiente. Su utilidad se ha disparado con el auge de los LLMs, ya que permiten conectar estos modelos con datos privados o específicos mediante el proceso de **Generación Aumentada por Recuperación (RAG)** . Este enfoque combina la recuperación de información relevante de una base de datos vectorial con la capacidad de razonamiento de un LLM para generar respuestas contextualizadas. 

## **Extensiones Clave de Postgres para IA** 

### **1. PG Vector** 

La extensión fundamental que proporciona: 

- **Tipo de dato vectorial** : Permite almacenar vectores como un tipo de columna nativo. 

- **<mark>Funciones de distancia</mark>** <mark>: Soportadas: coseno, L1, L2, producto interno.</mark> 

- **<mark>Índices de búsqueda vectorial</mark>** <mark>: HNSW e IVF Flat.</mark> 

### **<mark>2. PG Vector Scale</mark>** 

Un complemento a PG Vector que lo acelera para cargas de trabajo a gran escala: 

- Búsqueda filtrada de alta precisión. 

- <mark>Índice Streaming DISCANN (basado en gráfcos de una sola capa).</mark> 

- <mark>Escalabilidad a más de mil millones de vectores.</mark> 

- <mark>Costos que escalan con disco y RAM, no solo con memoria.</mark> 

### **3. PG AI** 

Extensión que lleva flujos de trabajo de IA a la base de datos. 

**Nota importante** : Aunque <mark>pgai</mark> incluye funciones para OpenAI, también es compatible con **Ollama** , lo que permite usar modelos locales y gratuitos (como <mark>nomic-embed-text</mark> o cualquier modelo de Hugging Face alojado en Ollama) directamente desde SQL. De esta forma, se puede generar embeddings sin depender de servicios externos de pago. Además, los embeddings pueden generarse completamente en Python con la librería <mark>sentence-transformers</mark> . 

Todas estas extensiones son de código abierto, compatibles con la mayoría de proveedores en la nube, y pueden instalarse y usarse conjuntamente. De hecho, PG Vector Scale y PG AI dependen automáticamente de PG Vector. 

## **Tipos de Aplicaciones de IA con Postgres** 

1. **RAG (Retrieval-Augmented Generation)** : Chatbots de soporte, co-pilotos de investigación, documentación interactiva. Combina LLMs (locales o externos) con datos propios. 

2. **Búsqueda Semántica** : Búsqueda por significado en lugar de palabras clave. Aplicable a imágenes, documentos, frases. 

3. **Agentes** : Sistemas de IA que usan herramientas, planifican y toman acciones autónomas (ej. búsqueda web, consulta de bases de datos, llamadas a APIs). 

4. **Text-to-SQL** : Permite consultar datos estructurados en lenguaje natural, ideal para análisis de datos y dashboards interactivos. 

<mark>5.</mark> **<mark>Sistemas de Recomendación</mark>** <mark>: Basados en similitud de preferencias o comportamientos.</mark> 

<mark>6.</mark> **<mark>Detección de Anomalías</mark>** <mark>: Especialmente útil para series temporales.</mark> 

## **Beneficios de Usar Postgres para IA (con Enfoque Local)** 

1. **Una sola base de datos** : Elimina la complejidad de sincronizar y duplicar datos entre sistemas separados. 

2. **Almacenamiento conjunto** : Vectores junto con metadatos y otros tipos de datos (series temporales, geoespaciales). 

3. **Rendimiento y escalabilidad** : Demostrado comparable o superior a bases de datos vectoriales especializadas (ej. Pinecone). 

<mark>4.</mark> **<mark>Confabilidad y ecosistema</mark>** <mark>: Todas las ventajas de una base de datos madura.</mark> 

5. **Gratuito y privado** : Al usar modelos locales de Hugging Face ( _sentence-transformers_ ) o vía Ollama, se eliminan los costes por llamadas a APIs externas, se mejora la privacidad de los datos (todo reside en tu infraestructura) y no hay límites de tasa. 

6. **Capacidades avanzadas** : Búsqueda híbrida, filtrado, multi-tenencia, todo en una única plataforma SQL. 

## **Índices de Búsqueda Vectorial: Comparativa y Uso** 

### **IVF Flat (Inverted File Flat)** 

- **Primer índice introducido en pgvector** . 

- **<mark>Ventajas</mark>** <mark>: Bajo uso de memoria.</mark> 

- **Desventajas** : Requiere reconstrucción del índice tras actualizaciones; menor precisión que otros índices. 

- **<mark>Recomendación</mark>** <mark>: Uso limitado a cargas de trabajo con pocas actualizaciones.</mark> 

### **HNSW (Hierarchical Navigable Small World)** 

- . 

- **Índice basado en gráficos multicapa** 

- **Ventajas** : Buen equilibrio velocidad/precisión; maneja actualizaciones sin reconstrucción; opciones de cuantización; construcción paralelizable. 

- **Desventajas** : Alta demanda de memoria (los vectores deben permanecer en RAM); problemas de precisión en búsqueda filtrada; limitaciones de escala. 

- **<mark>Recomendación</mark>** <mark>: Ideal para cargas de trabajo de tamaño mediano (100k–1M vectores).</mark> 

### **Streaming DISCANN (en PG Vector Scale)** 

- . 

- **Índice basado en gráficos de una sola capa** 

- **Ventajas** : Súper alta precisión en búsqueda filtrada; escala a >1000M vectores; cuantización por defecto; costos escalan con disco+RAM; maneja actualizaciones sin reconstrucción. 

- **<mark>Desventajas</mark>** <mark>: Tiempos de construcción más largos (solo al inicio).</mark> 

- **Recomendación** : Para cargas de trabajo a gran escala (>10M vectores) y búsqueda filtrada compleja. 

**Regla práctica** : Con menos de 100,000 vectores, la búsqueda de fuerza bruta es suficiente. A partir de ese umbral, recomiendan HNSW o Streaming DISCANN según el volumen y necesidades. 

### **<mark>Implementación de Índices en SQL</mark>** 

sql 

_-- IVF Flat_ CREATE INDEX ON quotes USING ivfflat (embedding vector_cosine_ops); 

_-- HNSW_ 

CREATE INDEX ON quotes USING hnsw (embedding vector_cosine_ops); 

##### _-- Streaming DISCANN_ 

CREATE INDEX ON quotes USING discann (embedding vector_cosine_ops); 

## **<mark>Flujo de Trabajo Práctico: Confguración y Uso (Totalmente Local)</mark>** 

### **1. Configuración de la Base de Datos con Docker** 

###### bash 

docker pull pgvector/pgvector:pg17 

docker run --name pgvector-demo -e POSTGRES_PASSWORD=test -p 5432:5432 -d pgvector/pgvector:pg17 

### **<mark>2. Instalación de Extensiones en Postgres</mark>** 

sql 

CREATE EXTENSION vector; CREATE EXTENSION ai; _-- Opcional, si se usa pgai con Ollama_ CREATE EXTENSION vectorscale; _-- Opcional, para grandes volúmenes_ 

### **<mark>3. Creación de Tabla con Columna Vectorial</mark>** 

sql 

CREATE TABLE quotes ( id SERIAL PRIMARY KEY, quote TEXT, person TEXT, embedding VECTOR(384) _-- Dimensión típica de modelos como all-MiniLM-L6-v2_ ); 

### **<mark>4. Generación de Embeddings con Hugging Face (desde Python)</mark>** 

Usamos la librería <mark>sentence-transformers</mark> y <mark>langchain_community</mark> , sin necesidad de claves API. 

python 

_# Instalación previa: pip install sentence-transformers langchain-community psycopg2-binary pgvector_ 

from langchain_community.embeddings import HuggingFaceEmbeddings 

_# Cargamos el modelo gratuito y ligero de Hugging Face_ 

embeddings = HuggingFaceEmbeddings( model_name="sentence-transformers/all-MiniLM-L6-v2" ) 

_# Ejemplo: generar embedding para un texto_ 

texto_ejemplo = "Esta es una cita histórica sobre Nueva York." vector = embeddings.embed_query(texto_ejemplo) _# Devuelve una lista de 384 floats_ print(f"Dimensión del vector: {len(vector)}") 

### **<mark>5. Almacenar los Vectores en Postgres (usando Python y SQL)</mark>** 

python 

import psycopg2 

from pgvector.psycopg2 import register_vector 

conn = psycopg2.connect( 

dbname="vector_db", user="postgres", password="test", host="localhost" 

) 

conn.autocommit = True 

register_vector(conn) _# Habilita el tipo vector en psycopg2_ 

cursor = conn.cursor() 

_# Suponiendo que tenemos una lista de fragmentos de texto (chunks)_ 

chunks = ["Texto 1...", "Texto 2...", ...] _# Ejemplo_ 

for chunk in chunks: 

vector = embeddings.embed_query(chunk) 

cursor.execute( 

"INSERT INTO quotes (quote, embedding) VALUES (%s, %s)", 

(chunk, vector) 

) 

#### **Alternativa directa desde SQL con pgai + Ollama** (totalmente local): 

Si se prefiere generar embeddings directamente en la base de datos sin Python, se puede configurar Ollama y usar la función <mark>ollama_embed()</mark> de la extensión <mark>pgai</mark> . Ejemplo: <mark>UPDATE quotes SET embedding = ollama_embed('nomic-embed-text', quote);</mark> 

Esto ejecuta el modelo local de Hugging Face a través de Ollama, sin costes ni dependencias externas. 

### **6. Búsqueda de Similitud en SQL (usando vectores generados localmente)** 

En Python, generamos el vector de la consulta y lo pasamos a SQL: 

python consulta_usuario = "Frases sobre el espíritu de Nueva York" vector_consulta = embeddings.embed_query(consulta_usuario) 

""" cursor.execute( SELECT id, quote, person, 1 - (embedding <=> %s) AS similitud FROM quotes ORDER BY embedding <=> %s LIMIT 3; """, (vector_consulta, vector_consulta)) 

resultados = cursor.fetchall() for row in resultados: print(row) 

### **<mark>7. Integración con Langchain (Store de Vectores)</mark>** 

<mark>HuggingFaceEmbeddings</mark> es compatible con el almacén de vectores <mark>PGVector</mark> de Langchain: 

python 

from langchain.vectorstores.pgvector import PGVector from langchain_community.embeddings import HuggingFaceEmbeddings 

CONNECTION_STRING = "postgresql+psycopg2://postgres:test@localhost:5432/vector_db" embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2") 

_# Crear y almacenar documentos (ej. desde fragmentos)_ 

store = PGVector.from_documents( 

documents=docs, _# Lista de objetos Document de Langchain_ 

= embedding embeddings, connection_string=CONNECTION_STRING ) 

_# Búsqueda semántica_ 

resultados = store.similarity_search("consulta de ejemplo", k=3) 

## **<mark>Técnicas Avanzadas para Mejorar Sistemas de IA</mark>** 

### **1. Desarrollo Basado en Evaluaciones (** **_Evaluation-Driven Development_ )** 

Metodología para medir y mejorar sistemáticamente aplicaciones de IA: 

- **Crear un conjunto de evaluación** : Comenzar con 10 preguntas que se espera que responda la aplicación. 

- **Medir cambios** : Evaluar el impacto de cambios (nuevos modelos locales, parámetros de chunking, etc.) en el rendimiento. 

- **Descomponer problemas** : Analizar cada componente del sistema (recuperación, razonamiento, selección de herramientas) por separado. 

- **Expandir el conjunto** : Crecer a 20, 30, 50 preguntas a medida que la aplicación evoluciona. 

### **2. Búsqueda Filtrada** 

Combinar búsqueda vectorial con filtros SQL para mejorar la relevancia: 

#### **a) Filtro por metadatos** : 

###### sql 

SELECT * FROM documents WHERE product = 'CRM' AND doc_type = 'API_REFERENCE' ORDER BY embedding <=> query_vector LIMIT 5; 

#### **<mark>b) Filtro compuesto</mark>** <mark>(múltiples condiciones):</mark> 

###### sql 

SELECT * FROM products WHERE category = 'Electronics' AND price BETWEEN 500 AND 2000 AND in_stock = TRUE ORDER BY embedding <=> query_vector LIMIT 10; 

#### **<mark>c) Filtro temporal</mark>** <mark>:</mark> 

sql 

SELECT * FROM news WHERE published_date > NOW() - INTERVAL '7 days' ORDER BY embedding <=> query_vector; 

**<mark>d) Filtro por permisos</mark>** <mark>:</mark> 

sql 

SELECT * FROM documents 

WHERE access_level <= current_user_access_level 

ORDER BY embedding <=> query_vector; 

#### **<mark>e) Filtro geoespacial</mark>** <mark>(combinando pgvector con PostGIS):</mark> 

sql 

SELECT * FROM attractions 

WHERE ST_DWithin(location, ST_MakePoint(lat, lon), 5000) 

ORDER BY embedding <=> query_vector, ST_Distance(location, point); 

### **<mark>3. Búsqueda Híbrida</mark>** 

Combina búsqueda vectorial y búsqueda por palabras clave (texto completo de Postgres) para obtener lo mejor de ambos mundos: 

- **Búsqueda por keywords** en títulos o metadatos específicos. 

- **<mark>Búsqueda semántica</mark>** <mark>en contenido extenso.</mark> 

- **<mark>Re-ranking</mark>** <mark>de resultados combinados.</mark> 

### **4. Multi-tenencia** 

Estrategias para aislar datos de diferentes inquilinos en aplicaciones SaaS: 

- **Tabla por inquilino** : Aislamiento fuerte, pero difícil de gestionar con muchos inquilinos. 

- **<mark>Esquema por inquilino</mark>** <mark>: Mayor organización que tablas separadas.</mark> 

- **Columna tenant_id** : Filtrado en cada consulta (requiere índices y cuidado en la planificación). 

- **<mark>Base de datos lógica</mark>** <mark>: Aislamiento a nivel de base de datos dentro del mismo clúster.</mark> 

- **<mark>Base de datos física</mark>** <mark>: Máximo aislamiento pero mayor complejidad operativa.</mark> 

### **5. Text-to-SQL** 

Permite a usuarios no técnicos consultar datos mediante lenguaje natural: 

- Los LLMs (locales o externos) pueden traducir preguntas en inglés a consultas SQL válidas. 

- <mark>Los agentes pueden usar esta herramienta para responder preguntas analíticas.</mark> 

- Aplicaciones como "chatea con tus datos" permiten democratizar el acceso a información. 

## **Consideraciones Prácticas y Mejores Prácticas (con Enfoque Local)** 

### **Ventajas de Almacenar Embeddings en Postgres** 

1. **Eliminación de costes de API** : Al usar modelos gratuitos de Hugging Face (como <mark>allMiniLM-L6-v2</mark> ), no hay cargos por generación de embeddings. 

2. **Privacidad y soberanía de datos** : Todo el proceso se ejecuta en tu infraestructura; los datos sensibles no salen de tu red. 

<mark>3.</mark> **<mark>Rendimiento</mark>** <mark>: Consultas locales sin latencia de red a APIs externas.</mark> 

4. **Simplicidad** : Una sola base de datos para todos los datos, sin sincronización entre sistemas. 

5. **Sin límites de tasa** : Puedes generar tantos embeddings como necesites sin restricciones impuestas por terceros. 

### **Consejos para la Producción** 

- **Evaluación continua** : Implementar un sistema de evaluación automatizado en CI/CD. 

- **<mark>Monitoreo de calidad</mark>** <mark>: Seguimiento de métricas de precisión y relevancia.</mark> 

- **Pruebas A/B** : Comparar diferentes modelos de _sentence-transformers_ , parámetros de chunking y estrategias de búsqueda. 

- **Escalabilidad** : Considerar PG Vector Scale desde el inicio si se espera crecimiento masivo. 

- **Hardware** : Para modelos locales más potentes (ej. <mark>all-mpnet-base-v2</mark> ), se recomienda disponer de GPU, aunque los modelos pequeños como <mark>MiniLM</mark> funcionan bien en CPU. 

### **Recursos Recomendados** 

- **Repositorio de pgvector** : Código fuente, ejemplos y documentación técnica. 

- **Librería sentence-transformers** : Modelos gratuitos y optimizados para generar embeddings. 

- **<mark>Blogs de TimeScale</mark>** <mark>: Artículos detallados sobre cada tipo de índice y casos de uso.</mark> 

- **"RAG es más que búsqueda vectorial"** : Blog que profundiza en la metodología de evaluación. 

- **<mark>Ollama + pgai</mark>** <mark>: Guía para integrar modelos locales directamente en SQL.</mark> 

## **Conclusión** 

PostgreSQL con pgvector ofrece una plataforma poderosa y **completamente gratuita** para construir aplicaciones de IA, eliminando la necesidad de bases de datos vectoriales 

especializadas y de costosas APIs externas. La combinación de pgvector con extensiones como PG AI (usando Ollama) y PG Vector Scale proporciona un ecosistema maduro, escalable y respetuoso con la privacidad para desarrolladores de todos los niveles. Al sustituir <mark>OpenAIEmbeddings</mark> por <mark>HuggingFaceEmbeddings</mark> (mediante <mark>sentence-transformers</mark> o vía Ollama), se logra un flujo de trabajo 100% local, sin dependencias de pago, con pleno control de los datos. Las técnicas avanzadas (búsqueda filtrada, híbrida, multi-tenencia) permiten crear aplicaciones robustas y útiles, mientras que el desarrollo basado en evaluaciones asegura una mejora continua y medible. Con estos conocimientos, los desarrolladores pueden construir desde MVPs sencillos hasta sistemas empresariales complejos, todo dentro del entorno familiar de PostgreSQL y el ecosistema abierto de Hugging Face. 


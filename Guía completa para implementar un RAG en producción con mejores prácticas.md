# **Guía completa para implementar un RAG en producción con mejores prácticas** 

Basado en los conceptos fundamentales y las técnicas avanzadas presentadas en los materiales de EvoAcademy y Julio Andrés Dev, esta guía te llevará desde los fundamentos hasta una implementación robusta de RAG (Retrieval-Augmented Generation) lista para producción. 

## **¿Qué es RAG y por qué necesitas algo más que el enfoque básico?** 

RAG (Retrieval-Augmented Generation) es una técnica que combina la generación de texto de un LLM con la recuperación de información desde una base de conocimiento externa. El enfoque básico o "naive RAG" sigue estos pasos: 

1. Dividir documentos en chunks de tamaño fijo 

<mark>2. Convertir cada chunk en un embedding</mark> 

<mark>3. Almacenar en una base de datos vectorial</mark> 

<mark>4. Convertir la pregunta del usuario en embedding</mark> 

<mark>5. Buscar los chunks más similares</mark> 

<mark>6. Pasar esos chunks al LLM junto con la pregunta</mark> 

**Problema** : Este enfoque naive **falla en producción** por varias razones: 

- Los chunks de tamaño fijo cortan información a la mitad, perdiendo contexto 

- La búsqueda semántica pura no funciona bien para términos exactos o códigos de error 

- Los usuarios hacen preguntas ambiguas, con múltiples partes o con errores ortográficos 

## **Paso 1: Preparación del entorno y herramientas** 

### **1.1 Configuración básica** 

```
python
```

```
# Instalación de dependencias
```

```
-
pip install langchain langchainopenai pandas numpy
pip install chromadb  # o qdrant-client, pypinecone
pip install tiktoken  # para conteo de tokens
```

### **<mark>1.2 Confguración de API keys</mark>** 

```
python
```

```
import os
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
```

```
os.environ["OPENAI_API_KEY"]="tu-api-key"
```

```
# Configurar el modelo de lenguaje
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
```

```
# Configurar el modelo de embeddings
```

```
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
```

## **Paso 2: Indexación - Preparación de documentos (La parte más crítica)** 

### **2.1 Limpieza y preprocesamiento** 

Antes de chunkear, **limpia tus documentos** . Esto incluye: 

- Eliminar encabezados, pies de página y números de página irrelevantes 

- <mark>Extraer tablas y convertirlas a texto estructurado</mark> 

- <mark>Preservar metadatos (título, sección, fecha, autor)</mark> 

### **2.2 Chunking avanzado (¡No uses tamaño fijo!)** 

El chunking es **el factor más importante** para un RAG exitoso. Estas son las técnicas recomendadas: 

#### **Técnica 1: Chunking por estructura** 

<mark>Aprovecha la estructura natural del documento (títulos, secciones, párrafos):</mark> 

```
python
```

```
from langchain.text_splitter import MarkdownHeaderTextSplitter
```

```
# Para documentos con estructura (Markdown, HTML, etc.)
headers_to_split_on =[
("#","Header 1"),
("##","Header 2"),
("###","Header 3"),
]
markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on)
chunks = markdown_splitter.split_text(documento)
```

#### **Técnica 2: Chunking semántico** 

Agrupa oraciones por similitud semántica en lugar de por tamaño fijo: 

```
python
```

```
from langchain_experimental.text_splitter import SemanticChunker
```

```
semantic_splitter = SemanticChunker(
    embeddings=embeddings,
    breakpoint_threshold_type="percentile"
)
chunks = semantic_splitter.split_text(documento)
```

#### **Técnica 3: RecursiveCharacterTextSplitter (con solapamiento)** 

Si usas splitter por tamaño, **siempre usa solapamiento** para no perder contexto entre chunks: 

```
python
```

```
from langchain.text_splitter import RecursiveCharacterTextSplitter
```

```
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,# tamaño en caracteres
    chunk_overlap=200,# solapamiento para mantener contexto
    separators=["\n\n","\n","."," ",""],
```

```
    length_function=len,
```

```
)
```

```
chunks = text_splitter.split_documents(documents)
```

### **<mark>2.3 Embeddings y almacenamiento vectorial</mark>** 

```
python
```

```
from langchain_community.vectorstores import Chroma
```

```
# Crear embeddings y almacenar
```

```
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db"
)
```

**Recomendación** : En producción, usa bases de datos vectoriales dedicadas como Pinecone, Qdrant o Milvus. 

## **Paso 3: Búsqueda híbrida (Semántica + Léxica)** 

La búsqueda semántica pura falla para términos exactos, códigos de error o nombres propios. La **búsqueda híbrida** combina ambos enfoques. 

### **3.1 Implementación con BM25 + Búsqueda vectorial** 

```
python
```

```
from rank_bm25 import BM25Okapi
import numpy as np
```

```
# 1. Índice BM25 para búsqueda léxica
```

```
tokenized_chunks =[chunk.page_content.split()for chunk in chunks]
bm25 = BM25Okapi(tokenized_chunks)
```

```
# 2. Búsqueda vectorial (semántica)
```

```
defsemantic_search(query, top_k=20):
    query_embedding = embeddings.embed_query(query)
    results = vectorstore.similarity_search_by_vector(
```

```
        query_embedding, k=top_k
)
return results
```

```
# 3. Búsqueda BM25 (léxica)
```

```
defbm25_search(query, top_k=20):
    tokenized_query = query.split()
    scores = bm25.get_scores(tokenized_query)
    top_indices = np.argsort(scores)[-top_k:][::-1]
return[chunks[i]for i in top_indices]
```

### **<mark>3.2 Fusión con Reciprocal Rank Fusion (RRF)</mark>** 

RRF combina los rankings de ambas búsquedas: 

```
python
```

```
defreciprocal_rank_fusion(semantic_results, bm25_results, k=60):
"""Fusiona dos listas de resultados usando RRF"""
    scores ={}
# Asignar puntuaciones RRF
for rank, doc inenumerate(semantic_results):
        doc_id = doc.page_content  # o usa un ID único
        scores[doc_id]= scores.get(doc_id,0)+1/(k + rank +1)
for rank, doc inenumerate(bm25_results):
        doc_id = doc.page_content
        scores[doc_id]= scores.get(doc_id,0)+1/(k + rank +1)
```

```
# Ordenar por puntuación
    sorted_docs =sorted(scores.items(), key=lambda x: x[1],
reverse=True)
return[doc for doc, _ in sorted_docs]
```

#### **<mark>Regla de oro</mark>** <mark>: En producción,</mark> **<mark>siempre usa búsqueda híbrida</mark>** <mark>.</mark> 

## **Paso 4: Reranking - El gran diferenciador** 

El reranking reordena los resultados iniciales usando un modelo cross-encoder, que es más preciso pero más costoso. 

```
python
```

```
from sentence_transformers import CrossEncoder
```

```
# Modelo de reranking (puedes usar Cohere, BGE-reranker, etc.)
reranker = CrossEncoder('BAAI/bge-reranker-large')
```

```
defrerank_results(query, documents, top_k=5):
"""Reordena documentos según relevancia a la query"""
    pairs =[[query, doc.page_content]for doc in documents]
    scores = reranker.predict(pairs)
```

```
# Ordenar por puntuación
    scored_docs =list(zip(documents, scores))
    scored_docs.sort(key=lambda x: x[1], reverse=True)
```

```
return[doc for doc, _ in scored_docs[:top_k]]
```

**Ventaja del reranking** : Puede rescatar documentos que estaban en posiciones bajas pero son muy relevantes. 

## **Paso 5: Optimización de queries del usuario** 

Los usuarios hacen preguntas imperfectas. Estas técnicas mejoran la recuperación: 

### **5.1 Query Rewriting (Reescritura de queries)** 

Reescribe la pregunta del usuario para que sea más compatible con tu base de conocimiento: 

```
python
```

```
defrewrite_query(original_query, conversation_history=None):
    prompt =f"""
```

```
    Reescribe la siguiente pregunta del usuario para que sea más clara
y
```

```
    fácil de buscar en una base de conocimiento.
```

```
    Pregunta original: {original_query}
```

```
{f"Historial de conversación: {conversation_history}"if
conversation_history else""}
```

```
    Pregunta reescrita:
    """
    response = llm.invoke(prompt)
return response.content
```

### **<mark>5.2 Query Decomposition (Descomposición)</mark>** 

Divide preguntas complejas en subpreguntas: 

```
python
defdecompose_query(query):
    prompt =f"""
    La siguiente pregunta del usuario contiene múltiples partes.
    Sepárala en preguntas individuales.
    Pregunta: {query}
    Preguntas separadas (una por línea):
    """
    response = llm.invoke(prompt)
return[q.strip()for q in response.content.split('\n')if
q.strip()]
```

### **<mark>5.3 Multi-Query</mark>** 

Genera múltiples versiones de la misma pregunta para abarcar más documentos: 

```
python
defgenerate_multi_queries(query, num_queries=3):
    prompt =f"""
    Genera {num_queries} versiones diferentes de la siguiente
pregunta,
    usando sinónimos y reformulaciones.
```

```
    Pregunta original: {query}
```

```
    Versiones:
    """
    response = llm.invoke(prompt)
return[q.strip()for q in response.content.split('\n')if
q.strip()]
```

### **<mark>5.4 HyDE (Hypothetical Document Embeddings)</mark>** 

Genera una respuesta hipotética y usa su embedding para buscar: 

```
python
```

```
defhyde_search(query, top_k=10):
# Generar respuesta ficticia
    prompt =f"Responde brevemente a esta pregunta (inventa si no
sabes): {query}"
    hypothetical_answer = llm.invoke(prompt).content
# Usar el embedding de la respuesta hipotética para buscar
    answer_embedding = embeddings.embed_query(hypothetical_answer)
    results = vectorstore.similarity_search_by_vector(answer_embedding,
k=top_k)
return results
```

## **<mark>Paso 6: Generación de respuesta con contexto enriquecido</mark>** 

### **6.1 Prompt engineering para RAG** 

```
python
defbuild_rag_prompt(query, context_documents):
    context ="\n\n".join([doc.page_content for doc in
context_documents])
```

```
    prompt =f"""
    Eres un asistente útil e informativo. Responde la pregunta del
usuario
    usando ÚNICAMENTE la información proporcionada en el contexto.
```

```
    Si la información no está en el contexto, di que no la sabes.
    Contexto:
{context}
    Pregunta del usuario: {query}
    Respuesta:
    """
return prompt
```

### **<mark>6.2 Pipeline completo de generación</mark>** 

```
python
defcomplete_rag_pipeline(query, conversation_history=None):
# 1. Rewriting (opcional)
    rewritten_query = rewrite_query(query, conversation_history)
# 2. Decomposition (si aplica)
    sub_queries = decompose_query(rewritten_query)
    all_docs =[]
for sub_query in sub_queries:
# 3. Búsqueda híbrida
        semantic_results = semantic_search(sub_query, top_k=20)
        bm25_results = bm25_search(sub_query, top_k=20)
# 4. RRF Fusion
        fused_results = reciprocal_rank_fusion(semantic_results,
bm25_results)
# 5. Reranking
        reranked = rerank_results(sub_query, fused_results, top_k=5)
        all_docs.extend(reranked)
# 6. Generación
    prompt = build_rag_prompt(query, all_docs[:5])# top 5 únicos
    response = llm.invoke(prompt)
return{
"answer": response.content,
"sources":[doc.metadata for doc in all_docs[:5]],
"chunks_used":[doc.page_content for doc in all_docs[:5]]
}
```

## **<mark>Paso 7: Evaluación y monitoreo</mark>** 

### **<mark>7.1 Métricas clave para evaluar tu RAG</mark>** 

|**Componente**|**Métrica**|**Descripción**|
|---|---|---|
|Retrieval|Recall@k|% de documentos relevantes en top-k|
|Retrieval|MRR|Mean Reciprocal Rank|
|Generation|Faithfulness|¿La respuesta se basa en el contexto?|
|Generation|Answer Relevance|¿Responde la pregunta?|
|End-to-end|Latencia|Tiempo total de respuesta|



### **<mark>7.2 Framework de evaluación</mark>** 

```
python
defevaluate_retrieval(test_queries, ground_truth_docs, k=5):
"""Evalúa la calidad de la recuperación"""
    recalls =[]
    mrrs =[]
for query, relevant_docs in test_queries:
        retrieved = retrieve_documents(query, top_k=k)
        retrieved_ids =[doc.metadata.get('id')for doc in retrieved]
        relevant_ids =[doc.metadata.get('id')for doc in
relevant_docs]
# Recall@k
        hit_count =len(set(retrieved_ids)&set(relevant_ids))
        recalls.append(hit_count /len(relevant_ids))
# MRR
for rank, doc_id inenumerate(retrieved_ids):
if doc_id in relevant_ids:
                mrrs.append(1/(rank +1))
break
else:
            mrrs.append(0)
return{
"recall@k": np.mean(recalls),
"mrr": np.mean(mrrs)
}
```

## **<mark>Paso 8: RAG Agéntico (Agentic RAG) - El futuro</mark>** 

El RAG agéntico añade un bucle de razonamiento donde el agente decide: 

1. Si necesita buscar información 

<mark>2. Qué buscar</mark> 

<mark>3. Si la respuesta es sufciente</mark> 

```
python
```

```
from langgraph.graph import StateGraph, END
```

```
classRAGAgentState:
def__init__(self):
        self.query =""
        self.context =[]
        self.answer =""
        self.retrieval_count =0
        self.max_retrievals =3
defshould_retrieve(state):
"""Decide si necesita más información"""
if state.retrieval_count >= state.max_retrievals:
return"generate"
# Si la respuesta está incompleta o no tiene suficiente contexto
iflen(state.context)<2:
return"retrieve"
```

```
return"generate"
```

```
# Construir el grafo del agente
workflow = StateGraph(RAGAgentState)
workflow.add_node("retrieve", retrieve_documents)
workflow.add_node("generate", generate_answer)
workflow.add_conditional_edges("generate", should_retrieve)
```

## **<mark>Resumen de mejores prácticas para producción</mark>** 

|**Fase**|**Práctica recomendada**|**Por qué**|
|---|---|---|
|**Chunking**|Usar chunking semántico o por<br>estructura|Preserva el contexto y signifcado|
|**Embedding**<br>**s**|Modelos especializados por dominio|Mejor captura de signifcado específco|



|**Fase**|**Práctica recomendada**|**Por qué**|
|---|---|---|
|**Búsqueda**|Híbrida (semántica + BM25)|Cubre tanto signifcado como términos<br>exactos|
|**Fusión**|Reciprocal Rank Fusion (RRF)|Combina rankings de forma justa|
|**Reranking**|Cross-encoder después de la búsqueda<br>inicial|Mejora precisión con costo controlado|
|**Queries**|Rewriting + Decomposition|Adapta preguntas imperfectas|
|**Evaluación**|Evals con métricas claras|Mides mejora real|
|**Monitoreo**|Logs de retrievals y respuestas|Detectas degradación temprana|



## **<mark>Conclusión</mark>** 

Un RAG en producción requiere mucho más que el enfoque naive que ves en tutoriales. La clave está en: 

1. **Chunking inteligente** - Respeta la estructura del documento 

<mark>2.</mark> **<mark>Búsqueda híbrida</mark>** <mark>- Combina semántica y términos exactos</mark> 

<mark>3.</mark> **<mark>Reranking</mark>** <mark>- Refna los resultados con un modelo cross-encoder</mark> 

<mark>4.</mark> **<mark>Optimización de queries</mark>** <mark>- Reescribe y descompone preguntas</mark> 

<mark>5.</mark> **<mark>Evaluación continua</mark>** <mark>- Mide y mejora iterativamente</mark> 

**Recuerda** : El RAG no es "set it and forget it". Cada documento y caso de uso requiere ajustes, y la evaluación constante es la única forma de saber si estás mejorando. 


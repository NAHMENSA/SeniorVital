**<mark>Tu bienestar, nuestra prioridad. Plataforma integral para el cuidado de adultos mayores.</mark>** 



# **Estructura de Base de Conocimiento Especializada para SeniorVital** 

## **1. INTRODUCCIÓN: EL CEREBRO COLECTIVO DE SENIORVITAL** 

Latinoamérica enfrenta un cambio demográfico sin precedentes: para 2050, más del 25% de la población superará los 60 años, con un aumento significativo de enfermedades crónicas, sarcopenia y fragilidad. Sin embargo, las soluciones tecnológicas actuales son monolíticas, rígidas y desconectadas de la realidad sociocultural de la región, donde la familia, la comunidad, la calidez humana y los recursos limitados definen el día a día del adulto mayor. 

**SeniorVital** nace para romper este paradigma. Es una plataforma cloud-native y serverless con un enfoque **AI-First** , diseñada específicamente para abordar las necesidades de movilidad, flexibilidad, resistencia y fuerza en adultos mayores (+60 años). Su arquitectura disruptiva se basa en un **Modelo Multi-Agente Autónomo** , donde cada agente (Nutricional, Fisiológico, de Entrenamiento, de Seguridad, Cognitivoemocional y Contextual) opera de forma independiente pero coordinada para ofrecer respuestas personalizadas y en tiempo real. 

La presente **Base de Conocimiento Especializada (Knowledge Base - KB)** constituye el "cerebro colectivo" de SeniorVital. No es un simple repositorio de documentos, sino una ontología dinámica estructurada para alimentar el sistema RAG (Retrieval-Augmented Generation) que dota de inteligencia a cada agente. Esta KB integra más de **28.500 palabras** distribuidas en **13 documentos técnicos, clínicos y prácticos** (provenientes de la OMS, la Sociedad Española de Geriatría, ACSM y estudios de vanguardia), organizados para que los agentes recuperen información precisa, contextualizada y culturalmente adaptada al entorno latinoamericano. 

## **2. OBJETIVOS DE LA BASE DE CONOCIMIENTO EN EL ECOSISTEMA SENIORVITAL** 

## **2.1. Objetivo General** 

Proveer una estructura semántica y jerárquica que permita a los agentes autónomos de SeniorVital recuperar conocimiento experto multidisciplinar, garantizando que las 

**<mark>Tu bienestar, nuestra prioridad. Plataforma integral para el cuidado de adultos mayores.</mark>** 



recomendaciones de ejercicio, nutrición y hábitos de vida sean **basadas en evidencia, personalizables por nivel funcional y sensibles al contexto latinoamericano** . 

## **2.2. Objetivos Específicos para la Arquitectura Multi-Agente** 

1. **Dotar de "Memoria Funcional" a cada Agente** : 

   - _Agente de Fisiología_ : Acceso inmediato a documentos sobre sarcopenia, dinapenia, osteoporosis y movilidad articular. 

   - _Agente de Prescripción de Ejercicio_ : Recuperación de rutinas específicas de fuerza, aeróbico, equilibrio y flexibilidad, con progresiones claras para niveles frágil, activo y muy activo. 

   - _Agente de Seguridad Clínica_ : Indexación de contraindicaciones, señales de alerta (dolor, mareo, hipertensión) y adaptaciones por patologías (artrosis, diabetes, enfermedades cardiacas). 

<mark>2.</mark> **<mark>Adaptación al Contexto Sociocultural Latinoamericano</mark>** <mark>:</mark> 

   - Estructurar la KB para permitir al _Agente Contextual_ inferir recomendaciones basadas en viviendas típicas (pisos de baldosa, patios, escaleras empinadas), clima variado (desde calor extremo en el norte hasta frío en el sur), alimentación base (frijoles, maíz, plátano, pescados locales) y dinámicas familiares (cuidado multigeneracional, espacios reducidos). 

<mark>3.</mark> **<mark>Facilitar la Personalización Dinámica</mark>** <mark>:</mark> 

   - La KB está clasificada por niveles funcionales (Frágil, Activo, Muy Activo) para que el _Agente de Orquestación_ pueda combinar fragmentos de distintos documentos según el perfil del usuario, creando una trayectoria de entrenamiento única y progresiva. 

### <mark>4.</mark> **<mark>Asegurar la Robustez Científca</mark>** <mark>:</mark> 

   - Estructurar los documentos por peso de evidencia (guías clínicas > estudios metaanalíticos > manuales prácticos) para que los agentes prioricen fuentes confiables (SEGG, OMS, ACSM) al generar respuestas críticas. 

<mark>5.</mark> **<mark>Optimizar la Recuperación en Baja Latencia (Serverless)</mark>** <mark>:</mark> 

   - Organizar la información en fragmentos semánticos (chunks) asociados a metadatos estrictos, permitiendo búsquedas vectoriales rápidas sin depender de infraestructura pesada, alineándose con la naturaleza _serverless_ de SeniorVital. 

<mark>6.</mark> **<mark>Soporte para Multimodalidad Futura</mark>** <mark>:</mark> 



**<mark>Tu bienestar, nuestra prioridad. Plataforma integral para el cuidado de adultos mayores.</mark>** 

- Aunque actualmente son textos, la estructura permite vincular ejercicios descritos (ej. "sentadilla con silla") con instrucciones verbales en español neutro y coloquial, preparando el terreno para interacciones por voz (común en adultos mayores con baja alfabetización digital). 



## **3. ESTRUCTURA DE LA BASE DE CONOCIMIENTO PARA RAG (MULTIAGENTE)** 

La KB se organiza en **6 Macrodominios Funcionales** , que mapean directamente con las responsabilidades de los agentes autónomos de SeniorVital. Cada macrodominio agrupa documentos específicos, etiquetados con metadatos para una recuperación ultrafina. 

## **MACRODOMINIO A: FUNDAMENTOS FISIOLÓGICOS Y PATOLOGÍAS (Agente de Evaluación Física)** 

|**Documento**|**Descripción Específca**|**Palabras Clave RAG**|**Metadatos para**<br>**Agentes**|
|---|---|---|---|
|**Sarcopenia y**<br>**dinapenia.txt**|Diferencia entre pérdida<br>de masa y fuerza;<br>criterios EWGSOP2;<br>impacto funcional.|_sarcopenia, dinapenia,_<br>_fuerza muscular,_<br>_diagnóstico, prevención,_<br>_fbras tipo II_|Patología: Sarcopenia,<br>Dinapenia;<br>Nivel:<br>Todos;<br>Evidencia: Alta|
|**Movilidad**<br>**articular en**<br>**adultos mayores**<br>**+ ejercicios -**<br>**ESHI.txt**|Pérdida de colágeno,<br>rigidez fascial; ejercicios<br>específcos para tobillo,<br>cadera, hombro.|_colágeno, fascia, rigidez,_<br>_rango de movimiento,_<br>_propiocepción, ejercicios_|Patología: Rigidez<br>articular;<br>Nivel: Frágil,<br>Activo;<br>Tipo: Movilidad|
|**Cómo frenar la**<br>**osteoporosis 8**<br>**claves basadas**<br>**en la evidencia -**<br>**ESHI.txt**|Mecanotransducción,<br>microimpactos,<br>diferencia entre tensión y<br>dolor, rol del entrenador.|_osteoporosis, densidad_<br>_ósea,_<br>_mecanotransducción,_<br>_impacto, carga,_<br>_seguridad_|Patología:<br>Osteoporosis;<br>Nivel:<br>Frágil, Activo;<br>Tipo:<br>Seguridad|
|**La diabetes.txt**|Datos OMS, tipos (1, 2,<br>gestacional), síntomas,<br>prevención, ejercicio|_diabetes tipo 2,_<br>_hiperglucemia, insulina,_<br>_prevención, ejercicio,_|Patología:<br>Diabetes;<br>Nivel:<br>Todos;<br>Contexto: Salud|



**<mark>Tu bienestar, nuestra prioridad. Plataforma integral para el cuidado de adultos mayores.</mark>** 



|**Documento**|**Descripción Específca**|**Palabras Clave RAG**|**Metadatos para**<br>**Agentes**|
|---|---|---|---|
||como tratamiento.|_OMS_|Pública|



## **MACRODOMINIO B: TAXONOMÍA DEL EJERCICIO (Fuerza, Aeróbico, Equilibrio, Flexibilidad) - Agente Prescriptor** 

|**Documento**|**Descripción Específca**|**Palabras Clave RAG**|**Metadatos para**<br>**Agentes**|
|---|---|---|---|
|**Mejores ejercicios**<br>**de fuerza para**<br>**mayores de 60 años**<br>**- Guía.txt**|9 ejercicios (sentadilla,<br>remo, puente, zancadas)<br>con progresiones y<br>correcciones por<br>patología.|_sentadilla, remo,_<br>_banda elástica,_<br>_zancada, progresión,_<br>_artrosis, core_|Tipo: Fuerza;<br>Nivel:<br>Activo, Muy<br>activo;<br>Recurso:<br>Bandas, Silla|
|**Los tres tipos de**<br>**ejercicio que**<br>**pueden mejorar su**<br>**salud y capacidad**<br>**física.txt**|Explicación de aeróbico<br>(150 min),<br>fortalecimiento (2<br>días/semana) y<br>equilibrio (3+ días).|_aeróbico,_<br>_fortalecimiento,_<br>_equilibrio, frecuencia_<br>_cardíaca, 150 minutos_|Tipo: Multi-<br>componente;<br>Nivel:<br>Activo;<br>Guía: ACSM|
|**guia-ejercicio-**<br>**mayores-segg.txt**<br>**(Secciones)**|Ejercicios específcos de<br>bíceps, tríceps, fexión<br>plantar, cadera, rodillas<br>y estiramientos.|_bíceps, tríceps, fexión_<br>_plantar, cadera,_<br>_isquiotibiales, 8-15_<br>_repeticiones_|Tipo: Fuerza,<br>Flexibilidad;<br>Nivel:<br>Todos;<br>Fuente: SEGG|
|**Entrenamiento en**<br>**adultos mayores -**<br>**guía completa -**<br>**ESHI.txt**|Recomendaciones OMS<br>multicomponente;<br>estructura de sesión<br>(calentamiento,<br>principal, vuelta).|_entrenamiento_<br>_multicomponente,_<br>_sarcopenia, volumen,_<br>_frecuencia, OMS, sesión_|Tipo:<br>Planifcación;<br>Nivel:<br>Todos;<br>Estructura: 60<br>min|



**<mark>Tu bienestar, nuestra prioridad. Plataforma integral para el cuidado de adultos mayores.</mark>** 



## **MACRODOMINIO C: CONTEXTO Y ENTORNO (Latinoamérica, Domicilio y Exterior) - Agente Contextual** 

|**Documento**|**Descripción Específca**|**Palabras Clave**<br>**RAG**|**Metadatos para**<br>**Agentes**|
|---|---|---|---|
|**Manual_ejercicio_perso**<br>**na_mayor_domicilio2.tx**<br>**t**|Rutinas en casa con<br>materiales caseros<br>(botellas, sillas, toallas);<br>ejercicios de fuerza y<br>equilibrio.|_ejercicios en casa,_<br>_silla, botellas,_<br>_hidratación, espacio_<br>_seguro, alfombras_|Entorno:<br>Domicilio;<br>Nivel:<br>Frágil,<br>Activo;<br>Recurso:<br>Casero|
|**Exercising Outdoors_**<br>**Safety Tips for Older**<br>**Adults.txt**|Seguridad en exteriores:<br>ropa por capas,<br>hidratación, tránsito,<br>calor/frío extremo,<br>material refectante.|_seguridad exterior,_<br>_calor, frío, tránsito,_<br>_bicicleta, ropa clara,_<br>_hidratación_|Entorno:<br>Exterior;<br>Clima:<br>Calor, Frío,<br>Lluvia;<br>Seguridad:<br>Alta|
|**Tips for Getting and**<br>**Staying Active as You**<br>**Age.txt**|Estrategias de<br>adherencia, apoyo social<br>(buddy system),<br>superación de barreras<br>(clima, coste).|_adherencia,_<br>_motivación, grupo,_<br>_barreras, objetivos_<br>_SMART, apoyo social_|Tipo:<br>Psicosocial;<br>Contexto<br>:<br>Comunidad;<br>Idioma:<br>EN/ES|



## **MACRODOMINIO D: COMORBILIDADES Y SEGURIDAD CLÍNICA - Agente de Seguridad y Salud** 

|**Documento**|**Descripción Específca**|**Palabras Clave RAG**|**Metadatos para**<br>**Agentes**|
|---|---|---|---|
|**Hacer ejercicio con**<br>**enfermedades**<br>**crónicas.txt**|Recomendaciones para<br>Alzheimer, Artritis,<br>EPOC, Diabetes,<br>Cardiopatías,<br>Osteoporosis y Dolor<br>Crónico.|_Alzheimer, artritis,_<br>_EPOC, diabetes,_<br>_corazón,_<br>_osteoporosis, dolor_<br>_crónico, ejercicio_<br>_adaptado_|Patología: Múltiple;<br>Tipo:<br>Adaptación;<br>Prioridad:<br>Seguridad|
|**guia-ejercicio-**|Combinaciones de|_cardiopatía,_|Patología: Renal,|



**<mark>Tu bienestar, nuestra prioridad. Plataforma integral para el cuidado de adultos mayores.</mark>** 



|**Documento**|**Descripción Específca**|**Palabras Clave RAG**|**Metadatos para**<br>**Agentes**|
|---|---|---|---|
|**mayores-segg.txt**<br>**(Sección**<br>**comorbilidades)**|ejercicio para<br>enfermedades<br>cardiacas, osteoporosis,<br>artrosis, fragilidad,<br>depresión.|_insufciencia renal,_<br>_depresión,_<br>_incontinencia, Kegel,_<br>_estrés_|Depresión;<br>Tipo:<br>Terapéutico|
|**Alimentación**<br>**saludable para**<br>**personas**<br>**mayores.txt**|Plan DASH, sodio,<br>hidratación, fbra,<br>interacciones<br>medicamentosas.|_sodio, DASH,_<br>_hidratación, fbra,_<br>_potasio,_<br>_medicamentos,_<br>_presión alta_|Tipo: Nutrición<br>Clínica;<br>Prioridad: Alta en<br>Hipertensos|



## **MACRODOMINIO E: NUTRICIÓN Y METABOLISMO (Enfoque Gastronómico Latinoamericano) - Agente Nutricional** 

|**Documento**|**Descripción Específca**|**Palabras Clave**<br>**RAG**|**Metadatos para**<br>**Agentes**|
|---|---|---|---|
|**WEB-GUIA-MAYORES-**<br>**version-publicacion.txt**<br>**(Secciones Nutrición)**|Menús para diabetes,<br>obesidad, dietas<br>trituradas; tablas de<br>IMC por edad y sexo<br>(población española,<br>extrapolable a LA).|_menús diabetes,_<br>_menús obesidad,_<br>_IMC, percentiles,_<br>_dieta astringente,_<br>_hidratos de carbono_|Tipo: Planifcación<br>Nutricional;<br>Población<br>: Latina;<br>Recurso:<br>Recetas|
|**Alimentación saludable**<br>**para personas**<br>**mayores.txt**|Porciones de<br>verduras/frutas,<br>cereales integrales,<br>proteínas magras,<br>lacteos bajos en grasa.|_porciones, tazas,_<br>_onzas, calorías,_<br>_grupos alimenticios,_<br>_colores_|Tipo: Guía<br>General;<br>Nivel: Todos|
|_Nota contextual LA_: La KB<br>permitirá al RAG sugerir<br>sustitutos locales (ej.<br>"reemplazar pan integral|||Adaptación LA: Alta|



**<mark>Tu bienestar, nuestra prioridad. Plataforma integral para el cuidado de adultos mayores.</mark>** 



|**Documento**<br>por arepa de maíz<br>integral", "pescado azul<br>local como jurel o<br>bonito").|**Descripción Específca**|**Palabras Clave**<br>**RAG**|**Metadatos para**<br>**Agentes**|
|---|---|---|---|



## **MACRODOMINIO F: ESTIMULACIÓN COGNITIVA Y BIENESTAR EMOCIONAL (Enfoque Holístico) - Agente Cognitivo-Emocional** 

|**Documento**|**Descripción Específca**|**Palabras Clave RAG**|**Metadatos para**<br>**Agentes**|
|---|---|---|---|
|**WEB-GUIA-**<br>**MAYORES-version-**<br>**publicacion.txt**<br>**(Secciones fnales)**|Ejercicios de memoria<br>(dado, palillos,<br>clasifcación de monedas),<br>gimnasia facial, relajación<br>(respiración china, masaje<br>con pelota).|_memoria,_<br>_estimulación_<br>_cognitiva, relajación,_<br>_respiración, Tai Chi,_<br>_masaje_|Tipo: Cognitivo;<br>Nivel:<br>Frágil, Activo;<br>Entorno:<br>Domicilio|
|**Gimnasia para**<br>**mayores guía ofcial**<br>**para una vida**<br>**activa y feliz.txt**|Sesión completa con<br>énfasis en coordinación y<br>prevención de caídas.|_coordinación, ritmo,_<br>_socialización, caídas,_<br>_autoestima_|Tipo:<br>Psicomotricidad;<br>Nivel:<br>Activo|
|**Tips for Getting and**<br>**Staying Active as**<br>**You Age.txt**|Benefcios de las<br>actividades grupales y el<br>apoyo social para evitar la<br>soledad.|_soledad, comunidad,_<br>_amistad, grupos,_<br>_envejecimiento activo_|Tipo:<br>Psicosocial;<br>Contexto:<br>Latino (familia)|



## **4. ANEXO TÉCNICO: MAPEO DE AGENTES A DOCUMENTOS (Matriz de Recuperación RAG)** 

Para implementar el RAG, se recomienda indexar los documentos con los siguientes **metadatos de enrutamiento** , permitiendo que el orquestador dirija la consulta al agente correcto y este al chunk exacto: 



### **<mark>Tu bienestar, nuestra prioridad. Plataforma integral para el cuidado de adultos mayores.</mark>** 

|**Agente Autónomo**|**Macrodomini**<br>**o**|**Documentos Prioritarios (Top 3)**|
|---|---|---|
|**Physio-Evaluator**(Evaluació<br>n Física)|A|Sarcopenia y dinapenia; Movilidad articular; Cómo<br>frenar la osteoporosis|
|**Exercise**<br>**Architect**(Prescripción)|B|Mejores ejercicios de fuerza; Los tres tipos de<br>ejercicio; Entrenamiento adultos mayores|
|**Safety**<br>**Guardian**(Seguridad<br>Clínica)|D|Hacer ejercicio con enfermedades crónicas; Exercising<br>Outdoors; Alimentación (interacciones)|
|**Context-Adaptor**(Entorno<br>LA)|C|Manual ejercicio domicilio; Exercising Outdoors; WEB-<br>GUIA (caminatas)|
|**Nutri-Buddy**(Nutrición)|E|Alimentación saludable; WEB-GUIA (menús/IMC); La<br>diabetes|
|**Mind & Soul**(Cognitivo)|F|WEB-GUIA (memoria/relajación); Gimnasia para<br>mayores; Tips for Staying Active|



## **5. CONCLUSIONES** 

La estructura propuesta transforma un conjunto de documentos estáticos en un **ecosistema de conocimiento vivo y modular** . Al adoptar esta KB en el corazón de SeniorVital, se logra: 

1. **Escalabilidad Inteligente** : A medida que crezca la evidencia científica, solo se añaden nuevos documentos al macrodominio correspondiente sin reestructurar todo el sistema. 

2. **Interacción Natural** : Los agentes pueden "dialogar" entre sí (ej. el _Agente de Seguridad_ alerta al _Agente de Prescripción_ si un usuario con hipertensión realiza un esfuerzo excesivo). 

3. **Relevancia Cultural** : La inclusión de metadatos de contexto latinoamericano asegura que las respuestas no sean una traducción literal de guías anglosajonas, sino consejos prácticos aplicables a la vida real en la región (adaptación de ejercicios en 



<!-- Start of picture text -->
IOR ¢<br>SV60+<br>4)<br><!-- End of picture text -->




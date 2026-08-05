****Informe Técnico Sprint 1: Ingeniería de Requisitos y Calidad Proyecto SeniorVital****

# Introducción

De acuerdo con el cuerpo de conocimiento SWEBOK (Software Engineering Body of Knowledge), la Ingeniería de Requisitos es un proceso iterativo e interdisciplinario que abarca la licitación, el análisis, la especificación y la validación de las necesidades del negocio. Basado en este principio, el presente informe detalla los entregables del Sprint Técnico 1: Ingeniería de Requisitos y Calidad del proyecto SeniorVital. El propósito de esta fase es sentar las bases formales del sistema mediante una definición rigurosa, absteniéndose de iniciar procesos de codificación prematuros con el fin de blindar la arquitectura contra el crecimiento caótico de requisitos.

## 1\. 1. Declaración del Propósito del Sistema

SeniorVital se concibe como una plataforma inteligente de gestión del bienestar cloud-native y serverless, diseñada con un enfoque AI-First para resolver las necesidades específicas de movilidad, flexibilidad, resistencia y fuerza de adultos mayores (+60 años), con especial atención al contexto sociocultural latinoamericano. A diferencia de las soluciones monolíticas tradicionales, SeniorVital plantea una arquitectura disruptiva basada en un modelo Multi-Agente Autónomo orquestado sobre plataforma local. El sistema delega la personalización y el análisis a dos entidades lógicas con propósito específico:

**Agente Wellness Coach:** Encargado del razonamiento clínico y la adaptación de rutinas de ejercicio en tiempo real, considerando estrictamente las restricciones médicas y los objetivos individuales del usuario.

**Agente Preventivo / Analytics:** Responsable del monitoreo continuo de la adherencia, la predicción del progreso físico y la detección temprana de patrones para la mitigación del abandono.

## 1\. 2. Límites del Sistema y Contexto del MVP

El alcance del Mínimo Producto Viable (MVP) queda rígidamente acotado a un ciclo de desarrollo ágil de 4 semanas. Este se enfocará en una biblioteca base de ejercicios funcionales seguros, el seguimiento del esfuerzo autopercibido y un entorno colaborativo que delimita tres perfiles de interacción:

*   El Adulto Mayor (usuario principal).
*   El Familiar/Cuidador (integrado mediante un "Modo Cuidador" para supervisión remota con privilegios de lectura).
*   El Fisioterapeuta/Administrador clínico.

## 1\. 3. Alcance del Informe y Metodología

El documento abarca los artefactos fundamentales para el inicio del proyecto: la definición de historias de usuario y casos de uso, la especificación de requisitos funcionales y no funcionales, la evaluación de la calidad del software bajo la norma ISO/IEC 25010, el diseño preliminar de los agentes de IA y la documentación inicial. Todas las actividades y decisiones técnicas adoptadas se enmarcan dentro de una metodología ágil combinada con prácticas de AI-Augmented Development (Desarrollo Aumentado por IA), utilizando herramientas colaborativas y de modelado moderno como Mermaid, Markdown y GitHub, garantizando así el cumplimiento de los estándares y buenas prácticas de la ingeniería de software actual.

## 1\. 4. Identificación Temprana y Matriz de Riesgos (Enfoque _Shift-Left_)

De acuerdo con las directrices del SWEBOK para la gestión proactiva de proyectos, y en alineación con los estándares de calidad ISO/IEC 25010, el equipo ha aplicado un enfoque _Shift-Left_ (desplazamiento a la izquierda). Antes de detallar las especificaciones funcionales y de iniciar fases de codificación, se han identificado los riesgos críticos que podrían comprometer la viabilidad clínica, técnica, financiera y metodológica del Mínimo Producto Viable (MVP).

A continuación, se presenta la matriz de riesgos estratégicos y arquitectónicos, junto con sus mitigaciones inyectadas directamente en el diseño del sistema:

**ID**

**Categoría**

**Descripción del Riesgo**

**Prob.**

**Impacto**

**Estrategia de Mitigación Arquitectónica y de Proceso**

**R01**

Clínico y Usabilidad

Brecha digital y mala interpretación de la fatiga: El adulto mayor podría malinterpretar la escala visual de esfuerzo (RPE) o los requisitos pueden fallar por falta de empatía con sus limitaciones visuales.

Alta

Alto (Peligro físico)

Mitigación: Implementar validación cruzada en UI (confirmación en texto simple y contraste 4.5:1 tras elegir un emoji). Realizar pruebas de usabilidad con adultos mayores e involucrar a un fisioterapeuta en la validación.

**R02**

Financiero y Arquitectura IA

Sobrecostos de IA Generativa y Sobredimensionamiento: Definir agentes demasiado complejos o el uso continuo de la API de Gemini podría disparar la facturación mensual en GCP.

Media

Alto (Financiero)

Mitigación: Priorizar agentes esenciales con respuestas lineales en el MVP. Usar el Batch API de Gemini para procesamientos nocturnos y aplicar Caché en Cloud Firestore para reciclar rutinas idénticas, evitando llamadas redundantes.

**R03**

Accesibilidad (Normativa)

Cumplimiento inadecuado de WCAG 2.1 AA: La documentación puede obviar la accesibilidad, resultando en un producto inutilizable para la tercera edad.

Alta

Alto (Exclusión)

Mitigación: Incluir Criterios de Aceptación obligatorios (ej. área táctil mínima 44x44pt) en cada Historia de Usuario y realizar auditorías automatizadas con axe DevTools sobre los prototipos.

**R04**

Seguridad e Integridad

Alteración de Datos Clínicos: Modificación no autorizada o accidental de las rutinas terapéuticas por parte de familiares con acceso a la app.

Baja

Crítico (Clínico)

Mitigación: Implementar estricto Control de Acceso Basado en Roles (RBAC) en Firebase Auth. Firestore aplicará reglas Read-Only inquebrantables para el "Modo Cuidador".

**R05**

Infraestructura Cloud

Egress de Red por Descarga Multimedia: Las tarifas de salida de datos pueden ser prohibitivas si los usuarios descargan videos de ejercicios en alta definición.

Alta

Medio

Mitigación: Forzar transcodificación de videos en Google Cloud Storage a 360p/480p y aplicar políticas agresivas de caché local (Offline-first).

**R06**

Gestión y Alcance

Deriva del Alcance (Scope Creep) y Falta de Trazabilidad: Aparición de requisitos no planificados (ej. integraciones con wearables) y pérdida del hilo conductor entre el diseño y los objetivos.

Media

Alto (Retraso)

Mitigación: Establecer un control de cambios formal. Mantener la matriz de trazabilidad actualizada y relegar explícitamente cualquier integración compleja a la Fase 2 del producto.

# ESPECIFICACIÓN DE REQUISITOS DEL SISTEMA

El sistema SeniorVital es una plataforma web y móvil cloud-native orientada a la gestión del bienestar físico de adultos mayores (+60 años). Su arquitectura se fundamenta en un ecosistema Serverless sobre Google Cloud Platform (GCP) y un modelo AI-First (Multi-Agente Autónomo).

El sistema debe resolver las necesidades de movilidad y fuerza del usuario final garantizando la seguridad clínica mediante el filtrado de restricciones médicas, permitiendo la supervisión remota por parte de familiares (modo cuidador) y la intervención clínica de profesionales (fisioterapeutas), todo bajo los estándares de accesibilidad WCAG 2.1 AA y el modelo de calidad ISO/IEC 25010.

## 2\. 1. Especificaciones Funcionales

### Módulo del Usuario Final (Adulto +60)

El sistema **SeniorVital** es una plataforma web y móvil orientada a la gestión del bienestar físico de adultos mayores (+60 años). Esta versión adapta la arquitectura para **entornos de desarrollo local** (sin contenedores Docker) manteniendo toda la funcionalidad descrita en la especificación original, pero sustituyendo los servicios de Google Cloud Platform por alternativas ligeras y auto-contenidas.

## Arquitectura Simplificada para Desarrollo Local

**Componente Original (GCP)**

**Simplificación Local**

**Notas**

Firestore (NoSQL)

**PostgreSQL + JSONB**

ACID + flexibilidad de documentos

Pub/Sub

**Redis Streams**

Suficiente para mensajería asíncrona en MVP

Cloud Storage

**MinIO** (compatible S3)

Almacenamiento de videos y fotos de progreso

Vertex AI

**Ollama** con modelo llama3.2:3b o phi3:mini

Inferencia local de agentes IA

BigQuery

**DuckDB**

Análisis embebido, sin servidor

FCM (Firebase Cloud Messaging)

**Web Push API** (o desactivar en MVP)

Notificaciones push nativas del navegador

Firebase Auth

**FastAPI Users** + JWT

Autenticación local, menos compleja

Todos los componentes se ejecutan de forma nativa (sin Docker) en el equipo de desarrollo, utilizando ejecutables directos, entornos virtuales de Python/Node, y servicios instalados localmente (PostgreSQL, Redis, MinIO, Ollama).

## 1\. Especificaciones Funcionales

### Módulo del Usuario Final (Adulto +60)

#### **1.1 Registro y Onboarding con Perfil de Salud**

*   **Acción:** Registrar nuevo usuario y configurar perfil de salud inicial.
*   **Actor(es):** Usuario final (+60), opcionalmente familiar/cuidador.
*   **Condición de disparo:** Primera apertura de la aplicación.
*   **Respuesta esperada del sistema:**
*   Presentar un proceso guiado de **máximo 5 preguntas iniciales** (onboarding progresivo).
*   Capturar datos antropométricos: edad, peso, altura.
*   Capturar nivel de condición física autopercibido.
*   Capturar objetivos principales (fuerza, movilidad, flexibilidad, pérdida de peso, etc.).
*   **Capturar restricciones médicas** (artritis, osteoporosis, hipertensión, dolor articular, uso de prótesis) para que el **Agente Wellness Coach** filtre automáticamente los ejercicios contraindicados.
*   Preguntar por disponibilidad de equipamiento (ninguno, bandas elásticas, etc.).
*   Generar el perfil de usuario y almacenarlo en formato de documento (JSON) dentro de **PostgreSQL (columna JSONB)**.
*   **Datos involucrados:** Edad, peso, altura, restricciones médicas (array/lista de strings), objetivos (array/lista de strings), equipamiento disponible (lista), rol del usuario, fecha de registro.

#### **1.2 Generación de Rutina Diaria Personalizada**

*   **Acción:** Sugerir rutina de ejercicios del día.
*   **Actor(es):** Agente Wellness Coach (implementado con Ollama + lógica de filtrado).
*   **Condición de disparo:** Diario (ej. al abrir la app) o tras completar evaluación de fatiga.
*   **Respuesta esperada del sistema:**
*   Generar una rutina de **bajo impacto** (ej. "rutina de movilidad en silla", "entrenamiento de fuerza asistida").
*   Priorizar ejercicios **sin equipamiento costoso** ni riesgos de caídas.
*   Adaptar la dificultad según el nivel actual del usuario utilizando **3-4 niveles de progresión segura** (Nivel 1: Sentado, Nivel 2: Con apoyo de silla, Nivel 3: De pie dinámico).
*   Incluir **calentamiento articular** obligatorio y ejercicios de equilibrio.
*   Mostrar cada ejercicio con **video demostrativo** (almacenado en MinIO) y voz guía opcional.
*   Ajustar dinámicamente la rutina si el usuario reporta fatiga/dolor en la escala RPE.
*   **Datos involucrados:** Historial de rutinas (PostgreSQL), nivel de fuerza, restricciones médicas, fatiga reportada, equipamiento disponible.

#### **1.3 Seguimiento de Ejercicio y Progresión**

*   **Acción:** Registrar series, repeticiones y esfuerzo percibido durante la rutina.
*   **Actor(es):** Usuario final (+60) o cuidador.
*   **Condición de disparo:** Durante la ejecución de una rutina.
*   **Respuesta esperada del sistema:**
*   Permitir marcar **serie completada** (tiempo de respuesta <500 ms) y registrar repeticiones.
*   Ofrecer **temporizador de descanso** configurable con alertas sonoras/visuales.
*   Registrar la **escala RPE** (1-10 con emojis/colores) al final de cada ejercicio.
*   Almacenar los datos transaccionales de la sesión en **PostgreSQL**.
*   Enviar los datos al **Agente Preventivo / Analytics** (vía Redis Streams) para actualizar la progresión.
*   **Datos involucrados:** Ejercicio ID, número de series, repeticiones, peso utilizado (si aplica), RPE, fecha-hora, duración de descanso.

#### **1.4 Proyecciones Temporales Personalizadas (Diferenciador Clave)**

*   **Acción:** Mostrar proyección de logros futuros basada en ritmo actual.
*   **Actor(es):** Agente Preventivo / Analytics (DuckDB + Ollama para generar mensajes).
*   **Condición de disparo:** Al finalizar la semana o al alcanzar una racha constante.
*   **Respuesta esperada del sistema:**
*   Calcular una **proyección lineal automatizada** para 4 semanas (ganancia de movilidad o resistencia).
*   Mostrar mensaje motivador con lectura de voz opcional: "María, llevas 2 semanas constante. Si mantienes este ritmo, el Agente calcula que en 4 semanas tu flexibilidad de hombro mejorará lo suficiente para peinarte con mayor facilidad."
*   Proyectar la fecha estimada para avanzar al siguiente nivel de progresión física.
*   **Datos involucrados:** Historial de cumplimiento (racha), evolución de repeticiones y RPE por ejercicio, objetivo declarado.

#### **1.5 Dashboard de Progreso Visual**

*   **Acción:** Visualizar evolución de métricas clave de salud y bienestar.
*   **Actor(es):** Usuario final, familiar/cuidador.
*   **Condición de disparo:** Navegación a sección "Mi progreso".
*   **Respuesta esperada del sistema:**
*   Calendario de entrenamiento simplificado con indicadores de alto contraste.
*   Gráfico de barras/líneas de evolución de movilidad o disminución del RPE.
*   Mapa anatómico bidimensional que resalte grupos musculares estimulados.
*   Resumen de la racha actual (sin penalizaciones psicológicas).
*   Opción de cargar registro fotográfico mensual almacenado en **MinIO**.
*   **Datos involucrados:** Historial de sesiones (PostgreSQL), registros de RPE, archivos de imagen (MinIO).

#### **1.6 Modo Cuidador/Familiar**

*   **Acción:** Supervisar de forma remota el progreso físico de un adulto mayor.
*   **Actor(es):** Familiar o cuidador (rol secundario).
*   **Condición de disparo:** Vinculación de cuentas autorizada por el usuario principal.
*   **Respuesta esperada del sistema:**
*   Panel espejo de lectura simplificada (cumplimiento semanal, alertas proactivas).
*   Disparar notificaciones push (Web Push API) si el usuario principal acumula inactividad inusual.
*   Privilegios estrictamente **solo lectura (Read-Only)**.
*   **Datos involucrados:** ID del usuario supervisado, token de vinculación, bandera de alertas activas en PostgreSQL.

### Módulo de Administrador / Entrenador (Staff)

#### **2.1 Gestión de Usuarios y Supervisión de Rutinas**

*   **Acción:** Supervisar, ajustar o asignar rutinas terapéuticas.
*   **Actor(es):** Administrador (Fisioterapeuta/Entrenador), Agente Preventivo / Analytics.
*   **Condición de disparo:** Acceso autenticado al panel web de administración.
*   **Respuesta esperada del sistema:**
*   Listar usuarios con **vista de semáforo** gestionada por IA: verde (en ritmo), ámbar (riesgo de abandono), rojo (inactivo >7 días o fatiga severa).
*   Permitir al administrador **sobrescribir o ajustar** la rutina sugerida por el Agente Wellness Coach.
*   Visualizar el historial detallado almacenado en PostgreSQL.
*   Exportar datos a CSV/PDF para informe médico.
*   **Datos involucrados:** Tabla de usuarios, rutinas asignadas, historial de RPE, métricas agregadas.

#### **2.2 Biblioteca de Ejercicios y Progresiones Seguras**

*   **Acción:** Crear y parametrizar el catálogo de ejercicios de bajo impacto.
*   **Actor(es):** Administrador (fisioterapeuta).
*   **Condición de disparo:** Acceso al módulo de "Gestión de ejercicios".
*   **Respuesta esperada del sistema:**
*   Definir ejercicios funcionales con **límite de 3-4 niveles de progresión segura**.
*   Asociar a cada nivel: descripción, URL del video (MinIO), criterios de paso conservadores.
*   Marcar **etiquetas de contraindicaciones médicas obligatorias**.
*   Actualizar el diccionario de datos en PostgreSQL para que el Agente Wellness Coach filtre ejercicios peligrosos.
*   **Datos involucrados:** Nombre del ejercicio, niveles (1..4), video URL (MinIO), tags de contraindicaciones, grupos musculares.

### Módulo Automático (Backend)

#### **3.1 Detección de Estancamiento y Ajuste de Rutina**

*   **Acción:** Detectar mesetas de rendimiento o dolor prolongado y reestructurar la rutina autónomamente.
*   **Actor(es):** Agente Preventivo / Analytics, Agente Wellness Coach (Ollama + lógica local).
*   **Condición de disparo:** Evaluación semanal del historial del usuario en PostgreSQL.
*   **Respuesta esperada del sistema:**
*   El Agente Preventivo analiza datos (DuckDB) y detecta meseta o fatiga alta.
*   Notificar al usuario con empatía: "Noté que este ejercicio te está costando un poco más. ¿Qué te parece si probamos una variante más cómoda?"
*   El Agente Preventivo instruye al Agente Wellness Coach para sugerir un ejercicio del mismo nivel pero distinto patrón.
*   **Datos involucrados:** Historial temporal de repeticiones (últimas 2-4 semanas), valores de RPE, fecha del último ajuste.

#### **3.2 Recordatorios y Notificaciones Proactivas**

*   **Acción:** Enviar recordatorios amigables de rutina, hidratación y bienestar general.
*   **Actor(es):** Agente Preventivo / Analytics (mediante Web Push API o desactivable en MVP).
*   **Condición de disparo:** Horario configurado por el usuario o detección de inactividad >2 días.
*   **Respuesta esperada del sistema:**
*   Generar notificaciones push dinámicas: "Hora de tu rutina de movilidad. ¡Unos minutos al día hacen la diferencia!"
*   Refuerzo positivo estricto, **sin rachas punitivas**.
*   Configuración granular en el perfil.
*   **Datos involucrados:** Preferencias de horario, token de suscripción push, timestamp de última notificación.

#### **3.3 Registro de Hábitos y Wearables (MVP 4 semanas)**

*   **Acción:** Registrar métricas complementarias de salud (pasos, sueño, frecuencia cardíaca).
*   **Actor(es):** Usuario final, Agente Preventivo.
*   **Condición de disparo:** Carga manual del usuario (MVP) o sincronización futura.
*   **Respuesta esperada del sistema:**
*   **Para MVP:** Entrada manual simplificada mediante botones grandes.
*   **Para trabajo futuro:** Integración con Google Fit / Apple HealthKit (fuera del alcance local).
*   Correlacionar hábitos con rendimiento: insight "Cuando duermes menos de 6 horas, tu fatiga aumenta."
*   **Datos involucrados:** Pasos diarios, frecuencia cardíaca, horas de sueño (manuales en MVP).

## 2\. Notas de Implementación para Desarrollo Local (sin Docker)

*   **Base de datos:** PostgreSQL (versión 14+) con soporte JSONB. Tablas principales: users, health\_profiles, exercise\_library, workout\_sessions, rpe\_logs, notifications\_prefs.
*   **Mensajería asíncrona:** Redis Stack (incluye Redis Streams) para comunicación entre módulos (ej. al finalizar sesión → agente preventivo).
*   **Almacenamiento de archivos:** MinIO en modo standalone (ejecutable binario). Los buckets necesarios: videos-ejercicios, fotos-progreso.
*   **Inferencia IA:** Ollama sirviendo modelos localmente. Se recomienda phi3:mini (2GB RAM) para equipos con recursos limitados, o llama3.2:3b (3GB RAM). Los agentes (Wellness Coach, Preventivo) se implementan como procesos Python que consultan Ollama + lógica determinista.
*   **Analítica embebida:** DuckDB ejecutado dentro del backend (FastAPI) para consultas analíticas sobre el historial.
*   **Notificaciones push:** Web Push API (funciona en navegadores modernos sin servicios externos). Para desarrollo, se puede simular con logs o desactivar temporalmente.
*   **Autenticación:** FastAPI Users con JWT (almacenamiento de usuarios en PostgreSQL). Incluye endpoints de registro, login, recuperación de contraseña, y roles (usuario, cuidador, admin).
*   **Exclusión de Docker:** Todos los servicios se instalan directamente en el sistema operativo (Windows, macOS o Linux) mediante paquetes nativos, binarios precompilados o gestores (apt, brew, choco). El backend se ejecuta en un entorno virtual Python (venv) y el frontend (React/Vue) con npm. No se requiere orquestación con contenedores.

Esta adaptación garantiza la **misma funcionalidad** que la especificación original, pero con una pila tecnológica 100% ejecutable en un ordenador personal sin dependencia de la nube ni Docker, ideal para desarrollo, pruebas de concepto o tesis.

## 2\. 2. Especificaciones No Funcionales

Para asegurar un producto de software maduro y auditable, los requisitos no funcionales se han extraído y categorizado siguiendo de forma estricta los atributos de calidad de la norma ISO/IEC 25010, traduciéndolos en métricas técnicas e innegociables para el equipo de desarrollo.

### Usabilidad y Accesibilidad Senior (WCAG 2.1 AA)

*   **RNF-USA-01 (Tamaño del Objetivo Táctil):** Todo elemento interactivo, botón o selector en la interfaz móvil debe poseer un área táctil mínima e innegociable de 44x44 pt para mitigar errores de interacción derivados de la pérdida de motricidad fina o temblores articulares.
*   **RNF-USA-02 (Legibilidad Tipográfica):** La fuente del sistema debe ser limpia (_sans-serif_), con un tamaño base mínimo de 16pt escalable nativamente por el sistema operativo hasta 24pt sin romper _layouts_ o causar desbordamientos visuales.
*   **RNF-USA-03 (Contraste Cromático):** Siguiendo las pautas WCAG 2.1 AA, todos los textos informativos, instrucciones médicas y etiquetas de control deben mantener un ratio de contraste cromático mínimo de 4.5:1 para compensar la prevalencia de presbicia y cataratas seniles.
*   **RNF-USA-04 (Arquitectura de Información):** La navegación de la interfaz móvil debe limitarse a un máximo de 3 niveles de profundidad para evitar la desorientación espacial. El tiempo de aprendizaje para completar la primera rutina debe ser menor a 3 minutos.
*   **RNF-USA-05 (Accesibilidad Asistiva):** El sistema debe proveer soporte fluido para lectores de pantalla nativos (TalkBack/VoiceOver), integración de navegación por teclado/periféricos y zoom fluido de hasta el 200%.

### Fiabilidad y Resiliencia

*   **RNF-FIA-01 (Arquitectura Offline-First):** El sistema debe garantizar la continuidad transaccional de los entrenamientos en zonas con nula conectividad (sótanos, parques). Se exige la implementación de la caché local nativa de Cloud Firestore, la cual persistirá los registros de forma atómica y sincronizará de manera transparente con la nube en un lapso $< 5$ segundos tras restablecerse la red.
*   **RNF-FIA-02 (Disponibilidad Serverless):** La plataforma en su capa backend debe certificar un _uptime_ mensual de 99.5%, sustentado sobre la infraestructura autogestionada y elástica de Google Cloud Run.

### Eficiencia de Desempeño

*   **RNF-EFI-01 (Comportamiento Temporal):** El tiempo total de procesamiento de la IA para el filtrado clínico y la renderización de la rutina diaria debe ser inferior a 2 segundos (latencia de punta a punta). Asimismo, la respuesta de la interfaz de usuario (ej. registro RPE) debe ejecutarse en $< 500$ ms.
*   **RNF-EFI-02 (Optimización de Carga Útil):** El tamaño de instalación de la aplicación móvil no debe superar los 50 MB. Toda multimedia pesada (videos demostrativos, audios guía) se servirá vía _streaming_ asíncrono optimizado.

**2.4 Seguridad y Confidencialidad**

*   **RNF-SEG-01 (Control de Acceso RBAC Estricto):** El sistema aplicará Control de Acceso Basado en Roles integrado con Firebase Auth. Los usuarios "Cuidador/Familiar" tendrán una restricción inquebrantable a nivel de backend (_Read-Only_), impidiendo la alteración de registros médicos.
*   **RNF-SEG-02 (Cifrado y Normativa Médica):** Toda comunicación debe ejecutarse bajo el protocolo TLS 1.3 en tránsito, y algoritmos AES-256 para los datos en reposo en Cloud Firestore, cumpliendo con los principios de privacidad de la ley HIPAA para datos de salud.

### Mantenibilidad y Portabilidad

*   **RNF-MAN-01 (Evolución de Arquitectura):** Uso de modelo de datos NoSQL (Firestore) para facilitar la escalabilidad sin alterar esquemas rígidos. La documentación será "viva" en GitHub, utilizando modelado moderno con Mermaid.js.
*   **RNF-POR-01 (Soporte de Dispositivos):** El despliegue móvil (_Flutter/React Native_) debe garantizar soporte estable para sistemas operativos Android 10+ e iOS 15+, incluyendo compatibilidad web absoluta para los paneles de administración y modo cuidador.

### Matriz Resumen de Atributos de Calidad

Las especificaciones no funcionales se centran en atributos de calidad críticos para el éxito del proyecto, sintetizados en la siguiente matriz según estándares de la industria:

**Atributo de Calidad (ISO 25010)**

**Especificación / Métrica Clave**

**Estándar Aplicado**

**Usabilidad**

Tamaño de botón mínimo: 44x44 pt. Contraste mínimo: 4.5:1. Profundidad máxima: 3 niveles. Curva de aprendizaje: < 3 minutos.

WCAG 2.1 AA, UX Gerontológica

**Accesibilidad**

Soporte TalkBack/VoiceOver. Zoom nativo 200%. Navegación con periféricos.

WCAG 2.1 AA (Perceptible, Operable, Robusto)

**Rendimiento / Eficiencia**

Procesamiento IA < 2 seg. Respuesta UI < 500 ms. Peso de la aplicación < 50 MB.

Arquitectura Móvil Optimizada

**Fiabilidad**

Sincronización offline-first < 5 seg. Disponibilidad del servidor 99.5%.

SRE (Site Reliability Engineering)

**Seguridad**

Cifrado AES-256 (reposo) y TLS 1.3 (tránsito). RBAC inquebrantable para modo lectura.

ISO/IEC 25010, OWASP, HIPAA

**Mantenibilidad**

Microservicios Serverless (Cloud Run). Base de datos flexible NoSQL. Documentación viva.

SWEBOK, AI-Augmented Development

**Portabilidad**

Soporte universal: Android 10+, iOS 15+ y navegadores web modernos (Chrome/Safari).

ISO/IEC 25010

# Historias de Usuario y Product Backlog

Para asegurar la trazabilidad y la consistencia técnica exigida en el desarrollo del sistema, los requisitos se han estructurado bajo la metodología ágil mediante Historias de Usuario (HU). Se definieron 11 historias de usuario, priorizadas estratégicamente para conformar el Product Backlog del Mínimo Producto Viable (MVP) con un ciclo de desarrollo de 4 semanas. Estas historias han sido redactadas desde la perspectiva de los actores clave del sistema: el Usuario Adulto Mayor, el Familiar/Cuidador, el Administrador/Fisioterapeuta y los Agentes de Inteligencia Artificial.

Cada historia incluye sus respectivos Criterios de Aceptación (Definición de Hecho / DoD), los cuales no solo determinan el cumplimiento funcional, sino que vinculan directamente la funcionalidad con métricas específicas de calidad arquitectónica (nube y rendimiento) y pautas rigurosas de accesibilidad y usabilidad para adultos mayores (alineados con la norma ISO/IEC 25010 y WCAG 2.1 AA).

### Matriz de Trazabilidad del Sprint 1 (Product Backlog Completo)

La siguiente tabla maestra representa el Product Backlog priorizado del MVP de SeniorVital, estableciendo una trazabilidad lineal y directa de 1 a 1 entre los requisitos del negocio, los enunciados ágiles y sus restricciones técnicas:

**ID**

**Historia de Usuario**

**Enunciado Ágil (User Story)**

**Criterios de Aceptación (DoD / Definición de Hecho)**

**HU01**

Registro y Onboarding del Perfil de Salud

Como Adulto Mayor (+60),quiero completar un proceso de registro guiado y corto donde declare mis restricciones médicas,para que la app conozca mi estado de salud desde el primer día y garantice mi seguridad física.

CA1.1: Formulario interactivo limitado a máximo 5 pasos, prohibiendo la mecanografía extensa.CA1.2: Botones de opción con área táctil ≥ 44x44 pt para mitigar temblores.CA1.3: Inserción automática de tags médicos críticos en Cloud Firestore ante patologías declaradas.

**HU02**

Generación Inteligente de Rutina Diaria

Como Usuario Senior,quiero que el sistema me asigne automáticamente una rutina de ejercicios adaptada a mis dolores,para ejercitarme en casa sin riesgo de caídas o lesiones severas.

CA2.1: El Agente Wellness Coach debe filtrar y omitir el 100% de los ejercicios contraindicados en un tiempo de procesamiento <2 segundos.CA2.2: Carga física limitada estrictamente a ejercicios de progresión segura (Nivel 1 o 2: sentados o asistidos).CA2.3: Multimedia servida vía streaming directo desde GCP Storage sin descargas locales.

**HU03**

Registro de Ejecución y Fatiga (RPE)

Como Adulto Mayor en entrenamiento,quiero registrar que terminé una serie y mi nivel de cansancio tocando controles grandes,para llevar control de mi esfuerzo sin complicarme con la tecnología.

CA3.1: Retroalimentación háptica (vibración 50ms) y sonora instantánea al pulsar "Serie Completada".CA3.2: Escala RPE (1 al 10) operada 100% de forma visual mediante emojis de tamaño masivo y códigos de color.CA3.3: Activación transparente de la caché NoSQL offline ante pérdidas de red con sincronización automática en <5 segundos.

**HU04**

Proyecciones Temporales de Logros

Como Usuario Constante,quiero ver estimaciones de cuándo mejoraré mi movilidad corporal,para mantenerme motivado con metas realistas de la vida diaria.

CA4.1: El Agente Preventivo / Analytics debe procesar en lote (batch) el historial acumulado cada 7 días continuos.CA4.2: Insights dinámicos redactados con lenguaje empático, humano y libre de tecnicismos obsesivos.CA4.3: Ocultamiento automático del componente predictivo si el volumen de datos históricos es menor a una semana.

**HU05**

Dashboard Visual de Progreso

Como Usuario Senior,quiero ver un panel visual limpio con los días entrenados y la tendencia de mi fatiga,para sentirme orgulloso de mi esfuerzo y poder exportarlo a mi médico.

CA5.1: Renderizado de calendario de asistencia con paleta cromática de alto contraste (Ratio 4.5:1).CA5.2: Exclusión absoluta de métricas obsesivas de peso corporal y prohibición de penalizaciones punitivas por "rachas rotas".CA5.3: Botón dedicado para compilar y exportar el historial a un reporte PDF portable.

**HU06**

Monitoreo Remoto por el Cuidador

Como Familiar o Cuidador,quiero revisar un resumen de la actividad de mi adulto mayor desde mi dispositivo móvil,para asegurar su bienestar a distancia sin invadir su privacidad.

CA6.1: Intercepción en backend y bloqueo de peticiones de escritura para cuentas con rol Cuidador (Read-Only).CA6.2: Consumo de datos cifrado de extremo a extremo vía TLS 1.3.CA6.3: Disparo automatizado de alerta proactiva push (FCM) si el adulto mayor acumula 4 días de inactividad consecutiva.

**HU07**

Gestión de Pacientes y Rutinas (Admin)

Como Fisioterapeuta / Administrador,quiero auditar a los usuarios con semáforos de riesgo y ajustar sus rutinas manualmente,para intervenir clínicamente si un paciente se estanca.

CA7.1: Consola web con despliegue de un Semáforo IA de Riesgo (Verde/Ámbar/Rojo) calculado por el backend.CA7.2: Habilitación de una función de anulación (override) manual sobre las sugerencias del Agente autónomo.CA7.3: Panel administrativo responsivo y compatible con las últimas versiones de navegadores web.

**HU08**

Gestión de Biblioteca de Ejercicios

Como Fisioterapeuta / Administrador,quiero cargar nuevos movimientos asociándolos a sus contraindicaciones médicas,para enriquecer el catálogo analizado por la IA.

CA8.1: El formulario web debe validar y restringir la creación de ejercicios a un máximo estricto de 4 niveles de progresión.CA8.2: Soporte de metadatos NoSQL para inyectar tags médicos dinámicos.CA8.3: Procesamiento automático y almacenamiento optimizado del archivo MP4 demostrativo en Google Cloud Storage.

**HU09**

Prevención Automática de Estancamiento

Como Usuario Senior,quiero que la app detecte si un ejercicio me cuesta mucho o no avanzo y me ofrezca variantes,para ejercitarme de forma segura sin frustración.

CA9.1: Escaneo en segundo plano por el Agente Preventivo para identificar mesetas de rendimiento o RPE crítico (dolor).CA9.2: Comunicación interna de inter-agente para sustituir el ejercicio estancado por un patrón biomecánico equivalente.CA9.3: Despliegue empático del cambio en la siguiente sesión sin interrumpir el flujo de entrenamiento del usuario.

**HU10**

Recordatorios Proactivos y Empáticos

Como Usuario Senior,quiero recibir alertas oportunas y amables sobre mi hidratación y entrenamiento,para sostener mis hábitos saludables sin sentirme presionado o regañado.

CA10.1: Despacho automatizado de notificaciones asíncronas vía Firebase Cloud Messaging (FCM).CA10.2: Validación obligatoria del tono de refuerzo positivo en la plantilla de mensajería generada por la IA.CA10.3: Integración de un switch accesible para activar el "Modo No Molestar" en tiempo real.

**HU11**

Registro Simplificado de Hábitos Diarios

Como Usuario Senior,quiero registrar mis vasos de agua y horas de sueño con controles simples de suma y resta,para prescindir de relojes inteligentes costosos y complejos.

CA11.1: Interfaz de hábitos operada al 100% mediante controles masivos de \[+\] y \[-\], eliminando el despliegue del teclado táctil.CA11.2: Estructuración de marcas de tiempo (timestamps) indexadas para correlación agéntica.CA11.3: Arquitectura NoSQL diseñada bajo el principio Fase 2 Ready para recibir APIs de wearables en el futuro.

# ESPECIFICACIÓN DE CASOS DE USO

A continuación, se documentan de forma exhaustiva los 11 Casos de Uso (CU01 al CU11) mapeados a partir de las especificaciones del MVP. Se utiliza estrictamente la estructura formal de la plantilla de la cátedra para garantizar el rigor de la ingeniería de software y la correcta trazabilidad con los requisitos del sistema.

## 1\. Diagrama Global de Casos de Uso

## ![]()El siguiente diagrama UML modela las fronteras del sistema del MVP de SeniorVital, ilustrando las interacciones directas entre los actores humanos (Adulto Mayor, Cuidador, Fisioterapeuta), los actores de Inteligencia Artificial (Agente Wellness Coach, Agente Preventivo) y los principales módulos de la plataforma.

## 5\. 2. Especificación Detallada de Casos de Uso

Toda la funcionalidad original se mantiene íntegra, pero ejecutable en un equipo local sin dependencia de la nube ni Docker.

## CU01: Registro y Onboarding con Perfil de Salud

**Elemento**

**Descripción**

**Nombre del Caso de Uso**

Registrar Usuario y Configurar Perfil de Salud Inicial

**Identificador (ID)**

CU01

**Actor Principal**

Usuario final (+60) o Familiar/Cuidador

**Actores Secundarios**

FastAPI Users + JWT, PostgreSQL

**Descripción**

Permite el registro seguro de una nueva cuenta y la estructuración del perfil médico inicial (tags de salud) mediante un onboarding interactivo.

**Precondiciones**

El dispositivo no debe poseer una sesión activa y debe ser la primera ejecución de la app.

**Postcondiciones**

El registro del usuario queda creado en PostgreSQL (columna JSONB), las credenciales quedan validadas con JWT y se redirige al Home de forma autenticada.

**Flujo Principal (Normal)**

1\. El usuario abre la aplicación y selecciona la opción de registro guiado.
2\. El sistema solicita credenciales de correo electrónico y contraseña gestionadas por FastAPI Users (JWT).
3\. El usuario avanza en un formulario secuencial interactivo limitado a máximo 5 preguntas.
4\. El sistema captura la edad, peso, altura y el nivel de condición física autopercibido.
5\. El usuario selecciona de una lista gerontológica sus restricciones médicas preexistentes (tags: hipertensión, osteoporosis, artrosis, etc.).
6\. El sistema compila las respuestas en un documento estructurado (JSON), lo almacena en la tabla users de PostgreSQL (campo health\_profile tipo JSONB) e inicia la sesión (Token JWT).

**Flujos Alternativos**

4a. Formato de datos antropométricos inválido: El sistema detecta un valor fuera de rango lógico (ej. peso negativo), despliega una alerta visual instantánea (< 500 ms) y bloquea el botón "Siguiente".
5a. Declaración de patología crítica: El usuario marca una restricción de alta peligrosidad (ej. prótesis de cadera reciente). El sistema guarda la etiqueta en PostgreSQL y despliega en pantalla un Disclaimer médico restrictivo exigiendo aceptación obligatoria antes de finalizar.

**Requisitos Especiales**

Cumplimiento estricto de usabilidad senior: fuentes ≥ 16pt, botones ≥ 44x44 pt y contraste cromático mínimo de 4.5:1.

**Puntos de Inicio/Fin**

Inicio: Interacción con el botón de registro en la bienvenida. Fin: Renderizado exitoso del Home con el perfil guardado.

**Frecuencia de Uso**

Única vez por cuenta de usuario registrada.

**Notas Adicionales**

Los tags médicos son campos obligatorios ya que constituyen los datos de entrada indispensables para que la IA actúe de manera segura.

## CU02: Generar Rutina Diaria Personalizada

**Elemento**

**Descripción**

**Nombre del Caso de Uso**

Generar Rutina Diaria Personalizada

**Identificador (ID)**

CU02

**Actor Principal**

Agente Wellness Coach (Ollama + lógica local)

**Actores Secundarios**

Usuario final (+60), PostgreSQL, MinIO

**Descripción**

El agente autónomo evalúa las condiciones de salud y restricciones del usuario para filtrar, seleccionar y renderizar una rutina física diaria de bajo impacto totalmente segura.

**Precondiciones**

El usuario debe estar autenticado y poseer un perfil médico completo en la base de datos (CU01).

**Postcondiciones**

La rutina personalizada del día se renderiza en la interfaz móvil en menos de 2 segundos.

**Flujo Principal (Normal)**

1\. El usuario inicia la aplicación o accede al módulo de entrenamiento diario.
2\. El sistema dispara una petición automática a la tabla users de PostgreSQL (columna JSONB del perfil).
3\. El Agente Wellness Coach (Ollama + script Python) analiza los tags médicos del usuario (ej. artrosis severa de rodilla).
4\. El Agente filtra e intercepta la biblioteca base (tabla exercises), descartando de forma automática el 100% de los ejercicios contraindicados.
5\. El Agente selecciona un set equilibrado de movimientos de progresión funcional segura (Nivel 1 o 2: ejercicios sentados o asistidos por silla).
6\. El sistema recupera las URLs de los videos demostrativos y audios alojados en MinIO (bucket videos-ejercicios).
7\. La rutina estructurada se despliega en la interfaz móvil en un lapso total inferior a 2 segundos.

**Flujos Alternativos**

1a. Reporte previo de dolor articular (Escala RPE inicial alta): Si el usuario declara dolor agudo antes de iniciar, el Agente Wellness Coach altera de forma autónoma la recomendación, eliminando patrones de fuerza y sustituyéndolos exclusivamente por estiramientos pasivos o movilidad articular en silla.

**Requisitos Especiales**

El procesamiento se realiza del lado del servidor (backend FastAPI) para no saturar el hardware del dispositivo móvil. Los videos se sirven por streaming (resolución optimizada 480p) desde MinIO.

**Extensiones**

CU03: Registrar Ejecución de Ejercicio (Opcional si el usuario entrena).

**Inclusiones**

CU01: (El Agente incluye la lectura obligatoria del perfil de salud).

**Puntos de Inicio/Fin**

Inicio: Carga automatizada del módulo de entrenamiento. Fin: Renderizado completo de la sesión multimedia en pantalla.

**Frecuencia de Uso**

Diario (Una o más veces al día si el usuario repite entrenamientos).

## CU03: Registrar Ejecución de Ejercicio y Esfuerzo Percibido (RPE)

**Elemento**

**Descripción**

**Nombre del Caso de Uso**

Registrar Ejecución de Ejercicio y Esfuerzo Percibido (RPE)

**Identificador (ID)**

CU03

**Actor Principal**

Usuario final (+60)

**Actores Secundarios**

PostgreSQL

**Descripción**

Permite capturar las series completadas por el usuario y su percepción del esfuerzo físico mediante la escala visual RPE al término de cada patrón de movimiento.

**Precondiciones**

Una rutina personalizada debe haber sido orquestada previamente (CU02) y estar activa en pantalla.

**Postcondiciones**

Los registros de rendimiento y fatiga quedan persistidos de forma atómica en PostgreSQL.

**Flujo Principal (Normal)**

1\. El usuario visualiza el ejercicio en ejecución en el dispositivo móvil.
2\. Al terminar la serie, el usuario pulsa el botón expandido "Serie Completada" (Tiempo de respuesta visual < 500 ms).
3\. El sistema activa un temporizador visual de descanso con alertas sonoras suaves.
4\. Al concluir las series del ejercicio, la app despliega la escala RPE (1 al 10) utilizando colores y emojis de gran tamaño.
5\. El usuario registra su fatiga (ej. selecciona Emoji Amarillo - Nivel 4: Esfuerzo Moderado) mediante un solo toque táctil.
6\. El sistema emite una confirmación multisensorial (vibración) y guarda el objeto de datos en la tabla workout\_sessions de PostgreSQL (formato JSONB).
7\. La interfaz avanza automáticamente al siguiente ejercicio de la rutina.

**Flujos Alternativos**

6a. Pérdida crítica de conectividad a Internet (Entorno Offline): El sistema detecta la caída de red de forma transparente. Activa la persistencia local en IndexedDB (caché del navegador) y guarda el progreso. Al detectar el restablecimiento de la conexión, sincroniza los datos con PostgreSQL en un lapso menor a 5 segundos sin fricción al usuario.

**Requisitos Especiales**

Operabilidad WCAG 2.1 AA (Botones ≥ 44x44 pt), feedback háptico (vibración 50ms) obligatorio.

**Puntos de Inicio/Fin**

Inicio: Marcado de la primera serie del ejercicio activo. Fin: Escritura atómica del registro en PostgreSQL y avance de pantalla.

**Frecuencia de Uso**

Múltiples veces por sesión de entrenamiento (tras cada ejercicio de la rutina).

## CU04: Generar Proyecciones Temporales de Logros

**Elemento**

**Descripción**

**Nombre del Caso de Uso**

Generar Proyecciones Temporales de Logros

**Identificador (ID)**

CU04

**Actor Principal**

Agente Preventivo / Analytics (DuckDB + Ollama)

**Actores Secundarios**

Usuario final (+60)

**Descripción**

La IA procesa en lotes nocturnos el historial acumulado para generar estimaciones predictivas y empáticas sobre la mejora de la movilidad futura del usuario.

**Precondiciones**

El usuario debe poseer una racha mínima de 7 días continuos de registros válidos en PostgreSQL (CU03).

**Postcondiciones**

Un insight predictivo personalizado en lenguaje natural queda disponible en el dashboard de progreso.

**Flujo Principal (Normal)**

1\. El sistema dispara un disparador de cronograma (cron job del sistema operativo o tarea programada) al finalizar la semana de entrenamiento.
2\. El Agente Preventivo ejecuta un análisis de tendencia lineal procesando el historial de series, repeticiones y la reducción de la escala RPE. Utiliza DuckDB para consultas analíticas embebidas sobre los datos de PostgreSQL.
3\. El Agente infiere el ritmo de ganancia de movilidad funcional para actividades de la vida diaria.
4\. El Agente genera un mensaje personalizado y empático utilizando el modelo local de Ollama (llama3.2:3b o phi3:mini).
5\. El sistema inyecta el texto generado en el dashboard de progreso del usuario (almacenado en PostgreSQL).

**Flujos Alternativos**

2a. Volumen de datos históricos insuficientes (< 7 días): El Agente detecta la escasez de datos. Aborta de forma segura la proyección lineal, oculta la sección predictiva del dashboard y genera un mensaje enfocado exclusivamente en el refuerzo positivo inicial.

**Requisitos Especiales**

Redacción predictiva libre de tecnicismos médicos alarmantes o jerga obsesiva de control de peso.

**Inclusiones**

CU03: (Requiere la existencia de registros históricos previos).

**Puntos de Inicio/Fin**

Inicio: Disparo automatizado del procesamiento batch nocturno. Fin: Escritura del insight dinámico en el panel del usuario (tabla user\_insights).

**Frecuencia de Uso**

Semanal (Ejecución automatizada en segundo plano).

## CU05: Dashboard de Progreso Visual

Elemento

Descripción

**Nombre del Caso de Uso**

Visualizar Dashboard de Progreso Funcional

**Identificador (ID)**

CU05

**Actor Principal**

Usuario final (+60)

**Actores Secundarios**

PostgreSQL

**Descripción**

Renderiza un panel de control gráfico de alto contraste que ilustra la constancia, la asistencia y la reducción progresiva de la fatiga física del adulto mayor.

**Precondiciones**

Deben existir registros históricos vinculados a la cuenta (CU03).

**Postcondiciones**

Las métricas funcionales son expuestas bajo principios estrictos de usabilidad gerontológica.

**Flujo Principal (Normal)**

1\. El usuario pulsa la pestaña "Mi Progreso" desde la barra de navegación principal.
2\. El sistema realiza una consulta indexada a PostgreSQL para extraer las sesiones del mes actual (tabla workout\_sessions).
3\. La interfaz renderiza un calendario de asistencia simplificado codificado por colores de alta visibilidad.
4\. El sistema dibuja una gráfica de tendencia limpia que demuestra cómo el nivel RPE ha disminuido para el mismo patrón de movimiento.
5\. Se expone de forma destacada el mensaje de proyección empática generado por la IA (CU04).
6\. El usuario pulsa el botón de exportación; el sistema compila los datos (usando DuckDB para agregaciones) y descarga un reporte en PDF.

**Flujos Alternativos**

3a. Cero registros históricos detectados: El sistema oculta los contenedores gráficos vacíos y renderiza una pantalla de bienvenida limpia con un mensaje motivador y un acceso directo para iniciar la primera rutina.

**Requisitos Especiales**

Paleta de colores validada para daltonismo senil (Ratio 4.5:1). Prohibición de leyendas con tipografía inferior a 12pt o saturación de datos.

**Puntos de Inicio/Fin**

Inicio: Selección de la pestaña de progreso por el usuario. Fin: Renderizado completo del panel y/o descarga exitosa del PDF.

**Frecuencia de Uso**

Frecuente (A demanda del usuario).

**Notas Adicionales**

Exclusión absoluta de métricas obsesivas de peso corporal.

## CU06: Modo Cuidador/Familiar

**Elemento**

**Descripción**

**Nombre del Caso de Uso**

Supervisar Progreso de Adulto Mayor (Modo Cuidador)

**Identificador (ID)**

CU06

**Actor Principal**

Familiar / Cuidador

**Actores Secundarios**

🤖 Agente Preventivo / Analytics, PostgreSQL, FastAPI Users + JWT

**Descripción**

Permite a un familiar autorizado vincularse a la cuenta del adulto mayor para monitorear sus indicadores de constancia en una vista espejo segura de solo lectura con alertas automatizadas.

**Precondiciones**

El cuidador debe estar autenticado. Debe existir un enlace de autorización previo aceptado por el adulto mayor.

**Postcondiciones**

El cuidador accede al estado de bienestar sin capacidad de alterar la integridad clínica de la base de datos.

**Flujo Principal (Normal)**

1\. El cuidador inicia sesión en la app o consola web. FastAPI Users valida credenciales y token JWT con rol de "cuidador".
2\. El backend verifica las reglas de acceso en PostgreSQL, validando privilegios estrictos de Solo Lectura (Read-Only).
3\. El sistema renderiza una vista espejo simplificada del dashboard del adulto mayor (CU05).
4\. El sistema expone las banderas de alerta preventiva generadas en segundo plano por los agentes de IA.
5\. El cuidador cierra el módulo de supervisión de manera segura.

**Flujos Alternativos**

3a. Intento malicioso de alteración de datos: El cuidador intenta forzar una mutación de datos (ej. vía API). El backend intercepta la transacción (violación RBAC), aborta la operación y registra un log de auditoría en PostgreSQL.
4a. Activación de Alerta por Inactividad: El Agente Preventivo detecta 4 días sin actividad. El sistema genera de forma automática una notificación push (Web Push API) al navegador/móvil del cuidador.

**Requisitos Especiales**

Transmisión protegida bajo cifrado TLS 1.3 de extremo a extremo (ISO 25010).

**Puntos de Inicio/Fin**

Inicio: Acceso al perfil del adulto mayor desde el panel del cuidador. Fin: Cierre seguro de la sesión de monitoreo.

**Frecuencia de Uso**

Periódico / Diario.

## CU07: Panel Web de Gestión y Supervisión Clínica (Admin)

**Elemento**

**Descripción**

**Nombre del Caso de Uso**

Gestionar Usuarios y Supervisar Rutinas Terapéuticas

**Identificador (ID)**

CU07

**Actor Principal**

Administrador / Fisioterapeuta

**Actores Secundarios**

PostgreSQL

**Descripción**

Consola web administrativa que expone la población total de adultos mayores mediante un semáforo de riesgo clínico, permitiendo la anulación manual de rutinas asignadas por la IA.

**Precondiciones**

El actor debe estar autenticado con rol exclusivo de "Admin / Clínico" en la plataforma web (FastAPI Users).

**Postcondiciones**

Los ajustes manuales (overrides) del fisioterapeuta quedan inyectados con prioridad jerárquica en el perfil del paciente.

**Flujo Principal (Normal)**

1\. El fisioterapeuta inicia sesión en el panel web administrativo.
2\. El sistema renderiza una tabla de pacientes controlada por un Semáforo IA de Riesgo (Rojo/Ámbar/Verde) calculado a partir de datos en PostgreSQL.
3\. El especialista selecciona un usuario en estado "Rojo" y audita su historial clínico, hábitos y escala RPE.
4\. El fisioterapeuta activa la opción de Anulación Manual (Override) sobre el Agente Wellness Coach.
5\. Modifica las series, repeticiones o descarta ejercicios específicos usando selectores web.
6\. El sistema actualiza el campo JSONB del usuario en PostgreSQL (ej. custom\_routine\_override). El cambio se refleja instantáneamente en el móvil del adulto mayor.

**Flujos Alternativos**

2a. Exportación de Datos de Gestión: El administrador presiona "Exportar Analíticas". El sistema compila las métricas agregadas (usando DuckDB) y descarga un archivo CSV.

**Requisitos Especiales**

Interfaz web responsive compatible con navegadores de escritorio (Chrome, Safari, Edge) bajo directiva de portabilidad ISO 25010.

**Puntos de Inicio/Fin**

Inicio: Autenticación en consola web. Fin: Persistencia del cambio manual de rutina en PostgreSQL.

**Frecuencia de Uso**

Semanal / Periódico.

## CU08: Mantenimiento de Biblioteca de Ejercicios y Restricciones

**Elemento**

**Descripción**

**Nombre del Caso de Uso**

Gestionar Biblioteca de Ejercicios Seguros

**Identificador (ID)**

CU08

**Actor Principal**

Administrador / Fisioterapeuta

**Actores Secundarios**

PostgreSQL, MinIO

**Descripción**

Módulo técnico para cargar nuevos ejercicios al sistema, acotando su dificultad y asociándolos a tags de contraindicación médica que leerá la IA.

**Precondiciones**

Sesión de Administrador activa en el panel web.

**Postcondiciones**

El nuevo ejercicio queda indexado en la base de datos PostgreSQL y su video disponible en MinIO.

**Flujo Principal (Normal)**

1\. El administrador navega al módulo "Biblioteca de Ejercicios Funcionales".
2\. Selecciona "Añadir Nuevo Ejercicio" e introduce título, descripción y patrón biomecánico.
3\. El sistema exige parametrizar la dificultad dentro de un límite de máximo 4 niveles de progresión (almacenados como JSON en columna progression\_levels).
4\. El administrador vincula los Tags de Prohibición Médica (ej. contraindicado para osteoporosis) – array de strings en JSONB.
5\. El sistema procesa y carga el video demostrativo (.mp4 optimizado) en MinIO (bucket videos-ejercicios).
6\. El sistema guarda el registro del ejercicio en la tabla exercises de PostgreSQL para que sea consumido por la IA.

**Flujos Alternativos**

3a. Intento de añadir Nivel 5 de dificultad: El validador detecta que viola la regla de negocio del MVP (+60 bajo impacto). Bloquea el envío de datos y resalta el error en pantalla.

**Requisitos Especiales**

Uso del esquema JSONB de PostgreSQL para inyectar tags médicos dinámicamente sin necesidad de migraciones estructurales.

**Puntos de Inicio/Fin**

Inicio: Selección de añadir ejercicio. Fin: Indexación exitosa en PostgreSQL y almacenamiento en MinIO.

**Frecuencia de Uso**

Ocasional.

## CU09: Detección Automatizada de Estancamiento y Ajuste Pasivo

**Elemento**

**Descripción**

**Nombre del Caso de Uso**

Detectar Estancamiento y Ajustar Rutina Automáticamente

**Identificador (ID)**

CU09

**Actor Principal**

🤖 Agente Preventivo / Analytics (DuckDB + Redis Streams)

**Actores Secundarios**

🤖 Agente Wellness Coach (Ollama), PostgreSQL

**Descripción**

Orquestación en segundo plano inter-agente que detecta mesetas de rendimiento o picos de fatiga/dolor y reestructura de forma pasiva la rutina diaria del usuario.

**Precondiciones**

El usuario debe registrar actividad de entrenamiento continua (CU03) durante al menos 14 días.

**Postcondiciones**

La rutina del usuario es modificada de manera transparente por la IA sin intervención manual.

**Flujo Principal (Normal)**

1\. El Agente Preventivo ejecuta un análisis histórico periódico (vía cron job) sobre los datos de PostgreSQL usando DuckDB para consultas analíticas.
2\. El Agente detecta un patrón de estancamiento (ej. 14 días estancado en repeticiones o nivel RPE crítico).
3\. El Agente Preventivo despacha una instrucción interna a través de Redis Streams (canal agent\_coach\_commands) al Agente Wellness Coach indicando la necesidad de una variante.
4\. El Agente Wellness Coach evalúa los tags médicos (almacenados en JSONB) y sustituye el ejercicio estancado por un patrón motor alternativo equivalente de diferente impacto articular. Utiliza Ollama para generar la sugerencia.
5\. El sistema actualiza la cola de rutinas del usuario en PostgreSQL (campo current\_routine) y genera una alerta empática para la siguiente sesión.

**Requisitos Especiales**

Orquestación asíncrona desacoplada mediante Redis Streams (ligero y sin necesidad de brokers externos).

**Puntos de Inicio/Fin**

Inicio: Disparo automático del script analítico. Fin: Actualización del campo JSONB de rutina con la variante.

**Frecuencia de Uso**

Automático y periódico (Ciclos de control del backend cada 24h).

## CU10: Recordatorios Proactivos y Empáticos

**Elemento**

**Descripción**

**Nombre del Caso de Uso**

Enviar Alertas y Recordatorios Preventivos

**Identificador (ID)**

CU10

**Actor Principal**

🤖 Agente Preventivo

**Actores Secundarios**

Web Push API (o desactivado en MVP)

**Descripción**

Genera y despacha notificaciones push contextuales y personalizadas dirigidas al navegador/móvil del adulto mayor para reforzar hábitos (hidratación, descanso, actividad física).

**Precondiciones**

El navegador/dispositivo debe haber otorgado permiso para notificaciones push (Web Push API). El token de suscripción se almacena en PostgreSQL.

**Postcondiciones**

La notificación push es entregada de forma asíncrona en el dispositivo respetando el Modo No Molestar del navegador.

**Flujo Principal (Normal)**

1\. El Agente Preventivo evalúa la ventana de tiempo óptima del usuario configurada en su perfil (PostgreSQL) o detecta horas excesivas de inactividad.
2\. El Agente redacta dinámicamente el mensaje utilizando un prompt con restricción estricta de Refuerzo Positivo (puede usar Ollama o plantillas predefinidas).
3\. El sistema dispara la notificación mediante Web Push API (usando web-push library en el backend).
4\. El navegador del adulto mayor recibe y renderiza la notificación push con tipografía clara.

**Flujos Alternativos**

1a. Módulo "Modo No Molestar" activo: El sistema detecta el switch de bloqueo activado (almacenado en perfil). El Agente Preventivo suprime automáticamente la generación del mensaje y lo pospone.
1b. MVP sin notificaciones: Si se decide desactivar, el Agente simplemente registra el intento en logs y no envía nada.

**Requisitos Especiales**

Prohibición absoluta de redactar alertas punitivas o de culpabilidad (ej. "Perdiste tu racha"), protegiendo la salud psicológica del senior.

**Puntos de Inicio/Fin**

Inicio: Cumplimiento del disparador de tiempo en el servidor. Fin: Entrega exitosa del push message en el terminal del cliente (o log si desactivado).

**Frecuencia de Uso**

Diario / Periódico.

## CU11: Registro Simplificado de Hábitos Diarios (Mecánica MVP)

**Elemento**

**Descripción**

**Nombre del Caso de Uso**

Registrar Hábitos Complementarios (Manual MVP)

**Identificador (ID)**

CU11

**Actor Principal**

Usuario final (+60)

**Actores Secundarios**

PostgreSQL

**Descripción**

Permite al usuario registrar de forma manual variables clave de bienestar (vasos de agua, horas de sueño) empleando una interfaz simplificada libre de mecanografía, supliendo la ausencia de wearables en la Fase 1.

**Precondiciones**

El usuario debe estar autenticado y posicionado en la pantalla de hábitos.

**Postcondiciones**

Los datos de estilo de vida quedan indexados con timestamps en PostgreSQL para ser analizados por la IA (CU09).

**Flujo Principal (Normal)**

1\. El usuario accede al panel complementario "Mis Hábitos Diarios".
2\. El sistema renderiza tarjetas masivas independientes para Agua y Sueño, exponiendo botones gigantes de \[+\] y \[-\].
3\. El usuario pulsa repetidamente el control gigante de \[+\] para registrar cantidades (ej. 4 vasos de agua).
4\. El sistema actualiza el contador visual de forma instantánea (< 500 ms) emitiendo confirmación sonora suave.
5\. Los datos transaccionales se persisten de forma inmediata en PostgreSQL (tabla daily\_habits con campos water\_intake, sleep\_hours, timestamp) mediante una llamada API REST.

**Flujos Alternativos**

N/A (Se aplican las directivas de control Offline-First detalladas en el CU03 si falla la red: almacenamiento en IndexedDB y sincronización posterior).

**Requisitos Especiales**

Exclusión absoluta de teclados virtuales o campos de texto libre. Estructura de tabla diseñada bajo el principio Fase 2 Ready (compatible con futuras APIs de wearables, con campos adicionales JSONB para extensibilidad).

**Puntos de Inicio/Fin**

Inicio: Selección del panel de hábitos. Fin: Persistencia exitosa del dato numérico indexado en PostgreSQL.

**Frecuencia de Uso**

Diario (A demanda del usuario).

# EVALUACIÓN DE CALIDAD DEL SOFTWARE Y METODOLOGÍA MODERNIZADA

Se ha diseñado una estrategia de evaluación proactiva y continua de la calidad del software, alineando conceptualmente el modelado y la construcción del sistema con estándares internacionales vigentes y prácticas avanzadas de desarrollo asistido por Inteligencia Artificial.

## 6\. 1. Alineación con SWEBOK V4, ISO/IEC 25010 y Buenas Prácticas

El ciclo de vida de este proyecto se rige estrictamente por el cuerpo de conocimiento consolidado en la _Guide to the Software Engineering Body of Knowledge_ (SWEBOK V4.0). Los artefactos y decisiones metodológicas de este sprint se concentran con rigurosidad en las áreas fundamentales de **Software Requirements** (Ingeniería de Requisitos) y **Software Design** (Diseño de la Arquitectura), absteniéndose de fases de codificación prematuras para mitigar el crecimiento caótico de necesidades no controladas.

Para auditar y garantizar la madurez estructural del Mínimo Producto Viable (MVP), se adopta la norma estándar **ISO/IEC 25010** evaluando de manera transversal sus características clave. Para un sistema agéntico inteligente, se han inyectado métricas de validación técnica innegociables en los frentes de mayor criticidad:

*   **Mantenibilidad:** Evaluada formalmente a través de la modularidad del código (microservicios _decoupled_), la implementación de un esquema flexible NoSQL que permite la inyección dinámica de variables y la generación automática de la infraestructura documental (_Living Documentation_).
*   **Seguridad y Confidencialidad:** Verificada mediante la configuración de un Control de Acceso Basado en Roles (RBAC) inquebrantable a nivel de backend, esquemas de solo lectura para mitigar riesgos clínicos e inyección de cifrado avanzado bajo normativas estándar de protección de datos de salud (HIPAA).
*   **Eficiencia de Desempeño y Escalabilidad:** Abordada mediante el despliegue nativo sobre una infraestructura _Cloud-Native_ que permite el escalado elástico horizontal automático con reducciones operativas a cero.

## 6\. 2. Modelado Moderno (AI-Augmented Development y Documentación Viva)

En cumplimiento con las pautas de ingeniería moderna, el proyecto rompe con el paradigma de los manuales estáticos, adoptando la filosofía de **Documentación Viva** (_Living Documentation_). Este enfoque garantiza la veracidad del sistema al sincronizar automáticamente el diseño funcional con la evolución del repositorio:

*   **Architecture-as-Code (Mermaid.js):** Todos los diagramas de modelado (casos de uso, interacciones y arquitectura global) se estructuran directamente utilizando texto declarativo basado en código Mermaid. Esto permite el control de versiones (Git), auditorías semánticas eficientes y la renderización en tiempo real en la plataforma.
*   **Markdown as-Code:** La totalidad de las especificaciones funcionales, especificaciones de atributos de calidad, historias de usuario y matrices de trazabilidad se documentan nativamente en formato Markdown (.md), conviviendo directamente en la rama raíz junto al código fuente del _backend_.

## 6\. 3. Metodología de Gestión y Definición de Hecho (DoD)

El desarrollo ágil se administra mediante marcos de trabajo ágiles adaptados para **AI-Augmented Development** operando en sprints técnicos acotados. El _Product Backlog_ priorizado se compone de 11 Historias de Usuario optimizadas gerontológicamente para ejecutarse en el MVP de 4 semanas.

Para garantizar que un incremento o ítem cumpla con las condiciones operativas de producción, se establece una rigurosa **Definición de Hecho (DoD / Definition of Done)** compuesta por los siguientes criterios:

*   **Cumplimiento Verificable:** Satisfecho al 100% el comportamiento de los Criterios de Aceptación especificados bajo el formato formal "Dado-Cuando-Entonces".
*   **Calidad de Código y Pruebas:** Ejecución exitosa de análisis estático de código y cobertura mínima aprobada mediante _tests_ unitarios.
*   **Documentación Sincronizada:** Actualización obligatoria del diccionario de datos en los archivos Markdown del repositorio y mantenimiento de los diagramas Mermaid involucrados.
*   **Revisión por Pares (Peer Review):** Aprobación mandatoria del código y fusiones de ramas mediante un revisor secundario del equipo de arquitectura.

# DISEÑO DE LA ARQUITECTURA DEL SISTEMA Y AGENTES DE IA

El diseño arquitectónico de SeniorVital responde a los principios de sistemas modernos distribuidos, escalables, tolerantes a fallos y orientados de manera nativa a la inteligencia artificial de propósito específico (_AI-First_).

## 7\. 1. Descripción del Ecosistema de Infraestructura (GCP AI-First)

La plataforma se orquesta bajo un enfoque desacoplado, independiente y modular, utilizando los servicios administrados de **Google Cloud Platform (GCP)** y **Firebase** para mitigar la carga operativa y asegurar altos niveles de eficiencia:

*   **Firebase Authentication:** Actúa como el punto de control de seguridad perimetral. Centraliza el registro inicial y la autenticación (CU01), inyectando los _Custom Claims_ en tokens JWT firmados para validar los roles de los perfiles en el backend.
*   **Google Cloud Run:** Hospeda los microservicios encapsulados del sistema en contenedores elásticos de escalado automático a cero (_Serverless_), aislando por completo la ejecución lógica de la plataforma.
*   **Cloud Firestore NoSQL:** Motor de base de datos de documentos JSON flexible. Es la base que garantiza la continuidad transaccional a través de su persistencia local nativa (**Arquitectura Offline-First**), permitiendo inyectar etiquetas médicas dinámicas sin recurrir a costosas migraciones de esquemas relacionales tradicionales.
*   **Google Cloud Storage:** B buckets distribuidos encargados de servir la multimedia demostrativa de ejercicios de bajo impacto a resoluciones optimizadas, consumidas mediante _streaming_ asíncrono directo para no saturar el almacenamiento de los terminales móviles.
*   **Firebase Cloud Messaging (FCM):** Canal asíncrono encargado de despachar notificaciones _push_ proactivas personalizadas hacia los clientes a partir de los triggers de inactividad o hidratación.

## 7\. 2. Agentes de IA Autónomos y Modelo MCP-Ready

En lugar de un monolito conceptual rígido, SeniorVital delega el análisis clínico y motivacional a un ecosistema de **Agentes de IA Autónomos** especializados, impulsados por modelos de lenguaje ligeros optimizados por token (Gemini en Vertex AI):

*   **Agente Wellness Coach:** Núcleo de razonamiento clínico en tiempo real. Analiza los _tags_ médicos restrictivos del perfil y el esfuerzo autopercibido para filtrar, omitir y reestructurar de manera proactiva las cargas físicas diarias de forma segura (CU02).
*   **Agente Preventivo / Analytics:** Entidad en segundo plano encargada del análisis predictivo. Procesa historiales en lotes (_batch processing_), infiere tendencias lineales de mejora funcional y dispara alertas tempranas push para mitigar el abandono (CU04, CU10).
*   **Agente de Nutrición e Hidratación (Fase 2 Comercial):** Encargado de correlacionar variables biológicas manuales para recomendar pautas alimenticias complementarias de bajo impacto metabólico.
*   **Agente de Motivación Empática (Fase 2 Comercial):** Entidad lingüística dedicada a adaptar la voz guía y las interfaces conversacionales del adulto mayor en función de su estado anímico y constancia histórica.
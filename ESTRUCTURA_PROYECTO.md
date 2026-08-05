# Estructura del Proyecto SeniorVital

> **Propósito:** Documento de referencia técnica para desarrolladores. Describe cada carpeta y archivo del proyecto, su responsabilidad, cómo se integra y con qué otros componentes se conecta.
>
> **Última actualización:** Junio 2026

---

## 1. Carpetas

### Raíz del proyecto (`E:\SeniorVital\`)

Contiene los artefactos de configuración global, orquestación y documentación. Alberga los 7 microservicios, el frontend, la librería compartida, los scripts de infraestructura, los tests, el almacenamiento de archivos y el entorno virtual Python (`venv/`, excluido del detalle).

---

### `auth-profile-service/`

**Funcionalidad:** Microservicio de autenticación y perfiles de usuario. Gestiona el registro, inicio de sesión, roles (senior, caregiver, admin), vinculación de cuidadores con seniors (máximo 3 por senior) y el perfil de salud.

**Uso y aplicabilidad:** Servicio independiente que expone API REST en el puerto `8001`. Se comunica directamente con PostgreSQL para persistencia de usuarios y perfiles. Es el punto de entrada de autenticación: emite tokens JWT firmados con bcrypt que el gateway valida en rutas protegidas. No tiene comunicación directa con el frontend; todo el tráfico pasa por el API Gateway (puerto `8000`).

**Archivos:**
```
auth-profile-service/
├── main.py
└── requirements.txt
```

---

### `catalog-service/`

**Funcionalidad:** Catálogo de ejercicios y gestión de vídeos. CRUD completo de ejercicios, cada uno con nombre, descripción, duración, URL de miniatura y vídeo almacenado localmente.

**Uso y aplicabilidad:** Microservicio REST en el puerto `8002`. Persiste en PostgreSQL y sirve archivos de vídeo desde `storage/videos/` mediante `FileResponse` de Starlette. Es la fuente de datos para la página de vídeos del frontend.

**Archivos:**
```
catalog-service/
├── main.py
└── requirements.txt
```

---

### `routines-ai-service/`

**Funcionalidad:** Generación de rutinas de bienestar personalizadas mediante IA local (Ollama + modelo phi3:mini). Expone endpoints para generar una rutina diaria y consultar la rutina del día actual.

**Uso y aplicabilidad:** Microservicio REST en el puerto `8003`. Se conecta a Ollama (`localhost:11434`) vía HTTP y persiste las rutinas generadas en PostgreSQL. Las rutinas se almacenan como documentos JSON con actividades (título, hora, descripción, duración). Timeout de 180s configurado para cold start del modelo.

**Archivos:**
```
routines-ai-service/
├── main.py
└── requirements.txt
```

---

### `tracking-service/`

**Funcionalidad:** Registro de sesiones de ejercicio completadas por los usuarios. Publica eventos asíncronos en la tabla `event_queue` de PostgreSQL cuando se completa un ejercicio. Detecta fatiga alta (RPE ≥ 8) y emite eventos `fatiga-alta`.

**Uso y aplicabilidad:** Microservicio REST en el puerto `8004`. Es la fuente de datos para el dashboard de progreso y para los workers de análisis. No expone consultas de lectura; solo escritura. Los consumidores leen los eventos desde `event_queue`.

**Archivos:**
```
tracking-service/
├── main.py
└── requirements.txt
```

---

### `dashboard-service/`

**Funcionalidad:** Consultas de progreso y analíticas para los seniors. Expone endpoints de progreso semanal (repeticiones, RPE promedio, racha de días consecutivos), proyecciones de salud y recomendaciones basadas en datos históricos.

**Uso y aplicabilidad:** Microservicio REST en el puerto `8005`. Es de solo lectura: consulta las tablas `tracking`, `health_profiles` y `users` en PostgreSQL. Es la capa de datos que alimenta la página de progreso del frontend.

**Archivos:**
```
dashboard-service/
├── main.py
└── requirements.txt
```

---

### `notification-service/`

**Funcionalidad:** Gestión de suscripciones a Web Push y envío de notificaciones push a los navegadores de los usuarios. Implementa el protocolo Web Push (VAPID) usando la librería `pywebpush`.

**Uso y aplicabilidad:** Microservicio REST en el puerto `8006`. Almacena suscripciones en la tabla `push_subscriptions` de PostgreSQL. Permite sobrescribir suscripciones existentes por usuario. Es invocado por otros servicios o workers cuando necesitan notificar a un usuario.

**Archivos:**
```
notification-service/
├── main.py
└── requirements.txt
```

---

### `gateway/`

**Funcionalidad:** API Gateway / proxy inverso. Unifica todos los microservicios bajo un mismo puerto (`8000`), sirve el frontend compilado en producción y expone la documentación interactiva de FastAPI. Implementa SPA catch-all para React Router.

**Uso y aplicabilidad:** Punto de entrada único para el frontend. Enruta peticiones según el prefijo de la ruta:
- `/auth/*` → auth-profile-service (`:8001`)
- `/catalog/*` → catalog-service (`:8002`)
- `/routines/*` → routines-ai-service (`:8003`)
- `/tracking/*` → tracking-service (`:8004`)
- `/dashboard/*` → dashboard-service (`:8005`)
- `/notify/*` → notification-service (`:8006`)
- `/storage/*` → archivos estáticos locales
- Cualquier otra ruta → frontend SPA (React Router)

En desarrollo, el Vite dev server usa proxy hacia el gateway. En producción, el gateway compila y sirve los assets estáticos del frontend (`frontend/dist/`).

**Archivos:**
```
gateway/
├── main.py
└── requirements.txt
```

---

### `frontend/`

**Funcionalidad:** Aplicación web React 18 con Vite 4, Tailwind CSS 3 (tema Material Design 3) y React Router 6. Consta de 7 páginas, 4 componentes compartidos, 6 servicios de API y un contexto de autenticación.

**Uso y aplicabilidad:** Interfaz de usuario completa para seniors, cuidadores y administradores. Se comunica exclusivamente con el API Gateway en el puerto `8000` (sin llamadas directas a microservicios). En desarrollo usa el proxy de Vite; en producción el gateway sirve los archivos compilados.

**Estructura interna:**

```
frontend/
├── dist/                              # Build de producción (compilado)
│   ├── index.html
│   └── assets/
│       ├── index-<hash>.js
│       └── index-<hash>.css
│
├── src/
│   ├── App.jsx                        # Router principal con AuthProvider
│   ├── main.jsx                       # Punto de entrada ReactDOM
│   ├── index.css                      # Estilos globales Tailwind
│   │
│   ├── components/
│   │   ├── AdminSidebar.jsx           # Barra lateral del panel admin
│   │   ├── BottomNavBar.jsx           # Barra de navegación inferior (móvil)
│   │   ├── ProtectedRoute.jsx         # Guardia de ruta (redirige a /login si no hay sesión)
│   │   └── TopAppBar.jsx              # Barra superior con título y botón de retroceso
│   │
│   ├── contexts/
│   │   └── AuthContext.jsx            # Estado global de autenticación
│   │
│   ├── pages/
│   │   ├── AdminDashboard.jsx         # Panel de administración clínica
│   │   ├── Habits.jsx                 # Seguimiento de hábitos diarios
│   │   ├── Home.jsx                   # Página principal con generación de rutina IA
│   │   ├── Login.jsx                  # Inicio de sesión
│   │   ├── Progress.jsx               # Calendario de progreso mensual
│   │   ├── Register.jsx               # Registro de nuevo usuario
│   │   └── Video.jsx                  # Reproductor de vídeos de ejercicios
│   │
│   └── services/
│       ├── api.js                     # Cliente HTTP base con inyección de JWT
│       ├── auth.js                    # Servicio de autenticación
│       ├── catalog.js                 # Servicio de catálogo de ejercicios
│       ├── dashboard.js               # Servicio de dashboard y progreso
│       ├── routines.js                # Servicio de rutinas IA
│       └── tracking.js                # Servicio de tracking de ejercicios
│
├── package.json
├── package-lock.json
├── postcss.config.js
├── tailwind.config.js
└── vite.config.js
```

---

### `seniorvital_shared/`

**Funcionalidad:** Biblioteca compartida entre todos los microservicios y scripts. Centraliza el pool de conexiones a PostgreSQL, los modelos Pydantic de datos compartidos y los tipos de eventos del sistema.

**Uso y aplicabilidad:** Paquete Python importable por cualquier servicio mediante `from seniorvital_shared import ...`. Es la única dependencia común a todos los microservicios. Instalado en el `venv` mediante `pip install -e .` o incluyendo la ruta en `PYTHONPATH`.

**Archivos:**
```
seniorvital_shared/
├── __init__.py          # Exporta get_pool, init_pool, close_pool + modelos y eventos
├── db.py                # Pool de conexiones PostgreSQL con sistema de owners
├── events.py            # Definiciones de streams de eventos
└── models.py            # Modelos Pydantic v2 compartidos (HealthProfile, etc.)
```

---

### `scripts/`

**Funcionalidad:** Automatización del ciclo de vida del sistema. Incluye workers asíncronos (consumidores de `event_queue`), scripts de arranque/parada, migraciones SQL y utilidades de verificación.

**Uso y aplicabilidad:** Los scripts de arranque (`start_all.ps1`, `start_all.sh`) orquestan el inicio de todos los microservicios y workers. Los workers (`replicator.py`, `preventive_worker.py`, `weekly_analysis.py`, `daily_inactivity.py`) son procesos independientes que escuchan eventos en `event_queue` y ejecutan lógica de negocio asíncrona. Las migraciones SQL se ejecutan una sola vez contra PostgreSQL.

**Archivos:**
```
scripts/
├── daily_inactivity.py        # Worker: detecta inactividad > 24h y emite alertas
├── migrations.sql             # Migraciones de esquema PostgreSQL
├── preventive_worker.py       # Worker: reacciona a eventos fatiga-alta
├── quick_check.py             # Verificación rápida de integración frontend-backend
├── replicator.py              # Worker: replica eventos PostgreSQL → DuckDB (analytics)
├── smoke_test.py              # Smoke test automatizado de todos los endpoints
├── start_all.ps1              # Orquestador de inicio (PowerShell Windows)
├── start_all.sh               # Orquestador de inicio (Bash Linux/Mac)
├── stop_all.ps1               # Orquestador de parada (PowerShell Windows)
├── stop_all.sh                # Orquestador de parada (Bash Linux/Mac)
├── verify_integration.py      # Verificación completa de integración
└── weekly_analysis.py         # Worker: análisis semanal con IA (Ollama)
```

---

### `tests/`

**Funcionalidad:** Suite de tests unitarios y de integración basada en pytest. Cubre todos los criterios de aceptación documentados en los requisitos funcionales.

**Uso y aplicabilidad:** Se ejecuta con `pytest tests/ -v` desde la raíz. Usa `conftest.py` para configurar un pool de conexiones compartido con las fixtures de test. Crea y limpia datos de prueba en PostgreSQL, simulando servicios externos (Ollama) mediante monkeypatch.

**Archivos:**
```
tests/
├── __init__.py
├── conftest.py                    # Fixtures globales: clientes de prueba, seed de usuarios
├── get_pg_credential.py           # Utilidad de obtención de credenciales PostgreSQL
├── get_pg_credential2.py          # (alternativa)
├── get_pgpass.py                  # Lectura de pgpass.conf
├── get_windows_credential.py      # Lectura de Credential Manager de Windows
├── test_auth.py                   # 5 tests: registro, roles, vinculación cuidadores
├── test_catalog.py                # 6 tests: CRUD ejercicios + subida/servicio vídeo
├── test_dashboard.py              # 3 tests: progreso, proyecciones, insights
├── test_db_conn.py                # Test de conectividad a PostgreSQL
├── test_notification.py           # 3 tests: suscripción push, sobrescritura, envío
├── test_persistence.py            # 4 tests: perfil salud, vinculación, event_queue
├── test_routines.py               # 3 tests: generación, consulta, idempotencia
└── test_tracking.py               # 3 tests: registro, fatiga alta, batch
```

---

### `storage/`

**Funcionalidad:** Almacenamiento local de archivos multimedia subidos por los usuarios y el sistema.

**Uso y aplicabilidad:** Montgomery directorio de almacenamiento montado por el sistema de archivos. El catálogo de ejercicios almacena aquí los vídeos subidos. Las fotos de progreso se almacenan en `progress-photos/` (pendiente de implementación). Los archivos se sirven a través del gateway o directamente por el catalog-service.

**Archivos:**
```
storage/
├── progress-photos/        # (vacío) - Fotos de progreso de seniors
└── videos/
    ├── <uuid>.mp4          # 14 archivos de vídeo de ejercicios
    └── ...                 # Identificados por UUID, referenciados desde catalog-service
```

---

### `logs/`

**Funcionalidad:** Almacena los archivos de log y PID de cada microservicio para monitorización y gestión del ciclo de vida.

**Uso y aplicabilidad:** Cada servicio escribe su salida estándar en un archivo `<nombre>.log`. Los scripts de parada leen los archivos `<nombre>.pid` para enviar la señal de terminación al proceso correcto.

**Archivos:**
```
logs/
├── auth-profile.log
├── auth-profile.pid
├── catalog.log
├── catalog.pid
├── dashboard.log
├── dashboard.pid
├── gateway.log
├── gateway.pid
├── notification.log
├── notification.pid
├── routines-ai.log
├── routines-ai.pid
├── tracking.log
└── tracking.pid
```

---

### `config/`

**Funcionalidad:** (Vacío) Directorio预备ado para archivos de configuración centralizada. Actualmente sin uso; las configuraciones se manejan mediante variables de entorno en `.env`.

---

## 2. Archivos

### Archivos raíz

---

#### `.env`

**Funcionalidad:** Variables de entorno del proyecto en ejecución. Contiene las credenciales reales de PostgreSQL (`DATABASE_URL=postgresql://postgres:9739185@localhost:5432/seniorvital`), la clave secreta JWT y la configuración de Ollama.

**Uso y aplicabilidad:** Cargado por `python-dotenv` al iniciar cada microservicio. Es el único punto donde se definen credenciales en tiempo de ejecución. No versionado (incluido en `.gitignore`).

**Conexiones:** Leído por cada servicio mediante `load_dotenv()` o lectura directa de `os.environ`. Define el valor de `DATABASE_URL` que `seniorvital_shared/db.py` utiliza para conectar a PostgreSQL.

---

#### `.env.example`

**Funcionalidad:** Plantilla de variables de entorno con valores de ejemplo. Sirve como guía para nuevos desarrolladores.

**Uso y aplicabilidad:** Versionado en Git. Copiar a `.env` y reemplazar los valores por los reales del entorno local.

---

#### `.gitignore`

**Funcionalidad:** Exclusiones de Git. Ignora `venv/`, `node_modules/`, `__pycache__/`, `.env`, `dist/`, `logs/*.log`, `*.pid`, `seniorvital_analytics.duckdb` y archivos del sistema operativo.

---

#### `AGENTS.md`

**Funcionalidad:** Archivo de instrucciones para OpenCode (asistente de desarrollo). Describe la estructura del proyecto, comandos, dependencias y arquitectura.

**Uso y aplicabilidad:** Leído automáticamente por OpenCode al iniciar una sesión en el proyecto. Mejora la precisión de las respuestas del asistente.

---

#### `ESTRUCTURA_BACKEND.md`

**Funcionalidad:** Documentación detallada de la estructura del backend, generada en fases tempranas del proyecto. Contiene la descripción de cada servicio, script y paquete compartido.

**Uso y aplicabilidad:** Mantenida como referencia histórica. El documento actual (`ESTRUCTURA_PROYECTO.md`) la reemplaza y amplía para incluir el frontend.

---

#### `ESTRUCTURA_FRONTEND.md`

**Funcionalidad:** Documentación específica del frontend, extraída del análisis del código fuente original del ZIP. Describe componentes, páginas, rutas y configuración.

**Uso y aplicabilidad:** Complemento del presente documento para quien necesite detalle exclusivo del frontend.

---

#### `GUIA_DESARROLLO.md`

**Funcionalidad:** Guía de desarrollo para nuevos integrantes. Incluye instrucciones de setup, estándares de código, flujo de trabajo Git y convenciones del proyecto.

---

#### `README.md`

**Funcionalidad:** Presentación del proyecto. Describe el propósito, arquitectura de alto nivel, requisitos previos, cómo iniciar y cómo ejecutar tests.

---

#### `REQUISITOS_FUNCIONALES.md`

**Funcionalidad:** Documento de requisitos funcionales del sistema. Lista los criterios de aceptación (AC-*) que los tests validan.

**Uso y aplicabilidad:** Fuente de verdad para el equipo de QA. Cada `AC-*` se corresponde con uno o más tests en `tests/`.

---

#### `SDD.md`

**Funcionalidad:** System Design Document. Describe la arquitectura técnica completa: diagrama de flujo de datos, esquema de base de datos, decisiones de diseño, stack tecnológico y justificaciones.

**Uso y aplicabilidad:** Fuente de verdad de la arquitectura. No debe modificarse sin revisión del equipo. Es el documento de referencia para entender el diseño del sistema.

---

#### `init_db.sql`

**Funcionalidad:** Script de inicialización de la base de datos PostgreSQL. Crea el esquema completo: tablas (`users`, `health_profiles`, `exercises`, `tracking`, `routines`, `event_queue`, `push_subscriptions`), índices y relaciones.

**Uso y aplicabilidad:** Se ejecuta una sola vez contra PostgreSQL antes de iniciar los servicios. Ejecutable desde pgAdmin o psql.

**Conexiones:** Define la estructura que todos los microservicios asumen al hacer consultas. `seniorvital_shared/db.py` se conecta a la base de datos creada por este script.

---

#### `package.json` (raíz)

**Funcionalidad:** Scripts de orquestación del monorepo. Define comandos npm para instalar dependencias del frontend (`install:frontend`), compilarlo (`build:frontend`) e iniciar el dev server (`dev:frontend`).

**Uso y aplicabilidad:** Facilita la integración desde la raíz del proyecto sin necesidad de cambiar de directorio.

---

#### `pytest.ini`

**Funcionalidad:** Configuración de pytest para toda la suite. Define `asyncio_mode=auto` para habilitar tests asíncronos sin decoradores adicionales.

**Uso y aplicabilidad:** Afecta a todos los archivos en `tests/`. Permite que las funciones `async def` sean reconocidas automáticamente como corrutinas de test.

---

#### `requirements.txt`

**Funcionalidad:** Dependencias Python del proyecto. Lista completa de paquetes necesarios para ejecutar backend, tests y workers.

**Uso y aplicabilidad:** Instalar con `pip install -r requirements.txt`. Define versiones específicas: `fastapi==0.136.3`, `bcrypt==4.0.1`, `passlib[bcrypt]>=1.7.4`, `pydantic==2.13.4`, `asyncpg==0.31.0`, `duckdb`, `pywebpush`, etc.

---

### `seniorvital_shared/` — Biblioteca compartida

---

#### `__init__.py`

**Funcionalidad:** Inicializador del paquete Python. Exporta los símbolos públicos del paquete: `get_pool`, `init_pool`, `close_pool`, `EventType`, modelos Pydantic.

**Uso y aplicabilidad:** Permite `from seniorvital_shared import get_pool, EventType`. Sin este archivo, Python no reconocería la carpeta como un paquete.

---

#### `db.py`

**Funcionalidad:** Pool de conexiones PostgreSQL con sistema de "owners". Implementa tres funciones principales:
- `init_pool(owner)` — Inicializa `asyncpg.create_pool` con `DATABASE_URL` del entorno.
- `get_pool()` — Retorna el pool singleton. Cada owner puede llamarlo concurrentemente.
- `close_pool(owner)` — Cierra el pool cuando todos los owners lo solicitan.

**Uso y aplicabilidad:** Esencial para la persistencia. Cada microservicio lo usa en su ciclo de vida (lifespan) y en cada endpoint que requiere base de datos. El sistema de owners evita que los tests cierren el pool prematuramente cuando comparten el proceso con servicios en vivo.

**Conexiones:** Depende de `os.environ["DATABASE_URL"]`. Es importado por todos los servicios (`from seniorvital_shared import get_pool`) y por `conftest.py`.

---

#### `events.py`

**Funcionalidad:** Define la enumeración `EventType` con los nombres de stream de eventos del sistema:
- `EJERCICIO_COMPLETADO`
- `FATIGA_ALTA`
- `INACTIVIDAD_DETECTADA`
- `RUTINA_GENERADA`
- `REPLICACION_COMPLETADA`

**Uso y aplicabilidad:** Centraliza los nombres de eventos para evitar errores tipográficos. Es importado por servicios que publican eventos (tracking-service) y por workers que los consumen.

**Conexiones:** Importado por `tracking-service/main.py` para publicar eventos y por scripts en `scripts/` que consumen.

---

#### `models.py`

**Funcionalidad:** Modelos Pydantic v2 de datos compartidos. Contiene:
- `HealthProfile` — Valida y serializa el perfil de salud de un senior (restricciones médicas, nivel de movilidad, condiciones preexistentes).

Usa `@field_validator` de Pydantic v2 (heredado de `@validator` v1) para normalizar valores booleanos y numéricos.

**Uso y aplicabilidad:** Importado por `auth-profile-service` al crear/actualizar perfiles y por `dashboard-service` al serializar datos de proyección.

**Conexiones:** Importado por `auth-profile-service/main.py` y `dashboard-service/main.py`.

---

### Microservicios (`auth-profile-service`, `catalog-service`, etc.)

Cada microservicio comparte la misma estructura de dos archivos:

---

#### `<servicio>/main.py`

**Funcionalidad:** Aplicación FastAPI completa del microservicio. Incluye:
- Lifespan con `init_pool`/`close_pool`.
- Definición de modelos Pydantic específicos del dominio.
- Endpoints REST documentados con docstrings.
- Lógica de negocio y persistencia.

**Uso y aplicabilidad:** Ejecutable con `uvicorn main:app --port <PORT> --reload`. Cada uno escucha en su puerto asignado y expone documentación interactiva en `/docs`.

**Conexiones comunes a todos:**
- `from seniorvital_shared import get_pool, init_pool, close_pool` — Pool de base de datos.
- `sys.path.insert(0, ...)` para resolver importaciones desde la raíz del proyecto.
- `os.environ["DATABASE_URL"]` — Cadena de conexión a PostgreSQL.

---

#### `<servicio>/requirements.txt`

**Funcionalidad:** Dependencias específicas del microservicio (si las hay). La mayoría heredan las dependencias globales del `requirements.txt` raíz; estos archivos existen para documentar dependencias adicionales o permitir despliegues independientes.

---

##### `auth-profile-service/main.py`

**Funcionalidad específica:** Endpoints de autenticación y perfiles:
- `POST /auth/register` — Registro con email, password y rol. Hash bcrypt del password.
- `POST /auth/login` — Verifica credenciales, retorna JWT (firmado con `python-jose`).
- `GET /auth/me` — Retorna perfil del usuario autenticado (requiere token).
- `GET /auth/users` — Lista usuarios (admin).
- `POST /auth/link-caregiver` — Vincula cuidador con senior (máximo 3).
- `GET /auth/linked-seniors/{caregiver_id}` — Seniors vinculados a un cuidador.
- `POST /auth/profile` — Crea/actualiza perfil de salud (`HealthProfile`).
- `GET /auth/profile/{user_id}` — Obtiene perfil de salud.

**Conexiones:** Importa `HealthProfile` desde `seniorvital_shared/models.py`. Usa `get_pool` para todas las operaciones de base de datos. Depende de `passlib` para bcrypt y `python-jose` para JWT.

---

##### `catalog-service/main.py`

**Funcionalidad específica:** CRUD de ejercicios:
- `POST /catalog/exercises` — Crea ejercicio (con subida de vídeo opcional).
- `GET /catalog/exercises` — Lista todos los ejercicios.
- `GET /catalog/exercises/{exercise_id}` — Detalle de un ejercicio.
- `PUT /catalog/exercises/{exercise_id}` — Actualiza ejercicio.
- `DELETE /catalog/exercises/{exercise_id}` — Elimina ejercicio y su vídeo.
- `GET /storage/videos/{filename}` — Sirve archivos de vídeo.

**Conexiones:** Lee/escribe en tabla `exercises`. Almacena vídeos en `storage/videos/`. Usa `FileResponse` de Starlette para servir archivos.

---

##### `routines-ai-service/main.py`

**Funcionalidad específica:** Rutinas con IA:
- `POST /routines/generate` — Genera rutina diaria vía Ollama. Body: `{ user_id }`. La rutina se genera con un prompt que incluye edad, condiciones y restricciones del usuario. Es idempotente: si ya existe rutina para hoy, la retorna sin regenerar.
- `GET /routines/today?user_id=...` — Obtiene la rutina del día actual.

**Conexiones:** Llama a Ollama (`http://localhost:11434/api/generate`) con modelo `phi3:mini` y timeout de 180s. Lee perfil de salud desde `health_profiles`. Lee/escribe en tabla `routines`.

---

##### `tracking-service/main.py`

**Funcionalidad específica:** Registro de ejercicios:
- `POST /tracking/record` — Registra una sesión de ejercicio. Publica evento en `event_queue`. Si RPE ≥ 8, publica también evento `fatiga-alta`.
- `POST /tracking/batch` — Registro batch en una sola transacción.

**Conexiones:** Importa `EventType` de `seniorvital_shared/events.py`. Inserta en tablas `tracking` y `event_queue` dentro de una misma transacción.

---

##### `dashboard-service/main.py`

**Funcionalidad específica:** Consultas de análisis:
- `GET /dashboard/progress/{user_id}` — Progreso semanal: calendario de repeticiones, RPE promedio, racha de días consecutivos, total de sesiones.
- `GET /dashboard/projection/{user_id}` — Proyección de salud basada en tendencias.
- `GET /dashboard/insights/{user_id}` — Recomendaciones generadas a partir de datos históricos.

**Conexiones:** Solo lectura en `tracking`, `users`, `health_profiles`. Usa `date.today()` y `timedelta(days=7)` para cálculos semanales.

---

##### `notification-service/main.py`

**Funcionalidad específica:** Web Push:
- `POST /notify/subscribe` — Almacena suscripción push del navegador. Sobrescribe si ya existe para el mismo usuario.
- `POST /notify/send` — Envía notificación push a un usuario específico.

**Conexiones:** Almacena en tabla `push_subscriptions`. Usa `pywebpush` para envío de notificaciones VAPID.

---

##### `gateway/main.py`

**Funcionalidad específica:** Proxy y servidor de estáticos:
- Proxy inverso: reenvía peticiones a los microservicios según el prefijo de ruta.
- Sirve `frontend/dist/` en producción: monta `/assets/` como StaticFiles y usa catch-all para SPA (React Router).
- CORS configurado para `localhost:5173` (Vite dev) y `localhost:8000` (producción).
- Expone su propia documentación en `/docs` (endpoints propios) y redirige a las docs de cada servicio.

**Conexiones:** Depende de `httpx` para el proxy asíncrono. Apunta a `http://localhost:8001` a `8006` para cada servicio. Sirve archivos desde `frontend/dist/`.

---

### Frontend

---

#### `vite.config.js`

**Funcionalidad:** Configuración de Vite. Define el puerto de desarrollo (`5173`), el plugin React y los proxies hacia el gateway para todas las rutas API (`/auth`, `/catalog`, `/routines`, `/tracking`, `/dashboard`, `/notify`, `/storage`).

**Uso y aplicabilidad:** Esencial para el desarrollo local. Sin él, las peticiones del frontend desde `localhost:5173` no llegarían al backend en `localhost:8000`.

---

#### `tailwind.config.js`

**Funcionalidad:** Configuración de Tailwind CSS 3 con tema Material Design 3. Define colores primarios, secundarios, terciarios, errores, superficies y tipografía (Lexend).

**Uso y aplicabilidad:** Aplica el sistema de diseño Material 3 a todos los componentes mediante clases utilitarias.

---

#### `postcss.config.js`

**Funcionalidad:** Configura PostCSS con Tailwind y Autoprefixer. Necesario para que Vite procese las directivas `@tailwind` en `index.css`.

---

#### `src/main.jsx`

**Funcionalidad:** Punto de entrada de React. Monta el componente `<App />` en el elemento `#root` del DOM, envuelto en `<React.StrictMode>`.

**Conexiones:** Importa `App` desde `./App.jsx`. Renderiza en `index.html`.

---

#### `src/App.jsx`

**Funcionalidad:** Componente raíz de la aplicación. Define el enrutamiento con React Router:
- Rutas públicas: `/login`, `/register`.
- Rutas protegidas (envueltas en `<ProtectedRoute>`): `/`, `/habits`, `/video`, `/progress`, `/admin`.

Envuelve todas las rutas en `<AuthProvider>` para que cualquier página pueda acceder al estado de autenticación.

**Conexiones:** Importa `AuthProvider` desde `contexts/AuthContext`, `ProtectedRoute` desde `components/ProtectedRoute`, y todas las páginas desde `pages/`.

---

#### `src/index.css`

**Funcionalidad:** Estilos globales. Importa las directivas de Tailwind y define estilos base para `body` (fuente Lexend). Configura las variables de Material Symbols (`material-symbols-outlined`).

---

#### `src/components/ProtectedRoute.jsx`

**Funcionalidad:** Guardia de ruta. Muestra un spinner mientras el estado de autenticación se resuelve. Si el usuario no está autenticado, redirige a `/login`. Si está autenticado, renderiza los hijos.

**Conexiones:** Usa `useAuth()` de `AuthContext`. Depende de `react-router-dom` para `Navigate`.

---

#### `src/components/TopAppBar.jsx`

**Funcionalidad:** Barra superior fija. Muestra el título y un botón de retroceso (condicional). Usa `useNavigate` para la navegación hacia atrás.

**Props:** `title` (string, default "SeniorVital"), `showBack` (boolean, default false).

---

#### `src/components/BottomNavBar.jsx`

**Funcionalidad:** Barra de navegación inferior (visible solo en móvil, `md:hidden`). 4 pestañas: Inicio, Hábitos, Vídeo, Progreso. Resalta la pestaña activa según `location.pathname`.

**Conexiones:** Usa `useLocation` de React Router.

---

#### `src/components/AdminSidebar.jsx`

**Funcionalidad:** Barra lateral del panel de administración (visible solo en desktop). Enlaces a Panel Clínico, Vista Móvil y Cerrar Sesión. El botón de cerrar sesión ejecuta `logout()` del AuthContext y redirige a `/login`.

**Conexiones:** Usa `useAuth()` de `AuthContext`. Usa `useNavigate` para la redirección post-logout.

---

#### `src/contexts/AuthContext.jsx`

**Funcionalidad:** Estado global de autenticación. Provee:
- `user` — Objeto con datos del usuario autenticado (o `null`).
- `loading` — Booleano que indica si se está verificando el token almacenado.
- `login(email, password)` — Llama al endpoint de login, almacena el JWT en `localStorage` y carga el perfil.
- `register(email, password, role)` — Registra, inicia sesión automáticamente y carga el perfil.
- `logout()` — Limpia el token y establece `user = null`.

Al montar, intenta recuperar el token de `localStorage` y llama a `GET /auth/me` para validarlo. Escucha el evento personalizado `sv:unauthorized` (disparado por `api.js` ante un 401) para cerrar sesión automáticamente.

**Conexiones:** Importa `login`, `register`, `getMe` desde `services/auth`. Importa `setToken`, `clearToken`, `getToken` desde `services/api`. Envuelve la aplicación en `App.jsx`.

---

#### `src/services/api.js`

**Funcionalidad:** Cliente HTTP base para toda la aplicación. Exporta:
- `getToken()`, `setToken(token)`, `clearToken()` — Gestión del JWT en `localStorage`.
- `api(path, options)` — Función genérica que:
  1. Inyecta `Authorization: Bearer <token>` en los headers si existe token.
  2. En caso de respuesta `401`, limpia el token y dispara evento `sv:unauthorized`.
  3. Retorna el JSON parseado o lanza `Error` con el mensaje del servidor.

**Uso y aplicabilidad:** Fundamental para la comunicación con el backend. Todos los servicios (`auth.js`, `catalog.js`, etc.) importan y usan `api()`.

**Conexiones:** Usado por `services/auth.js`, `services/catalog.js`, `services/tracking.js`, `services/routines.js`, `services/dashboard.js`. Escuchado por `AuthContext.jsx` mediante el evento `sv:unauthorized`.

---

#### `src/services/auth.js`

**Funcionalidad:** Servicio de autenticación. Exporta:
- `register(email, password, role)` → `POST /auth/register`
- `login(email, password)` → `POST /auth/login`
- `getMe()` → `GET /auth/me`

**Conexiones:** Importa `api` desde `./api`. Usado por `AuthContext.jsx`.

---

#### `src/services/catalog.js`

**Funcionalidad:** Servicio de catálogo de ejercicios. Exporta:
- `getExercises()` → `GET /catalog/exercises`

**Conexiones:** Importa `api` desde `./api`. Usado por `pages/Video.jsx`.

---

#### `src/services/tracking.js`

**Funcionalidad:** Servicio de tracking de ejercicios. Exporta:
- `recordExercise(data)` → `POST /tracking/record`

**Conexiones:** Importa `api` desde `./api`. Preparado para ser usado por páginas de registro de actividad.

---

#### `src/services/routines.js`

**Funcionalidad:** Servicio de rutinas IA. Exporta:
- `generateRoutine(userId)` → `POST /routines/generate`
- `getTodayRoutine(userId)` → `GET /routines/today?user_id={userId}`

**Conexiones:** Importa `api` desde `./api`. Usado por `pages/Home.jsx`.

---

#### `src/services/dashboard.js`

**Funcionalidad:** Servicio de dashboard y progreso. Exporta:
- `getProgress(userId)` → `GET /dashboard/progress/{userId}`
- `getInsights(userId)` → `GET /dashboard/insights/{userId}`

**Conexiones:** Importa `api` desde `./api`. Usado por `pages/Progress.jsx`.

---

#### `src/pages/Login.jsx`

**Funcionalidad:** Página de inicio de sesión. Formulario con email y contraseña. Muestra errores de validación del backend. Tras login exitoso, redirige a `/`.

**Conexiones:** Usa `useAuth().login`. Redirige con `useNavigate`.

---

#### `src/pages/Register.jsx`

**Funcionalidad:** Página de registro. Formulario con email, contraseña y selección de rol (senior, caregiver, admin). Tras registro exitoso, inicia sesión automáticamente y redirige a `/`.

**Conexiones:** Usa `useAuth().register`. Redirige con `useNavigate`.

---

#### `src/pages/Home.jsx`

**Funcionalidad:** Página principal del senior. Muestra un botón para generar rutina diaria con IA. Al cargar, intenta obtener la rutina del día (`getTodayRoutine`). Al pulsar el botón, llama a `generateRoutine`. Muestra las actividades generadas o datos mock de fallback.

**Conexiones:** Usa `useAuth()` para obtener `user.id`. Importa `getTodayRoutine` y `generateRoutine` desde `services/routines`.

---

#### `src/pages/Habits.jsx`

**Funcionalidad:** Seguimiento de hábitos diarios. Controles para:
- Consumo de agua (vasos de 8oz, +1/-1).
- Minutos de caminata (+5/-5).
- Medicación matutina (Sí/No/Pendiente).

Muestra mensaje motivacional según el progreso. Datos en estado local con sincronización opcional al backend.

**Conexiones:** Usa `useAuth()` para mostrar email del usuario.

---

#### `src/pages/Video.jsx`

**Funcionalidad:** Reproductor de vídeos de ejercicios. Al cargar, obtiene la lista de ejercicios desde el catálogo (`getExercises`). Muestra un reproductor simulado (placeholder visual con barra de progreso) y una cuadrícula de vídeos relacionados. Si la API falla, usa datos mock de fallback.

**Conexiones:** Importa `getExercises` desde `services/catalog`.

---

#### `src/pages/Progress.jsx`

**Funcionalidad:** Calendario de progreso mensual. Al cargar, intenta obtener datos de `getProgress` y construir un calendario. Muestra un grid de días con indicadores de actividad completada. Navegación entre meses. Panel de detalle del día seleccionado con desglose de agua, caminata y medicación.

**Conexiones:** Usa `useAuth()` para obtener `user.id`. Importa `getProgress` desde `services/dashboard`.

---

#### `src/pages/AdminDashboard.jsx`

**Funcionalidad:** Panel de administración clínica. Tabla de residentes con búsqueda por nombre/unidad, filtro por estado (stable, observation, review, offline), paginación (5 por página) y tarjetas KPI (total monitoreados, activos hoy, atención sugerida).

**Conexiones:** Importa `AdminSidebar` desde `components/AdminSidebar`. Datos mock con preparación para API futura.

---

### `scripts/` — Automatización y Workers

---

#### `start_all.ps1` / `start_all.sh`

**Funcionalidad:** Orquestador de inicio. Para cada microservicio:
1. Crea el directorio `logs/` si no existe.
2. Inicia `uvicorn main:app` en segundo plano, redirigiendo stdout al archivo de log.
3. Guarda el PID en un archivo `.pid`.
4. Espera 3 segundos entre servicios para evitar condiciones de carrera.

Además, construye el frontend si `dist/` no existe.

**Uso y aplicabilidad:** Script principal para levantar todo el sistema. Ejecutar desde la raíz del proyecto.

---

#### `stop_all.ps1` / `stop_all.sh`

**Funcionalidad:** Orquestador de parada. Lee cada archivo `.pid` en `logs/` y envía `SIGTERM` (o `Stop-Process` en Windows) al proceso correspondiente. Limpia los archivos `.pid` tras la parada.

---

#### `migrations.sql`

**Funcionalidad:** Migraciones de esquema PostgreSQL. Agrega:
- Columna `password` a la tabla `users`.
- Tabla `push_subscriptions`.
- Índices y restricciones faltantes.

**Uso y aplicabilidad:** Ejecutar en orden secuencial sobre la base de datos creada por `init_db.sql`.

---

#### `replicator.py`

**Funcionalidad:** Worker de replicación PostgreSQL → DuckDB. Escucha la tabla `event_queue` en PostgreSQL, lee eventos de tipo `REPLICACION_COMPLETADA` y replica los datos relevantes en la base de datos analítica DuckDB (`seniorvital_analytics.duckdb`).

Usa `DELETE + INSERT` en lugar de `INSERT OR REPLACE` porque DuckDB no tiene claves primarias en todas las tablas.

**Conexiones:** Conecta a PostgreSQL via `asyncpg` y a DuckDB local via `duckdb` (archivo embebido). Depende de `seniorvital_shared/db.py` para el pool de PostgreSQL.

---

#### `preventive_worker.py`

**Funcionalidad:** Worker de prevención. Escucha eventos `fatiga-alta` en `event_queue` y ejecuta lógica de alerta temprana (actualmente notifica al sistema; extensible a envío de notificaciones push).

**Conexiones:** Lee `event_queue` de PostgreSQL. Usa `json.loads()` para decodificar el payload.

---

#### `weekly_analysis.py`

**Funcionalidad:** Worker de análisis semanal con IA. Para cada usuario con actividad en la última semana, consulta sus datos de tracking, construye un prompt y llama a Ollama para generar un resumen y recomendaciones personalizadas.

Incluye validación de UUID, manejo de errores por usuario (no interrumpe el batch si un usuario falla) y timeout de 180s para Ollama.

**Conexiones:** Lee `tracking` y `users` de PostgreSQL. Llama a Ollama (`localhost:11434`). Depende de `seniorvital_shared/db.py`.

---

#### `daily_inactivity.py`

**Funcionalidad:** Worker de detección de inactividad. Consulta usuarios sin actividad registrada en las últimas 24 horas y emite eventos `INACTIVIDAD_DETECTADA` en `event_queue`.

**Conexiones:** Lee `tracking` y escribe en `event_queue` de PostgreSQL.

---

#### `smoke_test.py`

**Funcionalidad:** Smoke test automatizado. Verifica que todos los endpoints de todos los servicios responden correctamente (16 checks). Usa `httpx` para hacer peticiones reales a `localhost:8000` a `8006`.

---

#### `quick_check.py`

**Funcionalidad:** Verificación rápida de integración frontend-backend. 9 checks que validan: HTML servido, rutas SPA, assets estáticos, registro, login con JWT, proxy API y endpoint `/auth/me`.

---

#### `verify_integration.py`

**Funcionalidad:** Verificación completa de integración. Extiende `quick_check.py` con más escenarios: rutas SPA adicionales, assets JS, y flujo completo de registro+login.

---

### `tests/` — Suite de Tests

---

#### `conftest.py`

**Funcionalidad:** Fixtures globales de pytest. Provee:
- `pool` — Pool de conexiones PostgreSQL con owner "test".
- `seed_users` — Inserta usuarios de prueba (`ollama_test@test.com`, `test@example.com`, etc.).
- `client(service_path, app_variable)` — Cliente HTTP de prueba basado en `ASGITransport` (no requiere servidor real).

Usa `importlib` para cargar módulos desde directorios con guiones (ej. `auth-profile-service`).

**Conexiones:** Importa `seniorvital_shared/db.py` para el pool. Carga módulos de cada microservicio bajo test.

---

#### `test_auth.py`

**Funcionalidad:** 5 tests que validan:
1. `AC-AUTH-01`: El password se almacena hasheado (bcrypt), no en texto plano.
2. `AC-AUTH-02`: Roles inválidos son rechazados.
3. `AC-AUTH-03`: Cuidador sin seniors vinculados puede registrarse.
4. `AC-AUTH-04`: No se pueden vincular más de 3 cuidadores a un senior.
5. `AC-AUTH-05`: Cuidador con un senior vinculado funciona correctamente.

---

#### `test_catalog.py`

**Funcionalidad:** 6 tests que validan:
1. Creación de ejercicio.
2. Listado de ejercicios.
3. Obtención por ID.
4. Actualización.
5. Eliminación.
6. Subida y servicio de archivo de vídeo.

---

#### `test_dashboard.py`

**Funcionalidad:** 3 tests que validan:
1. Progreso de usuario no encontrado (404).
2. Proyección con datos nulos.
3. Insights con datos vacíos.

---

#### `test_notification.py`

**Funcionalidad:** 3 tests que validan:
1. Suscripción push exitosa.
2. Sobrescritura de suscripción existente.
3. Envío de notificación.

---

#### `test_persistence.py`

**Funcionalidad:** 4 tests que validan:
1. Perfil de salud válido.
2. Perfil de salud con restricción inválida.
3. Vinculación cuidador-senior.
4. Inserción en event_queue.

---

#### `test_routines.py`

**Funcionalidad:** 3 tests que validan:
1. Generación de rutina para usuario inexistente (404).
2. Consulta de rutina del día cuando no existe (404).
3. Generación dos veces retorna la misma rutina (idempotencia).

Usa monkeypatch para simular Ollama sin necesidad del servidor real.

---

#### `test_tracking.py`

**Funcionalidad:** 3 tests que validan:
1. Registro de ejercicio simple.
2. Registro con fatiga alta (RPE ≥ 8).
3. Registro batch.

---

#### `test_db_conn.py`

**Funcionalidad:** Test de conectividad a PostgreSQL. Verifica que `DATABASE_URL` sea accesible y que las tablas del esquema existan.

---

### `storage/` — Archivos

---

#### `storage/videos/<uuid>.mp4`

**Funcionalidad:** Archivos de vídeo de ejercicios. Almacenados con nombre UUID (generado por `uuid4()` en el catalog-service). Referenciados por el campo `video_path` en la tabla `exercises`.

**Uso y aplicabilidad:** Servidos por el catalog-service (`GET /storage/videos/{filename}`) y accesibles desde el frontend mediante `<video>` o `FileResponse`. Son el contenido multimedia del catálogo de ejercicios.

---

### Archivos de configuración y documentación (raíz)

Los archivos `ESTRUCTURA_BACKEND.md`, `ESTRUCTURA_FRONTEND.md`, `GUIA_DESARROLLO.md`, `README.md`, `REQUISITOS_FUNCIONALES.md`, `SDD.md`, `AGENTS.md` cumplen funciones de documentación y orquestación del equipo. No contienen lógica ejecutable pero son esenciales para la mantenibilidad del proyecto. Sus funcionalidades se describen en la sección de archivos raíz.

---

*Fin del documento*

# Environment Variables — SeniorVital

> Referencia completa de todas las variables de entorno requeridas por los servicios del backend y workers de fondo.
> Este documento reemplaza y amplía la información del archivo `.env.example`.

---

## Tabla de contenido

1. [Base de datos](#1-base-de-datos)
2. [Autenticación y seguridad](#2-autenticación-y-seguridad)
3. [Inteligencia artificial (Ollama)](#3-inteligencia-artificial-ollama)
4. [Notificaciones Web Push (VAPID)](#4-notificaciones-web-push-vapid)
5. [Entorno de ejecución](#5-entorno-de-ejecución)
6. [RAG y Chunking](#6-rag-y-chunking)
7. [Variables por servicio](#7-variables-por-servicio)
8. [Ejemplo completo de archivo `.env`](#8-ejemplo-completo-de-archivo-env)
9. [Diferencias por entorno](#9-diferencias-por-entorno)

---

## 1. Base de datos

### `DATABASE_URL`

| Campo | Detalle |
|---|---|
| **Tipo** | `string` (URL de conexión PostgreSQL) |
| **Obligatoriedad** | **Requerida** |
| **Valor por defecto** | `postgresql://postgres:9739185@127.0.0.1:5432/seniorvital` |
| **Servicios que la usan** | Todos los microservicios (`seniorvital_shared/db.py`), workers (`replicator.py`, `preventive_worker.py`, `weekly_analysis.py`, `daily_inactivity.py`) |
| **Formato válido** | `postgresql://[usuario]:[contraseña]@[host]:[puerto]/[nombre_base]` |
| **Notas de seguridad** | Contiene credenciales de acceso a la base de datos. **Nunca** commitear este valor en repositorios. Usar un secret manager o variable de entorno del sistema operativo en producción. |

**Comportamiento:** Todas las conexiones a PostgreSQL se realizan a través de `asyncpg` usando esta variable. Si no se define, se usa el valor por defecto apuntando a una instancia local con credenciales de desarrollo.

---

## 2. Autenticación y seguridad

### `JWT_SECRET`

| Campo | Detalle |
|---|---|
| **Tipo** | `string` |
| **Obligatoriedad** | **Requerida** (crítico en producción) |
| **Valor por defecto** | `super-secret-key-change-in-production` |
| **Servicios que la usan** | `auth-profile-service/main.py` |
| **Formato válido** | Cadena de texto libre (mínimo 32 caracteres recomendados) |
| **Notas de seguridad** | Se usa para firmar tokens JWT de acceso y refresco. Si se expone, cualquier persona puede forjar tokens válidos. En producción, generar una clave aleatoria de al menos 64 caracteres con `openssl rand -hex 64`. |

**Comportamiento:** Controla la firma y verificación de tokens JWT emitidos en `/auth/login` y validados en cada petición autenticada.

---

## 3. Inteligencia artificial (Ollama)

### `OLLAMA_URL`

| Campo | Detalle |
|---|---|
| **Tipo** | `string` (URL) |
| **Obligatoriedad** | **Requerida** |
| **Valor por defecto** | `http://localhost:11434` |
| **Servicios que la usan** | `routines-ai-service/main.py`, `scripts/weekly_analysis.py` |
| **Formato válido** | URL completa con esquema `http://` o `https://` |
| **Notas de seguridad** | En desarrollo apunta a localhost. En producción con Ollama remoto, asegurar que la comunicación sea over TLS si se expone a red pública. |

**Comportamiento:** URL base del servicio Ollama donde se ejecuta el modelo de lenguaje. Se usa para generar rutinas de ejercicio personalizadas mediante streaming SSE.

---

### `OLLAMA_MODEL`

| Campo | Detalle |
|---|---|
| **Tipo** | `string` |
| **Obligatoriedad** | Opcional |
| **Valor por defecto** | `phi3:mini` |
| **Servicios que la usan** | `routines-ai-service/main.py`, `scripts/weekly_analysis.py` |
| **Formato válido** | Nombre de modelo válido en Ollama (ej. `phi3:mini`, `llama3`, `mistral`) |
| **Notas de seguridad** | Sin riesgo de seguridad. Afecta la calidad y latencia de las respuestas generadas. |

**Comportamiento:** Identificador del modelo de lenguaje utilizado para generar rutinas personalizadas. Debe estar previamente descargado en Ollama con `ollama pull`.

---

### `OLLAMA_TIMEOUT`

| Campo | Detalle |
|---|---|
| **Tipo** | `float` (segundos) |
| **Obligatoriedad** | Opcional |
| **Valor por defecto** | `600` (10 minutos) |
| **Servicios que la usan** | `routines-ai-service/main.py` |
| **Formato válido** | Número positivo (segundos) |
| **Notas de seguridad** | Sin riesgo. Valores muy bajos pueden cortar generaciones largas. |

**Comportamiento:** Tiempo máximo de espera para que Ollama complete la generación de una rutina. Modelos más grandes o rutinas complejas requieren timeouts mayores.

---

### `OLLAMA_HEALTH_TIMEOUT`

| Campo | Detalle |
|---|---|
| **Tipo** | `float` (segundos) |
| **Obligatoriedad** | Opcional |
| **Valor por defecto** | `15` |
| **Servicios que la usan** | `routines-ai-service/main.py` |
| **Formato válido** | Número positivo (segundos) |
| **Notas de seguridad** | Sin riesgo. Usado para health checks del servicio de IA. |

**Comportamiento:** Timeout para las verificaciones de salud del servicio Ollama. Permite determinar si Ollama está disponible antes de intentar generaciones.

---

## 4. Notificaciones Web Push (VAPID)

### `VAPID_PUBLIC_KEY`

| Campo | Detalle |
|---|---|
| **Tipo** | `string` (clave en formato PEM o base64url) |
| **Obligatoriedad** | **Requerida** (para notificaciones push) |
| **Valor por defecto** | *(vacío)* |
| **Servicios que la usan** | `notification-service/main.py` |
| **Formato válido** | Clave pública VAPID en formato estándar (generada con `pywebpush` o `web-push` CLI) |
| **Notas de seguridad** | Es pública por diseño (se comparte al navegador). No contiene información sensible. |

**Comportamiento:** Clave pública VAPID utilizada para suscribir clientes al servicio de Web Push. Se entrega al navegador durante la suscripción.

---

### `VAPID_PRIVATE_KEY`

| Campo | Detalle |
|---|---|
| **Tipo** | `string` (clave en formato PEM o base64url) |
| **Obligatoriedad** | **Requerida** (para notificaciones push) |
| **Valor por defecto** | *(vacío)* |
| **Servicios que la usan** | `notification-service/main.py` |
| **Formato válido** | Clave privada VAPID correspondiente a `VAPID_PUBLIC_KEY` |
| **Notas de seguridad** | **Altamente sensible.** Permite firmar notificaciones push en nombre del servidor. Al exponerse, un atacante podría enviar notificaciones falsas a los usuarios. Usar un secret manager y nunca exponerla en logs o clientes. |

**Comportamiento:** Clave privada VAPID usada para firmar las notificaciones push antes de enviarlas a los servidores de los navegadores (FCM, WNS, etc.).

---

### `VAPID_CLAIM_EMAIL`

| Campo | Detalle |
|---|---|
| **Tipo** | `string` (email) |
| **Obligatoriedad** | Opcional |
| **Valor por defecto** | `admin@seniorvital.com` |
| **Servicios que la usan** | `notification-service/main.py` |
| **Formato válido** | Email válido (`mailto:` se agrega automáticamente internamente) |
| **Notas de seguridad** | Sin riesgo. Se usa como identificador de contacto en el estándar VAPID (RFC 8292). |

**Comportamiento:** Email de contacto incluido en los headers `Authorization` de las notificaciones Web Push. Permite a los receptores identificar al emisor.

---

## 5. Entorno de ejecución

### `ENVIRONMENT`

| Campo | Detalle |
|---|---|
| **Tipo** | `string` |
| **Obligatoriedad** | Opcional |
| **Valor por defecto** | `development` |
| **Servicios que la usan** | Todos (inferido desde la configuración de la aplicación) |
| **Formato válido** | `development`, `staging`, `production` |
| **Notas de seguridad** | Sin riesgo directo. En producción, puede desactivar endpoints de debug como `/docs`. |

**Comportamiento:** Indica el entorno de ejecución actual. Puede usarse para condicionar comportamientos (logging verbose en desarrollo, cache agresivo en producción, etc.).

---

## 6. RAG y Chunking

### `EMBEDDING_MODEL_NAME`

| Campo | Detalle |
|---|---|
| **Tipo** | `string` |
| **Obligatoriedad** | Opcional |
| **Valor por defecto** | `intfloat/multilingual-e5-small` |
| **Servicios que la usan** | `src/knowledge/chunking/semantic_chunker.py`, `src/rag/embeddings/embedding_generator.py` (Fase 5) |
| **Formato válido** | Cualquier modelo de embeddings compatible con HuggingFace `sentence-transformers` |
| **Notas de seguridad** | Sin riesgo. Modelo se descarga localmente desde HuggingFace Hub. |

**Comportamiento:** Define el modelo de embeddings usado para el chunking semántico y la generación de embeddings de la pipeline RAG. El modelo por defecto (`multilingual-e5-small`) es multilingüe, gratuito y funciona bien en español.

### `CHUNKING_LOG_LEVEL`

| Campo | Detalle |
|---|---|
| **Tipo** | `string` |
| **Obligatoriedad** | Opcional |
| **Valor por defecto** | `INFO` |
| **Servicios que la usan** | `scripts/indexing/run_chunking.py` |
| **Formato válido** | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| **Notas de seguridad** | Sin riesgo. |

**Comportamiento:** Controla el nivel de detalle del logging durante el proceso de chunking.

### `OPENAI_API_KEY` (opcional)

| Campo | Detalle |
|---|---|
| **Tipo** | `string` |
| **Obligatoriedad** | Opcional (no requerida para chunking local) |
| **Valor por defecto** | *(vacío)* |
| **Servicios que la usan** | Solo si se configura explícitamente `SemanticChunker` con `OpenAIEmbeddings` |
| **Formato válido** | Clave de API de OpenAI |
| **Notas de seguridad** | **Sensible.** No commitear. Usar secret manager si se decide usar OpenAI en lugar de embeddings locales. |

**Comportamiento:** Por defecto el sistema usa embeddings locales de HuggingFace. Esta variable solo se requiere si se opta por `OpenAIEmbeddings`.

---

## 7. Variables por servicio

La siguiente tabla resume qué variables consume cada servicio y worker:

| Servicio | Variables requeridas | Variables opcionales |
|---|---|---|
| **Gateway** (8000) | — | — |
| **Auth & Profile** (8001) | `DATABASE_URL`, `JWT_SECRET` | — |
| **Catalog** (8002) | `DATABASE_URL` | — |
| **Routines AI** (8003) | `DATABASE_URL`, `OLLAMA_URL` | `OLLAMA_MODEL`, `OLLAMA_TIMEOUT`, `OLLAMA_HEALTH_TIMEOUT` |
| **Tracking** (8004) | `DATABASE_URL` | — |
| **Dashboard** (8005) | `DATABASE_URL` | — |
| **Notification** (8006) | `DATABASE_URL`, `VAPID_PUBLIC_KEY`, `VAPID_PRIVATE_KEY` | `VAPID_CLAIM_EMAIL` |
| **replicator.py** | `DATABASE_URL` | — |
| **preventive_worker.py** | `DATABASE_URL` | — |
| **weekly_analysis.py** | `DATABASE_URL`, `OLLAMA_URL` | `OLLAMA_MODEL` |
| **daily_inactivity.py** | `DATABASE_URL` | — |

---

## 8. Ejemplo completo de archivo `.env`

```bash
# ═══════════════════════════════════════════════════════════════
# SeniorVital — Variables de entorno (plantilla completa)
# Copia este archivo como .env y ajusta los valores según tu entorno.
# ═══════════════════════════════════════════════════════════════

# ── Base de datos ──────────────────────────────────────────────
DATABASE_URL=postgresql://postgres:9739185@127.0.0.1:5432/seniorvital

# ── Autenticación JWT ─────────────────────────────────────────
# IMPORTANTE: Cambiar en producción. Generar con: openssl rand -hex 64
JWT_SECRET=super-secret-key-change-in-production

# ── IA local (Ollama) ─────────────────────────────────────────
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=phi3:mini
OLLAMA_TIMEOUT=600
OLLAMA_HEALTH_TIMEOUT=15

# ── Notificaciones Web Push (VAPID) ──────────────────────────
# Generar claves con: pywebpush vapid_gen
VAPID_PUBLIC_KEY=
VAPID_PRIVATE_KEY=
VAPID_CLAIM_EMAIL=admin@seniorvital.com

# ── Entorno ───────────────────────────────────────────────────
ENVIRONMENT=development

# ── RAG y Chunking (local-first) ───────────────────────────────
EMBEDDING_MODEL_NAME=intfloat/multilingual-e5-small
CHUNKING_LOG_LEVEL=INFO

# Opcional: solo si se decide usar OpenAI en lugar de HuggingFace local
# OPENAI_API_KEY=sk-...
```

---

## 9. Diferencias por entorno

| Variable | Desarrollo | Producción |
|---|---|---|
| `DATABASE_URL` | `postgresql://postgres:pass@127.0.0.1:5432/seniorvital` | `postgresql://user:SECRET@db-host:5432/seniorvital` |
| `JWT_SECRET` | Valor corto de desarrollo (ej. `dev-secret-123`) | Clave aleatoria de ≥64 caracteres |
| `OLLAMA_URL` | `http://localhost:11434` | URL del servidor Ollama en red interna |
| `OLLAMA_MODEL` | `phi3:mini` | Modelo optimizado para producción |
| `EMBEDDING_MODEL_NAME` | `intfloat/multilingual-e5-small` | Modelo de embeddings más grande si la calidad lo justifica |
| `VAPID_PUBLIC_KEY` | *(vacío o test)* | Clave pública generada para el dominio |
| `VAPID_PRIVATE_KEY` | *(vacío o test)* | Clave privada almacenada en secret manager |
| `ENVIRONMENT` | `development` | `production` |

### Recomendaciones por entorno

**Desarrollo:**
- Los valores por defecto están configurados para funcionar out-of-the-box con PostgreSQL y Ollama locales.
- Las credenciales de la base de datos son las de desarrollo (no usar en producción).

**Producción:**
- Usar un secret manager (AWS Secrets Manager, HashiCorp Vault, Azure Key Vault) para `JWT_SECRET`, `VAPID_PRIVATE_KEY` y `DATABASE_URL`.
- Configurar `ENVIRONMENT=production` para desactivar endpoints de documentación y logs verbosos.
- Asegurar que Ollama esté accesible solo desde la red interna (no exponer el puerto 11434 a internet).
- Usar conexiones TLS a PostgreSQL (`sslmode=require` en `DATABASE_URL`).

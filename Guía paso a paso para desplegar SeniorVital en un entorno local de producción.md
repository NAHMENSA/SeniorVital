**Guía paso a paso para desplegar SeniorVital en un entorno local de producción**

A continuación se presenta una guía paso a paso para desplegar **SeniorVital** en un entorno local de producción. Al finalizar, el sistema completo debería estar accesible desde el navegador, con el frontend comunicándose correctamente con el backend y la base de datos.

1.  **Requisitos previos**

Instala el siguiente software (versiones mínimas recomendadas):

**Software**

**Versión**

**Notas**

**Python**

3.10 – 3.12

Usado por todos los microservicios y _workers_

**Node.js**

18.x o 20.x

Para el frontend (React + Vite)

**PostgreSQL**

14 o superior

Base de datos principal

**Git**

cualquier

Para clonar el repositorio

**PowerShell**

5.1+ (Win)

Los scripts \*.ps1 requieren PowerShell (Windows)

**Bash**

4+ (Linux/Mac)

Los scripts \*.sh para entornos Unix

**Opcional (para funcionalidad completa de IA)**

*   **Ollama** con modelo phi3:mini (usado por routines-ai-service y weekly\_analysis.py).
    Si no se instala, los endpoints de rutinas fallarán con timeout, pero el resto del sistema seguirá funcionando.

**Herramientas globales recomendadas**

bash

_\# Windows / Linux / Mac_

pip install --upgrade pip _\# actualizar pip_

npm install -g npm@latest _\# asegurar npm actual_

1.  **Configuración del entorno**

**2.1 Clonar el repositorio**

bash

git clone <url-del-repositorio> E:\\SeniorVital _\# o la ruta que prefieras_

cd E:\\SeniorVital

**2.2 Variables de entorno (.**env**)**

Copia el archivo de ejemplo y edítalo con tus credenciales locales:

bash

copy .env.example .env _\# Windows_

cp .env.example .env _\# Linux / Mac_

Abre .env y asegura los siguientes valores (ajústalos a tu entorno):

ini

_\# PostgreSQL (obligatorio)_

DATABASE\_URL=postgresql://postgres:tu\_contraseña@localhost:5432/seniorvital

_\# JWT para autenticación (obligatorio - genera una clave aleatoria)_

JWT\_SECRET=un\_secreto\_muy\_largo\_y\_aleatorio\_minimo\_32\_caracteres

_\# Opcional (solo si usas Ollama)_

OLLAMA\_HOST=http://localhost:11434

**Nota:** El archivo .env **no debe subirse al control de versiones** (ya está en .gitignore). Contiene credenciales reales.

**2.3 Verificar credenciales de PostgreSQL**

Asegúrate de que el usuario y contraseña coincidan con los que tienes en PostgreSQL.
Prueba la conexión:

bash

psql -U postgres -h localhost -c "SELECT 1"

Si no existe el usuario postgres o la contraseña es otra, modifica DATABASE\_URL en .env.

1.  **Instalación de dependencias**

**3.1 Backend (Python)**

Desde la raíz del proyecto:

bash

_\# Crear y activar entorno virtual_

python -m venv venv

_\# Windows:_

venv\\Scripts\\activate

_\# Linux/Mac:_

source venv/bin/activate

_\# Instalar todas las dependencias del backend (incluye FastAPI, asyncpg, bcrypt, etc.)_

pip install -r requirements.txt

_\# Instalar la librería compartida en modo editable (para que los servicios la encuentren)_

pip install -e .

Si pip install -e . falla porque falta setup.py, alternativamente añade la ruta raíz al PYTHONPATH:

bash

_\# Windows (PowerShell)_

$env:PYTHONPATH = "E:\\SeniorVital"

_\# Linux/Mac_

export PYTHONPATH="$PWD"

**3.2 Frontend (React)**

bash

cd frontend

npm install

cd ..

1.  **Preparación de la base de datos**

**4.1 Crear la base de datos (si no existe)**

bash

_\# Conectarse a PostgreSQL y crear la base de datos_

psql -U postgres -c "CREATE DATABASE seniorvital;"

**4.2 Ejecutar el esquema inicial**

bash

psql -U postgres -d seniorvital -f init\_db.sql

**4.3 Aplicar migraciones adicionales**

bash

psql -U postgres -d seniorvital -f scripts/migrations.sql

**4.4 Verificar tablas**

bash

psql -U postgres -d seniorvital -c "\\dt"

Deberías ver tablas como: users, health\_profiles, exercises, tracking, routines, event\_queue, push\_subscriptions.

1.  **Construcción del frontend**

El frontend debe compilarse para que el _gateway_ sirva los archivos estáticos en producción.

bash

cd frontend

npm run build

cd ..

Esto generará la carpeta frontend/dist/ con el HTML, CSS y JS optimizados.

El _gateway_ está configurado para servir frontend/dist/ cuando se ejecuta en modo producción (variable ENV=production o por defecto si existe la carpeta).

1.  **Arranque del sistema**

**6.1 Usar los scripts oficiales de orquestación**

El proyecto incluye scripts start\_all que levantan todos los microservicios, el _gateway_ y verifican la existencia del frontend compilado.

**Windows (PowerShell):**

bash

.\\scripts\\start\_all.ps1

**Linux / Mac:**

bash

chmod +x scripts/\*.sh

./scripts/start\_all.sh

**¿Qué hace el script?**

*   Inicia cada servicio en segundo plano (auth, catalog, routines‑ai, tracking, dashboard, notification, gateway).
*   Guarda los PID en logs/\*.pid.
*   Redirige la salida a logs/\*.log.
*   Si frontend/dist/ no existe, ejecuta npm run build automáticamente.
*   Espera 3 segundos entre servicios para evitar conflictos de puertos.

**6.2 Puertos de cada servicio (accesibles solo internamente)**

**Servicio**

**Puerto**

**Ruta de acceso vía Gateway**

Gateway (público)

8000

[http://localhost:8000](http://localhost:8000/)

auth-profile-service

8001

[http://localhost:8000/auth/](http://localhost:8000/auth/)\*

catalog-service

8002

[http://localhost:8000/catalog/](http://localhost:8000/catalog/)\*

routines-ai-service

8003

[http://localhost:8000/routines/](http://localhost:8000/routines/)\*

tracking-service

8004

[http://localhost:8000/tracking/](http://localhost:8000/tracking/)\*

dashboard-service

8005

[http://localhost:8000/dashboard/](http://localhost:8000/dashboard/)\*

notification-service

8006

[http://localhost:8000/notify/](http://localhost:8000/notify/)\*

El **único puerto que debes abrir en el navegador** es el **8000**.

**6.3 Detener el sistema**

bash

_\# Windows_

.\\scripts\\stop\_all.ps1

_\# Linux/Mac_

./scripts/stop\_all.sh

**6.4 (Alternativa) Un solo comando con npm**

Si prefieres un flujo tipo npm install && npm run build && npm start, crea un package.json en la raíz con:

json

{

"scripts": {

"install:all": "pip install -r requirements.txt && pip install -e . && cd frontend && npm install",

"build": "cd frontend && npm run build",

"start": "./scripts/start\_all.sh",

"stop": "./scripts/stop\_all.sh"

}

}

Luego ejecuta:

bash

npm run install:all

npm run build

npm start

1.  **Verificación de conectividad y flujos clave**

**7.1 Comprobar que el frontend carga**

Abre [http://localhost:8000](http://localhost:8000/) en el navegador. Debes ver la página de login de SeniorVital.

**7.2 Registrar un nuevo usuario**

*   1.  Haz clic en **"Registrarse"**.
    2.  Introduce email (ej. test@example.com), contraseña y selecciona rol senior.
    3.  Tras el registro, serás redirigido automáticamente al panel principal (/).

**7.3 Probar una llamada a la API**

Abre la consola del navegador (F12) y en la pestaña **Network** deberías ver peticiones a:

*   POST /auth/register
*   POST /auth/login
*   GET /auth/me
*   GET /catalog/exercises

Todas deben responder con **HTTP 200** (o 201 en registro).

**7.4 Verificar que la base de datos recibe datos**

bash

psql -U postgres -d seniorvital -c "SELECT email, role FROM users;"

Debería aparecer el usuario recién registrado.

**7.5 Comprobar logs de servicios**

Cada servicio escribe logs detallados en:

bash

logs/auth-profile.log

logs/catalog.log

logs/routines-ai.log

_\# etc._

Si alguna funcionalidad falla, revisa el log correspondiente.

**7.6 Probar el _smoke test_ automatizado**

bash

_\# Asegúrate de que el sistema esté corriendo_

python scripts/smoke\_test.py

Este script verifica 16 endpoints críticos y reportará si alguno no responde.

1.  **Solución de problemas comunes**

**Problema**

**Posible causa**

**Solución**

ModuleNotFoundError: No module named 'seniorvital\_shared'

PYTHONPATH no incluye la raíz.

Activar entorno virtual y ejecutar pip install -e . o export PYTHONPATH="$PWD"

Error: Cannot connect to PostgreSQL

PostgreSQL no está corriendo o credenciales incorrectas.

Verificar servicio PostgreSQL y editar DATABASE\_URL en .env.

El frontend carga pero las API devuelven 404

El gateway no enruta correctamente.

Comprobar que todos los servicios estén corriendo (tail logs/\*.log).

401 Unauthorized en peticiones autenticadas

Token JWT inválido o expirado.

Revisar JWT\_SECRET en .env; limpiar localStorage en el navegador.

El endpoint /routines/generate se queda colgado

Ollama no instalado o modelo no descargado.

Instalar Ollama y ejecutar ollama pull phi3:mini. O bien usar mocks (los tests lo hacen automáticamente).

1.  **Conclusión**

Siguiendo estos pasos tendrás **SeniorVital** funcionando localmente como en producción:

*   **Base de datos PostgreSQL** con esquema completo.
*   **7 microservicios** + **gateway** orquestados.
*   **Frontend React** compilado y servido por el gateway.
*   **Acceso desde el navegador** en http://localhost:8000.

Para reiniciar el sistema, usa ./scripts/stop\_all.ps1 (o .sh) y luego ./scripts/start\_all.ps1.
Para verificar el correcto funcionamiento, ejecuta python scripts/smoke\_test.py y prueba el flujo de registro/login.

¡El proyecto está listo para ser utilizado o desplegado!
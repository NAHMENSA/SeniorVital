**Captura de nombres y perfil JSONB en el frontend**

1.  **Pantallas del proceso de registro**

El flujo de registro distingue el rol del usuario para solicitar el nombre correspondiente:

*   **Pantalla de selección de rol**:
    Opciones: “Soy Adulto Mayor” o “Soy Familiar / Cuidador”.
*   **Si elige “Adulto Mayor” (rol** senior**)**:
*   Paso 1: Solicitar nombre\_senior (nombre completo).
*   Paso 2: Solicitar email y contraseña.
*   Una vez registrado, redirigir al **onboarding de salud** (edad, peso, restricciones médicas, etc.) que se almacenará en health\_profile (JSONB).
*   **Si elige “Familiar / Cuidador” (**rol caregiver**):**
*   Paso 1: Solicitar nombre\_cuidador (nombre completo del cuidador).
*   Paso 2: Solicitar email y contraseña.
*   Tras el registro, redirigir a la sección “Vincular con adulto mayor” (enviar invitación por email o código). No se pide el nombre del senior en este momento.
*   **Administrador (admin):
    **Se crea por backend (no desde el frontend del MVP).

1.  **Validación y almacenamiento**

*   **Backend (FastAPI Users + JWT)**:
*   En el endpoint /auth/register se espera role (senior, caregiver, admin).
*   Si role = "senior", el campo nombre\_senior es obligatorio y nombre\_cuidador se ignora (se almacena como NULL).
*   Si role = "caregiver", el campo nombre\_cuidador es obligatorio y nombre\_senior es NULL.
*   El resto de datos clínicos y preferencias se guardan después, mediante PATCH /users/me/health-profile con el objeto JSONB.
*   **Mapeo a la tabla users:**
*   nombre\_senior (TEXT) → solo para rol senior.
*   nombre\_cuidador (TEXT) → solo para rol caregiver.
*   health\_profile (JSONB) → contiene edad, peso, restricciones, objetivos, etc.

1.  **Ejemplo de interacción en la interfaz**

**Pseudocódigo del flujo de registro (React + TypeScript)**

tsx

_// Paso 0: selección de rol_

const \[role, setRole\] = useState<'senior' | 'caregiver'>('senior');

_// Paso 1: capturar nombre según rol_

const \[nombreSenior, setNombreSenior\] = useState('');

const \[nombreCuidador, setNombreCuidador\] = useState('');

_// Paso 2: credenciales_

const \[email, setEmail\] = useState('');

const \[password, setPassword\] = useState('');

const handleRegister = async () => {

const payload = {

email,

password,

role,

nombre\_senior: role === 'senior' ? nombreSenior : null,

nombre\_cuidador: role === 'caregiver' ? nombreCuidador : null,

};

await api.post('/auth/register', payload);

_// Tras login, redirigir al onboarding de salud si es senior_

if (role === 'senior') {

navigate('/onboarding/health-profile');

} else {

navigate('/caregiver/link-senior');

}

};

_// Onboarding de salud (solo senior) – almacena en health\_profile_

const saveHealthProfile = async (data) => {

await api.patch('/users/me/health-profile', {

health\_profile: {

age: data.age,

weight\_kg: data.weight,

height\_cm: data.height,

fitness\_level: data.fitnessLevel,

goals: data.goals,

medical\_restrictions: data.restrictions,

equipment: data.equipment,

preferred\_schedule: data.schedule,

},

});

};

1.  **Visualización en los dashboards**

*   **Dashboard del senior**:
    Muestra “Hola, {nombre\_senior}” en el encabezado.
    El health\_profile se usa para personalizar rutinas y no se muestra directamente al senior (solo se muestra edad, restricciones, etc. en sección “Mi perfil”).
*   **Modo cuidador**:
    Cuando el cuidador accede a la vista de un senior vinculado, el panel muestra el nombre\_senior del adulto mayor.
    El cuidador ve su propio nombre\_cuidador en su perfil (menú de usuario).
*   **Panel de administración**:
    Listado de usuarios: columna “Nombre” que muestra nombre\_senior para seniors y nombre\_cuidador para cuidadores.
    Búsqueda por nombre (índice sobre ambas columnas).

**Modelo de base de datos PostgreSQL (esquema completo)**

El siguiente script SQL define todas las tablas, restricciones, índices y comentarios necesarios para el MVP local de SeniorVital, cumpliendo con los requisitos de nombre\_senior y nombre\_cuidador como columnas explícitas, y utilizando JSONB donde se requiere flexibilidad.

sql

_\-- ============================================================_

_\-- Esquema: seniorvital_

_\-- ============================================================_

CREATE SCHEMA IF NOT EXISTS seniorvital;

SET search\_path TO seniorvital;

_\-- ============================================================_

_\-- Tabla: users (autenticación y perfiles)_

_\-- ============================================================_

CREATE TABLE users (

id SERIAL PRIMARY KEY,

email TEXT NOT NULL UNIQUE,

hashed\_password TEXT NOT NULL,

role TEXT NOT NULL CHECK (role IN ('senior', 'caregiver', 'admin')),

nombre\_senior TEXT, _\-- Obligatorio si role='senior'_

nombre\_cuidador TEXT, _\-- Obligatorio si role='caregiver'_

is\_active BOOLEAN DEFAULT TRUE,

created\_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

updated\_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

health\_profile JSONB NOT NULL DEFAULT '{}'::jsonb, _\-- edad, peso, restricciones, etc._

custom\_routine\_override JSONB, _\-- Anulación manual por fisioterapeuta_

preferences JSONB DEFAULT '{}'::jsonb, _\-- Preferencias generales (zona horaria, etc.)_

CONSTRAINT check\_nombres CHECK (

(role = 'senior' AND nombre\_senior IS NOT NULL AND nombre\_cuidador IS NULL) OR

(role = 'caregiver' AND nombre\_cuidador IS NOT NULL AND nombre\_senior IS NULL) OR

(role = 'admin' AND nombre\_senior IS NULL AND nombre\_cuidador IS NULL)

)

);

COMMENT ON TABLE users IS 'Usuarios del sistema: adultos mayores, cuidadores y administradores.';

COMMENT ON COLUMN users.nombre\_senior IS 'Nombre completo del adulto mayor (solo para role senior).';

COMMENT ON COLUMN users.nombre\_cuidador IS 'Nombre completo del familiar/cuidador (solo para role caregiver).';

COMMENT ON COLUMN users.health\_profile IS 'JSONB con edad, peso, altura, nivel de condición física, objetivos, restricciones médicas, equipamiento disponible, horario preferido, etc.';

_\-- Índices para búsquedas frecuentes_

CREATE INDEX idx\_users\_email ON users(email);

CREATE INDEX idx\_users\_nombre\_senior ON users(nombre\_senior) WHERE nombre\_senior IS NOT NULL;

CREATE INDEX idx\_users\_role ON users(role);

_\-- ============================================================_

_\-- Tabla: caregiver\_links (vinculación cuidador-paciente)_

_\-- ============================================================_

CREATE TABLE caregiver\_links (

id SERIAL PRIMARY KEY,

caregiver\_user\_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,

senior\_user\_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,

status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'pending', 'rejected')),

created\_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

UNIQUE(caregiver\_user\_id, senior\_user\_id)

);

COMMENT ON TABLE caregiver\_links IS 'Relación muchos a muchos entre cuidadores y adultos mayores.';

CREATE INDEX idx\_caregiver\_links\_caregiver ON caregiver\_links(caregiver\_user\_id);

CREATE INDEX idx\_caregiver\_links\_senior ON caregiver\_links(senior\_user\_id);

_\-- ============================================================_

_\-- Tabla: exercise\_library (catálogo de ejercicios)_

_\-- ============================================================_

CREATE TABLE exercise\_library (

id SERIAL PRIMARY KEY,

name TEXT NOT NULL,

description TEXT,

progression\_levels JSONB NOT NULL, _\-- Niveles 1..4: { "1": {"desc": "...", "video\_url": "...", "pass\_criteria": "..." }, ... }_

medical\_tags JSONB, _\-- Array de strings: \["artrosis\_rodilla", "hipertension"\]_

muscle\_groups TEXT\[\], _\-- Array nativo de PostgreSQL_

video\_url TEXT, _\-- Ruta en MinIO_

created\_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

updated\_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()

);

COMMENT ON COLUMN exercise\_library.progression\_levels IS 'JSON con hasta 4 niveles de progresión segura.';

COMMENT ON COLUMN exercise\_library.medical\_tags IS 'Contraindicaciones médicas (ej. osteoporosis, artritis).';

_\-- Índices GIN para búsquedas dentro de JSONB_

CREATE INDEX idx\_exercise\_progression ON exercise\_library USING GIN (progression\_levels);

CREATE INDEX idx\_exercise\_medical\_tags ON exercise\_library USING GIN (medical\_tags);

_\-- ============================================================_

_\-- Tabla: workout\_sessions (cabecera de sesión de entrenamiento)_

_\-- ============================================================_

CREATE TABLE workout\_sessions (

id SERIAL PRIMARY KEY,

user\_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,

scheduled\_date DATE NOT NULL, _\-- Día al que pertenece la sesión_

started\_at TIMESTAMP WITH TIME ZONE,

completed\_at TIMESTAMP WITH TIME ZONE,

notes TEXT,

created\_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()

);

COMMENT ON TABLE workout\_sessions IS 'Cada sesión de entrenamiento (rutina diaria).';

CREATE INDEX idx\_workout\_sessions\_user\_date ON workout\_sessions(user\_id, scheduled\_date);

CREATE INDEX idx\_workout\_sessions\_started ON workout\_sessions(started\_at);

_\-- ============================================================_

_\-- Tabla: workout\_exercises (ejercicios dentro de una sesión)_

_\-- ============================================================_

CREATE TABLE workout\_exercises (

id SERIAL PRIMARY KEY,

session\_id INTEGER NOT NULL REFERENCES workout\_sessions(id) ON DELETE CASCADE,

exercise\_id INTEGER REFERENCES exercise\_library(id) ON DELETE RESTRICT,

order\_number INTEGER NOT NULL,

progression\_level\_used INTEGER CHECK (progression\_level\_used BETWEEN 1 AND 4),

notes TEXT

);

CREATE INDEX idx\_workout\_exercises\_session ON workout\_exercises(session\_id);

_\-- ============================================================_

_\-- Tabla: workout\_sets (series individuales de cada ejercicio)_

_\-- ============================================================_

CREATE TABLE workout\_sets (

id SERIAL PRIMARY KEY,

workout\_exercise\_id INTEGER NOT NULL REFERENCES workout\_exercises(id) ON DELETE CASCADE,

set\_number INTEGER NOT NULL,

reps INTEGER CHECK (reps >= 0),

weight\_kg DECIMAL(5,2),

rpe INTEGER CHECK (rpe BETWEEN 1 AND 10), _\-- Escala de esfuerzo percibido_

completed\_at TIMESTAMP WITH TIME ZONE,

rest\_duration\_sec INTEGER CHECK (rest\_duration\_sec >= 0)

);

COMMENT ON COLUMN workout\_sets.rpe IS 'Rating of Perceived Exertion (1-10) con ayuda visual de emojis.';

CREATE INDEX idx\_workout\_sets\_exercise ON workout\_sets(workout\_exercise\_id);

_\-- ============================================================_

_\-- Tabla: daily\_habits (registro manual de agua y sueño)_

_\-- ============================================================_

CREATE TABLE daily\_habits (

id SERIAL PRIMARY KEY,

user\_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,

date DATE NOT NULL,

water\_intake\_glasses INTEGER DEFAULT 0 CHECK (water\_intake\_glasses >= 0),

sleep\_hours DECIMAL(3,1) CHECK (sleep\_hours >= 0 AND sleep\_hours <= 24),

created\_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

updated\_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

UNIQUE(user\_id, date)

);

CREATE INDEX idx\_daily\_habits\_user\_date ON daily\_habits(user\_id, date);

_\-- ============================================================_

_\-- Tabla: notifications\_prefs (preferencias y suscripción a Web Push)_

_\-- ============================================================_

CREATE TABLE notifications\_prefs (

id SERIAL PRIMARY KEY,

user\_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,

push\_subscription JSONB, _\-- Objeto { endpoint, keys, ... }_

quiet\_mode BOOLEAN DEFAULT FALSE,

preferred\_time TIME, _\-- Horario preferido para recordatorios_

reminder\_enabled BOOLEAN DEFAULT TRUE,

updated\_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()

);

COMMENT ON COLUMN notifications\_prefs.push\_subscription IS 'Suscripción Web Push API (endpoint, p256dh, auth).';

_\-- ============================================================_

_\-- Tabla: agent\_queue (cola de comandos entre agentes IA)_

_\-- ============================================================_

CREATE TABLE agent\_queue (

id SERIAL PRIMARY KEY,

command\_type TEXT NOT NULL, _\-- 'adjust\_routine', 'generate\_insight', 'detect\_plateau'_

payload JSONB NOT NULL, _\-- Datos específicos del comando_

status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),

created\_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

processed\_at TIMESTAMP WITH TIME ZONE,

error\_message TEXT

);

CREATE INDEX idx\_agent\_queue\_status ON agent\_queue(status);

CREATE INDEX idx\_agent\_queue\_created ON agent\_queue(created\_at);

_\-- ============================================================_

_\-- Tabla: agent\_insights (insights generados por el Agente Preventivo)_

_\-- ============================================================_

CREATE TABLE agent\_insights (

id SERIAL PRIMARY KEY,

user\_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,

insight\_type TEXT NOT NULL, _\-- 'projection', 'motivation', 'plateau\_detection'_

message TEXT NOT NULL,

metadata JSONB, _\-- Datos adicionales (fecha proyectada, etc.)_

displayed BOOLEAN DEFAULT FALSE,

generated\_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()

);

CREATE INDEX idx\_agent\_insights\_user\_displayed ON agent\_insights(user\_id, displayed);

_\-- ============================================================_

_\-- Tabla: admin\_logs (opcional – auditoría de acciones de administradores)_

_\-- ============================================================_

CREATE TABLE admin\_logs (

id SERIAL PRIMARY KEY,

admin\_user\_id INTEGER NOT NULL REFERENCES users(id) ON DELETE SET NULL,

action TEXT NOT NULL,

target\_user\_id INTEGER REFERENCES users(id) ON DELETE SET NULL,

details JSONB,

created\_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()

);

CREATE INDEX idx\_admin\_logs\_admin ON admin\_logs(admin\_user\_id);

CREATE INDEX idx\_admin\_logs\_created ON admin\_logs(created\_at);

_\-- ============================================================_

_\-- Función para actualizar updated\_at automáticamente_

_\-- ============================================================_

CREATE OR REPLACE FUNCTION update\_updated\_at\_column()

RETURNS TRIGGER AS $$

BEGIN

NEW.updated\_at = NOW();

RETURN NEW;

END;

$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger\_users\_updated\_at BEFORE UPDATE ON users

FOR EACH ROW EXECUTE FUNCTION update\_updated\_at\_column();

CREATE TRIGGER trigger\_exercise\_library\_updated\_at BEFORE UPDATE ON exercise\_library

FOR EACH ROW EXECUTE FUNCTION update\_updated\_at\_column();

CREATE TRIGGER trigger\_daily\_habits\_updated\_at BEFORE UPDATE ON daily\_habits

FOR EACH ROW EXECUTE FUNCTION update\_updated\_at\_column();

CREATE TRIGGER trigger\_notifications\_prefs\_updated\_at BEFORE UPDATE ON notifications\_prefs

FOR EACH ROW EXECUTE FUNCTION update\_updated\_at\_column();

_\-- ============================================================_

_\-- Ejemplo de inserción de un usuario senior con health\_profile_

_\-- ============================================================_

_/\*_

INSERT INTO users (email, hashed\_password, role, nombre\_senior, health\_profile)

VALUES (

'juan.perez@example.com',

'hashed\_fake',

'senior',

'Juan Pérez',

'{

"age": 70,

"weight\_kg": 65,

"height\_cm": 158,

"fitness\_level": "principiante",

"goals": \["movilidad"\],

"medical\_restrictions": \["artrosis\_rodilla"\],

"equipment": \["silla"\],

"preferred\_schedule": "10:00"

}'::jsonb

);

\*/

Este modelo cumple con:

*   Columnas nombre\_senior y nombre\_cuidador explícitas para búsqueda/visualización.
*   JSONB en health\_profile, progression\_levels, medical\_tags, custom\_routine\_override, agent\_insights.metadata.
*   Índices necesarios para rendimiento.
*   Soporte para vinculación cuidador-paciente, registro de sesiones y series, hábitos diarios, notificaciones push y cola de comandos entre agentes.
*   Compatibilidad con la arquitectura offline-first (el esquema maestro puede replicarse en cliente mediante Sync).

El script es autocontenido y se ejecuta directamente en PostgreSQL + (con extensión JSONB nativa).
-- ============================================================
-- Esquema: seniorvital
-- ============================================================
CREATE SCHEMA IF NOT EXISTS seniorvital;
SET search_path TO seniorvital;

-- ============================================================
-- Tabla: users (autenticación y perfiles)
-- ============================================================
CREATE TABLE users (
    id                SERIAL PRIMARY KEY,
    email             TEXT NOT NULL UNIQUE,
    password          TEXT NOT NULL,
    role              TEXT NOT NULL CHECK (role IN ('senior', 'caregiver', 'admin')),
    profile           JSONB DEFAULT '{}',
    linked_senior_id  INTEGER,
    nombre_senior     TEXT,                     -- Obligatorio si role='senior'
    nombre_cuidador   TEXT,                     -- Obligatorio si role='caregiver'
    is_active         BOOLEAN DEFAULT TRUE,
    created_at        TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at        TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    health_profile    JSONB NOT NULL DEFAULT '{}'::jsonb,   -- edad, peso, restricciones, etc.
    custom_routine_override JSONB,                          -- Anulación manual por fisioterapeuta
    preferences       JSONB DEFAULT '{}'::jsonb,            -- Preferencias generales (zona horaria, etc.)
    CONSTRAINT check_nombres CHECK (
        (role = 'senior' AND nombre_senior IS NOT NULL AND nombre_cuidador IS NULL) OR
        (role = 'caregiver' AND nombre_cuidador IS NOT NULL AND nombre_senior IS NULL) OR
        (role = 'admin' AND nombre_senior IS NULL AND nombre_cuidador IS NULL)
    )
);

COMMENT ON TABLE users IS 'Usuarios del sistema: adultos mayores, cuidadores y administradores.';
COMMENT ON COLUMN users.password IS 'Contraseña hasheada con bcrypt.';
COMMENT ON COLUMN users.profile IS 'Perfil JSONB adicional del usuario.';
COMMENT ON COLUMN users.linked_senior_id IS 'ID del senior vinculado (para cuidadores).';
COMMENT ON COLUMN users.nombre_senior IS 'Nombre completo del adulto mayor (solo para role senior).';
COMMENT ON COLUMN users.nombre_cuidador IS 'Nombre completo del familiar/cuidador (solo para role caregiver).';
COMMENT ON COLUMN users.health_profile IS 'JSONB con edad, peso, altura, nivel de condición física, objetivos, restricciones médicas, equipamiento disponible, horario preferido, etc.';

-- Índices para búsquedas frecuentes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_nombre_senior ON users(nombre_senior) WHERE nombre_senior IS NOT NULL;
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_linked_senior ON users(linked_senior_id) WHERE linked_senior_id IS NOT NULL;

-- ============================================================
-- Tabla: caregiver_links (vinculación cuidador-paciente)
-- ============================================================
CREATE TABLE caregiver_links (
    id                  SERIAL PRIMARY KEY,
    caregiver_user_id   INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    senior_user_id      INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status              TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'pending', 'rejected')),
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(caregiver_user_id, senior_user_id)
);

COMMENT ON TABLE caregiver_links IS 'Relación muchos a muchos entre cuidadores y adultos mayores.';
CREATE INDEX idx_caregiver_links_caregiver ON caregiver_links(caregiver_user_id);
CREATE INDEX idx_caregiver_links_senior ON caregiver_links(senior_user_id);

-- ============================================================
-- Tabla: exercises (catálogo de ejercicios)
-- ============================================================
CREATE TABLE exercises (
    id              SERIAL PRIMARY KEY,
    name            TEXT NOT NULL,
    level           INTEGER NOT NULL DEFAULT 1 CHECK (level BETWEEN 1 AND 4),
    contraindications TEXT DEFAULT '',
    video_url       TEXT DEFAULT '',
    description     TEXT,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE exercises IS 'Catálogo de ejercicios con niveles de progresión 1-4.';
COMMENT ON COLUMN exercises.level IS 'Nivel de dificultad: 1 (principiante) a 4 (avanzado).';
COMMENT ON COLUMN exercises.contraindications IS 'Lista separada por comas de contraindicaciones médicas.';
CREATE INDEX idx_exercises_level ON exercises(level);

-- ============================================================
-- Tabla: workout_sessions (cabecera de sesión de entrenamiento)
-- ============================================================
CREATE TABLE workout_sessions (
    id             SERIAL PRIMARY KEY,
    user_id        INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    scheduled_date DATE NOT NULL,                 -- Día al que pertenece la sesión
    started_at     TIMESTAMP WITH TIME ZONE,
    completed_at   TIMESTAMP WITH TIME ZONE,
    notes          TEXT,
    created_at     TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE workout_sessions IS 'Cada sesión de entrenamiento (rutina diaria).';
CREATE INDEX idx_workout_sessions_user_date ON workout_sessions(user_id, scheduled_date);
CREATE INDEX idx_workout_sessions_started ON workout_sessions(started_at);

-- ============================================================
-- Tabla: workout_exercises (ejercicios dentro de una sesión)
-- ============================================================
CREATE TABLE workout_exercises (
    id                      SERIAL PRIMARY KEY,
    session_id              INTEGER NOT NULL REFERENCES workout_sessions(id) ON DELETE CASCADE,
    exercise_id             INTEGER REFERENCES exercises(id) ON DELETE RESTRICT,
    order_number            INTEGER NOT NULL,
    progression_level_used  INTEGER CHECK (progression_level_used BETWEEN 1 AND 4),
    notes                   TEXT
);

CREATE INDEX idx_workout_exercises_session ON workout_exercises(session_id);

-- ============================================================
-- Tabla: workout_sets (series individuales de cada ejercicio)
-- ============================================================
CREATE TABLE workout_sets (
    id                    SERIAL PRIMARY KEY,
    workout_exercise_id   INTEGER NOT NULL REFERENCES workout_exercises(id) ON DELETE CASCADE,
    set_number            INTEGER NOT NULL,
    reps                  INTEGER CHECK (reps >= 0),
    weight_kg             DECIMAL(5,2),
    rpe                   INTEGER CHECK (rpe BETWEEN 1 AND 10),   -- Escala de esfuerzo percibido
    completed_at          TIMESTAMP WITH TIME ZONE,
    rest_duration_sec     INTEGER CHECK (rest_duration_sec >= 0)
);

COMMENT ON COLUMN workout_sets.rpe IS 'Rating of Perceived Exertion (1-10) con ayuda visual de emojis.';
CREATE INDEX idx_workout_sets_exercise ON workout_sets(workout_exercise_id);

-- ============================================================
-- Tabla: tracking (registro de ejercicios completados)
-- ============================================================
CREATE TABLE tracking (
    id             SERIAL PRIMARY KEY,
    user_id        INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    exercise_id    INTEGER REFERENCES exercises(id) ON DELETE SET NULL,
    sets           INTEGER DEFAULT 1,
    reps           INTEGER DEFAULT 0,
    rpe            INTEGER CHECK (rpe BETWEEN 1 AND 10),
    felt_difficulty TEXT,
    completed_at   TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE tracking IS 'Histórico de ejercicios completados por usuario.';
CREATE INDEX idx_tracking_user_id ON tracking(user_id);

-- ============================================================
-- Tabla: routines (rutinas diarias generadas por IA)
-- ============================================================
CREATE TABLE routines (
    id         SERIAL PRIMARY KEY,
    user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    date       DATE NOT NULL,
    active     BOOLEAN DEFAULT TRUE,
    exercises  JSONB DEFAULT '[]',
    warmup     TEXT DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE routines IS 'Rutinas diarias generadas por el servicio de IA.';
CREATE INDEX idx_routines_user_date ON routines(user_id, date);

-- ============================================================
-- Tabla: projections (proyecciones y insights semanales)
-- ============================================================
CREATE TABLE projections (
    id             SERIAL PRIMARY KEY,
    user_id        INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    week_start     DATE NOT NULL,
    insight_text   TEXT DEFAULT '',
    estimated_level INTEGER,
    created_at     TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE projections IS 'Proyecciones de progreso e insights semanales del dashboard.';
CREATE INDEX idx_projections_user_id ON projections(user_id);

-- ============================================================
-- Tabla: habits (registro manual de agua y sueño)
-- ============================================================
CREATE TABLE habits (
    id                   SERIAL PRIMARY KEY,
    user_id              INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    date                 DATE NOT NULL,
    water_intake_glasses INTEGER DEFAULT 0 CHECK (water_intake_glasses >= 0),
    sleep_hours          DECIMAL(3,1) CHECK (sleep_hours >= 0 AND sleep_hours <= 24),
    created_at           TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at           TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, date)
);

CREATE INDEX idx_habits_user_date ON habits(user_id, date);

-- ============================================================
-- Tabla: push_subscriptions (suscripción Web Push por usuario)
-- ============================================================
CREATE TABLE push_subscriptions (
    user_id   TEXT PRIMARY KEY,
    endpoint  TEXT NOT NULL,
    p256dh    TEXT NOT NULL,
    auth      TEXT NOT NULL
);

COMMENT ON TABLE push_subscriptions IS 'Suscripciones Web Push API para notificaciones al navegador.';

-- ============================================================
-- Tabla: event_queue (cola de eventos para replicación async)
-- ============================================================
CREATE TABLE event_queue (
    id           SERIAL PRIMARY KEY,
    stream_name  TEXT NOT NULL,
    payload      JSONB DEFAULT '{}',
    processed    BOOLEAN DEFAULT FALSE,
    created_at   TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE
);

COMMENT ON TABLE event_queue IS 'Cola de eventos para replicación asíncrona a DuckDB y procesamiento de trabajadores.';
CREATE INDEX idx_event_queue_stream_status ON event_queue(stream_name, processed);
CREATE INDEX idx_event_queue_created ON event_queue(created_at);

-- ============================================================
-- Tabla: agent_queue (cola de comandos entre agentes IA)
-- ============================================================
CREATE TABLE agent_queue (
    id             SERIAL PRIMARY KEY,
    command_type   TEXT NOT NULL,          -- 'adjust_routine', 'generate_insight', 'detect_plateau'
    payload        JSONB NOT NULL,         -- Datos específicos del comando
    status         TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    created_at     TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at   TIMESTAMP WITH TIME ZONE,
    error_message  TEXT
);

CREATE INDEX idx_agent_queue_status ON agent_queue(status);
CREATE INDEX idx_agent_queue_created ON agent_queue(created_at);

-- ============================================================
-- Tabla: agent_insights (insights generados por el Agente Preventivo)
-- ============================================================
CREATE TABLE agent_insights (
    id           SERIAL PRIMARY KEY,
    user_id      INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    insight_type TEXT NOT NULL,          -- 'projection', 'motivation', 'plateau_detection'
    message      TEXT NOT NULL,
    metadata     JSONB,                  -- Datos adicionales (fecha proyectada, etc.)
    displayed    BOOLEAN DEFAULT FALSE,
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_agent_insights_user_displayed ON agent_insights(user_id, displayed);

-- ============================================================
-- Tabla: admin_logs (opcional – auditoría de acciones de administradores)
-- ============================================================
CREATE TABLE admin_logs (
    id             SERIAL PRIMARY KEY,
    admin_user_id  INTEGER NOT NULL REFERENCES users(id) ON DELETE SET NULL,
    action         TEXT NOT NULL,
    target_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    details        JSONB,
    created_at     TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_admin_logs_admin ON admin_logs(admin_user_id);
CREATE INDEX idx_admin_logs_created ON admin_logs(created_at);

-- ============================================================
-- Función para actualizar updated_at automáticamente
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_exercises_updated_at BEFORE UPDATE ON exercises
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_habits_updated_at BEFORE UPDATE ON habits
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- Ejemplo de inserción de un usuario senior con health_profile
-- ============================================================
/*
INSERT INTO users (email, password, role, nombre_senior, health_profile)
VALUES (
    'juan.perez@example.com',
    'hashed_fake',
    'senior',
    'Juan Pérez',
    '{
        "age": 70,
        "weight_kg": 65,
        "height_cm": 158,
        "fitness_level": "principiante",
        "goals": ["movilidad"],
        "medical_restrictions": ["artrosis_rodilla"],
        "equipment": ["silla"],
        "preferred_schedule": "10:00"
    }'::jsonb
);
*/

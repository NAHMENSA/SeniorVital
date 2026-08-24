-- ============================================================
-- Fix: Recrear todas las tablas para SeniorVital
-- Sincronizado completamente con init_db.sql
-- ============================================================

DROP TABLE IF EXISTS admin_logs CASCADE;
DROP TABLE IF EXISTS agent_insights CASCADE;
DROP TABLE IF EXISTS agent_queue CASCADE;
DROP TABLE IF EXISTS push_subscriptions CASCADE;
DROP TABLE IF EXISTS habits CASCADE;
DROP TABLE IF EXISTS projections CASCADE;
DROP TABLE IF EXISTS routines CASCADE;
DROP TABLE IF EXISTS workout_sets CASCADE;
DROP TABLE IF EXISTS workout_exercises CASCADE;
DROP TABLE IF EXISTS workout_sessions CASCADE;
DROP TABLE IF EXISTS tracking CASCADE;
DROP TABLE IF EXISTS exercises CASCADE;
DROP TABLE IF EXISTS caregiver_links CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- =========== users ===========
CREATE TABLE users (
    id                SERIAL PRIMARY KEY,
    email             TEXT NOT NULL UNIQUE,
    password          TEXT NOT NULL,
    role              TEXT NOT NULL CHECK (role IN ('senior', 'caregiver', 'admin')),
    profile           JSONB DEFAULT '{}',
    linked_senior_id  INTEGER,
    nombre_senior     TEXT,
    nombre_cuidador   TEXT,
    is_active         BOOLEAN DEFAULT TRUE,
    created_at        TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at        TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    health_profile    JSONB NOT NULL DEFAULT '{}'::jsonb,
    custom_routine_override JSONB,
    preferences       JSONB DEFAULT '{}'::jsonb,
    CONSTRAINT check_nombres CHECK (
        (role = 'senior' AND nombre_senior IS NOT NULL AND nombre_cuidador IS NULL) OR
        (role = 'caregiver' AND nombre_cuidador IS NOT NULL AND nombre_senior IS NULL) OR
        (role = 'admin' AND nombre_senior IS NULL AND nombre_cuidador IS NULL)
    )
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_nombre_senior ON users(nombre_senior) WHERE nombre_senior IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_linked_senior ON users(linked_senior_id) WHERE linked_senior_id IS NOT NULL;

-- =========== caregiver_links ===========
CREATE TABLE caregiver_links (
    id                  SERIAL PRIMARY KEY,
    caregiver_user_id   INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    senior_user_id      INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status              TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'pending', 'rejected')),
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(caregiver_user_id, senior_user_id)
);

CREATE INDEX IF NOT EXISTS idx_caregiver_links_caregiver ON caregiver_links(caregiver_user_id);
CREATE INDEX IF NOT EXISTS idx_caregiver_links_senior ON caregiver_links(senior_user_id);

-- =========== exercises ===========
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

CREATE INDEX IF NOT EXISTS idx_exercises_level ON exercises(level);

-- =========== workout_sessions ===========
CREATE TABLE workout_sessions (
    id             SERIAL PRIMARY KEY,
    user_id        INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    scheduled_date DATE NOT NULL,
    started_at     TIMESTAMP WITH TIME ZONE,
    completed_at   TIMESTAMP WITH TIME ZONE,
    notes          TEXT,
    created_at     TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_workout_sessions_user_date ON workout_sessions(user_id, scheduled_date);
CREATE INDEX IF NOT EXISTS idx_workout_sessions_started ON workout_sessions(started_at);

-- =========== workout_exercises ===========
CREATE TABLE workout_exercises (
    id                      SERIAL PRIMARY KEY,
    session_id              INTEGER NOT NULL REFERENCES workout_sessions(id) ON DELETE CASCADE,
    exercise_id             INTEGER REFERENCES exercises(id) ON DELETE RESTRICT,
    order_number            INTEGER NOT NULL,
    progression_level_used  INTEGER CHECK (progression_level_used BETWEEN 1 AND 4),
    notes                   TEXT
);

CREATE INDEX IF NOT EXISTS idx_workout_exercises_session ON workout_exercises(session_id);

-- =========== workout_sets ===========
CREATE TABLE workout_sets (
    id                    SERIAL PRIMARY KEY,
    workout_exercise_id   INTEGER NOT NULL REFERENCES workout_exercises(id) ON DELETE CASCADE,
    set_number            INTEGER NOT NULL,
    reps                  INTEGER CHECK (reps >= 0),
    weight_kg             DECIMAL(5,2),
    rpe                   INTEGER CHECK (rpe BETWEEN 1 AND 10),
    completed_at          TIMESTAMP WITH TIME ZONE,
    rest_duration_sec     INTEGER CHECK (rest_duration_sec >= 0)
);

CREATE INDEX IF NOT EXISTS idx_workout_sets_exercise ON workout_sets(workout_exercise_id);

-- =========== tracking ===========
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

CREATE INDEX IF NOT EXISTS idx_tracking_user_id ON tracking(user_id);
CREATE INDEX IF NOT EXISTS idx_tracking_completed_at ON tracking(completed_at);

-- =========== routines ===========
CREATE TABLE routines (
    id           SERIAL PRIMARY KEY,
    user_id      INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    date         DATE NOT NULL,
    active       BOOLEAN DEFAULT TRUE,
    exercises    JSONB DEFAULT '[]',
    warmup       TEXT DEFAULT '',
    generated_by TEXT DEFAULT 'ollama',
    created_at   TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_routines_user_date ON routines(user_id, date);

-- =========== projections ===========
CREATE TABLE projections (
    id             SERIAL PRIMARY KEY,
    user_id        INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    week_start     DATE NOT NULL,
    insight_text   TEXT DEFAULT '',
    estimated_level INTEGER,
    created_at     TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_projections_user_id ON projections(user_id);

-- =========== habits ===========
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

CREATE INDEX IF NOT EXISTS idx_habits_user_date ON habits(user_id, date);

-- =========== event_queue ===========
CREATE TABLE event_queue (
    id           SERIAL PRIMARY KEY,
    stream_name  TEXT NOT NULL,
    payload      JSONB DEFAULT '{}',
    processed    BOOLEAN DEFAULT FALSE,
    created_at   TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_event_queue_stream_status ON event_queue(stream_name, processed);
CREATE INDEX IF NOT EXISTS idx_event_queue_created ON event_queue(created_at);

-- =========== agent_queue ===========
CREATE TABLE agent_queue (
    id             SERIAL PRIMARY KEY,
    command_type   TEXT NOT NULL,
    payload        JSONB NOT NULL,
    status         TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    created_at     TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at   TIMESTAMP WITH TIME ZONE,
    error_message  TEXT
);

CREATE INDEX IF NOT EXISTS idx_agent_queue_status ON agent_queue(status);
CREATE INDEX IF NOT EXISTS idx_agent_queue_created ON agent_queue(created_at);

-- =========== agent_insights ===========
CREATE TABLE agent_insights (
    id           SERIAL PRIMARY KEY,
    user_id      INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    insight_type TEXT NOT NULL,
    message      TEXT NOT NULL,
    metadata     JSONB,
    displayed    BOOLEAN DEFAULT FALSE,
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_agent_insights_user_displayed ON agent_insights(user_id, displayed);

-- =========== push_subscriptions ===========
CREATE TABLE push_subscriptions (
    user_id   TEXT PRIMARY KEY,
    endpoint  TEXT NOT NULL,
    p256dh    TEXT NOT NULL,
    auth      TEXT NOT NULL
);

-- =========== admin_logs ===========
CREATE TABLE admin_logs (
    id             SERIAL PRIMARY KEY,
    admin_user_id  INTEGER NOT NULL REFERENCES users(id) ON DELETE SET NULL,
    action         TEXT NOT NULL,
    target_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    details        JSONB,
    created_at     TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_admin_logs_admin ON admin_logs(admin_user_id);
CREATE INDEX IF NOT EXISTS idx_admin_logs_created ON admin_logs(created_at);

-- =========== conversation_history (S2-03 — memoria conversacional) ===========
CREATE TABLE conversation_history (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role        TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content     TEXT NOT NULL,
    metadata    JSONB DEFAULT '{}',
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_conv_history_user_created
    ON conversation_history(user_id, created_at DESC);

-- Note: updated_at triggers are defined in init_db.sql for manual DB setup.
-- Application code manually sets updated_at = NOW() in UPDATE queries.
-- Do NOT include CREATE FUNCTION/trigger here — asyncpg cannot parse
-- dollar-quoted ($ $) strings in batch execute().

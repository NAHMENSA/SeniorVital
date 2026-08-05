-- Migration: Add missing columns to users table (from old init_db.sql schema)
-- The old init_db.sql used hashed_password instead of password
-- and did not have profile or linked_senior_id columns
ALTER TABLE users ADD COLUMN IF NOT EXISTS password TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS profile JSONB DEFAULT '{}';
ALTER TABLE users ADD COLUMN IF NOT EXISTS linked_senior_id INTEGER;

-- Migration: Create exercises table (renamed from exercise_library)
CREATE TABLE IF NOT EXISTS exercises (
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

-- Migration: Create tracking table
CREATE TABLE IF NOT EXISTS tracking (
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

-- Migration: Create routines table
CREATE TABLE IF NOT EXISTS routines (
    id         SERIAL PRIMARY KEY,
    user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    date       DATE NOT NULL,
    active     BOOLEAN DEFAULT TRUE,
    exercises  JSONB DEFAULT '[]',
    warmup     TEXT DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_routines_user_date ON routines(user_id, date);

-- Migration: Create projections table
CREATE TABLE IF NOT EXISTS projections (
    id             SERIAL PRIMARY KEY,
    user_id        INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    week_start     DATE NOT NULL,
    insight_text   TEXT DEFAULT '',
    estimated_level INTEGER,
    created_at     TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_projections_user_id ON projections(user_id);

-- Migration: Create habits table (renamed from daily_habits)
CREATE TABLE IF NOT EXISTS habits (
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

-- Migration: Create push_subscriptions table
CREATE TABLE IF NOT EXISTS push_subscriptions (
    user_id   TEXT PRIMARY KEY,
    endpoint  TEXT NOT NULL,
    p256dh    TEXT NOT NULL,
    auth      TEXT NOT NULL
);

-- Migration: Create event_queue table
CREATE TABLE IF NOT EXISTS event_queue (
    id           SERIAL PRIMARY KEY,
    stream_name  TEXT NOT NULL,
    payload      JSONB DEFAULT '{}',
    processed    BOOLEAN DEFAULT FALSE,
    created_at   TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE
);
CREATE INDEX IF NOT EXISTS idx_event_queue_stream_status ON event_queue(stream_name, processed);
CREATE INDEX IF NOT EXISTS idx_event_queue_created ON event_queue(created_at);

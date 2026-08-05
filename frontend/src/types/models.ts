// ── Enums ──
export type Role = 'senior' | 'caregiver' | 'admin'
export type CaregiverLinkStatus = 'active' | 'pending' | 'rejected'
export type AgentCommandType = 'adjust_routine' | 'generate_insight' | 'detect_plateau'
export type AgentCommandStatus = 'pending' | 'processing' | 'completed' | 'failed'
export type InsightType = 'projection' | 'motivation' | 'plateau_detection'
export type FitnessLevel = 'principiante' | 'intermedio' | 'avanzado'
export type Goal = 'movilidad' | 'fuerza' | 'flexibilidad' | 'equilibrio' | 'resistencia'
export type MedicalRestriction = 'artrosis_rodilla' | 'osteoporosis' | 'hipertension' | 'artritis' | 'dolor_articular' | 'prótesis' | 'diabetes' | 'cardiopatia'
export type Equipment = 'ninguno' | 'silla' | 'bandas_elasticas' | 'pesas_ligeras' | 'colchoneta'

// ── Health Profile (JSONB) ──
export interface HealthProfile {
  age: number
  weight_kg: number
  height_cm: number
  fitness_level: FitnessLevel
  goals: Goal[]
  medical_restrictions: MedicalRestriction[]
  equipment: Equipment[]
  preferred_schedule: string // HH:MM
}

// ── User ──
export interface User {
  id: string
  email: string
  role: Role
  nombre_senior: string | null
  nombre_cuidador: string | null
  is_active: boolean
  created_at: string
  updated_at: string
  health_profile: HealthProfile
  custom_routine_override: RoutineOverride | null
  preferences: Record<string, unknown>
}

export interface RoutineOverride {
  exclude_exercise_ids?: number[]
  custom_notes?: string
  forced_level?: 1 | 2 | 3 | 4
  series_adjustment?: { exercise_id: number; sets: number; reps: number }[]
}

// ── Auth ──
export interface RegisterPayload {
  email: string
  password: string
  role: Role
  nombre_senior?: string
  nombre_cuidador?: string
}

export interface LoginPayload {
  email: string
  password: string
}

export interface AuthResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

// ── Exercise Library ──
export interface ProgressionLevel {
  desc: string
  video_url: string
  pass_criteria: string
}

export interface ExerciseCreatePayload {
  name: string
  level: number
  contraindications: MedicalRestriction[]
  video_url?: string
  description?: string
}

export interface Exercise {
  id: string | number
  name: string
  description: string
  video_url: string
  created_at: string
  updated_at: string
}

// ── Workout / Routine ──
export interface RoutineExercise {
  exercise_id: number | string
  name: string
  description: string
  progression_level_used: 1 | 2 | 3 | 4
  video_url: string
  sets: number
  reps_per_set: number
  rest_duration_sec: number
  order_number: number
}

export interface DailyRoutine {
  id: string
  user_id: string
  scheduled_date: string
  exercises: RoutineExercise[]
  notes?: string
  generated_at: string
  generated_by?: 'ollama' | 'fallback'
  llm_available?: boolean
  llm_model?: string | null
  llm_error?: string | null
}

export interface WorkoutSet {
  id?: string
  workout_exercise_id?: string
  set_number: number
  reps: number
  weight_kg?: number
  rpe: number
  completed_at: string
  rest_duration_sec: number
}

export interface TrackEntryPayload {
  user_id: string
  exercise_id: number | string
  sets: number
  reps: number
  rpe: number
  felt_difficulty?: string
  completed_at: string
}

// ── Dashboard ──
export interface ProgressData {
  sessions_this_week: number
  current_streak: number
  total_sessions: number
  rpe_trend: { date: string; avg_rpe: number }[]
  calendar: Record<string, { completed: boolean; rpe_avg: number }>
  projection?: string
  insight?: AgentInsight
}

export interface AgentInsight {
  id: string
  insight_type: InsightType
  message: string
  metadata?: Record<string, unknown>
  generated_at: string
}

// ── Daily Habits ──
export interface DailyHabits {
  id?: string
  user_id: string
  date: string
  water_intake_glasses: number
  sleep_hours: number
}

// ── Caregiver ──
export interface CaregiverLink {
  id: string
  caregiver_user_id: string
  senior_user_id: string
  status: CaregiverLinkStatus
  created_at: string
  senior_name?: string
}

export type AlertType = 'fatigue' | 'inactivity' | 'general'
export type AlertSeverity = 'low' | 'medium' | 'high'

export interface CaregiverAlert {
  id: string
  type: AlertType
  severity: AlertSeverity
  title: string
  message: string
  senior_name: string
  senior_id: string
  created_at: string
  read: boolean
}

export interface CaregiverReport {
  id: string
  senior_id: string
  senior_name: string
  period_start: string
  period_end: string
  sessions_completed: number
  avg_rpe: number
  streak_days: number
  recommendations: string[]
  created_at: string
}

export interface SeniorProgressResponse {
  senior_name: string
  progress: ProgressData | null
}

// ── Admin ──
export type RiskTrafficLight = 'green' | 'amber' | 'red'

export interface AdminPatient {
  id: string
  nombre_senior: string
  email: string
  risk: RiskTrafficLight
  last_session: string | null
  streak: number
  rpe_trend: 'improving' | 'stable' | 'declining'
  total_sessions: number
}

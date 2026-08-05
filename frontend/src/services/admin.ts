import { api } from './api'
import type { AdminPatient, ExerciseCreatePayload, RoutineOverride } from '../types/models'

export function getPatients() {
  return api<AdminPatient[]>('/admin/users')
}

export function setRoutineOverride(userId: string, override: RoutineOverride) {
  return api(`/admin/users/${userId}/routine-override`, {
    method: 'PUT',
    body: JSON.stringify({ custom_routine_override: override }),
  })
}

export function createExercise(data: ExerciseCreatePayload) {
  return api<Exercise>('/catalog/exercises', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

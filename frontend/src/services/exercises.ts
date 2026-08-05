import { api } from './api'
import type { Exercise } from '../types/models'

export function getExercises() {
  return api<Exercise[]>('/catalog/exercises')
}

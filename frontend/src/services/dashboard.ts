import { api } from './api'
import type { ProgressData } from '../types/models'

export function getProgress(userId: string) {
  return api<ProgressData>(`/dashboard/progress/${userId}`)
}

export function getHistory(userId: string) {
  return api<ProgressData>(`/dashboard/history/${userId}`)
}

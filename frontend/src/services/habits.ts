import { api } from './api'
import type { DailyHabits } from '../types/models'

export function getTodayHabits(userId: string) {
  return api<DailyHabits>(`/habits/today?user_id=${userId}`)
}

export function saveHabits(data: Partial<DailyHabits> & { user_id: string; date: string }) {
  return api<DailyHabits>('/habits', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

import { useQuery } from '@tanstack/react-query'
import { getExercises } from '../services/exercises'
import type { Exercise } from '../types/models'

export function useExercises() {
  return useQuery<Exercise[]>({
    queryKey: ['exercises'],
    queryFn: getExercises,
    staleTime: 1000 * 60 * 30,
  })
}

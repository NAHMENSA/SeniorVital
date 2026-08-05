import { useQuery } from '@tanstack/react-query'
import { getProgress } from '../services/dashboard'
import type { ProgressData } from '../types/models'

export function useProgress(userId: string | undefined) {
  return useQuery<ProgressData | null>({
    queryKey: ['progress', userId],
    queryFn: async () => {
      if (!userId) return null
      return getProgress(userId)
    },
    enabled: !!userId,
    retry: 1,
    staleTime: 1000 * 60 * 2,
  })
}

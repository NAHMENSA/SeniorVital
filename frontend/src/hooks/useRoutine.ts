import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getTodayRoutine, generateRoutine, completeSet } from '../services/routines'
import { addToOfflineQueue } from '../services/api'
import type { TrackEntryPayload, DailyRoutine } from '../types/models'

export function useRoutine(userId: string | undefined) {
  return useQuery<DailyRoutine | null>({
    queryKey: ['routine', userId],
    queryFn: async () => {
      if (!userId) return null
      try {
        return await getTodayRoutine(userId)
      } catch {
        return await generateRoutine(userId)
      }
    },
    enabled: !!userId,
    retry: 1,
    staleTime: 1000 * 60 * 5,
  })
}

export function useGenerateRoutine() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (userId: string) => generateRoutine(userId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['routine'] })
    },
  })
}

export function useCompleteSet() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: TrackEntryPayload) => {
      try {
        return await completeSet(payload)
      } catch {
        await addToOfflineQueue({
          path: '/tracking/record',
          method: 'POST',
          body: payload,
        })
        return { id: crypto.randomUUID() }
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['routine'] })
    },
  })
}

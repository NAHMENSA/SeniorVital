import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface OfflineEntry {
  id: string
  path: string
  method: string
  body: unknown
  created_at: string
}

interface OfflineStore {
  queue: OfflineEntry[]
  add: (entry: Omit<OfflineEntry, 'id' | 'created_at'>) => void
  remove: (id: string) => void
  clear: () => void
  size: () => number
}

export const useOfflineStore = create<OfflineStore>()(
  persist(
    (set, get) => ({
      queue: [],

      add: (entry) => {
        const newEntry: OfflineEntry = {
          ...entry,
          id: crypto.randomUUID(),
          created_at: new Date().toISOString(),
        }
        set((state) => ({ queue: [...state.queue, newEntry] }))
      },

      remove: (id) => {
        set((state) => ({ queue: state.queue.filter((e) => e.id !== id) }))
      },

      clear: () => {
        set({ queue: [] })
      },

      size: () => get().queue.length,
    }),
    {
      name: 'sv-offline-store',
      partialize: (state) => ({ queue: state.queue }),
    }
  )
)

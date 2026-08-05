import { api, getToken } from './api'
import type { DailyRoutine, TrackEntryPayload } from '../types/models'

export interface OllamaStatus {
  available: boolean
  model: string
  ollama_url: string
  error?: string
}

export interface GenerateRoutineStreamCallbacks {
  onProgress: (msg: string, step?: number) => void
  onComplete: (routine: DailyRoutine) => void
  onError: (err: Error) => void
}

export function getTodayRoutine(userId: string) {
  return api<DailyRoutine>(`/routines/today?user_id=${userId}`)
}

export function generateRoutine(userId: string) {
  return api<DailyRoutine>('/routines/generate', {
    method: 'POST',
    body: JSON.stringify({ user_id: userId }),
  })
}

export async function generateRoutineStream(
  userId: string,
  callbacks: GenerateRoutineStreamCallbacks,
): Promise<void> {
  const { onProgress, onComplete, onError } = callbacks
  const token = getToken()

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  }
  if (token) headers['Authorization'] = `Bearer ${token}`

  const url = '/routines/generate-stream'

  try {
    const res = await fetch(url, {
      method: 'POST',
      headers,
      body: JSON.stringify({ user_id: userId }),
    })

    if (!res.ok) {
      const ct = res.headers.get('content-type') || ''
      let detail = `Error del servidor (${res.status})`
      if (ct.includes('application/json')) {
        try {
          const data = await res.json()
          detail = data.detail || detail
        } catch {
          // keep default
        }
      }
      throw new Error(detail)
    }

    onProgress('Generando rutina personalizada...', 1)

    const reader = res.body?.getReader()
    if (!reader) {
      throw new Error('No se pudo leer la respuesta del servidor')
    }

    const decoder = new TextDecoder()
    let buffer = ''

    try {
      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })

        // Process complete SSE events (separated by double newline)
        const eventBlocks = buffer.split('\n\n')
        // Keep the last partial block in buffer
        buffer = eventBlocks.pop() || ''

        for (const block of eventBlocks) {
          if (!block.trim()) continue

          const lines = block.split('\n')
          let eventType = 'message'
          let data = ''

          for (const line of lines) {
            if (line.startsWith('event: ')) {
              eventType = line.slice(7).trim()
            } else if (line.startsWith('data: ')) {
              data += line.slice(6)
            }
          }

          if (!data.trim()) continue

          try {
            const payload = JSON.parse(data)

            if (eventType === 'progress') {
              onProgress(payload.message, payload.step)
            } else if (eventType === 'complete') {
              onComplete(payload as DailyRoutine)
              return
            } else if (eventType === 'error') {
              throw new Error(payload.detail || 'Error desconocido')
            }
          } catch (parseErr) {
            // If JSON parse fails, skip this event
            console.warn('Failed to parse SSE event:', parseErr, data)
          }
        }
      }

      // If we exit the loop without a 'complete' event, it's an error
      throw new Error('La conexión se cerró inesperadamente')
    } finally {
      reader.releaseLock()
    }
  } catch (err) {
    onError(err instanceof Error ? err : new Error('Error desconocido'))
  }
}

export function checkOllamaStatus() {
  return api<OllamaStatus>('/ollama/status')
}

export function completeSet(payload: TrackEntryPayload) {
  return api<{ id: string }>('/tracking/record', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

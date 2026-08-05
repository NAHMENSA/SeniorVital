import React, { useEffect } from 'react'

export type ToastType = 'success' | 'error' | 'info' | 'warning'

interface ToastProps {
  message: string
  type?: ToastType
  onClose: () => void
  duration?: number
}

const VARIANTS: Record<ToastType, string> = {
  success: 'bg-green-100 border-green-500 text-green-800',
  error: 'bg-red-100 border-red-500 text-red-800',
  info: 'bg-blue-100 border-blue-500 text-blue-800',
  warning: 'bg-yellow-100 border-yellow-500 text-yellow-800',
}

/**
 * Toast — WCAG 2.1 AA + Senior-friendly.
 * - role="alert" + aria-live for screen reader announcement
 * - Close button: 56px (3.5rem) minimum touch target for seniors
 * - Responsive: max-width uses clamp for fluid sizing
 * - Texto más grande para mejor legibilidad
 */
export default function Toast({ message, type = 'info', onClose, duration = 4000 }: ToastProps) {
  useEffect(() => {
    const timer = setTimeout(onClose, duration)
    return () => clearTimeout(timer)
  }, [onClose, duration])

  return (
    <div
      className={`fixed top-4 right-4 z-50 max-w-[min(90vw,26rem)] p-5 rounded-xl border-2 shadow-lg animate-slide-in ${VARIANTS[type]}`}
      role="alert"
      aria-live="polite"
    >
      <div className="flex items-center justify-between gap-4">
        <p className="text-lg font-semibold">{message}</p>
        {/* Senior-friendly: 56px (3.5rem) touch target */}
        <button
          onClick={onClose}
          className="min-w-[3.5rem] min-h-[3.5rem] flex items-center justify-center rounded-lg hover:bg-black hover:bg-opacity-10 focus:outline-none focus:ring-2 focus:ring-current text-xl"
          aria-label="Cerrar notificación"
        >
          ✕
        </button>
      </div>
    </div>
  )
}

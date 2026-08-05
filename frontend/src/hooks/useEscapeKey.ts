import { useEffect } from 'react'

/**
 * WCAG 2.1 AA: Listens for the Escape key to close overlays/menus.
 * Ensures keyboard-only users can dismiss modal content.
 */
export function useEscapeKey(callback: () => void, active: boolean = true): void {
  useEffect(() => {
    if (!active) return

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        callback()
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [callback, active])
}

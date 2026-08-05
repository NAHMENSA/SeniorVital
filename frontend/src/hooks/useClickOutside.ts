import { useEffect, useRef, type RefObject } from 'react'

/**
 * WCAG 2.1 AA: Detects clicks outside a referenced element.
 * Used to close dropdowns/menus when user clicks outside,
 * ensuring keyboard and pointer users have equivalent UX.
 */
export function useClickOutside<T extends HTMLElement>(
  callback: () => void
): RefObject<T | null> {
  const ref = useRef<T | null>(null)

  useEffect(() => {
    const handlePointerDown = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        callback()
      }
    }

    document.addEventListener('mousedown', handlePointerDown)
    return () => document.removeEventListener('mousedown', handlePointerDown)
  }, [callback])

  return ref
}

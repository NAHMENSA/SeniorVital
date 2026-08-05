import { useState, useEffect, useCallback } from 'react'

/**
 * WCAG 2.1 AA: Detects viewport changes for responsive behavior.
 * Uses window.matchMedia for native CSS media query integration.
 * Returns true when the query matches (e.g. '(max-width: 767px)').
 */
export function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState<boolean>(() => {
    if (typeof window === 'undefined') return false
    return window.matchMedia(query).matches
  })

  const handleChange = useCallback((e: MediaQueryListEvent) => {
    setMatches(e.matches)
  }, [])

  useEffect(() => {
    const mql = window.matchMedia(query)
    setMatches(mql.matches)
    mql.addEventListener('change', handleChange)
    return () => mql.removeEventListener('change', handleChange)
  }, [query, handleChange])

  return matches
}

/** Convenience: true when viewport is mobile (<=767px) */
export function useIsMobile(): boolean {
  return useMediaQuery('(max-width: 767px)')
}

/** Convenience: true when viewport is tablet (768px-1199px) */
export function useIsTablet(): boolean {
  return useMediaQuery('(min-width: 768px) and (max-width: 1199px)')
}

/** Convenience: true when viewport is desktop (>=1200px) */
export function useIsDesktop(): boolean {
  return useMediaQuery('(min-width: 1200px)')
}

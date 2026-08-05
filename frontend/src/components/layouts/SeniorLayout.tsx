import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../../store/useAuth'
import { useIsMobile } from '../../hooks/useMediaQuery'
import HamburgerMenu from '../ui/HamburgerMenu'
import type { NavItem } from '../ui/HamburgerMenu'

interface LayoutNavItem {
  path: string
  label: string
  icon: string
}

const NAV_ITEMS: LayoutNavItem[] = [
  { path: '/routine', label: 'Rutina', icon: '🏋️' },
  { path: '/habits', label: 'Hábitos', icon: '💧' },
  { path: '/progress', label: 'Progreso', icon: '📊' },
  { path: '/profile', label: 'Perfil', icon: '👤' },
]

/**
 * SeniorLayout — Responsive layout for senior users.
 * Optimizado para adultos mayores con tamaños aumentados.
 *
 * Responsive strategy:
 * - Mobile (<=767px): HamburgerMenu in header + full-width content
 * - Tablet (768-1199px): Bottom tab navigation
 * - Desktop (>=1200px): Bottom tab navigation, wider content area
 *
 * WCAG 2.1 AA + Senior-friendly:
 * - Touch targets: 56px mínimo
 * - Iconos y texto más grandes
 * - Skip-to-content link
 * - ARIA roles y labels
 */
export default function SeniorLayout({ children }: { children: React.ReactNode }) {
  const { user, logout } = useAuth()
  const location = useLocation()
  const isMobile = useIsMobile()

  const hamburgerItems: NavItem[] = NAV_ITEMS.map((item) => ({
    path: item.path,
    label: item.label,
    icon: item.icon,
  }))

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* WCAG 2.4.1: Skip-to-content link */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:bg-secondary focus:text-on-secondary focus:px-6 focus:py-3 focus:rounded-xl focus:font-bold focus:text-lg"
      >
        Saltar al contenido principal
      </a>

      <header
        className="bg-surface-container-lowest border-b-2 border-primary px-5 py-4 flex items-center justify-between"
        role="banner"
      >
        <div className="flex items-center gap-3">
          <span className="text-3xl" aria-hidden="true">👴</span>
          <span className="font-bold text-primary text-xl">SeniorVital</span>
        </div>

        <div className="flex items-center gap-4">
          {/* Desktop/Tablet: show user name inline */}
          {!isMobile && (
            <span className="text-base text-on-surface-variant font-medium">
              {user?.nombre_senior || user?.email}
            </span>
          )}

          {/* Mobile: hamburger menu */}
          {isMobile && (
            <HamburgerMenu
              items={hamburgerItems}
              ariaLabel="Menú de navegación principal"
              onLogout={logout}
              userName={user?.nombre_senior || user?.email}
              logoutLabel="Cerrar sesión"
            />
          )}

          {/* Tablet/Desktop: logout button */}
          {!isMobile && (
            <button
              onClick={logout}
              className="min-h-[3.5rem] min-w-[3.5rem] flex items-center justify-center rounded-xl text-error hover:bg-error-container transition-all focus:outline-none focus:ring-4 focus:ring-error"
              aria-label="Cerrar sesión"
            >
              <span className="text-2xl" aria-hidden="true">🚪</span>
            </button>
          )}
        </div>
      </header>

      <main
        id="main-content"
        className="flex-1 pb-24"
        role="main"
        tabIndex={-1}
      >
        {children}
      </main>

      {/* Bottom tab nav: hidden on mobile (hamburger used instead) */}
      {!isMobile && (
        <nav
          className="fixed bottom-0 left-0 right-0 bg-surface-container-lowest border-t-2 border-primary z-40"
          role="navigation"
          aria-label="Navegación principal"
        >
          <div className="max-w-lg mx-auto flex justify-around">
            {NAV_ITEMS.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`flex flex-col items-center justify-center min-h-[4.5rem] min-w-[4.5rem] px-4 py-2 rounded-t-xl transition-all ${
                  location.pathname === item.path
                    ? 'text-secondary font-bold bg-secondary bg-opacity-10 border-t-3 border-secondary -mt-[2px]'
                    : 'text-on-surface-variant hover:text-primary hover:bg-surface-container-high'
                }`}
                aria-current={location.pathname === item.path ? 'page' : undefined}
              >
                <span className="text-3xl" aria-hidden="true">{item.icon}</span>
                <span className="text-sm mt-1 font-medium">{item.label}</span>
              </Link>
            ))}
          </div>
        </nav>
      )}
    </div>
  )
}

import React, { useState, useRef, useCallback, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useEscapeKey } from '../../hooks/useEscapeKey'
import styles from './HamburgerMenu.module.css'

export interface NavItem {
  path: string
  label: string
  icon: string
}

interface HamburgerMenuProps {
  items: NavItem[]
  ariaLabel?: string
  onLogout?: () => void
  userName?: string
  logoutLabel?: string
}

/**
 * HamburgerMenu — WCAG 2.1 AA compliant mobile navigation.
 *
 * Accessibility features:
 * - 44x44px minimum touch target (WCAG 2.5.5)
 * - aria-label on toggle button
 * - aria-expanded reflects menu state
 * - aria-controls links button to menu panel
 * - role="navigation" + aria-label on nav container
 * - Escape key closes menu (WCAG keyboard operable)
 * - Click outside closes menu
 * - Focus trapped inside menu when open
 * - Focus returns to toggle button on close
 * - Keyboard-navigable links (Tab/Shift+Tab)
 */
export default function HamburgerMenu({
  items,
  ariaLabel = 'Menú de navegación',
  onLogout,
  userName,
  logoutLabel = 'Cerrar sesión',
}: HamburgerMenuProps) {
  const [isOpen, setIsOpen] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)
  const toggleRef = useRef<HTMLButtonElement>(null)
  const firstLinkRef = useRef<HTMLAnchorElement>(null)
  const location = useLocation()

  const close = useCallback(() => {
    setIsOpen(false)
    toggleRef.current?.focus()
  }, [])

  const toggle = useCallback(() => {
    setIsOpen((prev) => !prev)
  }, [])

  useEscapeKey(close, isOpen)

  useEffect(() => {
    if (isOpen) {
      const timer = setTimeout(() => firstLinkRef.current?.focus(), 50)
      return () => clearTimeout(timer)
    }
  }, [isOpen])

  useEffect(() => {
    close()
  }, [location.pathname, close])

  const handleOverlayClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
      close()
    }
  }

  const handleLinkKeyDown = (e: React.KeyboardEvent<HTMLAnchorElement>) => {
    if (e.key === 'Escape') {
      e.preventDefault()
      close()
    }
  }

  return (
    <>
      {/* WCAG: 44x44px touch target, aria-expanded, aria-controls */}
      <button
        ref={toggleRef}
        className={styles.toggleButton}
        onClick={toggle}
        aria-label={isOpen ? 'Cerrar menú' : 'Abrir menú'}
        aria-expanded={isOpen}
        aria-controls="hamburger-nav-panel"
        type="button"
      >
        <span className={`${styles.hamburgerIcon} ${isOpen ? styles.open : ''}`} aria-hidden="true">
          <span className={styles.bar} />
          <span className={styles.bar} />
          <span className={styles.bar} />
        </span>
      </button>

      {/* Overlay backdrop */}
      {isOpen && (
        <div
          className={styles.overlay}
          onClick={handleOverlayClick}
          aria-hidden="true"
        />
      )}

      {/* Slide-in menu panel */}
      <div
        ref={menuRef}
        id="hamburger-nav-panel"
        className={`${styles.panel} ${isOpen ? styles.panelOpen : ''}`}
        role="dialog"
        aria-modal={isOpen}
        aria-label={ariaLabel}
      >
        <nav role="navigation" aria-label={ariaLabel}>
          <ul className={styles.navList}>
            {items.map((item, index) => (
              <li key={item.path}>
                <Link
                  ref={index === 0 ? firstLinkRef : undefined}
                  to={item.path}
                  className={`${styles.navLink} ${
                    location.pathname === item.path ? styles.navLinkActive : ''
                  }`}
                  aria-current={location.pathname === item.path ? 'page' : undefined}
                  onKeyDown={handleLinkKeyDown}
                >
                  <span className={styles.navIcon} aria-hidden="true">{item.icon}</span>
                  <span className={styles.navLabel}>{item.label}</span>
                </Link>
              </li>
            ))}
          </ul>

          {userName && (
            <div className={styles.userInfo}>
              <span className={styles.userName}>{userName}</span>
            </div>
          )}

          {onLogout && (
            <button
              className={styles.logoutButton}
              onClick={() => { onLogout(); close() }}
              type="button"
              aria-label={logoutLabel}
            >
              <span aria-hidden="true">🚪</span>
              <span>{logoutLabel}</span>
            </button>
          )}
        </nav>
      </div>
    </>
  )
}

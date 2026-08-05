import React from 'react'

interface AccessibleButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'tertiary' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  vibrateOnClick?: boolean
  announceText?: string
}

const variantClasses: Record<string, string> = {
  primary: 'bg-secondary text-on-secondary border-secondary hover:brightness-110 focus:ring-secondary',
  secondary: 'bg-surface text-primary border-primary hover:bg-surface-container-high focus:ring-primary',
  tertiary: 'bg-tertiary-fixed text-on-tertiary-fixed border-tertiary-fixed-dim hover:brightness-110 focus:ring-tertiary',
  ghost: 'bg-transparent text-primary border-transparent hover:bg-surface-container-high focus:ring-primary',
  danger: 'bg-error text-on-error border-error hover:brightness-110 focus:ring-error',
}

/**
 * AccessibleButton — WCAG 2.1 AA + Senior-friendly.
 *
 * Accessibility:
 * - Minimum 56px (3.5rem) touch target for seniors (WCAG 2.5.5)
 * - Uses rem units for sizing (zoom support)
 * - Focus-visible ring (4px offset) for keyboard navigation
 * - Vibration feedback on supported devices
 * - aria-live announcement for screen readers
 * - Disabled state: opacity + cursor change
 * - Active state: scale(0.95) for tactile feedback
 */
export default function AccessibleButton({
  variant = 'primary',
  size = 'md',
  vibrateOnClick = false,
  announceText,
  className = '',
  onClick,
  children,
  ...props
}: AccessibleButtonProps) {
  /*
   * All sizes enforce min 3.5rem (56px) height for seniors.
   * Uses rem units for zoom support.
   */
  const sizeClasses = size === 'sm'
    ? 'min-h-[3.5rem] px-5 text-base'
    : size === 'lg'
      ? 'min-h-[4.5rem] px-8 text-xl'
      : 'min-h-[4rem] px-6 text-lg'

  const base = `inline-flex items-center justify-center gap-3 rounded-xl border-2 font-bold transition-all duration-150 active:scale-95 focus:outline-none focus:ring-4 focus:ring-offset-2 focus:ring-offset-surface disabled:opacity-50 disabled:cursor-not-allowed min-w-[3.5rem]`

  const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    if (vibrateOnClick && navigator.vibrate) navigator.vibrate(50)
    if (announceText) {
      const el = document.createElement('div')
      el.setAttribute('role', 'status')
      el.setAttribute('aria-live', 'polite')
      el.className = 'sr-only'
      el.textContent = announceText
      document.body.appendChild(el)
      setTimeout(() => el.remove(), 3000)
    }
    onClick?.(e)
  }

  return (
    <button
      className={`${base} ${sizeClasses} ${variantClasses[variant]} ${className}`}
      onClick={handleClick}
      {...props}
    >
      {children}
    </button>
  )
}

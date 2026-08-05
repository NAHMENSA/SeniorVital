import React, { memo, useCallback } from 'react'
import { getRpeEmoji } from '../../lib/accessibility'
import styles from './RpeScale.module.css'

interface RpeScaleProps {
  value: number | null
  onChange: (rpe: number) => void
  disabled?: boolean
}

/**
 * RpeScale — WCAG 2.1 AA + Senior-friendly.
 *
 * Accessibility:
 * - role="radiogroup" with aria-label for screen readers
 * - Each button: role="radio", aria-checked, aria-label with level + description
 * - 56px (3.5rem) minimum touch targets for seniors (WCAG 2.5.5)
 * - Emoji icons marked aria-hidden="true" (decorative)
 * - Live region (aria-live="polite") announces selection
 * - Keyboard navigable (Tab between buttons, Enter/Space to select)
 * - Focus-visible ring for keyboard users
 * - Colors verified >= 4.5:1 contrast ratio
 * - Responsive grid: 5 cols mobile, 10 cols tablet+
 * - Relative units (rem, clamp) for zoom support
 */
const RpeScale = memo(function RpeScale({ value, onChange, disabled }: RpeScaleProps) {
  const levels = Array.from({ length: 10 }, (_, i) => i + 1)

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLButtonElement>, rpe: number) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault()
        onChange(rpe)
      }
    },
    [onChange]
  )

  const getButtonClass = (rpe: number, selected: boolean): string => {
    const baseClass = selected ? styles.rpeButtonSelected : styles.rpeButton
    const colorClass = selected
      ? styles[`rpe${rpe}Selected`]
      : styles[`rpe${rpe}`]
    return `${baseClass} ${colorClass || ''}`
  }

  return (
    <div className={styles.container}>
      <div
        role="radiogroup"
        aria-label="Escala de esfuerzo percibido del 1 al 10"
      >
        <p className={styles.label}>¿Cómo sentiste este ejercicio?</p>
        <div className={styles.grid}>
          {levels.map((rpe) => {
            const meta = getRpeEmoji(rpe)
            const selected = value === rpe
            return (
              <button
                key={rpe}
                type="button"
                role="radio"
                aria-checked={selected}
                aria-label={`Nivel ${rpe}: ${meta.label}`}
                disabled={disabled}
                onClick={() => onChange(rpe)}
                onKeyDown={(e) => handleKeyDown(e, rpe)}
                className={getButtonClass(rpe, selected)}
              >
                <span className={styles.emoji} aria-hidden="true">
                  {meta.emoji}
                </span>
                <span className={styles.number}>{rpe}</span>
              </button>
            )
          })}
        </div>
      </div>

      {/* WCAG: Live region announces selection to screen readers */}
      {value && (
        <p className={styles.selection} aria-live="polite">
          {getRpeEmoji(value).emoji} Nivel {value}: {getRpeEmoji(value).label}
        </p>
      )}
    </div>
  )
})

export default RpeScale

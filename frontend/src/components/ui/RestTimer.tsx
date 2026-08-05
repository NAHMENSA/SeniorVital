import React, { useEffect, useState, useRef, memo } from 'react'
import AccessibleButton from './AccessibleButton'

interface Props {
  durationSec: number
  onComplete: () => void
  onSkip: () => void
}

/**
 * RestTimer — Optimizado para adultos mayores.
 * - Display de tiempo muy grande
 * - Botones grandes (56px mínimo)
 *
 * Garantiza arranque desde `durationSec` (nunca hereda el cronómetro
 * de ejercicio previo). `onComplete` se invoca fuera del updater de
 * estado para evitar efectos colaterales en StrictMode.
 */
const RestTimer = memo(function RestTimer({ durationSec, onComplete, onSkip }: Props) {
  const [remaining, setRemaining] = useState(durationSec)
  const intervalRef = useRef<ReturnType<typeof setInterval>>()
  const onCompleteRef = useRef(onComplete)
  onCompleteRef.current = onComplete

  // Reset si durationSec cambia con el componente montado
  useEffect(() => {
    setRemaining(durationSec)
  }, [durationSec])

  useEffect(() => {
    intervalRef.current = setInterval(() => {
      setRemaining((prev) => (prev > 0 ? prev - 1 : 0))
    }, 1000)
    return () => clearInterval(intervalRef.current)
  }, [durationSec])

  useEffect(() => {
    if (remaining <= 0) {
      clearInterval(intervalRef.current)
      onCompleteRef.current()
    }
  }, [remaining])

  const minutes = Math.floor(remaining / 60)
  const seconds = remaining % 60

  return (
    <div className="text-center p-8" role="timer" aria-label={`Descanso: ${minutes} minutos ${seconds} segundos`}>
      <p className="text-2xl text-primary font-bold mb-4">Descanso</p>
      <p className="text-7xl font-mono font-bold text-secondary mb-8">
        {minutes}:{seconds.toString().padStart(2, '0')}
      </p>
      <AccessibleButton variant="ghost" size="lg" onClick={onSkip} announceText="Descanso omitido">
        Saltar descanso
      </AccessibleButton>
    </div>
  )
})

export default RestTimer

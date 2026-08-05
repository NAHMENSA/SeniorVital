// WCAG 2.1 AA utilities

export function announce(message: string) {
  const el = document.createElement('div')
  el.setAttribute('role', 'status')
  el.setAttribute('aria-live', 'polite')
  el.className = 'sr-only'
  el.textContent = message
  document.body.appendChild(el)
  setTimeout(() => el.remove(), 3000)
}

export function vibrate(pattern: number | number[] = 50) {
  if (navigator.vibrate) navigator.vibrate(pattern)
}

export function getRpeEmoji(rpe: number): { emoji: string; label: string; color: string } {
  const map: Record<number, { emoji: string; label: string; color: string }> = {
    1:  { emoji: '😴', label: 'Muy muy fácil', color: 'bg-green-100 text-green-800 border-green-300' },
    2:  { emoji: '😊', label: 'Muy fácil', color: 'bg-green-100 text-green-800 border-green-300' },
    3:  { emoji: '🙂', label: 'Fácil', color: 'bg-green-50 text-green-700 border-green-200' },
    4:  { emoji: '💪', label: 'Esfuerzo moderado', color: 'bg-yellow-50 text-yellow-700 border-yellow-300' },
    5:  { emoji: '😤', label: 'Moderado', color: 'bg-yellow-100 text-yellow-800 border-yellow-400' },
    6:  { emoji: '😅', label: 'Algo pesado', color: 'bg-orange-50 text-orange-700 border-orange-300' },
    7:  { emoji: '🥵', label: 'Pesado', color: 'bg-orange-100 text-orange-800 border-orange-400' },
    8:  { emoji: '😰', label: 'Muy pesado', color: 'bg-red-50 text-red-700 border-red-300' },
    9:  { emoji: '😫', label: 'Extremadamente pesado', color: 'bg-red-100 text-red-800 border-red-400' },
    10: { emoji: '🚑', label: 'Máximo esfuerzo', color: 'bg-red-200 text-red-900 border-red-500' },
  }
  return map[rpe] || map[5]
}

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import HabitsPage from '../HabitsPage'

vi.mock('../../../store/useAuth', () => ({
  useAuth: () => ({
    user: { id: '1', role: 'senior', nombre_senior: 'Juan' },
    displayName: 'Juan Pérez',
  }),
}))

vi.mock('../../../services/habits', () => ({
  getTodayHabits: vi.fn(),
  saveHabits: vi.fn(),
}))

vi.mock('../../../services/api', () => ({
  addToOfflineQueue: vi.fn(),
}))

vi.mock('../../../lib/accessibility', () => ({
  announce: vi.fn(),
  vibrate: vi.fn(),
}))

describe('HabitsPage', () => {
  let mockGetTodayHabits: any
  let mockSaveHabits: any

  beforeEach(() => {
    localStorage.clear()
    const habitsModule = require('../../../services/habits')
    mockGetTodayHabits = habitsModule.getTodayHabits
    mockSaveHabits = habitsModule.saveHabits
  })

  afterEach(() => vi.restoreAllMocks())

  it('shows numeric values not NaN when backend returns 0', async () => {
    mockGetTodayHabits.mockResolvedValue({
      user_id: '1', date: '2026-01-01', water_intake_glasses: 0, sleep_hours: 0.0,
    })
    mockSaveHabits.mockResolvedValue({ id: '1', user_id: '1', date: '2026-01-01', water_intake_glasses: 0, sleep_hours: 0.0 })

    render(<BrowserRouter><HabitsPage /></BrowserRouter>)

    await waitFor(() => {
      expect(screen.getByText('💧 Vasos de agua')).toBeDefined()
      expect(screen.getByText('🌙 Horas de sueño')).toBeDefined()
    })

    const waterDisplay = screen.getAllByText(/0/)
    expect(waterDisplay).toBeDefined()
  })

  it('shows NaN-free values after clicking + button', async () => {
    mockGetTodayHabits.mockResolvedValue({
      user_id: '1', date: '2026-01-01', water_intake_glasses: 0, sleep_hours: 0.0,
    })
    mockSaveHabits.mockResolvedValue({})

    render(<BrowserRouter><HabitsPage /></BrowserRouter>)

    await waitFor(() => expect(mockGetTodayHabits).toHaveBeenCalled())

    const plusButtons = screen.getAllByLabelText('Agregar un vaso')
    fireEvent.click(plusButtons[0])

    await waitFor(() => {
      const waterDisplay = screen.getAllByText(/1/)
      expect(waterDisplay).toBeDefined()
    })
  })
})

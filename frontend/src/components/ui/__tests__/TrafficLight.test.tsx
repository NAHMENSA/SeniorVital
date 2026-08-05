import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import TrafficLight from '../TrafficLight'

describe('TrafficLight', () => {
  it('renders green status with correct label', () => {
    render(<TrafficLight risk="green" />)
    expect(screen.getByText('Ritmo estable')).toBeDefined()
    expect(screen.getByRole('status')).toBeDefined()
  })

  it('renders amber status', () => {
    render(<TrafficLight risk="amber" />)
    expect(screen.getByText('Riesgo de abandono')).toBeDefined()
  })

  it('renders red status', () => {
    render(<TrafficLight risk="red" />)
    expect(screen.getByText('Inactivo o fatiga severa')).toBeDefined()
  })
})

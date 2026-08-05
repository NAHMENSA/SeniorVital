import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import RpeScale from '../RpeScale'

describe('RpeScale', () => {
  it('renders 10 levels', () => {
    const onChange = vi.fn()
    render(<RpeScale value={null} onChange={onChange} />)
    const buttons = screen.getAllByRole('radio')
    expect(buttons).toHaveLength(10)
  })

  it('calls onChange with correct RPE value', async () => {
    const onChange = vi.fn()
    render(<RpeScale value={null} onChange={onChange} />)
    await userEvent.click(screen.getByLabelText('Nivel 5: Moderado'))
    expect(onChange).toHaveBeenCalledWith(5)
  })

  it('shows selected value with aria-checked', () => {
    const onChange = vi.fn()
    render(<RpeScale value={7} onChange={onChange} />)
    const selected = screen.getByLabelText('Nivel 7: Pesado')
    expect(selected.getAttribute('aria-checked')).toBe('true')
  })

  it('has accessible radiogroup role', () => {
    const onChange = vi.fn()
    render(<RpeScale value={null} onChange={onChange} />)
    expect(screen.getByRole('radiogroup')).toBeDefined()
  })
})

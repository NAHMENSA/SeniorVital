import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import AccessibleButton from '../AccessibleButton'

describe('AccessibleButton', () => {
  it('renders with text content', () => {
    render(<AccessibleButton>Click me</AccessibleButton>)
    expect(screen.getByText('Click me')).toBeDefined()
  })

  it('calls onClick when clicked', async () => {
    const onClick = vi.fn()
    render(<AccessibleButton onClick={onClick}>Click</AccessibleButton>)
    await userEvent.click(screen.getByText('Click'))
    expect(onClick).toHaveBeenCalledOnce()
  })

  it('has correct variant classes', () => {
    render(<AccessibleButton variant="danger">Delete</AccessibleButton>)
    const btn = screen.getByText('Delete')
    expect(btn.className).toContain('bg-error')
  })

  it('respects disabled state', () => {
    render(<AccessibleButton disabled>Disabled</AccessibleButton>)
    const btn = screen.getByText('Disabled') as HTMLButtonElement
    expect(btn.disabled).toBe(true)
  })

  it('has accessible name via aria-label', () => {
    render(<AccessibleButton aria-label="Cerrar sesión">X</AccessibleButton>)
    expect(screen.getByLabelText('Cerrar sesión')).toBeDefined()
  })

  it('has minimum touch target size (Senior-friendly: 56px = 3.5rem)', () => {
    render(<AccessibleButton>Big</AccessibleButton>)
    const btn = screen.getByText('Big')
    expect(btn.className).toContain('min-w-[3.5rem]')
    expect(btn.className).toContain('min-h-[4rem]')
  })
})

import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import EmptyState from '../EmptyState'

describe('EmptyState', () => {
  it('renders title and description', () => {
    render(<EmptyState title="No data" description="Nothing to show" />)
    expect(screen.getByText('No data')).toBeDefined()
    expect(screen.getByText('Nothing to show')).toBeDefined()
  })

  it('renders custom icon', () => {
    render(<EmptyState icon="📊" title="Empty" />)
    expect(screen.getByText('📊')).toBeDefined()
  })
})

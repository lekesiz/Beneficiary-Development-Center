import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { Badge } from '../Badge'

describe('Badge', () => {
  it('renders children text', () => {
    render(<Badge>Test Badge</Badge>)
    expect(screen.getByText('Test Badge')).toBeInTheDocument()
  })

  it('applies default variant styling', () => {
    render(<Badge>Default</Badge>)
    const badge = screen.getByText('Default')
    expect(badge).toHaveClass('bg-primary', 'text-primary-foreground')
  })

  it('applies different variant styling', () => {
    const variants = [
      { variant: 'secondary' as const, classes: ['bg-secondary', 'text-secondary-foreground'] },
      { variant: 'success' as const, classes: ['bg-green-100', 'text-green-800'] },
      { variant: 'warning' as const, classes: ['bg-yellow-100', 'text-yellow-800'] },
      { variant: 'danger' as const, classes: ['bg-red-100', 'text-red-800'] },
      { variant: 'outline' as const, classes: ['border', 'border-input', 'bg-background'] },
    ]

    variants.forEach(({ variant, classes }) => {
      const { rerender } = render(<Badge variant={variant}>{variant}</Badge>)
      const badge = screen.getByText(variant)
      
      classes.forEach(className => {
        expect(badge).toHaveClass(className)
      })
      
      rerender(<div />)
    })
  })

  it('applies different size styling', () => {
    const sizes = [
      { size: 'sm' as const, classes: ['px-2', 'py-0.5', 'text-xs'] },
      { size: 'md' as const, classes: ['px-2.5', 'py-0.5', 'text-sm'] },
      { size: 'lg' as const, classes: ['px-3', 'py-1', 'text-base'] },
    ]

    sizes.forEach(({ size, classes }) => {
      const { rerender } = render(<Badge size={size}>{size}</Badge>)
      const badge = screen.getByText(size)
      
      classes.forEach(className => {
        expect(badge).toHaveClass(className)
      })
      
      rerender(<div />)
    })
  })

  it('applies custom className', () => {
    render(<Badge className="custom-class">Custom</Badge>)
    const badge = screen.getByText('Custom')
    expect(badge).toHaveClass('custom-class')
  })

  it('forwards additional props', () => {
    render(<Badge data-testid="test-badge">Props</Badge>)
    const badge = screen.getByTestId('test-badge')
    expect(badge).toBeInTheDocument()
  })
})
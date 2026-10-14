import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import ZuluClock from './ZuluClock'

describe('ZuluClock', () => {
  it('formats a fixed time as HH:MM:SSZ', () => {
    const fixed = new Date('2026-11-02T13:05:09Z')
    render(<ZuluClock now={fixed} />)
    expect(screen.getByTestId('zulu-clock')).toHaveTextContent('13:05:09Z')
  })

  it('pads single-digit hours/minutes/seconds with a leading zero', () => {
    const fixed = new Date('2026-11-02T01:02:03Z')
    render(<ZuluClock now={fixed} />)
    expect(screen.getByTestId('zulu-clock')).toHaveTextContent('01:02:03Z')
  })

  it('shows a speed badge only when the multiplier is not 1x', () => {
    const fixed = new Date('2026-11-02T13:05:09Z')
    const { rerender } = render(<ZuluClock now={fixed} speedMultiplier={1} />)
    expect(screen.queryByText('×1')).not.toBeInTheDocument()

    rerender(<ZuluClock now={fixed} speedMultiplier={10} />)
    expect(screen.getByText('×10')).toBeInTheDocument()
  })
})

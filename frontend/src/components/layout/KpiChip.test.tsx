import { render, screen } from '@testing-library/react'
import { Plane } from 'lucide-react'
import { describe, expect, it } from 'vitest'

import KpiChip, { type KpiTone } from './KpiChip'

describe('KpiChip', () => {
  it.each<[KpiTone, string]>([
    ['ok', 'text-ok'],
    ['warn', 'text-warn'],
    ['crit', 'text-crit'],
    ['info', 'text-accent'],
  ])('renders the %s tone with the %s value colour', (tone, expectedClass) => {
    render(<KpiChip icon={Plane} label="AIRCRAFT READY" value="33/42" tone={tone} />)

    const value = screen.getByText('33/42')
    expect(value).toHaveClass(expectedClass)

    const wrapper = value.closest('[data-tone]')
    expect(wrapper).toHaveAttribute('data-tone', tone)
  })

  it('renders as a button and fires onClick when one is given', () => {
    let clicked = false
    render(
      <KpiChip icon={Plane} label="AIRCRAFT READY" value="33/42" onClick={() => (clicked = true)} />,
    )
    screen.getByRole('button').click()
    expect(clicked).toBe(true)
  })

  it('renders as a plain div (no button role) when onClick is omitted', () => {
    render(<KpiChip icon={Plane} label="AIRCRAFT READY" value="33/42" />)
    expect(screen.queryByRole('button')).not.toBeInTheDocument()
  })
})

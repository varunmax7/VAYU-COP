import { fireEvent, render, screen } from '@testing-library/react'
import { beforeEach, describe, expect, it } from 'vitest'

import { useThemeEffect } from '@/lib/theme'
import { useUiStore } from '@/store/uiStore'

import ThemeToggle from './ThemeToggle'

/** ThemeToggle only dispatches to the store; useThemeEffect is what actually stamps
 * [data-theme] on <html>. Mount both together, the way App.tsx does, to prove clicking
 * a mode in ThemeToggle really does switch the resolved theme end to end. */
function Harness() {
  useThemeEffect()
  return <ThemeToggle />
}

beforeEach(() => {
  useUiStore.setState({ themeMode: 'auto' })
})

describe('ThemeToggle + useThemeEffect', () => {
  it('switches [data-theme] to dark when NIGHT is selected', () => {
    render(<Harness />)
    fireEvent.click(screen.getByRole('radio', { name: 'NIGHT' }))
    expect(document.documentElement.dataset.theme).toBe('dark')
  })

  it('switches [data-theme] to light when DAY is selected', () => {
    render(<Harness />)
    fireEvent.click(screen.getByRole('radio', { name: 'DAY' }))
    expect(document.documentElement.dataset.theme).toBe('light')
  })

  it('marks the active mode as checked', () => {
    render(<Harness />)
    const night = screen.getByRole('radio', { name: 'NIGHT' })
    fireEvent.click(night)
    expect(night).toHaveAttribute('aria-checked', 'true')
  })
})

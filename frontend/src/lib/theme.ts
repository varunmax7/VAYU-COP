import { useEffect, useState } from 'react'

import { isDaytimeLocal } from '@/lib/time'
import { useUiStore, type ThemeMode } from '@/store/uiStore'

export type ResolvedTheme = 'light' | 'dark'

function resolveTheme(mode: ThemeMode): ResolvedTheme {
  if (mode === 'day') return 'light'
  if (mode === 'night') return 'dark'
  return isDaytimeLocal() ? 'light' : 'dark'
}

/** Resolves AUTO/DAY/NIGHT to the actual light/dark theme and keeps [data-theme] on
 * <html> in sync — re-evaluated every minute so AUTO flips at the 06:00/18:00 boundary
 * without a reload (§13.3). */
export function useThemeEffect(): void {
  const themeMode = useUiStore((s) => s.themeMode)

  useEffect(() => {
    const apply = () => {
      document.documentElement.dataset.theme = resolveTheme(themeMode)
    }
    apply()
    if (themeMode !== 'auto') return
    const id = setInterval(apply, 60_000)
    return () => clearInterval(id)
  }, [themeMode])
}

/** Reads the resolved light/dark theme as state, for components (e.g. the map tile
 * layer) that need to react to it rather than just stamp an attribute. */
export function useResolvedTheme(): ResolvedTheme {
  const themeMode = useUiStore((s) => s.themeMode)
  const [resolved, setResolved] = useState<ResolvedTheme>(() => resolveTheme(themeMode))

  useEffect(() => {
    const apply = () => setResolved(resolveTheme(themeMode))
    apply()
    if (themeMode !== 'auto') return
    const id = setInterval(apply, 60_000)
    return () => clearInterval(id)
  }, [themeMode])

  return resolved
}

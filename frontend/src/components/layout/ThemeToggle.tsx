import { cn } from '@/lib/utils'
import { useUiStore, type ThemeMode } from '@/store/uiStore'

const OPTIONS: { mode: ThemeMode; label: string }[] = [
  { mode: 'auto', label: 'AUTO' },
  { mode: 'day', label: 'DAY MODE (06:00–18:00)' },
  { mode: 'night', label: 'NIGHT / C2 BUNKER MODE' },
]

export default function ThemeToggle() {
  const themeMode = useUiStore((s) => s.themeMode)
  const setThemeMode = useUiStore((s) => s.setThemeMode)

  return (
    <div
      className="label-text flex items-center gap-0.5 rounded border border-border bg-panel-2 p-0.5 text-[11px]"
      role="radiogroup"
      aria-label="Theme"
    >
      {OPTIONS.map(({ mode, label }) => (
        <button
          key={mode}
          type="button"
          role="radio"
          aria-checked={themeMode === mode}
          title={label}
          onClick={() => setThemeMode(mode)}
          className={cn(
            'rounded px-2 py-1 transition-colors',
            themeMode === mode
              ? 'bg-accent text-white'
              : 'text-text-muted hover:text-text',
          )}
        >
          {mode.toUpperCase()}
        </button>
      ))}
    </div>
  )
}

import { cn } from '@/lib/utils'
import { useCopStore } from '@/store/copStore'
import { useUiStore } from '@/store/uiStore'

const DOT_COLOR = {
  connected: 'bg-ok',
  connecting: 'bg-warn',
  disconnected: 'bg-crit',
} as const

export default function ConnectionDot() {
  const wsStatus = useUiStore((s) => s.wsStatus)
  const fusionHealth = useCopStore((s) => s.fusionHealth)

  const sources = Object.entries(fusionHealth)
  const tooltip =
    wsStatus !== 'connected'
      ? `WebSocket ${wsStatus}`
      : sources.length === 0
        ? 'WebSocket connected'
        : sources.map(([name, h]) => `${name}: ${h.status}`).join('\n')

  return (
    <span
      className={cn('inline-block h-2.5 w-2.5 rounded-full', DOT_COLOR[wsStatus])}
      title={tooltip}
      data-testid="connection-dot"
      data-status={wsStatus}
    />
  )
}

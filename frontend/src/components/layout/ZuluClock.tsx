import { useEffect, useState } from 'react'

import { formatZulu } from '@/lib/time'

interface ZuluClockProps {
  /** Overrides the ticking wall clock — Phase 9's sim clock will pass sim time here. */
  now?: Date
  /** Shown as an "×N" badge next to the clock when the sim is running faster than 1x. */
  speedMultiplier?: number
}

export default function ZuluClock({ now, speedMultiplier }: ZuluClockProps) {
  const [tick, setTick] = useState(() => new Date())

  useEffect(() => {
    if (now) return
    const id = setInterval(() => setTick(new Date()), 1000)
    return () => clearInterval(id)
  }, [now])

  const display = now ?? tick

  return (
    <div className="mono-text flex items-center gap-1.5 text-sm" data-testid="zulu-clock">
      <span className="label-text text-text-muted">ZULU TIME</span>
      <span>{formatZulu(display)}</span>
      {speedMultiplier && speedMultiplier !== 1 && (
        <span className="rounded border border-accent px-1 text-xs text-accent">
          ×{speedMultiplier}
        </span>
      )}
    </div>
  )
}

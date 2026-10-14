import { Fragment } from 'react'
import { Circle, Tooltip } from 'react-leaflet'

import type { ThreatZone } from '@/lib/copTypes'
import { useMapStore } from '@/store/mapStore'

const NEW_THREAT_PULSE_MS = 10_000

interface ThreatLayerProps {
  threats: ThreatZone[]
}

export default function ThreatLayer({ threats }: ThreatLayerProps) {
  const select = useMapStore((s) => s.select)
  const showLabels = useMapStore((s) => s.layers.labels)
  const now = Date.now()

  return (
    <>
      {threats.map((t) => {
        const isNew = now - new Date(t.firstSeen).getTime() < NEW_THREAT_PULSE_MS
        const eventHandlers = { click: () => select({ kind: 'threat', id: t.id }) }
        return (
          <Fragment key={t.id}>
            <Circle
              center={[t.centerLat, t.centerLon]}
              radius={t.radiusKm * 1000}
              pathOptions={{
                color: 'var(--threat-stroke)',
                fillColor: 'var(--threat-fill)',
                fillOpacity: 1,
                weight: 2,
                className: isNew ? 'pulse-ring' : undefined,
              }}
              eventHandlers={eventHandlers}
            >
              {showLabels && (
                <Tooltip permanent direction="top" className="mono-text" opacity={1}>
                  THREAT ZONE {t.label} · {t.level} · conf {t.confidence.toFixed(2)}
                </Tooltip>
              )}
            </Circle>
            <Circle
              center={[t.centerLat, t.centerLon]}
              radius={t.radiusKm * 1000 * 1.2}
              pathOptions={{
                color: 'var(--threat-stroke)',
                fill: false,
                weight: 1,
                dashArray: '6 6',
              }}
              eventHandlers={eventHandlers}
            />
          </Fragment>
        )
      })}
    </>
  )
}

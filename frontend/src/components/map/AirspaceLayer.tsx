import { GeoJSON, Tooltip } from 'react-leaflet'

import type { Airspace } from '@/lib/copTypes'
import { useMapStore } from '@/store/mapStore'

function windowLabel(a: Airspace): string {
  if (!a.activeFrom || !a.activeTo) return `AIRSPACE ${a.name} — ${a.status}`
  const from = new Date(a.activeFrom)
  const to = new Date(a.activeTo)
  const fmt = (d: Date) => `${String(d.getUTCHours()).padStart(2, '0')}${String(d.getUTCMinutes()).padStart(2, '0')}`
  return `AIRSPACE ${a.name} — ${a.status} ${fmt(from)}–${fmt(to)}Z`
}

interface AirspaceLayerProps {
  airspace: Airspace[]
}

export default function AirspaceLayer({ airspace }: AirspaceLayerProps) {
  const select = useMapStore((s) => s.select)
  const showLabels = useMapStore((s) => s.layers.labels)

  return (
    <>
      {airspace.map((a) => (
        <GeoJSON
          key={a.id}
          data={a.polygonGeojson}
          style={{
            color: a.status === 'CLOSED' || a.status === 'ACTIVE' ? 'var(--crit)' : 'var(--border)',
            weight: 1.5,
            fillColor: 'url(#vayu-hatch)',
            fillOpacity: 1,
          }}
          eventHandlers={{ click: () => select({ kind: 'airspace', id: a.id }) }}
        >
          {showLabels && (
            <Tooltip sticky className="mono-text text-xs" opacity={1}>
              {windowLabel(a)}
            </Tooltip>
          )}
        </GeoJSON>
      ))}
    </>
  )
}

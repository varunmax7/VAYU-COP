import L from 'leaflet'
import { useMemo } from 'react'
import { Marker } from 'react-leaflet'

import type { AirBase } from '@/lib/copTypes'
import { useMapStore } from '@/store/mapStore'

const STATUS_COLOR: Record<AirBase['status'], string> = {
  OPEN: 'var(--ok)',
  RESTRICTED: 'var(--warn)',
  CLOSED: 'var(--crit)',
}

function baseIcon(base: AirBase, showLabel: boolean): L.DivIcon {
  const color = STATUS_COLOR[base.status]
  const pulse = base.status === 'CLOSED' ? 'pulse-ring' : ''
  return L.divIcon({
    className: '',
    html: `
      <div style="display:flex;flex-direction:column;align-items:center;gap:2px;transform:translate(-50%,-50%)">
        <div class="${pulse}" style="width:22px;height:22px;border-radius:50%;border:2px solid ${color};display:flex;align-items:center;justify-content:center;background:var(--panel)">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="2.5">
            <path d="M2 16 L22 8 M2 16 L6 20 M22 8 L18 4" />
          </svg>
        </div>
        ${
          showLabel
            ? `<span class="label-text" style="font-size:10px;background:var(--panel);border:1px solid var(--border);border-radius:3px;padding:1px 4px;color:var(--text);white-space:nowrap">BASE ${base.name.replace(/^Base /i, '').toUpperCase()}</span>`
            : ''
        }
      </div>
    `,
    iconSize: [0, 0],
  })
}

interface BaseLayerProps {
  bases: AirBase[]
}

export default function BaseLayer({ bases }: BaseLayerProps) {
  const showLabels = useMapStore((s) => s.layers.labels)
  const select = useMapStore((s) => s.select)
  const setRangeRing = useMapStore((s) => s.setRangeRing)

  const icons = useMemo(
    () => bases.map((b) => ({ base: b, icon: baseIcon(b, showLabels) })),
    [bases, showLabels],
  )

  return (
    <>
      {icons.map(({ base, icon }) => (
        <Marker
          key={base.id}
          position={[base.lat, base.lon]}
          icon={icon}
          eventHandlers={{
            click: () => select({ kind: 'base', id: base.id }),
            contextmenu: (e) => {
              e.originalEvent.preventDefault()
              setRangeRing(base.id, null)
            },
          }}
        />
      ))}
    </>
  )
}

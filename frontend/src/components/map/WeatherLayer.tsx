import L from 'leaflet'
import { useEffect, useState } from 'react'
import { Circle, Marker } from 'react-leaflet'

import { useBaseWeather } from '@/lib/queries'
import type { AirBase, WeatherCell } from '@/lib/copTypes'
import { useMapStore } from '@/store/mapStore'

const KM_PER_DEG_LAT = 111.32

/** Simple direct ceiling/visibility threshold — the real per-aircraft-type GO/MARGINAL/
 * NO-GO model (§11) is Phase 11's trained predictive-analytics work; this is a
 * placeholder heuristic so the map has something meaningful to show today. */
function goNoGo(ceilingFt: number, visibilityKm: number): 'GO' | 'MARGINAL' | 'NO-GO' {
  if (ceilingFt >= 1000 && visibilityKm >= 3) return 'GO'
  if (ceilingFt >= 500 && visibilityKm >= 1.6) return 'MARGINAL'
  return 'NO-GO'
}

const BADGE_COLOR: Record<string, string> = {
  GO: 'var(--ok)',
  MARGINAL: 'var(--warn)',
  'NO-GO': 'var(--crit)',
}

function badgeIcon(label: string): L.DivIcon {
  const color = BADGE_COLOR[label]
  return L.divIcon({
    className: '',
    html: `<span class="label-text" style="transform:translate(-50%,10px);display:inline-block;font-size:9px;background:${color};color:#0a1322;border-radius:3px;padding:1px 4px;white-space:nowrap">${label}</span>`,
    iconSize: [0, 0],
  })
}

/** Dead-reckons a cell's visual position from its snapshot centre + motion vector —
 * the backend doesn't continuously move cells client-side until Phase 9's sim engine
 * exists, so this gives the "drifting" look (§13.4) from data that refreshes periodically. */
function useDriftingPosition(cell: WeatherCell) {
  const [pos, setPos] = useState<[number, number]>([cell.centerLat, cell.centerLon])

  useEffect(() => {
    const start = performance.now()
    const base: [number, number] = [cell.centerLat, cell.centerLon]
    let frame: number
    const tick = () => {
      const elapsedH = (performance.now() - start) / 3_600_000
      const distKm = cell.motionKts * 1.852 * elapsedH
      const rad = (cell.motionDeg * Math.PI) / 180
      const dLat = (distKm * Math.cos(rad)) / KM_PER_DEG_LAT
      const dLon = (distKm * Math.sin(rad)) / (KM_PER_DEG_LAT * Math.cos((base[0] * Math.PI) / 180))
      setPos([base[0] + dLat, base[1] + dLon])
      frame = requestAnimationFrame(tick)
    }
    frame = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(frame)
  }, [cell.centerLat, cell.centerLon, cell.motionDeg, cell.motionKts])

  return pos
}

function WeatherCellMarker({ cell }: { cell: WeatherCell }) {
  const position = useDriftingPosition(cell)
  const select = useMapStore((s) => s.select)
  return (
    <Circle
      center={position}
      radius={cell.radiusKm * 1000}
      pathOptions={{
        color: 'var(--text-muted)',
        fillColor: cell.severity === 'severe' ? 'var(--crit)' : 'var(--warn)',
        fillOpacity: 0.25,
        weight: 1,
      }}
      eventHandlers={{ click: () => select({ kind: 'weatherCell', id: cell.id }) }}
    />
  )
}

interface WeatherLayerProps {
  cells: WeatherCell[]
  bases: AirBase[]
}

export default function WeatherLayer({ cells, bases }: WeatherLayerProps) {
  const { data: obs } = useBaseWeather()

  const latestByBase = new Map<string, { ceilingFt: number; visibilityKm: number }>()
  for (const o of obs ?? []) {
    latestByBase.set(o.baseId, { ceilingFt: o.ceilingFt, visibilityKm: o.visibilityKm })
  }

  return (
    <>
      {cells.map((c) => (
        <WeatherCellMarker key={c.id} cell={c} />
      ))}
      {bases.map((b) => {
        const latest = latestByBase.get(b.id)
        if (!latest) return null
        const label = goNoGo(latest.ceilingFt, latest.visibilityKm)
        return <Marker key={b.id} position={[b.lat, b.lon]} icon={badgeIcon(label)} interactive={false} />
      })}
    </>
  )
}

import { Marker, Rectangle } from 'react-leaflet'
import L from 'leaflet'

import { THEATRE_BOUNDS } from '@/lib/geo'

/** Mirrors backend/app/seed/generator.py's invented 3x4 sector grid (S1-S12) — see
 * PROGRESS.md's Phase 1 deviation note: the spec names a sector grid but never defines
 * its boundaries, so this is the same made-up-but-consistent convention as the seed data. */
const ROWS = 3
const COLS = 4

function sectorLabelIcon(label: string): L.DivIcon {
  return L.divIcon({
    className: '',
    html: `<span class="label-text" style="color:var(--text-muted);font-size:10px;transform:translate(-50%,-50%)">${label}</span>`,
    iconSize: [0, 0],
  })
}

export default function SectorGrid() {
  const latStep = (THEATRE_BOUNDS.maxLat - THEATRE_BOUNDS.minLat) / ROWS
  const lonStep = (THEATRE_BOUNDS.maxLon - THEATRE_BOUNDS.minLon) / COLS

  const cells = []
  let n = 1
  for (let row = 0; row < ROWS; row++) {
    for (let col = 0; col < COLS; col++) {
      const lat0 = THEATRE_BOUNDS.minLat + row * latStep
      const lat1 = lat0 + latStep
      const lon0 = THEATRE_BOUNDS.minLon + col * lonStep
      const lon1 = lon0 + lonStep
      cells.push({ label: `S${n}`, bounds: [[lat0, lon0], [lat1, lon1]] as [[number, number], [number, number]] })
      n += 1
    }
  }

  return (
    <>
      {cells.map((c) => (
        <Rectangle
          key={c.label}
          bounds={c.bounds}
          pathOptions={{ color: 'var(--text-muted)', weight: 1, fill: false, dashArray: '3 5' }}
          interactive={false}
        />
      ))}
      {cells.map((c) => (
        <Marker
          key={`label-${c.label}`}
          position={[(c.bounds[0][0] + c.bounds[1][0]) / 2, (c.bounds[0][1] + c.bounds[1][1]) / 2]}
          icon={sectorLabelIcon(c.label)}
          interactive={false}
        />
      ))}
    </>
  )
}

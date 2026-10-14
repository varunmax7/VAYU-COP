import { useState } from 'react'
import { useMapEvents } from 'react-leaflet'

import { latToDms, lonToDms } from '@/lib/geo'

export default function CoordReadout() {
  const [coords, setCoords] = useState<{ lat: number; lon: number } | null>(null)

  useMapEvents({
    mousemove: (e) => setCoords({ lat: e.latlng.lat, lon: e.latlng.lng }),
    mouseout: () => setCoords(null),
  })

  return (
    <div className="panel pointer-events-none absolute right-3 top-3 z-[500] px-2 py-1">
      <span className="mono-text text-xs text-text-muted">
        {coords ? `${latToDms(coords.lat)}  ${lonToDms(coords.lon)}` : '— — —'}
      </span>
    </div>
  )
}

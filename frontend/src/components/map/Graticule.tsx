import L from 'leaflet'
import { useEffect, useState } from 'react'
import { GeoJSON, Marker } from 'react-leaflet'

import { THEATRE_BOUNDS } from '@/lib/geo'

interface GraticuleFeature {
  type: 'Feature'
  properties: { axis: 'lat' | 'lon'; value: number }
  geometry: GeoJSON.LineString
}

function labelIcon(text: string): L.DivIcon {
  return L.divIcon({
    className: '',
    html: `<span class="mono-text" style="color:var(--text-muted);font-size:10px;white-space:nowrap">${text}</span>`,
    iconSize: [0, 0],
  })
}

export default function Graticule() {
  const [lines, setLines] = useState<GraticuleFeature[]>([])
  const [outline, setOutline] = useState<GeoJSON.FeatureCollection | null>(null)

  useEffect(() => {
    fetch('/geo/graticule.geojson')
      .then((r) => r.json())
      .then((data: GeoJSON.FeatureCollection) =>
        setLines(data.features as unknown as GraticuleFeature[]),
      )
      .catch(() => setLines([]))
    fetch('/geo/theatre-outline.geojson')
      .then((r) => r.json())
      .then(setOutline)
      .catch(() => setOutline(null))
  }, [])

  return (
    <>
      {outline && (
        <GeoJSON
          data={outline}
          style={{ color: 'var(--border)', weight: 1.5, fill: false, dashArray: '4 4' }}
        />
      )}
      {lines.map((line) => (
        <GeoJSON
          key={`${line.properties.axis}-${line.properties.value}`}
          data={line as unknown as GeoJSON.Feature}
          style={{ color: 'var(--grid)', weight: 1 }}
        />
      ))}
      {lines
        .filter((l) => l.properties.axis === 'lat')
        .map((l) => (
          <Marker
            key={`label-lat-${l.properties.value}`}
            position={[l.properties.value, THEATRE_BOUNDS.minLon]}
            icon={labelIcon(`${l.properties.value}°N`)}
            interactive={false}
          />
        ))}
      {lines
        .filter((l) => l.properties.axis === 'lon')
        .map((l) => (
          <Marker
            key={`label-lon-${l.properties.value}`}
            position={[THEATRE_BOUNDS.minLat, l.properties.value]}
            icon={labelIcon(`${l.properties.value}°E`)}
            interactive={false}
          />
        ))}
    </>
  )
}

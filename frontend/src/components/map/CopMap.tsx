import { useState } from 'react'
import { MapContainer, ScaleControl, TileLayer } from 'react-leaflet'

import { useResolvedTheme } from '@/lib/theme'
import { MAP_CENTER, MAP_MAX_BOUNDS, MAP_MAX_ZOOM, MAP_MIN_ZOOM } from '@/lib/geo'
import { useCopSnapshot } from '@/lib/queries'
import { useCopStore } from '@/store/copStore'
import { useMapStore } from '@/store/mapStore'

import AircraftLayer from './AircraftLayer'
import AirspaceLayer from './AirspaceLayer'
import BaseLayer from './BaseLayer'
import CompassRose from './CompassRose'
import ConflictAlertsPanel from './ConflictAlertsPanel'
import CoordReadout from './CoordReadout'
import EntityDrawer from './EntityDrawer'
import Graticule from './Graticule'
import HatchPatternDefs from './HatchPatternDefs'
import LayerToggle from './LayerToggle'
import RangeRingPicker from './RangeRingPicker'
import RangeRingTool from './RangeRingTool'
import RouteLayer from './RouteLayer'
import SectorGrid from './SectorGrid'
import ThreatLayer from './ThreatLayer'
import WeatherLayer from './WeatherLayer'

const TILE_MODE = import.meta.env.VITE_MAP_TILES ?? 'auto'
const TILE_ERROR_THRESHOLD = 8

const TILE_URLS = {
  light: 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
  dark: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
}
const TILE_ATTRIBUTION = '&copy; OpenStreetMap contributors &copy; CARTO'

export default function CopMap() {
  const { data: snapshot } = useCopSnapshot()
  const theme = useResolvedTheme()
  const layers = useMapStore((s) => s.layers)
  const aircraftTracks = useCopStore((s) => s.aircraftTracks)

  const [tileErrorCount, setTileErrorCount] = useState(0)
  const offline = TILE_MODE === 'offline' || tileErrorCount >= TILE_ERROR_THRESHOLD

  if (!snapshot) {
    return (
      <div className="flex h-full items-center justify-center text-sm text-text-muted">
        Loading COP snapshot…
      </div>
    )
  }

  return (
    <div className="relative h-full w-full">
      <MapContainer
        center={MAP_CENTER}
        zoom={MAP_MIN_ZOOM}
        minZoom={MAP_MIN_ZOOM}
        maxZoom={MAP_MAX_ZOOM}
        maxBounds={MAP_MAX_BOUNDS}
        maxBoundsViscosity={1.0}
        className="h-full w-full"
        zoomControl={true}
      >
        <HatchPatternDefs />
        {!offline && (
          <TileLayer
            key={theme} // force a fresh layer when the theme flips, rather than re-tinting tiles
            url={TILE_URLS[theme]}
            attribution={TILE_ATTRIBUTION}
            eventHandlers={{ tileerror: () => setTileErrorCount((c) => c + 1) }}
          />
        )}
        <Graticule />
        {layers.sectorGrid && <SectorGrid />}
        {layers.airspace && <AirspaceLayer airspace={snapshot.airspace} />}
        {layers.weather && <WeatherLayer cells={snapshot.weatherCells} bases={snapshot.bases} />}
        {layers.threats && <ThreatLayer threats={snapshot.threats} />}
        {layers.routes && <RouteLayer routes={snapshot.routes} highlightedAssignmentId={null} />}
        {layers.bases && <BaseLayer bases={snapshot.bases} />}
        {layers.aircraft && (
          <AircraftLayer aircraft={snapshot.aircraft} tracks={aircraftTracks} />
        )}
        <RangeRingTool bases={snapshot.bases} />

        <CompassRose />
        <CoordReadout />
        <ScaleControl position="bottomright" />
      </MapContainer>

      <LayerToggle />
      <RangeRingPicker />
      <EntityDrawer snapshot={snapshot} />
      <ConflictAlertsPanel />

      {offline && (
        <div className="label-text pointer-events-none absolute bottom-10 right-3 z-[500] rounded border border-border bg-panel px-2 py-1 text-[10px] text-text-muted">
          OFFLINE MAP MODE
        </div>
      )}
    </div>
  )
}

/** Mirrors the backend's camelCase Pydantic Read schemas (§6.3). Kept as plain
 * hand-written interfaces rather than the generated api-types.ts because the map/resource
 * components want narrower, friendlier shapes — regenerate api-types.ts separately if a
 * phase needs the full OpenAPI-derived types. */

export interface ProvenanceFields {
  source: string
  sourceTs: string
  fusedTs: string
  confidence: number
  stale: boolean
}

export interface AirBase {
  id: string
  name: string
  code: string
  lat: number
  lon: number
  status: 'OPEN' | 'RESTRICTED' | 'CLOSED'
  runways: number
  runwayCapacityPer15Min: number
  parkingCapacity: number
  fuelStockKl: number
  closures: { from: string; to: string; reason: string }[]
}

export interface Aircraft extends ProvenanceFields {
  id: string
  tailNumber: string
  callsign: string
  typeCode: string
  baseId: string
  status: 'READY' | 'TASKED' | 'AIRBORNE' | 'TURNAROUND' | 'MAINTENANCE' | 'UNSERVICEABLE'
  fuelPct: number
  airframeHours: number
  hoursSinceMaint: number
  hoursToNextMaint: number
  storeConfig: string | null
  lat: number
  lon: number
  headingDeg: number
  altFt: number
  speedKts: number
  currentAssignmentId: string | null
  pUnserviceable24H: number
}

export interface AircraftType {
  code: string
  name: string
  roles: string[]
  cruiseKts: number
  rangeKm: number
  enduranceH: number
  turnaroundMin: number
  crewRequired: Record<string, number>
  compatibleStores: string[]
  wxMinima: { ceilingFt: number; visibilityKm: number; crosswindKt: number }
}

export interface Airspace extends ProvenanceFields {
  id: string
  name: string
  kind: 'RESTRICTED' | 'DANGER' | 'CORRIDOR' | 'MOA'
  polygonGeojson: GeoJSON.Polygon
  floorFt: number
  ceilingFt: number
  activeFrom: string | null
  activeTo: string | null
  status: 'ACTIVE' | 'CLOSED' | 'OPEN'
}

export interface ThreatZone extends ProvenanceFields {
  id: string
  label: string
  level: 'HIGH' | 'MED' | 'LOW'
  centerLat: number
  centerLon: number
  radiusKm: number
  mobile: boolean
  firstSeen: string
  lastSeen: string
  sources: string[]
}

export interface WeatherCell {
  id: string
  label: string
  centerLat: number
  centerLon: number
  radiusKm: number
  severity: string
  motionDeg: number
  motionKts: number
}

export interface WeatherObs extends ProvenanceFields {
  id: string
  baseId: string
  validTs: string
  ceilingFt: number
  visibilityKm: number
  windKt: number
  gustKt: number
  crosswindKt: number
  precipMm: number
  thunderstorm: boolean
  isForecast: boolean
}

export interface RouteSegment {
  assignmentId: string
  missionId: string
  missionType: string
  aircraftId: string
  phase: 'PLANNED' | 'AIRBORNE' | 'FLOWN'
  geometry: GeoJSON.LineString
}

export interface CopSnapshot {
  bases: AirBase[]
  aircraft: Aircraft[]
  airspace: Airspace[]
  threats: ThreatZone[]
  weatherCells: WeatherCell[]
  routes: RouteSegment[]
  activePlan: { id: string; version: number; profile: string; kpis: Record<string, number>; confidence: number } | null
}

export interface Alert {
  id: string
  ts: string
  severity: 'CRITICAL' | 'WARNING' | 'INFO'
  category: string
  message: string
  entityRefs: { kind: string; id: string }[]
  dedupKey: string
  acknowledgedBy: string | null
  acknowledgedAt: string | null
  resolved: boolean
  resolvedAt: string | null
}

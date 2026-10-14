/** Theatre bounds & geometry helpers shared by the map layers (§2, §13.4). */

export const THEATRE_BOUNDS = {
  minLat: 17.5,
  maxLat: 25.5,
  minLon: 74.0,
  maxLon: 84.0,
}

/** maxBounds = theatre box padded by 1°, per §2 (keeps international boundaries off-map). */
export const MAP_MAX_BOUNDS: [[number, number], [number, number]] = [
  [THEATRE_BOUNDS.minLat - 1, THEATRE_BOUNDS.minLon - 1],
  [THEATRE_BOUNDS.maxLat + 1, THEATRE_BOUNDS.maxLon + 1],
]

export const MAP_MIN_ZOOM = 6
export const MAP_MAX_ZOOM = 11
export const MAP_CENTER: [number, number] = [
  (THEATRE_BOUNDS.minLat + THEATRE_BOUNDS.maxLat) / 2,
  (THEATRE_BOUNDS.minLon + THEATRE_BOUNDS.maxLon) / 2,
]

function toDms(value: number, posHemi: string, negHemi: string): string {
  const hemi = value >= 0 ? posHemi : negHemi
  const abs = Math.abs(value)
  const deg = Math.floor(abs)
  const minutesFull = (abs - deg) * 60
  const minutes = Math.floor(minutesFull)
  const seconds = Math.round((minutesFull - minutes) * 60)
  return `${String(deg).padStart(posHemi === 'N' ? 2 : 3, '0')}°${String(minutes).padStart(2, '0')}'${String(seconds).padStart(2, '0')}"${hemi}`
}

export function latToDms(lat: number): string {
  return toDms(lat, 'N', 'S')
}

export function lonToDms(lon: number): string {
  return toDms(lon, 'E', 'W')
}

const EARTH_RADIUS_KM = 6371

export function haversineKm(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const toRad = (d: number) => (d * Math.PI) / 180
  const dLat = toRad(lat2 - lat1)
  const dLon = toRad(lon2 - lon1)
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) ** 2
  return 2 * EARTH_RADIUS_KM * Math.asin(Math.sqrt(a))
}

/** Points on a circle of `radiusKm` around (lat, lon) — for threat/range rings on the map. */
export function circlePoints(
  lat: number,
  lon: number,
  radiusKm: number,
  steps = 64,
): [number, number][] {
  const points: [number, number][] = []
  const latRad = (lat * Math.PI) / 180
  const kmPerDegLat = 111.32
  const kmPerDegLon = 111.32 * Math.cos(latRad)
  for (let i = 0; i <= steps; i++) {
    const angle = (i / steps) * 2 * Math.PI
    const dLat = (radiusKm * Math.sin(angle)) / kmPerDegLat
    const dLon = (radiusKm * Math.cos(angle)) / (kmPerDegLon || 1e-6)
    points.push([lat + dLat, lon + dLon])
  }
  return points
}

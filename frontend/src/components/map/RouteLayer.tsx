import { GeoJSON } from 'react-leaflet'

import type { RouteSegment } from '@/lib/copTypes'

const MISSION_COLOR: Record<string, string> = {
  CAP: 'var(--m-cap)',
  RECCE: 'var(--m-recce)',
  STRIKE: 'var(--m-strike)',
  AIRLIFT: 'var(--m-airlift)',
  TANKER: 'var(--m-tanker)',
  AEW: 'var(--m-aew)',
  SAR: 'var(--m-sar)',
  HADR: 'var(--m-hadr)',
}

const PHASE_DASH: Record<RouteSegment['phase'], string | undefined> = {
  PLANNED: '8 6',
  AIRBORNE: undefined, // solid
  FLOWN: '2 6',
}

interface RouteLayerProps {
  routes: RouteSegment[]
  highlightedAssignmentId: string | null
}

export default function RouteLayer({ routes, highlightedAssignmentId }: RouteLayerProps) {
  return (
    <>
      {routes.map((r) => {
        const highlighted = r.assignmentId === highlightedAssignmentId
        return (
          <GeoJSON
            key={r.assignmentId}
            data={r.geometry}
            style={{
              color: MISSION_COLOR[r.missionType] ?? 'var(--accent)',
              weight: highlighted ? 4 : 2,
              dashArray: PHASE_DASH[r.phase],
              opacity: highlighted ? 1 : 0.8,
            }}
          />
        )
      })}
    </>
  )
}

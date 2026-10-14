import { useEffect } from 'react'
import { Circle, Tooltip } from 'react-leaflet'

import type { AirBase } from '@/lib/copTypes'
import { useAircraftTypes } from '@/lib/queries'
import { useMapStore } from '@/store/mapStore'

interface RangeRingToolProps {
  bases: AirBase[]
}

/** Right-click a base (BaseLayer) to activate; shows the selected type's full range plus
 * the 30/60-minute transit rings at cruise speed (§13.4). */
export default function RangeRingTool({ bases }: RangeRingToolProps) {
  const rangeRingBaseId = useMapStore((s) => s.rangeRingBaseId)
  const rangeRingTypeCode = useMapStore((s) => s.rangeRingTypeCode)
  const setRangeRing = useMapStore((s) => s.setRangeRing)
  const { data: types } = useAircraftTypes()

  const base = bases.find((b) => b.id === rangeRingBaseId)
  const selectedType = types?.find((t) => t.code === rangeRingTypeCode) ?? types?.[0]

  useEffect(() => {
    if (rangeRingBaseId && !rangeRingTypeCode && types?.[0]) {
      setRangeRing(rangeRingBaseId, types[0].code)
    }
  }, [rangeRingBaseId, rangeRingTypeCode, types, setRangeRing])

  if (!base || !selectedType) return null

  const transit30Km = selectedType.cruiseKts * 1.852 * 0.5
  const transit60Km = selectedType.cruiseKts * 1.852 * 1.0

  return (
    <>
      <Circle
        center={[base.lat, base.lon]}
        radius={selectedType.rangeKm * 1000}
        pathOptions={{ color: 'var(--accent)', weight: 1.5, fill: false, dashArray: '2 8' }}
      >
        <Tooltip direction="right" permanent className="mono-text text-xs" opacity={1}>
          {selectedType.code} range {selectedType.rangeKm} km
        </Tooltip>
      </Circle>
      <Circle
        center={[base.lat, base.lon]}
        radius={transit60Km * 1000}
        pathOptions={{ color: 'var(--ok)', weight: 1, fill: false, dashArray: '6 6' }}
      >
        <Tooltip direction="top" permanent className="mono-text text-xs" opacity={1}>
          60 min
        </Tooltip>
      </Circle>
      <Circle
        center={[base.lat, base.lon]}
        radius={transit30Km * 1000}
        pathOptions={{ color: 'var(--ok)', weight: 1, fill: false, dashArray: '2 4' }}
      >
        <Tooltip direction="top" permanent className="mono-text text-xs" opacity={1}>
          30 min
        </Tooltip>
      </Circle>
    </>
  )
}

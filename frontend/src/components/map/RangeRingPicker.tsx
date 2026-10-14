import { X } from 'lucide-react'

import { useAircraftTypes } from '@/lib/queries'
import { useMapStore } from '@/store/mapStore'

export default function RangeRingPicker() {
  const rangeRingBaseId = useMapStore((s) => s.rangeRingBaseId)
  const rangeRingTypeCode = useMapStore((s) => s.rangeRingTypeCode)
  const setRangeRing = useMapStore((s) => s.setRangeRing)
  const { data: types } = useAircraftTypes()

  if (!rangeRingBaseId) return null

  return (
    <div className="panel pointer-events-auto absolute right-3 top-40 z-[500] w-36 p-2">
      <div className="mb-1 flex items-center justify-between">
        <h3 className="label-text text-[10px] text-text-muted">Range rings</h3>
        <button
          type="button"
          onClick={() => setRangeRing(null, null)}
          aria-label="Close range ring tool"
          className="text-text-muted hover:text-text"
        >
          <X className="h-3.5 w-3.5" />
        </button>
      </div>
      <select
        value={rangeRingTypeCode ?? ''}
        onChange={(e) => setRangeRing(rangeRingBaseId, e.target.value)}
        className="mono-text w-full rounded border border-border bg-panel-2 px-1 py-0.5 text-xs"
      >
        {types?.map((t) => (
          <option key={t.code} value={t.code}>
            {t.code}
          </option>
        ))}
      </select>
    </div>
  )
}

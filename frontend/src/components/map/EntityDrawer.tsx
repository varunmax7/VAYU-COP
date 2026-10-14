import { useQueryClient } from '@tanstack/react-query'
import { formatDistanceToNow } from 'date-fns'
import { X } from 'lucide-react'
import { useState } from 'react'
import { toast } from 'sonner'

import { api, ApiError } from '@/lib/api'
import type { Aircraft, Airspace, CopSnapshot, ThreatZone } from '@/lib/copTypes'
import { useAuth } from '@/lib/auth'
import { cn } from '@/lib/utils'
import { useMapStore } from '@/store/mapStore'

interface FieldRow {
  label: string
  value: string
  provenance?: string
}

function provenanceTooltip(source: string, sourceTs: string, confidence: number): string {
  const age = formatDistanceToNow(new Date(sourceTs), { addSuffix: true })
  return `Source: ${source} · ${age} · conf ${confidence.toFixed(2)}`
}

function buildFields(
  kind: string,
  snapshot: CopSnapshot,
  id: string,
): { title: string; subtitle: string; fields: FieldRow[]; raw: Aircraft | Airspace | ThreatZone | CopSnapshot['bases'][number] | CopSnapshot['weatherCells'][number] | null } {
  if (kind === 'base') {
    const b = snapshot.bases.find((x) => x.id === id)
    if (!b) return { title: 'Base', subtitle: '', fields: [], raw: null }
    return {
      title: b.name,
      subtitle: b.code,
      fields: [
        { label: 'Status', value: b.status },
        { label: 'Runways', value: String(b.runways) },
        { label: 'Runway cap / 15 min', value: String(b.runwayCapacityPer15Min) },
        { label: 'Parking capacity', value: String(b.parkingCapacity) },
        { label: 'Fuel stock', value: `${b.fuelStockKl} kL` },
        { label: 'Position', value: `${b.lat.toFixed(4)}, ${b.lon.toFixed(4)}` },
      ],
      raw: b,
    }
  }
  if (kind === 'aircraft') {
    const a = snapshot.aircraft.find((x) => x.id === id)
    if (!a) return { title: 'Aircraft', subtitle: '', fields: [], raw: null }
    const prov = provenanceTooltip(a.source, a.sourceTs, a.confidence)
    return {
      title: a.callsign,
      subtitle: `${a.typeCode} · ${a.tailNumber}`,
      fields: [
        { label: 'Status', value: a.status, provenance: prov },
        { label: 'Base', value: a.baseId },
        { label: 'Fuel', value: `${a.fuelPct.toFixed(0)}%` },
        { label: 'Hours to next maint.', value: `${a.hoursToNextMaint.toFixed(1)} h` },
        { label: 'P(U/S 24h)', value: `${(a.pUnserviceable24H * 100).toFixed(0)}%` },
        { label: 'Position', value: `${a.lat.toFixed(4)}, ${a.lon.toFixed(4)}`, provenance: 'Source: track_feed' },
        { label: 'Stale', value: a.stale ? 'yes' : 'no' },
      ],
      raw: a,
    }
  }
  if (kind === 'threat') {
    const t = snapshot.threats.find((x) => x.id === id)
    if (!t) return { title: 'Threat', subtitle: '', fields: [], raw: null }
    return {
      title: `Threat Zone ${t.label}`,
      subtitle: t.level,
      fields: [
        { label: 'Confidence', value: t.confidence.toFixed(2), provenance: provenanceTooltip(t.source, t.sourceTs, t.confidence) },
        { label: 'Radius', value: `${t.radiusKm} km` },
        { label: 'Mobile', value: t.mobile ? 'yes' : 'no' },
        { label: 'Sources', value: t.sources.join(', ') },
        { label: 'First seen', value: formatDistanceToNow(new Date(t.firstSeen), { addSuffix: true }) },
        { label: 'Last seen', value: formatDistanceToNow(new Date(t.lastSeen), { addSuffix: true }) },
      ],
      raw: t,
    }
  }
  if (kind === 'airspace') {
    const a = snapshot.airspace.find((x) => x.id === id)
    if (!a) return { title: 'Airspace', subtitle: '', fields: [], raw: null }
    return {
      title: `Airspace ${a.name}`,
      subtitle: a.kind,
      fields: [
        { label: 'Status', value: a.status, provenance: provenanceTooltip(a.source, a.sourceTs, a.confidence) },
        { label: 'Floor / ceiling', value: `${a.floorFt} / ${a.ceilingFt} ft` },
        { label: 'Active from', value: a.activeFrom ?? '—' },
        { label: 'Active to', value: a.activeTo ?? '—' },
      ],
      raw: a,
    }
  }
  if (kind === 'weatherCell') {
    const w = snapshot.weatherCells.find((x) => x.id === id)
    if (!w) return { title: 'Weather cell', subtitle: '', fields: [], raw: null }
    return {
      title: w.label,
      subtitle: w.severity,
      fields: [
        { label: 'Radius', value: `${w.radiusKm} km` },
        { label: 'Motion', value: `${w.motionDeg}° / ${w.motionKts} kt` },
        { label: 'Position', value: `${w.centerLat.toFixed(4)}, ${w.centerLon.toFixed(4)}` },
      ],
      raw: w,
    }
  }
  return { title: 'Unknown entity', subtitle: '', fields: [], raw: null }
}

interface EntityDrawerProps {
  snapshot: CopSnapshot
}

export default function EntityDrawer({ snapshot }: EntityDrawerProps) {
  const selected = useMapStore((s) => s.selected)
  const select = useMapStore((s) => s.select)
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const [isSubmitting, setIsSubmitting] = useState(false)

  if (!selected) return null

  const { title, subtitle, fields, raw } = buildFields(selected.kind, snapshot, selected.id)
  const aircraft = selected.kind === 'aircraft' ? (raw as Aircraft) : null

  async function markUnserviceable() {
    if (!aircraft) return
    setIsSubmitting(true)
    try {
      await api.patch(`/aircraft/${aircraft.id}/status`, { status: 'UNSERVICEABLE' })
      toast.success(`${aircraft.callsign} marked UNSERVICEABLE`)
      queryClient.invalidateQueries({ queryKey: ['cop-snapshot'] })
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : 'Failed to update status')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="panel pointer-events-auto absolute right-3 top-3 z-[600] max-h-[calc(100%-1.5rem)] w-72 overflow-y-auto">
      <div className="flex items-center justify-between border-b border-border p-3">
        <div>
          <h2 className="label-text text-sm">{title}</h2>
          {subtitle && <p className="mono-text text-xs text-text-muted">{subtitle}</p>}
        </div>
        <button
          type="button"
          onClick={() => select(null)}
          aria-label="Close"
          className="text-text-muted hover:text-text"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      <dl className="flex flex-col gap-2 p-3">
        {fields.map((f) => (
          <div key={f.label} title={f.provenance} className={cn(f.provenance && 'cursor-help')}>
            <dt className="label-text text-[10px] text-text-muted">{f.label}</dt>
            <dd className="mono-text text-sm">{f.value}</dd>
          </div>
        ))}
        {fields.length === 0 && <p className="text-xs text-text-muted">No data found.</p>}
      </dl>

      {aircraft && aircraft.status === 'MAINTENANCE' && (user?.role === 'MAINTENANCE' || user?.role === 'ADMIN') && (
        <div className="border-t border-border p-3">
          <button
            type="button"
            onClick={markUnserviceable}
            disabled={isSubmitting}
            className="label-text w-full rounded bg-crit px-3 py-1.5 text-xs text-white disabled:opacity-60"
          >
            {isSubmitting ? 'UPDATING…' : 'MARK U/S'}
          </button>
        </div>
      )}
    </div>
  )
}

import { useQuery } from '@tanstack/react-query'
import { AlertTriangle, Cpu, Navigation, Plane, Users } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

import { api } from '@/lib/api'
import { useCopStore, type KpiUpdateMsg } from '@/store/copStore'

import ZuluClock from './ZuluClock'

async function fetchKpis(): Promise<KpiUpdateMsg> {
  return api.get<KpiUpdateMsg>('/kpis')
}

export default function KpiStrip() {
  const navigate = useNavigate()
  const liveKpis = useCopStore((s) => s.kpis)
  const { data: fetchedKpis } = useQuery({
    queryKey: ['kpis'],
    queryFn: fetchKpis,
    refetchInterval: 5000, // WS pushes faster updates; this is just the pre-connect/fallback path
  })

  const kpis = liveKpis ?? fetchedKpis

  return (
    <div className="flex h-12 shrink-0 items-center gap-1 overflow-x-auto border-b border-border bg-panel px-3">
      <button
        type="button"
        onClick={() => navigate('/resources?status=READY')}
        className="label-text flex items-center gap-1.5 whitespace-nowrap rounded px-2 py-1 text-sm hover:bg-panel-2"
      >
        <Plane className="h-4 w-4 text-ok" aria-hidden />
        <span className="text-xs text-text-muted">AIRCRAFT READY</span>
        <span className="mono-text font-medium text-ok">
          {kpis ? `${kpis.aircraftReady}/${kpis.aircraftTotal}` : '—'}
        </span>
      </button>

      <button
        type="button"
        onClick={() => navigate('/resources?status=AIRBORNE')}
        className="label-text flex items-center gap-1.5 whitespace-nowrap rounded px-2 py-1 text-sm hover:bg-panel-2"
      >
        <Navigation className="h-4 w-4 text-accent" aria-hidden />
        <span className="text-xs text-text-muted">ACTIVE SORTIES</span>
        <span className="mono-text font-medium text-accent">{kpis?.activeSorties ?? '—'}</span>
      </button>

      <button
        type="button"
        onClick={() => navigate('/resources?tab=crew')}
        className="label-text flex items-center gap-1.5 whitespace-nowrap rounded px-2 py-1 text-sm hover:bg-panel-2"
      >
        <Users className="h-4 w-4 text-ok" aria-hidden />
        <span className="text-xs text-text-muted">CREW CURRENCY</span>
        <span className="mono-text font-medium text-ok">
          {kpis ? `${kpis.crewCurrencyPct}%` : '—'}
        </span>
      </button>

      <button
        type="button"
        onClick={() => navigate('/audit?severity=CRITICAL')}
        className="label-text flex items-center gap-1.5 whitespace-nowrap rounded px-2 py-1 text-sm hover:bg-panel-2"
      >
        <AlertTriangle
          className={`h-4 w-4 ${kpis && kpis.criticalAlerts > 0 ? 'text-crit' : 'text-text-muted'}`}
          aria-hidden
        />
        <span className="text-xs text-text-muted">CRITICAL ALERTS</span>
        <span
          className={`mono-text font-medium ${kpis && kpis.criticalAlerts > 0 ? 'text-crit' : 'text-text'}`}
        >
          {kpis?.criticalAlerts ?? '—'}
        </span>
      </button>

      <div className="label-text flex items-center gap-1.5 whitespace-nowrap rounded px-2 py-1 text-sm">
        <Cpu className="h-4 w-4 text-accent" aria-hidden />
        <span className="text-xs text-text-muted">AI ENGINE</span>
        <span className="mono-text font-medium text-accent">
          {kpis?.aiConfidencePct != null ? `${kpis.aiConfidencePct}% CONFIDENCE` : 'NO ACTIVE PLAN'}
        </span>
      </div>

      <div className="ml-auto">
        <ZuluClock now={kpis ? new Date(kpis.zuluTime) : undefined} />
      </div>
    </div>
  )
}

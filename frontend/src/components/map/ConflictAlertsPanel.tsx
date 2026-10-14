import { ChevronDown, ChevronUp } from 'lucide-react'
import { useState } from 'react'
import { toast } from 'sonner'

import { api, ApiError } from '@/lib/api'
import type { Alert } from '@/lib/copTypes'
import { useAlerts } from '@/lib/queries'
import { cn } from '@/lib/utils'
import { useMapStore } from '@/store/mapStore'

const SEVERITY_BORDER: Record<Alert['severity'], string> = {
  CRITICAL: 'border-l-crit',
  WARNING: 'border-l-warn',
  INFO: 'border-l-accent',
}

const HEADER_BY_CATEGORY: Record<string, string> = {
  ROUTE_THREAT: 'CONFLICT ALERT:',
  AIRSPACE_CLOSED: 'RE-ROUTE REQUIRED:',
}

function AlertItem({ alert }: { alert: Alert }) {
  const select = useMapStore((s) => s.select)

  async function ack() {
    try {
      await api.post(`/alerts/${alert.id}/ack`)
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : 'Failed to acknowledge')
    }
  }

  async function fixWithAi() {
    try {
      await api.post(`/alerts/${alert.id}/fix`)
      toast.success('Retask proposal requested')
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : 'Fix with AI is not available yet')
    }
  }

  function locate() {
    const ref = alert.entityRefs[0]
    if (ref) select({ kind: ref.kind as never, id: ref.id })
  }

  return (
    <li className={cn('border-l-2 py-1.5 pl-2', SEVERITY_BORDER[alert.severity])}>
      <p className="label-text text-[10px]">{HEADER_BY_CATEGORY[alert.category] ?? `${alert.category}:`}</p>
      <p className="text-xs">{alert.message}</p>
      <div className="mt-1 flex gap-2 text-[10px]">
        <button type="button" onClick={locate} className="label-text text-accent hover:underline">
          Locate
        </button>
        <button type="button" onClick={ack} className="label-text text-accent hover:underline">
          Ack
        </button>
        <button type="button" onClick={fixWithAi} className="label-text text-accent hover:underline">
          Fix with AI
        </button>
      </div>
    </li>
  )
}

export default function ConflictAlertsPanel() {
  const { data: alerts } = useAlerts()
  const [collapsed, setCollapsed] = useState(false)

  return (
    <div className="panel pointer-events-auto absolute bottom-3 left-3 z-[500] w-[300px] max-w-[calc(100%-1.5rem)]">
      <div className="flex items-center justify-between border-b border-border px-3 py-2">
        <h2 className="label-text text-xs">LIVE CONFLICT ALERTS</h2>
        <button
          type="button"
          onClick={() => setCollapsed((c) => !c)}
          aria-label={collapsed ? 'Expand' : 'Collapse'}
          className="text-text-muted hover:text-text"
        >
          {collapsed ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
        </button>
      </div>
      {!collapsed && (
        <ul className="max-h-48 overflow-y-auto px-3 py-2">
          {alerts && alerts.length > 0 ? (
            alerts.map((a) => <AlertItem key={a.id} alert={a} />)
          ) : (
            <li className="py-2 text-xs text-text-muted">No active conflicts.</li>
          )}
        </ul>
      )}
    </div>
  )
}

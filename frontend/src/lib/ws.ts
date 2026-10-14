import { getStoredToken } from '@/lib/api'
import { useCopStore } from '@/store/copStore'
import { useUiStore } from '@/store/uiStore'

/** Dispatched on the window after every successful (re)connect, so any screen can
 * refetch its REST snapshot to resync (§12.2: "client ... refetches /cop/snapshot
 * after each reconnect"). */
export const WS_OPEN_EVENT = 'vayu:ws-open'

interface WsEnvelope {
  type: string
  ts: string
  seq: number
  payload: unknown
}

let socket: WebSocket | null = null
let reconnectAttempt = 0
let reconnectTimer: ReturnType<typeof setTimeout> | null = null
let manuallyClosed = false

function scheduleReconnect(): void {
  if (manuallyClosed) return
  const delay = Math.min(30_000, 1000 * 2 ** reconnectAttempt)
  reconnectAttempt += 1
  reconnectTimer = setTimeout(connectWs, delay)
}

export function connectWs(): void {
  manuallyClosed = false
  const token = getStoredToken()
  if (!token) return

  socket?.close()

  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
  const ws = new WebSocket(`${protocol}://${window.location.host}/ws?token=${encodeURIComponent(token)}`)
  socket = ws
  useUiStore.getState().setWsStatus('connecting')

  ws.onopen = () => {
    reconnectAttempt = 0
    useUiStore.getState().setWsStatus('connected')
    window.dispatchEvent(new Event(WS_OPEN_EVENT))
  }

  ws.onclose = () => {
    useUiStore.getState().setWsStatus('disconnected')
    if (socket === ws) scheduleReconnect()
  }

  ws.onerror = () => ws.close()

  ws.onmessage = (event: MessageEvent<string>) => {
    try {
      handleEnvelope(JSON.parse(event.data) as WsEnvelope)
    } catch {
      // malformed frame — drop it
    }
  }
}

export function disconnectWs(): void {
  manuallyClosed = true
  if (reconnectTimer) clearTimeout(reconnectTimer)
  socket?.close()
  socket = null
}

function handleEnvelope(envelope: WsEnvelope): void {
  switch (envelope.type) {
    case 'aircraft.position':
      useCopStore.getState().setAircraftPositions(envelope.payload as never)
      break
    case 'kpi.update':
      useCopStore.getState().setKpis(envelope.payload as never)
      break
    case 'fusion.health':
      useCopStore.getState().setFusionHealth(envelope.payload as never)
      break
    case 'cop.delta':
      useCopStore.getState().setLastDelta(envelope.payload as never)
      break
    default:
      break
  }
}

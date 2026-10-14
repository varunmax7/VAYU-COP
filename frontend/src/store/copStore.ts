import { create } from 'zustand'

/** Live state pushed over the WebSocket (§12.2). */

export interface AircraftPositionMsg {
  id: string
  lat: number
  lon: number
  hdg: number
  alt: number
  spd: number
  fuel: number
}

/** Previous + current snapshot with timestamps, so AircraftLayer can tween the marker
 * smoothly between 1 Hz updates instead of jumping (§13.4: "smooth interpolation"). */
export interface AircraftTrack {
  prev: AircraftPositionMsg
  curr: AircraftPositionMsg
  prevTs: number
  currTs: number
}

export interface KpiUpdateMsg {
  aircraftReady: number
  aircraftTotal: number
  activeSorties: number
  crewCurrencyPct: number
  criticalAlerts: number
  aiConfidencePct: number | null
  zuluTime: string
}

export interface FusionHealthEntry {
  enabled: boolean
  status: 'OK' | 'DEGRADED' | 'DOWN'
  lastMsgTs: string | null
  msgsPerMin: number
  errors: number
  lagS: number | null
}

export interface CopDeltaMsg {
  kind: string
  id: string
  patch: Record<string, unknown>
}

interface CopState {
  aircraftTracks: Record<string, AircraftTrack>
  kpis: KpiUpdateMsg | null
  fusionHealth: Record<string, FusionHealthEntry>
  lastDelta: CopDeltaMsg[] | null
  setAircraftPositions: (batch: AircraftPositionMsg[]) => void
  setKpis: (kpis: KpiUpdateMsg) => void
  setFusionHealth: (health: Record<string, FusionHealthEntry>) => void
  setLastDelta: (deltas: CopDeltaMsg[]) => void
}

export const useCopStore = create<CopState>((set) => ({
  aircraftTracks: {},
  kpis: null,
  fusionHealth: {},
  lastDelta: null,
  setAircraftPositions: (batch) =>
    set((s) => {
      const now = performance.now()
      const next = { ...s.aircraftTracks }
      for (const a of batch) {
        const existing = next[a.id]
        next[a.id] = {
          prev: existing?.curr ?? a,
          curr: a,
          prevTs: existing?.currTs ?? now,
          currTs: now,
        }
      }
      return { aircraftTracks: next }
    }),
  setKpis: (kpis) => set({ kpis }),
  setFusionHealth: (health) => set({ fusionHealth: health }),
  setLastDelta: (deltas) => set({ lastDelta: deltas }),
}))

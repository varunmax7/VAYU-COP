import { useQuery } from '@tanstack/react-query'

import { api } from '@/lib/api'
import type { AircraftType, Alert, CopSnapshot, WeatherObs } from '@/lib/copTypes'

export function useCopSnapshot() {
  return useQuery({
    queryKey: ['cop-snapshot'],
    queryFn: () => api.get<CopSnapshot>('/cop/snapshot'),
    refetchInterval: 15_000, // WS cop.delta covers fast-moving changes; this just resyncs the rest
  })
}

export function useAircraftTypes() {
  return useQuery({
    queryKey: ['aircraft-types'],
    queryFn: () => api.get<AircraftType[]>('/aircraft-types'),
    staleTime: 5 * 60_000, // reference data — rarely changes
  })
}

export function useBaseWeather() {
  return useQuery({
    queryKey: ['weather-bases'],
    queryFn: () => api.get<WeatherObs[]>('/weather/bases'),
    refetchInterval: 30_000,
  })
}

/** GET /alerts doesn't exist until Phase 10 — this resolves to an empty list via a 404
 * rather than erroring, so ConflictAlertsPanel can render its empty state cleanly today
 * and "just work" once that endpoint ships. */
export function useAlerts() {
  return useQuery({
    queryKey: ['alerts'],
    queryFn: async () => {
      try {
        return await api.get<Alert[]>('/alerts?open=true')
      } catch {
        return [] as Alert[]
      }
    },
    refetchInterval: 10_000,
  })
}

import { create } from 'zustand'

export interface LayerVisibility {
  bases: boolean
  aircraft: boolean
  routes: boolean
  threats: boolean
  airspace: boolean
  weather: boolean
  sectorGrid: boolean
  labels: boolean
}

export type EntityKind = 'base' | 'aircraft' | 'threat' | 'airspace' | 'weatherCell'

export interface SelectedEntity {
  kind: EntityKind
  id: string
}

interface MapState {
  layers: LayerVisibility
  toggleLayer: (layer: keyof LayerVisibility) => void

  selected: SelectedEntity | null
  select: (entity: SelectedEntity | null) => void

  rangeRingBaseId: string | null
  rangeRingTypeCode: string | null
  setRangeRing: (baseId: string | null, typeCode: string | null) => void
}

export const useMapStore = create<MapState>((set) => ({
  layers: {
    bases: true,
    aircraft: true,
    routes: true,
    threats: true,
    airspace: true,
    weather: true,
    sectorGrid: false,
    labels: true,
  },
  toggleLayer: (layer) =>
    set((s) => ({ layers: { ...s.layers, [layer]: !s.layers[layer] } })),

  selected: null,
  select: (entity) => set({ selected: entity }),

  rangeRingBaseId: null,
  rangeRingTypeCode: null,
  setRangeRing: (baseId, typeCode) => set({ rangeRingBaseId: baseId, rangeRingTypeCode: typeCode }),
}))

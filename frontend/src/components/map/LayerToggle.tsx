import { useMapStore, type LayerVisibility } from '@/store/mapStore'

const LABELS: Record<keyof LayerVisibility, string> = {
  bases: 'Bases',
  aircraft: 'Aircraft',
  routes: 'Routes',
  threats: 'Threats',
  airspace: 'Airspace',
  weather: 'Weather',
  sectorGrid: 'Sector grid',
  labels: 'Labels',
}

export default function LayerToggle() {
  const layers = useMapStore((s) => s.layers)
  const toggleLayer = useMapStore((s) => s.toggleLayer)

  return (
    <div className="panel pointer-events-auto absolute right-3 top-16 z-[500] w-36 p-2">
      <h3 className="label-text mb-1 text-[10px] text-text-muted">Layers</h3>
      <ul className="flex flex-col gap-1">
        {(Object.keys(LABELS) as (keyof LayerVisibility)[]).map((key) => (
          <li key={key}>
            <label className="flex cursor-pointer items-center gap-2 text-xs">
              <input
                type="checkbox"
                checked={layers[key]}
                onChange={() => toggleLayer(key)}
                className="accent-accent"
              />
              {LABELS[key]}
            </label>
          </li>
        ))}
      </ul>
    </div>
  )
}

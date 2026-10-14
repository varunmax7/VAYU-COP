import { useEffect } from 'react'
import { useMap } from 'react-leaflet'

/** Leaflet's pathOptions.fillColor accepts any valid SVG fill string, including
 * `url(#id)` — so a hand-rolled <pattern> in the map's own SVG root gives restricted
 * airspace a real 45° hatch fill without pulling in a Leaflet plugin (§13.3/§13.4). */
export default function HatchPatternDefs() {
  const map = useMap()

  useEffect(() => {
    const svg = map.getContainer().querySelector('svg')
    if (!svg || svg.querySelector('#vayu-hatch')) return

    const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs')
    defs.innerHTML = `
      <pattern id="vayu-hatch" width="8" height="8" patternTransform="rotate(45)" patternUnits="userSpaceOnUse">
        <rect width="8" height="8" fill="transparent" />
        <line x1="0" y1="0" x2="0" y2="8" stroke="var(--text-muted)" stroke-width="2" />
      </pattern>
    `
    svg.insertBefore(defs, svg.firstChild)
  }, [map])

  return null
}

import L from 'leaflet'
import { useEffect, useRef, useState } from 'react'
import { Marker } from 'react-leaflet'

import type { AircraftTrack } from '@/store/copStore'
import { useMapStore } from '@/store/mapStore'

const STATUS_COLOR: Record<string, string> = {
  READY: 'var(--ok)',
  TASKED: 'var(--accent)',
  AIRBORNE: 'var(--accent)',
  TURNAROUND: 'var(--warn)',
  MAINTENANCE: 'var(--warn)',
  UNSERVICEABLE: 'var(--crit)',
}

function lerp(a: number, b: number, t: number): number {
  return a + (b - a) * t
}

function lerpAngle(a: number, b: number, t: number): number {
  let diff = ((b - a + 180) % 360) - 180
  if (diff < -180) diff += 360
  return a + diff * t
}

/** Tweens between the previous and current WS position over the interval between them,
 * instead of snapping on every 1 Hz update (§13.4: "smooth interpolation"). */
function useInterpolated(track: AircraftTrack) {
  const [state, setState] = useState(() => ({
    lat: track.curr.lat,
    lon: track.curr.lon,
    hdg: track.curr.hdg,
  }))
  const frameRef = useRef<number>()

  useEffect(() => {
    const span = Math.max(1, track.currTs - track.prevTs)
    const tick = () => {
      const elapsed = performance.now() - track.currTs
      const t = Math.min(1, Math.max(0, elapsed / span))
      setState({
        lat: lerp(track.prev.lat, track.curr.lat, t),
        lon: lerp(track.prev.lon, track.curr.lon, t),
        hdg: lerpAngle(track.prev.hdg, track.curr.hdg, t),
      })
      if (t < 1) frameRef.current = requestAnimationFrame(tick)
    }
    frameRef.current = requestAnimationFrame(tick)
    return () => {
      if (frameRef.current) cancelAnimationFrame(frameRef.current)
    }
  }, [track])

  return state
}

function aircraftIcon(
  callsign: string,
  status: string,
  heading: number,
  risky: boolean,
  showLabel: boolean,
): L.DivIcon {
  const color = STATUS_COLOR[status] ?? 'var(--text-muted)'
  return L.divIcon({
    className: '',
    html: `
      <div style="display:flex;flex-direction:column;align-items:center;gap:2px;transform:translate(-50%,-50%)">
        <div style="position:relative;width:20px;height:20px;transform:rotate(${heading}deg)">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="${color}">
            <path d="M12 2 L15 10 L22 14 L15 15 L15 20 L18 22 L12 20.5 L6 22 L9 20 L9 15 L2 14 L9 10 Z" />
          </svg>
          ${
            risky
              ? '<div style="position:absolute;top:-2px;right:-2px;width:7px;height:7px;border-radius:50%;background:var(--warn);border:1px solid var(--panel)"></div>'
              : ''
          }
        </div>
        ${
          showLabel
            ? `<span class="mono-text" style="font-size:9px;background:var(--panel);border:1px solid var(--border);border-radius:3px;padding:0 3px;color:var(--text);white-space:nowrap">${callsign}</span>`
            : ''
        }
      </div>
    `,
    iconSize: [0, 0],
  })
}

interface AircraftMarkerProps {
  id: string
  callsign: string
  status: string
  pUnserviceable24h: number
  track: AircraftTrack
}

function AircraftMarker({ id, callsign, status, pUnserviceable24h, track }: AircraftMarkerProps) {
  const { lat, lon, hdg } = useInterpolated(track)
  const showLabels = useMapStore((s) => s.layers.labels)
  const select = useMapStore((s) => s.select)

  const icon = aircraftIcon(callsign, status, hdg, pUnserviceable24h > 0.4, showLabels)

  return (
    <Marker
      position={[lat, lon]}
      icon={icon}
      eventHandlers={{ click: () => select({ kind: 'aircraft', id }) }}
    />
  )
}

interface AircraftLayerProps {
  aircraft: {
    id: string
    callsign: string
    status: string
    pUnserviceable24H: number
    lat: number
    lon: number
    headingDeg: number
  }[]
  tracks: Record<string, AircraftTrack>
}

export default function AircraftLayer({ aircraft, tracks }: AircraftLayerProps) {
  return (
    <>
      {aircraft.map((a) => {
        // Falls back to the REST snapshot's own position until the first WS tick
        // arrives for this aircraft, so markers don't disappear on first paint.
        const fallback = { id: a.id, lat: a.lat, lon: a.lon, hdg: a.headingDeg, alt: 0, spd: 0, fuel: 0 }
        const track = tracks[a.id] ?? {
          prev: fallback,
          curr: fallback,
          prevTs: performance.now(),
          currTs: performance.now(),
        }
        return (
          <AircraftMarker
            key={a.id}
            id={a.id}
            callsign={a.callsign}
            status={a.status}
            pUnserviceable24h={a.pUnserviceable24H}
            track={track}
          />
        )
      })}
    </>
  )
}

export default function CompassRose() {
  return (
    <div
      className="panel pointer-events-none absolute left-3 top-3 z-[500] flex h-12 w-12 items-center justify-center"
      aria-hidden
    >
      <svg viewBox="0 0 48 48" className="h-9 w-9 text-text-muted">
        <circle cx="24" cy="24" r="20" fill="none" stroke="currentColor" strokeWidth="1" />
        <path d="M24 6 L28 22 L24 19 L20 22 Z" fill="var(--crit)" />
        <path d="M24 42 L20 26 L24 29 L28 26 Z" fill="currentColor" />
        <text x="24" y="7" textAnchor="middle" fontSize="7" fill="currentColor" className="label-text">
          N
        </text>
      </svg>
    </div>
  )
}

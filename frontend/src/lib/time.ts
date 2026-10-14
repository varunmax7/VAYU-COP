/** Every time in the UI is shown in Zulu (UTC); hovering shows IST (§13.6). */

export function formatZulu(date: Date): string {
  const hh = String(date.getUTCHours()).padStart(2, '0')
  const mm = String(date.getUTCMinutes()).padStart(2, '0')
  const ss = String(date.getUTCSeconds()).padStart(2, '0')
  return `${hh}:${mm}:${ss}Z`
}

export function formatZuluHM(date: Date): string {
  const hh = String(date.getUTCHours()).padStart(2, '0')
  const mm = String(date.getUTCMinutes()).padStart(2, '0')
  return `${hh}:${mm}Z`
}

const IST_OFFSET_MIN = 5 * 60 + 30

export function formatIST(date: Date): string {
  const ist = new Date(date.getTime() + IST_OFFSET_MIN * 60_000)
  const hh = String(ist.getUTCHours()).padStart(2, '0')
  const mm = String(ist.getUTCMinutes()).padStart(2, '0')
  return `${hh}:${mm} IST`
}

/** AUTO theme picks DAY between 06:00 and 18:00 local time (§13.3). */
export function isDaytimeLocal(date: Date = new Date()): boolean {
  const hour = date.getHours()
  return hour >= 6 && hour < 18
}

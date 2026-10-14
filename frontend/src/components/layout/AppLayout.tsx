import { Outlet } from 'react-router-dom'

import { useMobileRedirect } from '@/lib/useMobileRedirect'

import ExerciseBanner from './ExerciseBanner'
import KpiStrip from './KpiStrip'
import SideNav from './SideNav'
import TopBar from './TopBar'

/** The reference-image frame (§13.2): banner, top bar, KPI strip, side nav, map area,
 * AI panel and Gantt strip. The map (Phase 5) is live; the AI panel and Gantt (Phase 8)
 * are still placeholders here. */
export default function AppLayout() {
  useMobileRedirect()

  return (
    <div className="flex h-screen flex-col overflow-hidden bg-bg text-text">
      <ExerciseBanner />
      <div className="flex flex-1 overflow-hidden">
        <SideNav />
        <div className="flex flex-1 flex-col overflow-hidden">
          <TopBar />
          <KpiStrip />
          <div className="flex flex-1 overflow-hidden">
            <main className="relative flex-1 overflow-hidden bg-map-bg">
              <Outlet />
            </main>
            <aside className="hidden w-[360px] shrink-0 overflow-y-auto border-l border-border bg-panel p-3 xl:block">
              <h2 className="label-text text-xs text-text-muted">
                AI DYNAMIC ALLOCATION ENGINE &amp; RETASKING
              </h2>
              <p className="mt-2 text-xs text-text-muted">
                Built in Phase 7 (optimiser) &amp; Phase 8 (plan panel, approval flow).
              </p>
            </aside>
          </div>
          <div className="h-[220px] shrink-0 border-t border-border bg-panel p-3">
            <h2 className="label-text text-xs text-text-muted">MISSION GANTT / RESOURCE TIMELINE</h2>
            <p className="mt-2 text-xs text-text-muted">Built in Phase 8.</p>
          </div>
        </div>
      </div>
    </div>
  )
}

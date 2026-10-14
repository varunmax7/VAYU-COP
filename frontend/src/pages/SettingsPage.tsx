import ThemeToggle from '@/components/layout/ThemeToggle'
import { useAuth } from '@/lib/auth'

export default function SettingsPage() {
  const { user } = useAuth()

  return (
    <div className="flex h-full flex-col gap-6 overflow-auto p-6">
      <h1 className="label-text text-lg">Settings</h1>

      <section className="panel max-w-md p-4">
        <h2 className="label-text text-xs text-text-muted">Theme</h2>
        <div className="mt-2">
          <ThemeToggle />
        </div>
      </section>

      <section className="panel max-w-md p-4">
        <h2 className="label-text text-xs text-text-muted">Signed in as</h2>
        <p className="mono-text mt-2 text-sm">
          {user?.displayName} <span className="text-text-muted">· {user?.role}</span>
        </p>
      </section>

      <section className="panel max-w-md p-4 text-text-muted">
        <h2 className="label-text text-xs">Planner weights, duty limits, alert thresholds</h2>
        <p className="mt-2 text-xs">Built in Phase 7 (optimiser) and Phase 10 (alerts).</p>
      </section>

      <section className="panel max-w-md p-4 text-text-muted">
        <h2 className="label-text text-xs">Data sources (fusion health)</h2>
        <p className="mt-2 text-xs">
          Live per-source health is already served by{' '}
          <code className="mono-text">GET /api/v1/fusion/sources</code> (Phase 3) — the toggle UI
          here is built in Phase 6.
        </p>
      </section>

      <section className="panel max-w-md p-4 text-text-muted">
        <h2 className="label-text text-xs">LLM provider status, user list</h2>
        <p className="mt-2 text-xs">Built in Phase 14.</p>
      </section>
    </div>
  )
}

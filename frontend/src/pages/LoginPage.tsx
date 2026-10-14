import { ShieldAlert } from 'lucide-react'
import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { toast } from 'sonner'

import { ApiError } from '@/lib/api'
import { useAuth } from '@/lib/auth'

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const from = (location.state as { from?: Location })?.from?.pathname ?? '/'

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setIsSubmitting(true)
    try {
      await login(username, password)
      navigate(from, { replace: true })
    } catch (err) {
      const message = err instanceof ApiError ? err.message : 'Login failed'
      toast.error(message)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div
      data-theme="dark"
      className="flex min-h-screen items-center justify-center bg-bg px-4 text-text"
    >
      <div className="panel w-full max-w-sm p-6">
        <div className="mb-6 flex flex-col items-center gap-2 text-center">
          <ShieldAlert className="h-8 w-8 text-accent" aria-hidden />
          <h1 className="label-text text-lg">VAYU-COP</h1>
          <p className="text-xs text-text-muted">
            AI Decision Support for Dynamic Air Operations &amp; Resource Optimisation
          </p>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-3">
          <label className="flex flex-col gap-1">
            <span className="label-text text-xs text-text-muted">Username</span>
            <input
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoComplete="username"
              autoFocus
              required
              className="mono-text rounded border border-border bg-panel-2 px-3 py-2 text-sm text-text outline-none focus:ring-2 focus:ring-accent"
            />
          </label>

          <label className="flex flex-col gap-1">
            <span className="label-text text-xs text-text-muted">Password</span>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
              required
              className="mono-text rounded border border-border bg-panel-2 px-3 py-2 text-sm text-text outline-none focus:ring-2 focus:ring-accent"
            />
          </label>

          <button
            type="submit"
            disabled={isSubmitting}
            className="label-text mt-2 rounded bg-accent px-3 py-2 text-sm text-white transition-opacity disabled:opacity-60"
          >
            {isSubmitting ? 'SIGNING IN…' : 'SIGN IN'}
          </button>
        </form>

        <p className="mt-4 text-center text-xs text-text-muted">
          Exercise VAYU SHIELD · synthetic data only
        </p>
      </div>
    </div>
  )
}

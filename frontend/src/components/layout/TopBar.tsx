import { LogOut, Menu, Settings } from 'lucide-react'
import { Link } from 'react-router-dom'

import { useAuth } from '@/lib/auth'
import { useUiStore } from '@/store/uiStore'

import ConnectionDot from './ConnectionDot'
import ThemeToggle from './ThemeToggle'

export default function TopBar() {
  const { user, logout } = useAuth()
  const toggleSidebar = useUiStore((s) => s.toggleSidebar)

  return (
    <header className="flex h-14 shrink-0 items-center gap-3 border-b border-border bg-panel px-3">
      <button
        type="button"
        onClick={toggleSidebar}
        aria-label="Toggle navigation"
        className="rounded p-1.5 text-text-muted hover:bg-panel-2 hover:text-text"
      >
        <Menu className="h-5 w-5" aria-hidden />
      </button>

      <h1 className="label-text whitespace-nowrap text-sm tracking-wide">
        COMMON OPERATING PICTURE (COP) <span className="text-text-muted">|</span> AI MISSION PLANNER
      </h1>

      <div className="ml-auto flex items-center gap-3">
        <ThemeToggle />

        <Link
          to="/settings"
          aria-label="Settings"
          className="rounded p-1.5 text-text-muted hover:bg-panel-2 hover:text-text"
        >
          <Settings className="h-5 w-5" aria-hidden />
        </Link>

        <div className="flex items-center gap-2 border-l border-border pl-3">
          <ConnectionDot />
          {user && (
            <span className="label-text text-xs text-text-muted">
              {user.displayName} <span className="text-text">· {user.role}</span>
            </span>
          )}
          <button
            type="button"
            onClick={logout}
            aria-label="Log out"
            className="rounded p-1.5 text-text-muted hover:bg-panel-2 hover:text-text"
          >
            <LogOut className="h-4 w-4" aria-hidden />
          </button>
        </div>
      </div>
    </header>
  )
}

import {
  Activity,
  AudioLines,
  Boxes,
  FileBarChart,
  ListTodo,
  Map,
  Settings,
} from 'lucide-react'
import { NavLink } from 'react-router-dom'

import { cn } from '@/lib/utils'
import { useUiStore } from '@/store/uiStore'

const ITEMS = [
  { to: '/', label: 'COP MAP', icon: Map, end: true },
  { to: '/resources', label: 'RESOURCE STATUS', icon: Boxes },
  { to: '/queue', label: 'AI QUEUE', icon: ListTodo },
  { to: '/analytics', label: 'PREDICTIVE ANALYTICS', icon: Activity },
  { to: '/simulation', label: 'SIMULATION', icon: AudioLines },
  { to: '/audit', label: 'AUDIT LOG', icon: FileBarChart },
  { to: '/reports', label: 'REPORTS', icon: FileBarChart },
]

export default function SideNav() {
  const collapsed = useUiStore((s) => s.sidebarCollapsed)

  return (
    <nav
      className={cn(
        'flex shrink-0 flex-col items-center border-r border-border bg-panel py-2 transition-[width]',
        collapsed ? 'w-14' : 'w-20',
      )}
    >
      <ul className="flex flex-1 flex-col items-center gap-1">
        {ITEMS.map(({ to, label, icon: Icon, end }) => (
          <li key={to} className="w-full">
            <NavLink
              to={to}
              end={end}
              title={label}
              className={({ isActive }) =>
                cn(
                  'flex w-full flex-col items-center gap-1 border-l-2 border-transparent px-1 py-2.5 text-[10px] transition-colors',
                  isActive
                    ? 'border-accent bg-panel-2 text-accent'
                    : 'text-text-muted hover:text-text',
                )
              }
            >
              <Icon className="h-5 w-5" aria-hidden />
              {!collapsed && <span className="label-text text-center leading-tight">{label}</span>}
            </NavLink>
          </li>
        ))}
      </ul>
      <NavLink
        to="/settings"
        title="SETTINGS"
        className={({ isActive }) =>
          cn(
            'flex w-full flex-col items-center gap-1 border-l-2 border-transparent px-1 py-2.5 text-[10px] transition-colors',
            isActive ? 'border-accent bg-panel-2 text-accent' : 'text-text-muted hover:text-text',
          )
        }
      >
        <Settings className="h-5 w-5" aria-hidden />
        {!collapsed && <span className="label-text">SETTINGS</span>}
      </NavLink>
    </nav>
  )
}

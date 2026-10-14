import { createBrowserRouter } from 'react-router-dom'

import RequireAuth from '@/components/RequireAuth'
import AppLayout from '@/components/layout/AppLayout'
import MobileShell from '@/mobile/MobileShell'
import AiQueuePage from '@/pages/AiQueuePage'
import AnalyticsPage from '@/pages/AnalyticsPage'
import AuditPage from '@/pages/AuditPage'
import CopPage from '@/pages/CopPage'
import LoginPage from '@/pages/LoginPage'
import ReportsPage from '@/pages/ReportsPage'
import ResourcesPage from '@/pages/ResourcesPage'
import SettingsPage from '@/pages/SettingsPage'
import SimulationPage from '@/pages/SimulationPage'

export const router = createBrowserRouter([
  { path: '/login', element: <LoginPage /> },
  { path: '/m', element: <MobileShell /> },
  {
    element: <RequireAuth />,
    children: [
      {
        element: <AppLayout />,
        children: [
          { index: true, element: <CopPage /> },
          { path: 'resources', element: <ResourcesPage /> },
          { path: 'queue', element: <AiQueuePage /> },
          { path: 'analytics', element: <AnalyticsPage /> },
          { path: 'simulation', element: <SimulationPage /> },
          { path: 'audit', element: <AuditPage /> },
          { path: 'reports', element: <ReportsPage /> },
          { path: 'settings', element: <SettingsPage /> },
        ],
      },
    ],
  },
])

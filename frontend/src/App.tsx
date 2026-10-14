import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'sonner'
import { RouterProvider } from 'react-router-dom'

import WsBridge from '@/components/WsBridge'
import { AuthProvider } from '@/lib/auth'
import { useThemeEffect } from '@/lib/theme'
import { router } from '@/routes'

const queryClient = new QueryClient({
  defaultOptions: { queries: { staleTime: 2000, retry: 1 } },
})

function ThemedApp() {
  useThemeEffect()
  return (
    <>
      <WsBridge />
      <RouterProvider router={router} />
      <Toaster richColors position="top-right" theme="dark" />
    </>
  )
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <ThemedApp />
      </AuthProvider>
    </QueryClientProvider>
  )
}

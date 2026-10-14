import { useQueryClient } from '@tanstack/react-query'
import { useEffect } from 'react'

import { useAuth } from '@/lib/auth'
import { connectWs, disconnectWs, WS_OPEN_EVENT } from '@/lib/ws'

/** Owns the WebSocket connection lifecycle: connects once authenticated, disconnects on
 * logout, and refetches REST snapshots after every (re)connect (§12.2). Renders nothing. */
export default function WsBridge() {
  const { token } = useAuth()
  const queryClient = useQueryClient()

  useEffect(() => {
    if (!token) {
      disconnectWs()
      return
    }
    connectWs()
    return () => disconnectWs()
  }, [token])

  useEffect(() => {
    const onOpen = () => {
      queryClient.invalidateQueries({ queryKey: ['kpis'] })
      queryClient.invalidateQueries({ queryKey: ['cop-snapshot'] })
    }
    window.addEventListener(WS_OPEN_EVENT, onOpen)
    return () => window.removeEventListener(WS_OPEN_EVENT, onOpen)
  }, [queryClient])

  return null
}

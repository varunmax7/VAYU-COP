import { useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

const MOBILE_BREAKPOINT_PX = 768

/** "< 768 px: redirect to the mobile field view (/m, Phase 15)" — §13.2. */
export function useMobileRedirect(): void {
  const navigate = useNavigate()
  const location = useLocation()

  useEffect(() => {
    const check = () => {
      if (window.innerWidth < MOBILE_BREAKPOINT_PX && !location.pathname.startsWith('/m')) {
        navigate('/m', { replace: true })
      }
    }
    check()
    window.addEventListener('resize', check)
    return () => window.removeEventListener('resize', check)
  }, [navigate, location.pathname])
}

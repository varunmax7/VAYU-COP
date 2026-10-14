import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from 'react'

import { api, getStoredToken, loginRequest, setStoredToken } from '@/lib/api'

export type UserRole = 'COMMANDER' | 'PLANNER' | 'MAINTENANCE' | 'MET' | 'INTEL' | 'AIRCREW' | 'ADMIN'

export interface AuthUser {
  id: string
  username: string
  displayName: string
  role: UserRole
}

interface AuthContextValue {
  user: AuthUser | null
  token: string | null
  isLoading: boolean
  login: (username: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => getStoredToken())
  const [user, setUser] = useState<AuthUser | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    if (!token) {
      setIsLoading(false)
      return
    }
    let cancelled = false
    api
      .get<AuthUser>('/auth/me')
      .then((me) => {
        if (!cancelled) setUser(me)
      })
      .catch(() => {
        if (!cancelled) {
          setStoredToken(null)
          setToken(null)
        }
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [token])

  const login = useCallback(async (username: string, password: string) => {
    const result = await loginRequest(username, password)
    setStoredToken(result.accessToken)
    setUser(result.user as AuthUser)
    setToken(result.accessToken)
  }, [])

  const logout = useCallback(() => {
    setStoredToken(null)
    setUser(null)
    setToken(null)
  }, [])

  return (
    <AuthContext.Provider value={{ user, token, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

// eslint-disable-next-line react-refresh/only-export-components -- context + hook belong together
export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within an AuthProvider')
  return ctx
}

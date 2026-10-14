const API_BASE = '/api/v1'
const TOKEN_KEY = 'vayu.token'

export function getStoredToken(): string | null {
  try {
    return localStorage.getItem(TOKEN_KEY)
  } catch {
    return null
  }
}

export function setStoredToken(token: string | null): void {
  try {
    if (token) localStorage.setItem(TOKEN_KEY, token)
    else localStorage.removeItem(TOKEN_KEY)
  } catch {
    // private browsing / storage disabled — the session just won't persist across reloads
  }
}

export class ApiError extends Error {
  status: number
  code: string
  details: unknown

  constructor(status: number, code: string, message: string, details?: unknown) {
    super(message)
    this.status = status
    this.code = code
    this.details = details
  }
}

interface RequestOptions {
  method?: string
  body?: unknown
  auth?: boolean
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', body, auth = true } = options
  const headers: Record<string, string> = {}
  if (body !== undefined) headers['Content-Type'] = 'application/json'
  if (auth) {
    const token = getStoredToken()
    if (token) headers.Authorization = `Bearer ${token}`
  }

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })

  if (!res.ok) {
    let code = 'ERROR'
    let message = res.statusText
    let details: unknown = null
    try {
      const data = await res.json()
      code = data?.error?.code ?? code
      message = data?.error?.message ?? message
      details = data?.error?.details ?? null
    } catch {
      // body wasn't JSON — fall back to statusText
    }
    throw new ApiError(res.status, code, message, details)
  }

  if (res.status === 204) return undefined as T
  return (await res.json()) as T
}

type Options = Omit<RequestOptions, 'method' | 'body'>

export const api = {
  get: <T>(path: string, options?: Options) => request<T>(path, { ...options, method: 'GET' }),
  post: <T>(path: string, body?: unknown, options?: Options) =>
    request<T>(path, { ...options, method: 'POST', body }),
  patch: <T>(path: string, body?: unknown, options?: Options) =>
    request<T>(path, { ...options, method: 'PATCH', body }),
  delete: <T>(path: string, options?: Options) =>
    request<T>(path, { ...options, method: 'DELETE' }),
}

export interface LoginResult {
  accessToken: string
  tokenType: string
  user: {
    id: string
    username: string
    displayName: string
    role: string
  }
}

export async function loginRequest(username: string, password: string): Promise<LoginResult> {
  const form = new URLSearchParams()
  form.set('username', username)
  form.set('password', password)

  const res = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: form.toString(),
  })

  if (!res.ok) {
    const data = await res.json().catch(() => null)
    throw new ApiError(
      res.status,
      data?.error?.code ?? 'UNAUTHORIZED',
      data?.error?.message ?? 'Login failed',
    )
  }
  return res.json() as Promise<LoginResult>
}

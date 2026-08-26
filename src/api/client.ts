const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export class ApiError extends Error {
  status: number
  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

/**
 * Thin fetch wrapper. Throws on network failure or non-2xx responses —
 * callers (the domain modules in src/api/*Api.ts) catch and fall back to
 * mock data, since there's no live backend to talk to yet.
 */
export async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`

  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  })

  if (!response.ok) {
    throw new ApiError(response.status, `API Error ${response.status}: ${response.statusText}`)
  }

  return await response.json()
}

/** Lightweight connectivity check used by TopNav's Live/Offline badge. */
export async function pingApi(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`, { method: 'GET' })
    return response.ok
  } catch {
    return false
  }
}

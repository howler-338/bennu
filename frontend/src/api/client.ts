import { useAuthStore } from '../store/auth'

export async function apiFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = useAuthStore.getState().token
  const headers: Record<string, string> = { ...(init.headers as Record<string, string>) }
  if (token) headers['Authorization'] = `Bearer ${token}`
  if (!(init.body instanceof FormData)) headers['Content-Type'] = 'application/json'

  const res = await fetch(`/api${path}`, { ...init, headers })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.message || `HTTP ${res.status}`)
  }
  return res.json()
}

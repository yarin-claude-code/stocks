import { useEffect, useState, useCallback } from 'react'
import { supabase } from '../lib/supabase'

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

async function getAuthHeader(): Promise<Record<string, string>> {
  const { data: { session } } = await supabase.auth.getSession()
  if (!session) return {}
  return { Authorization: `Bearer ${session.access_token}` }
}

export function usePreferences() {
  const [savedDomains, setSavedDomains] = useState<string[] | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    getAuthHeader().then(async headers => {
      if (!headers.Authorization) { setLoading(false); return }
      try {
        const res = await fetch(`${API_BASE}/api/preferences`, { headers })
        if (!res.ok) throw new Error('fetch failed')
        const data = await res.json()
        if (!cancelled) setSavedDomains(data.domains ?? [])
      } catch {
        if (!cancelled) setSavedDomains([])
      } finally {
        if (!cancelled) setLoading(false)
      }
    })
    return () => { cancelled = true }
  }, [])

  const saveDomains = useCallback(async (domains: string[]) => {
    const headers = await getAuthHeader()
    if (!headers.Authorization) return
    await fetch(`${API_BASE}/api/preferences`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', ...headers },
      body: JSON.stringify({ domains }),
    })
    setSavedDomains(domains)
  }, [])

  return { savedDomains, loading, saveDomains }
}

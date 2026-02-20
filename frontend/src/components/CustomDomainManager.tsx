import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { supabase } from '../lib/supabase'

async function getAuthHeader(): Promise<Record<string, string>> {
  const { data: { session } } = await supabase.auth.getSession()
  if (!session) return {}
  return { Authorization: `Bearer ${session.access_token}` }
}

function parseTickers(raw: string): string[] {
  return raw
    .split(/[,\n]/)
    .map(t => t.trim().toUpperCase())
    .filter(t => t.length > 0)
}

interface CustomDomain {
  id: number
  name: string
  tickers: string[]
}

export function CustomDomainManager() {
  const queryClient = useQueryClient()

  const [newName, setNewName] = useState('')
  const [newTickers, setNewTickers] = useState('')
  const [editingId, setEditingId] = useState<number | null>(null)
  const [editTickers, setEditTickers] = useState('')
  const [error, setError] = useState<string | null>(null)

  const { data: domains = [], isLoading } = useQuery<CustomDomain[]>({
    queryKey: ['custom-domains'],
    queryFn: async () => {
      const headers = await getAuthHeader()
      const res = await fetch('/api/domains/custom', { headers })
      if (!res.ok) throw new Error('Failed to fetch custom domains')
      return res.json()
    },
  })

  const createMutation = useMutation({
    mutationFn: async ({ name, tickers }: { name: string; tickers: string[] }) => {
      const headers = await getAuthHeader()
      const res = await fetch('/api/domains/custom', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...headers },
        body: JSON.stringify({ name, tickers }),
      })
      if (!res.ok) {
        const body = await res.json().catch(() => ({}))
        if (res.status === 422 && body.detail) {
          throw new Error(
            typeof body.detail === 'string'
              ? body.detail
              : `Invalid tickers: ${JSON.stringify(body.detail)}`
          )
        }
        throw new Error('Failed to create domain')
      }
      return res.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['custom-domains'] })
      setNewName('')
      setNewTickers('')
      setError(null)
    },
    onError: (err: Error) => {
      setError(err.message)
    },
  })

  const updateMutation = useMutation({
    mutationFn: async ({ id, tickers }: { id: number; tickers: string[] }) => {
      const headers = await getAuthHeader()
      const res = await fetch(`/api/domains/custom/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', ...headers },
        body: JSON.stringify({ tickers }),
      })
      if (!res.ok) {
        const body = await res.json().catch(() => ({}))
        if (res.status === 422 && body.detail) {
          throw new Error(
            typeof body.detail === 'string'
              ? body.detail
              : `Invalid tickers: ${JSON.stringify(body.detail)}`
          )
        }
        throw new Error('Failed to update domain')
      }
      return res.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['custom-domains'] })
      setEditingId(null)
      setEditTickers('')
      setError(null)
    },
    onError: (err: Error) => {
      setError(err.message)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: async (id: number) => {
      const headers = await getAuthHeader()
      const res = await fetch(`/api/domains/custom/${id}`, {
        method: 'DELETE',
        headers,
      })
      if (!res.ok) throw new Error('Failed to delete domain')
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['custom-domains'] })
    },
  })

  const handleCreate = () => {
    setError(null)
    const tickers = parseTickers(newTickers)
    if (!newName.trim()) { setError('Domain name is required'); return }
    if (tickers.length === 0) { setError('At least one ticker is required'); return }
    createMutation.mutate({ name: newName.trim(), tickers })
  }

  const handleSave = (id: number) => {
    setError(null)
    const tickers = parseTickers(editTickers)
    if (tickers.length === 0) { setError('At least one ticker is required'); return }
    updateMutation.mutate({ id, tickers })
  }

  return (
    <div className="max-w-2xl">
      <h2 className="text-xl font-bold text-white mb-6">My Custom Domains</h2>

      {/* Create form */}
      <div className="bg-slate-800/60 border border-slate-700 rounded-xl p-4 mb-6">
        <h3 className="text-sm font-semibold text-slate-300 mb-3">Create New Domain</h3>
        <input
          type="text"
          placeholder="Domain name (e.g. My Tech Picks)"
          value={newName}
          onChange={e => setNewName(e.target.value)}
          className="w-full bg-slate-900 border border-slate-600 rounded-lg px-3 py-2 text-white text-sm placeholder-slate-500 mb-2 focus:outline-none focus:border-indigo-500"
        />
        <textarea
          placeholder="Tickers, comma-separated or one per line (e.g. AAPL, MSFT, GOOGL)"
          value={newTickers}
          onChange={e => setNewTickers(e.target.value)}
          rows={3}
          className="w-full bg-slate-900 border border-slate-600 rounded-lg px-3 py-2 text-white text-sm placeholder-slate-500 mb-2 focus:outline-none focus:border-indigo-500 resize-none"
        />
        {error && <p className="text-red-400 text-sm mb-2">{error}</p>}
        <button
          onClick={handleCreate}
          disabled={createMutation.isPending}
          className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-sm font-medium px-4 py-2 rounded-lg"
        >
          {createMutation.isPending ? 'Creating...' : 'Create'}
        </button>
      </div>

      {/* Domains list */}
      {isLoading ? (
        <p className="text-slate-500 text-sm">Loading...</p>
      ) : domains.length === 0 ? (
        <p className="text-slate-500 text-sm">No custom domains yet.</p>
      ) : (
        <div className="space-y-3">
          {domains.map(domain => (
            <div key={domain.id} className="bg-slate-800/60 border border-slate-700 rounded-xl p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="font-semibold text-white">{domain.name}</span>
                <div className="flex gap-2">
                  <button
                    onClick={() => {
                      setEditingId(domain.id)
                      setEditTickers(domain.tickers.join(', '))
                      setError(null)
                    }}
                    className="text-xs text-indigo-400 hover:text-indigo-300 px-2 py-1 border border-indigo-500/30 rounded"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => deleteMutation.mutate(domain.id)}
                    disabled={deleteMutation.isPending}
                    className="text-xs text-red-400 hover:text-red-300 px-2 py-1 border border-red-500/30 rounded disabled:opacity-50"
                  >
                    Delete
                  </button>
                </div>
              </div>

              {/* Ticker chips */}
              <div className="flex flex-wrap gap-1 mb-2">
                {domain.tickers.map(ticker => (
                  <span key={ticker} className="text-xs bg-slate-700 text-slate-300 px-2 py-0.5 rounded">
                    {ticker}
                  </span>
                ))}
              </div>

              {/* Inline edit */}
              {editingId === domain.id && (
                <div className="mt-3 pt-3 border-t border-slate-700">
                  <textarea
                    value={editTickers}
                    onChange={e => setEditTickers(e.target.value)}
                    rows={3}
                    className="w-full bg-slate-900 border border-slate-600 rounded-lg px-3 py-2 text-white text-sm placeholder-slate-500 mb-2 focus:outline-none focus:border-indigo-500 resize-none"
                  />
                  {error && editingId === domain.id && (
                    <p className="text-red-400 text-sm mb-2">{error}</p>
                  )}
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleSave(domain.id)}
                      disabled={updateMutation.isPending}
                      className="text-xs bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white px-3 py-1 rounded"
                    >
                      {updateMutation.isPending ? 'Saving...' : 'Save'}
                    </button>
                    <button
                      onClick={() => { setEditingId(null); setError(null) }}
                      className="text-xs bg-slate-700 hover:bg-slate-600 text-slate-300 px-3 py-1 rounded"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

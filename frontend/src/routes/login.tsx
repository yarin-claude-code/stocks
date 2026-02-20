import { useState } from 'react'
import { createFileRoute, redirect, useNavigate } from '@tanstack/react-router'
import { supabase } from '../lib/supabase'

export const Route = createFileRoute('/login')({
  beforeLoad: async () => {
    const { data: { session } } = await supabase.auth.getSession()
    if (session) throw redirect({ to: '/_authenticated/dashboard' })
  },
  component: LoginPage,
})

function LoginPage() {
  const navigate = useNavigate()
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [displayName, setDisplayName] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      if (mode === 'register') {
        const { error } = await supabase.auth.signUp({
          email,
          password,
          options: { data: { display_name: displayName } },
        })
        if (error) throw error
      } else {
        const { error } = await supabase.auth.signInWithPassword({ email, password })
        if (error) throw error
      }
      navigate({ to: '/_authenticated/dashboard' })
    } catch (err: any) {
      setError(err.message ?? 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center">
      <div className="w-full max-w-sm bg-slate-900 border border-slate-800 rounded-xl p-8">
        <h1 className="text-xl font-bold text-white mb-6">Smart Stock Ranker</h1>
        <div className="flex gap-2 mb-6">
          <button
            className={`flex-1 py-1.5 rounded text-sm font-medium transition-colors ${mode === 'login' ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-slate-400'}`}
            onClick={() => setMode('login')}
          >Login</button>
          <button
            className={`flex-1 py-1.5 rounded text-sm font-medium transition-colors ${mode === 'register' ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-slate-400'}`}
            onClick={() => setMode('register')}
          >Register</button>
        </div>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          {mode === 'register' && (
            <div>
              <input
                className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-white text-sm placeholder:text-slate-500"
                placeholder="Display name"
                value={displayName}
                onChange={e => setDisplayName(e.target.value)}
                required
              />
            </div>
          )}
          <input
            className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-white text-sm placeholder:text-slate-500"
            type="email"
            placeholder="Email"
            value={email}
            onChange={e => setEmail(e.target.value)}
            required
          />
          <div>
            <input
              className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-white text-sm placeholder:text-slate-500"
              type="password"
              placeholder="Password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
            />
            {error && <p className="text-red-400 text-xs mt-1">{error}</p>}
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-medium py-2 rounded text-sm transition-colors"
          >
            {loading ? 'Loading...' : mode === 'login' ? 'Sign in' : 'Create account'}
          </button>
        </form>
      </div>
    </div>
  )
}

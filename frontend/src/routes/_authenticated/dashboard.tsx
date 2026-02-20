import { useState, useEffect, useRef } from 'react'
import { createFileRoute, Link } from '@tanstack/react-router'
import { useQuery } from '@tanstack/react-query'
import { fetchRankings } from '../../api/client'
import { isMarketOpen } from '../../hooks/useMarketOpen'
import { Skeleton } from '../../components/Skeleton'
import { BestOverall } from '../../components/BestOverall'
import { DomainSelector } from '../../components/DomainSelector'
import { StockCard } from '../../components/StockCard'
import { ScoreBreakdown } from '../../components/ScoreBreakdown'
import { supabase } from '../../lib/supabase'
import { usePreferences } from '../../hooks/usePreferences'

export const Route = createFileRoute('/_authenticated/dashboard')({
  component: Dashboard,
})

function Dashboard() {
  const { data, isLoading } = useQuery({
    queryKey: ['rankings'],
    queryFn: fetchRankings,
    refetchInterval: 300_000,
    refetchIntervalInBackground: false,
  })

  const [activeDomain, setActiveDomain] = useState<string | null>(null)
  const [selectedStock, setSelectedStock] = useState<any>(null)
  const [session, setSession] = useState<any>(null)
  const [menuOpen, setMenuOpen] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)
  const { savedDomains, loading: prefLoading, saveDomains } = usePreferences()

  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => setSession(data.session))
  }, [])

  useEffect(() => {
    if (!menuOpen) return
    const handler = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setMenuOpen(false)
      }
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [menuOpen])

  useEffect(() => {
    if (!prefLoading && savedDomains !== null && savedDomains.length === 0 && currentDomain) {
      saveDomains([currentDomain])
    }
  }, [prefLoading, savedDomains])

  const displayName = session?.user?.user_metadata?.display_name ?? session?.user?.email ?? ''

  const domains: any[] = data?.domains ?? []
  const domainNames = domains.map((d: any) => d.domain)
  const currentDomain = (() => {
    if (activeDomain) return activeDomain
    if (savedDomains && savedDomains.length > 0) {
      const match = domainNames.find(d => d === savedDomains[0])
      return match ?? domainNames[0] ?? null
    }
    return domainNames[0] ?? null
  })()
  const currentStocks = domains.find((d: any) => d.domain === currentDomain)?.top5 ?? []

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <div className="max-w-5xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-white tracking-tight">Smart Stock Ranker</h1>
            {data?.best_overall && (
              <p className="text-sm font-semibold text-indigo-400 mt-1">
                Algorithm Chose: <span className="text-white">{data.best_overall.ticker}</span> To Invest
              </p>
            )}
            {!data?.best_overall && !isLoading && (
              <p className="text-xs text-slate-500 mt-0.5">Quantitative ranking · refreshes every 5 min</p>
            )}
          </div>
          <div className="flex items-center gap-3">
            {isMarketOpen() ? (
              <span className="flex items-center gap-1.5 text-xs font-medium text-green-400 bg-green-500/10 border border-green-500/20 px-3 py-1 rounded-full">
                <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
                Market Open
              </span>
            ) : (
              <span className="text-xs font-medium bg-slate-800 text-slate-400 border border-slate-700 px-3 py-1 rounded-full">
                Market Closed
              </span>
            )}
            <div className="relative" ref={menuRef}>
              <button
                className="text-xs bg-slate-800 border border-slate-700 text-slate-300 px-3 py-1 rounded-full"
                onClick={() => setMenuOpen(o => !o)}
              >
                {displayName}
              </button>
              {menuOpen && (
                <div className="absolute right-0 mt-1 bg-slate-900 border border-slate-800 rounded shadow-lg z-10">
                  <button
                    className="block w-full text-left px-4 py-2 text-sm text-slate-300 hover:text-white hover:bg-slate-800"
                    onClick={async () => {
                      await supabase.auth.signOut()
                      window.location.href = '/login'
                    }}
                  >
                    Logout
                  </button>
                  <Link
                    to="/domains/custom"
                    className="block w-full text-left px-4 py-2 text-sm text-slate-300 hover:text-white hover:bg-slate-800"
                  >
                    My Domains
                  </Link>
                </div>
              )}
            </div>
          </div>
        </div>

        {isLoading ? (
          <>
            <Skeleton className="h-24 w-full mb-6" />
            <div className="flex gap-2 mb-6">{[...Array(5)].map((_, i) => <Skeleton key={i} className="h-9 w-24" />)}</div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {[...Array(5)].map((_, i) => <Skeleton key={i} className="h-48" />)}
            </div>
          </>
        ) : (
          <>
            {data?.best_overall && <BestOverall stock={data.best_overall} />}
            <DomainSelector domains={domainNames} active={currentDomain ?? ''} onSelect={(domain) => {
                setActiveDomain(domain)
                saveDomains([domain])
              }} />
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {currentStocks.map((stock: any) => (
                <StockCard key={stock.ticker} stock={stock} onClick={() => setSelectedStock(stock)} />
              ))}
            </div>
          </>
        )}
      </div>

      {selectedStock && (
        <ScoreBreakdown stock={selectedStock} onClose={() => setSelectedStock(null)} />
      )}
    </div>
  )
}

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { fetchRankings } from './api/client'
import { isMarketOpen } from './hooks/useMarketOpen'
import { Skeleton } from './components/Skeleton'
import { BestOverall } from './components/BestOverall'
import { DomainSelector } from './components/DomainSelector'
import { StockCard } from './components/StockCard'
import { ScoreBreakdown } from './components/ScoreBreakdown'

export default function App() {
  const { data, isLoading } = useQuery({
    queryKey: ['rankings'],
    queryFn: fetchRankings,
    refetchInterval: 300_000,
    refetchIntervalInBackground: false,
  })

  const [activeDomain, setActiveDomain] = useState<string | null>(null)
  const [selectedStock, setSelectedStock] = useState<any>(null)

  const domains: any[] = data?.domains ?? []
  const currentDomain = activeDomain ?? domains[0]?.domain ?? null
  const domainNames = domains.map((d: any) => d.domain)
  const currentStocks = domains.find((d: any) => d.domain === currentDomain)?.top5 ?? []

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <div className="max-w-5xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-white tracking-tight">Smart Stock Ranker</h1>
            <p className="text-xs text-slate-500 mt-0.5">Quantitative ranking · refreshes every 5 min</p>
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
            <DomainSelector domains={domainNames} active={currentDomain ?? ''} onSelect={setActiveDomain} />
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

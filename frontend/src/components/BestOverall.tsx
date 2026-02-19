interface StockRanking {
  ticker: string
  composite_score: number
  rank: number
  factors: {
    momentum: number | null
    volume_change: number | null
    volatility: number | null
    relative_strength: number | null
    financial_ratio: number | null
  }
}

export function BestOverall({ stock }: { stock: StockRanking }) {
  return (
    <div className="rounded-xl border border-yellow-300 bg-yellow-50 p-4 mb-6">
      <p className="text-xs font-semibold text-yellow-600 uppercase tracking-wide mb-1">Best Overall</p>
      <p className="text-xl font-bold">{stock.ticker}</p>
      <p className="text-sm text-gray-600">{stock.composite_score.toFixed(1)} / 100</p>
    </div>
  )
}

export type { StockRanking }

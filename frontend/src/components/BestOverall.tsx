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
  long_term_score: number | null
}

function ScoreRing({ score }: { score: number }) {
  const r = 28
  const circ = 2 * Math.PI * r
  const filled = (score / 100) * circ
  const color = score >= 70 ? '#22c55e' : score >= 45 ? '#f59e0b' : '#ef4444'
  return (
    <svg width="72" height="72" viewBox="0 0 72 72" className="shrink-0">
      <circle cx="36" cy="36" r={r} fill="none" stroke="#2a2d3e" strokeWidth="6" />
      <circle
        cx="36" cy="36" r={r} fill="none"
        stroke={color} strokeWidth="6"
        strokeDasharray={`${filled} ${circ - filled}`}
        strokeLinecap="round"
        transform="rotate(-90 36 36)"
      />
      <text x="36" y="41" textAnchor="middle" fontSize="13" fontWeight="700" fill={color}>{score.toFixed(0)}</text>
    </svg>
  )
}

export function BestOverall({ stock }: { stock: StockRanking }) {
  const momentum = stock.factors.momentum
  const momentumPct = momentum != null ? (momentum * 100).toFixed(2) : null

  return (
    <div className="rounded-2xl border border-indigo-500/30 bg-gradient-to-r from-indigo-950/60 to-indigo-900/30 p-5 mb-6 flex items-center gap-5">
      <ScoreRing score={stock.composite_score} />
      <div className="flex-1 min-w-0">
        <p className="text-xs font-semibold text-indigo-400 uppercase tracking-widest mb-1">Top Ranked</p>
        <p className="text-3xl font-bold text-white">{stock.ticker}</p>
        <p className="text-sm text-slate-400 mt-0.5">Composite score {stock.composite_score.toFixed(1)} / 100</p>
      </div>
      {momentumPct != null && (
        <div className="text-right shrink-0">
          <p className="text-xs text-slate-500 uppercase tracking-wide mb-1">5d momentum</p>
          <p className={`text-2xl font-bold ${parseFloat(momentumPct) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {parseFloat(momentumPct) >= 0 ? '+' : ''}{momentumPct}%
          </p>
        </div>
      )}
    </div>
  )
}

export type { StockRanking }

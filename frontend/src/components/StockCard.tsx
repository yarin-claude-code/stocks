import { Link } from '@tanstack/react-router'
import type { StockRanking } from './BestOverall'

function gradeColor(score: number) {
  if (score >= 75) return 'text-green-400'
  if (score >= 50) return 'text-amber-400'
  return 'text-red-400'
}

function gradeBg(score: number) {
  if (score >= 75) return 'bg-green-500/10 border-green-500/20'
  if (score >= 50) return 'bg-amber-500/10 border-amber-500/20'
  return 'bg-red-500/10 border-red-500/20'
}

function FactorBar({ label, value }: { label: string; value: number | null }) {
  if (value == null) return null
  // value is raw (pre-inversion, pre-normalization); clamp to [-3, 3] for display width
  const clamped = Math.max(-3, Math.min(3, value))
  const pct = ((clamped + 3) / 6) * 100
  const positive = value >= 0
  return (
    <div className="mb-1">
      <div className="flex justify-between text-xs text-slate-500 mb-0.5">
        <span>{label}</span>
        <span className={positive ? 'text-green-400' : 'text-red-400'}>{value.toFixed(3)}</span>
      </div>
      <div className="h-1 bg-slate-700 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all ${positive ? 'bg-green-500' : 'bg-red-500'}`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  )
}

export function StockCard({ stock, onClick }: { stock: StockRanking; onClick: () => void }) {
  const momentum = stock.factors.momentum
  const momentumPct = momentum != null ? (momentum * 100).toFixed(2) : null

  return (
    <button
      onClick={onClick}
      className={`text-left rounded-2xl border p-4 transition-all hover:scale-[1.02] hover:shadow-xl hover:shadow-black/30 w-full bg-slate-800/60 border-slate-700 hover:border-indigo-500/40`}
    >
      {/* Header */}
      <div className="flex justify-between items-start mb-3">
        <div>
          <span className="text-xs text-slate-500 font-medium">#{stock.rank}</span>
          <p className="text-xl font-bold text-white leading-tight">{stock.ticker}</p>
        </div>
        <div className="flex flex-col items-end gap-1">
          <div className={`px-2 py-0.5 rounded-lg border text-xs font-bold ${gradeBg(stock.composite_score)} ${gradeColor(stock.composite_score)}`}>
            {stock.composite_score.toFixed(1)}
          </div>
          {stock.long_term_score != null && (
            <div className={`px-2 py-0.5 rounded-lg border text-xs font-semibold ${gradeBg(stock.long_term_score)} ${gradeColor(stock.long_term_score)}`}>
              <span className="text-slate-400 font-normal">LT </span>{stock.long_term_score.toFixed(1)}
            </div>
          )}
        </div>
      </div>

      {/* Momentum badge */}
      {momentumPct != null && (
        <p className={`text-sm font-semibold mb-3 ${parseFloat(momentumPct) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
          {parseFloat(momentumPct) >= 0 ? '▲' : '▼'} {Math.abs(parseFloat(momentumPct))}% price change
        </p>
      )}

      {/* Factor bars */}
      <div className="space-y-1 mt-2">
        {stock.factors.momentum != null && <FactorBar label="Is the price going up?" value={stock.factors.momentum} />}
        {stock.factors.volume_change != null && <FactorBar label="Are people buying more?" value={stock.factors.volume_change} />}
        {stock.factors.relative_strength != null && <FactorBar label="Beating its sector?" value={stock.factors.relative_strength} />}
      </div>

      <div className="flex justify-between items-center mt-3">
        <Link
          to="/history/$ticker"
          params={{ ticker: stock.ticker }}
          onClick={(e) => e.stopPropagation()}
          className="text-xs text-indigo-400 hover:text-indigo-300"
        >
          View history →
        </Link>
        <p className="text-xs text-slate-600">Click for full breakdown →</p>
      </div>
    </button>
  )
}

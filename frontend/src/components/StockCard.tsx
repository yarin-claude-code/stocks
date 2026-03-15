import { Link } from '@tanstack/react-router'
import type { StockRanking } from './BestOverall'

function gradeLabel(score: number) {
  if (score >= 80) return { label: 'Strong Buy', color: 'text-green-400 bg-green-500/10 border-green-500/30' }
  if (score >= 60) return { label: 'Buy', color: 'text-green-300 bg-green-500/10 border-green-500/20' }
  if (score >= 40) return { label: 'Neutral', color: 'text-amber-400 bg-amber-500/10 border-amber-500/20' }
  if (score >= 20) return { label: 'Weak', color: 'text-orange-400 bg-orange-500/10 border-orange-500/20' }
  return { label: 'Avoid', color: 'text-red-400 bg-red-500/10 border-red-500/20' }
}

function SignalRow({ label, value }: { label: string; value: number | null }) {
  if (value == null) return null
  const clamped = Math.max(-3, Math.min(3, value))
  const pct = ((clamped + 3) / 6) * 100
  const positive = value >= 0
  return (
    <div className="mb-1.5">
      <div className="flex justify-between text-xs text-slate-400 mb-0.5">
        <span>{label}</span>
        <span className={positive ? 'text-green-400' : 'text-red-400'}>{positive ? '↑ Good' : '↓ Weak'}</span>
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
  const grade = gradeLabel(stock.composite_score)

  return (
    <button
      onClick={onClick}
      className="cursor-pointer text-left rounded-2xl border p-4 transition-all hover:scale-[1.02] hover:shadow-xl hover:shadow-black/30 w-full bg-slate-800/60 border-slate-700 hover:border-indigo-500/40"
    >
      {/* Header */}
      <div className="flex justify-between items-start mb-3">
        <div>
          <span className="text-xs text-slate-500 font-medium">#{stock.rank}</span>
          <p className="text-xl font-bold text-white leading-tight">{stock.ticker}</p>
        </div>
        <span className={`text-xs font-semibold px-2 py-0.5 rounded border ${grade.color}`}>{grade.label}</span>
      </div>

      {/* Price trend */}
      {momentumPct != null && (
        <p className={`text-sm font-semibold mb-3 ${parseFloat(momentumPct) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
          {parseFloat(momentumPct) >= 0 ? '▲ Up' : '▼ Down'} {Math.abs(parseFloat(momentumPct))}% this week
        </p>
      )}

      {/* Signals */}
      <div className="space-y-1 mt-2">
        {stock.factors.momentum != null && <SignalRow label="Price trending?" value={stock.factors.momentum} />}
        {stock.factors.volume_change != null && <SignalRow label="People buying more?" value={stock.factors.volume_change} />}
        {stock.factors.relative_strength != null && <SignalRow label="Beating its sector?" value={stock.factors.relative_strength} />}
      </div>

      <div className="flex justify-between items-center mt-3">
        <Link
          to="/history/$ticker"
          params={{ ticker: stock.ticker }}
          onClick={(e) => e.stopPropagation()}
          className="cursor-pointer text-xs text-indigo-400 hover:text-indigo-300"
        >
          Price history →
        </Link>
        <p className="text-xs text-slate-600">Tap for details →</p>
      </div>
    </button>
  )
}

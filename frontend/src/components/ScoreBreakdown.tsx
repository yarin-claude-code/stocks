import type { StockRanking } from './BestOverall'

const WEIGHTS: Record<string, number> = {
  momentum: 0.30,
  volume_change: 0.20,
  volatility: 0.20,
  relative_strength: 0.15,
  financial_ratio: 0.15,
}

const LABELS: Record<string, string> = {
  momentum: 'Momentum',
  volume_change: 'Volume Change',
  volatility: 'Volatility',
  relative_strength: 'Relative Strength',
  financial_ratio: 'Financial Ratio',
}

function gradeLabel(score: number) {
  if (score >= 80) return { label: 'Strong Buy', color: 'text-green-400 bg-green-500/10 border-green-500/30' }
  if (score >= 60) return { label: 'Buy', color: 'text-green-300 bg-green-500/10 border-green-500/20' }
  if (score >= 40) return { label: 'Neutral', color: 'text-amber-400 bg-amber-500/10 border-amber-500/20' }
  if (score >= 20) return { label: 'Weak', color: 'text-orange-400 bg-orange-500/10 border-orange-500/20' }
  return { label: 'Avoid', color: 'text-red-400 bg-red-500/10 border-red-500/20' }
}

function FactorRow({ name, value }: { name: string; value: number | null }) {
  const weight = WEIGHTS[name]
  const label = LABELS[name]
  const hasValue = value != null
  const clamped = hasValue ? Math.max(-3, Math.min(3, value!)) : 0
  const pct = ((clamped + 3) / 6) * 100
  const positive = hasValue && value! >= 0

  return (
    <div className="py-3 border-t border-slate-700/50">
      <div className="flex justify-between items-center mb-1.5">
        <div>
          <span className="text-sm text-slate-200 font-medium">{label}</span>
          <span className="text-xs text-slate-500 ml-2">{(weight * 100).toFixed(0)}% weight</span>
        </div>
        {hasValue ? (
          <span className={`text-sm font-mono font-semibold ${positive ? 'text-green-400' : 'text-red-400'}`}>
            {value!.toFixed(3)}
          </span>
        ) : (
          <span className="text-xs text-slate-600 italic">N/A</span>
        )}
      </div>
      <div className="h-1.5 bg-slate-700 rounded-full overflow-hidden">
        {hasValue && (
          <div
            className={`h-full rounded-full ${positive ? 'bg-green-500' : 'bg-red-500'}`}
            style={{ width: `${pct}%` }}
          />
        )}
      </div>
    </div>
  )
}

export function ScoreBreakdown({ stock, onClose }: { stock: StockRanking; onClose: () => void }) {
  const grade = gradeLabel(stock.composite_score)
  const r = 40
  const circ = 2 * Math.PI * r
  const filled = (stock.composite_score / 100) * circ
  const ringColor = stock.composite_score >= 70 ? '#22c55e' : stock.composite_score >= 45 ? '#f59e0b' : '#ef4444'

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div className="bg-slate-900 border border-slate-700 rounded-2xl p-6 max-w-sm w-full shadow-2xl" onClick={e => e.stopPropagation()}>
        {/* Header */}
        <div className="flex justify-between items-center mb-5">
          <div>
            <h2 className="text-2xl font-bold text-white">{stock.ticker}</h2>
            <span className={`text-xs font-semibold px-2 py-0.5 rounded border ${grade.color}`}>{grade.label}</span>
          </div>
          <button onClick={onClose} className="text-slate-500 hover:text-slate-200 text-xl transition-colors">✕</button>
        </div>

        {/* Score ring */}
        <div className="flex items-center justify-center gap-6 mb-5 py-2">
          <svg width="96" height="96" viewBox="0 0 96 96">
            <circle cx="48" cy="48" r={r} fill="none" stroke="#1e293b" strokeWidth="8" />
            <circle
              cx="48" cy="48" r={r} fill="none"
              stroke={ringColor} strokeWidth="8"
              strokeDasharray={`${filled} ${circ - filled}`}
              strokeLinecap="round"
              transform="rotate(-90 48 48)"
            />
            <text x="48" y="52" textAnchor="middle" fontSize="18" fontWeight="800" fill={ringColor}>
              {stock.composite_score.toFixed(0)}
            </text>
            <text x="48" y="66" textAnchor="middle" fontSize="10" fill="#64748b">/ 100</text>
          </svg>
          <div className="text-sm text-slate-400 space-y-1">
            <p>Rank <span className="text-white font-bold">#{stock.rank}</span></p>
            <p className="text-xs text-slate-500">Weighted composite<br />of 5 factors</p>
          </div>
        </div>

        {/* Factor breakdown */}
        <div>
          {Object.entries(stock.factors).map(([name, value]) => (
            <FactorRow key={name} name={name} value={value} />
          ))}
        </div>
      </div>
    </div>
  )
}

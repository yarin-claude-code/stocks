import type { StockRanking } from './BestOverall'

export function ScoreBreakdown({ stock, onClose }: { stock: StockRanking, onClose: () => void }) {
  const factors = [
    { label: 'Momentum', value: stock.factors.momentum },
    { label: 'Volume Change', value: stock.factors.volume_change },
    { label: 'Volatility', value: stock.factors.volatility },
    { label: 'Relative Strength', value: stock.factors.relative_strength },
    { label: 'Financial Ratio', value: stock.factors.financial_ratio },
  ]
  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div className="bg-white rounded-2xl p-6 max-w-sm w-full shadow-xl" onClick={e => e.stopPropagation()}>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">{stock.ticker}</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-xl">✕</button>
        </div>
        <p className="text-3xl font-bold text-blue-600 mb-4">{stock.composite_score.toFixed(1)}<span className="text-sm text-gray-400"> / 100</span></p>
        <table className="w-full text-sm">
          <tbody>
            {factors.map(f => (
              <tr key={f.label} className="border-t border-gray-100">
                <td className="py-2 text-gray-600">{f.label}</td>
                <td className="py-2 text-right font-medium">
                  {f.value != null ? f.value.toFixed(3) : <span className="text-gray-300">N/A</span>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

import type { StockRanking } from './BestOverall'

export function StockCard({ stock, onClick }: { stock: StockRanking, onClick: () => void }) {
  return (
    <button onClick={onClick} className="text-left rounded-xl border border-gray-200 bg-white p-4 shadow-sm hover:shadow-md transition-shadow w-full">
      <div className="flex justify-between items-start mb-2">
        <span className="text-xs text-gray-400">#{stock.rank}</span>
        <span className="text-xs font-semibold text-blue-600">{stock.composite_score.toFixed(1)}</span>
      </div>
      <p className="text-lg font-bold text-gray-900">{stock.ticker}</p>
    </button>
  )
}

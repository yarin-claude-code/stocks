import { useQuery } from '@tanstack/react-query'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { TrendBadge } from './TrendBadge'

interface HistoryPoint {
  snap_date: string
  composite_score: number
  rank: number
  trend_slope: number
}

export function ScoreHistoryChart({ ticker }: { ticker: string }) {
  const { data, isLoading } = useQuery<HistoryPoint[]>({
    queryKey: ['history', ticker],
    queryFn: async () => {
      const res = await fetch(`/api/history/${ticker}?days=30`)
      if (!res.ok) throw new Error('Failed to fetch history')
      return res.json()
    },
  })

  if (isLoading) return <p className="text-slate-400">Loading...</p>
  if (!data || data.length === 0) return <p className="text-slate-500">No history available yet.</p>

  return (
    <div>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis dataKey="snap_date" tick={{ fontSize: 11, fill: '#94a3b8' }} />
          <YAxis domain={[0, 100]} tick={{ fontSize: 11, fill: '#94a3b8' }} />
          <Tooltip
            contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: 8 }}
            labelStyle={{ color: '#94a3b8' }}
            itemStyle={{ color: '#e2e8f0' }}
          />
          <Line
            type="monotone"
            dataKey="composite_score"
            stroke="#6366f1"
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
      <div className="mt-3">
        <TrendBadge slope={data[data.length - 1].trend_slope} />
      </div>
    </div>
  )
}

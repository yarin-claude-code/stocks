import { createFileRoute, Link } from '@tanstack/react-router'
import { ScoreHistoryChart } from '../../components/ScoreHistoryChart'

export const Route = createFileRoute('/_authenticated/history/$ticker')({
  component: HistoryPage,
})

function HistoryPage() {
  const { ticker } = Route.useParams()

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <div className="max-w-3xl mx-auto px-4 py-8">
        <Link
          to="/dashboard"
          className="text-sm text-slate-400 hover:text-white mb-6 inline-block"
        >
          ← Back to Dashboard
        </Link>
        <h1 className="text-2xl font-bold text-white mb-6">{ticker} Score History</h1>
        <ScoreHistoryChart ticker={ticker} />
      </div>
    </div>
  )
}

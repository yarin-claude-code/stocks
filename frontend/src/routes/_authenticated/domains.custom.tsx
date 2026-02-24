import { createFileRoute, Link } from '@tanstack/react-router'
import { CustomDomainManager } from '../../components/CustomDomainManager'

export const Route = createFileRoute('/_authenticated/domains/custom')({
  component: CustomDomainsPage,
})

function CustomDomainsPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <div className="max-w-3xl mx-auto px-4 py-8">
        <Link
          to="/dashboard"
          className="text-sm text-slate-400 hover:text-white mb-6 inline-block"
        >
          ← Back to Dashboard
        </Link>
        <h1 className="text-2xl font-bold text-white mb-6">Custom Domains</h1>
        <CustomDomainManager />
      </div>
    </div>
  )
}

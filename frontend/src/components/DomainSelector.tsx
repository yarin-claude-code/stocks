export function DomainSelector({ domains, active, onSelect }: {
  domains: string[], active: string, onSelect: (d: string) => void
}) {
  return (
    <div className="flex gap-2 overflow-x-auto pb-2 mb-6">
      {domains.map(d => (
        <button
          key={d}
          onClick={() => onSelect(d)}
          className={`px-4 py-1.5 rounded-full text-sm font-medium whitespace-nowrap transition-all border ${
            d === active
              ? 'bg-indigo-600 border-indigo-500 text-white shadow-lg shadow-indigo-500/20'
              : 'bg-slate-800 border-slate-700 text-slate-300 hover:border-indigo-500/50 hover:text-white'
          }`}
        >
          {d}
        </button>
      ))}
    </div>
  )
}

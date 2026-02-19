export function DomainSelector({ domains, active, onSelect }: {
  domains: string[], active: string, onSelect: (d: string) => void
}) {
  return (
    <div className="flex gap-2 overflow-x-auto pb-2 mb-6">
      {domains.map(d => (
        <button
          key={d}
          onClick={() => onSelect(d)}
          className={`px-3 py-1.5 rounded-full text-sm font-medium whitespace-nowrap transition-colors
            ${active === d ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}
        >
          {d}
        </button>
      ))}
    </div>
  )
}

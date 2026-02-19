export async function fetchRankings() {
  const res = await fetch('/api/rankings')
  if (!res.ok) throw new Error('Failed to fetch rankings')
  return res.json()
}

export async function fetchDomains() {
  const res = await fetch('/api/domains')
  if (!res.ok) throw new Error('Failed to fetch domains')
  return res.json()
}

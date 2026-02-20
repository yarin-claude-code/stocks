export function isMarketOpen(): boolean {
  const now = new Date()
  const parts = new Intl.DateTimeFormat('en-US', {
    timeZone: 'America/New_York',
    hour: 'numeric', minute: 'numeric', hour12: false, weekday: 'short',
  }).formatToParts(now)
  const p = Object.fromEntries(parts.map(x => [x.type, x.value]))
  const mins = parseInt(p.hour) * 60 + parseInt(p.minute)
  return !['Sat', 'Sun'].includes(p.weekday) && mins >= 570 && mins < 960
}

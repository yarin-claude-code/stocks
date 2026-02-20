export function TrendBadge({ slope }: { slope: number }) {
  if (slope > 0.5) {
    return <span className="text-green-600 font-semibold">↑ Up</span>
  }
  if (slope < -0.5) {
    return <span className="text-red-600 font-semibold">↓ Down</span>
  }
  return <span className="text-gray-500 font-semibold">→ Flat</span>
}

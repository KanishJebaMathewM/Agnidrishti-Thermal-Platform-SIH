import { classificationHue, type Classification, type Agency, agencyColor } from '../data/mockData'

export function ClassificationBadge({ classification, size = 'sm' }: { classification: Classification; size?: 'sm' | 'md' }) {
  const hue = classificationHue[classification]
  const pad = size === 'md' ? 'px-3 py-1.5 text-sm' : 'px-2.5 py-1 text-xs'
  return (
    <span
      className={`inline-flex items-center gap-1.5 ${pad} rounded font-medium border`}
      style={{ backgroundColor: hue.light, color: hue.deep, borderColor: hue.mid }}
    >
      <span className="inline-block w-2 h-2 rounded-full" style={{ backgroundColor: hue.mid }} />
      {hue.label}
    </span>
  )
}

export function AgencyBadge({ agency }: { agency: Agency }) {
  const c = agencyColor[agency]
  return (
    <span
      className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded text-xs font-medium border"
      style={{ backgroundColor: c.bg, color: c.text, borderColor: c.border }}
    >
      {agency}
    </span>
  )
}

export function StatusBadge({ status }: { status: 'Suppressed' | 'Escalated' | 'Under Review' }) {
  const map = {
    Suppressed: { bg: '#E4EAD4', text: '#4A5C29', border: '#7A9448' },
    Escalated: { bg: '#F7DCD1', text: '#7A3117', border: '#C25A34' },
    'Under Review': { bg: '#FBEACD', text: '#8C5F14', border: '#D89B2E' },
  }
  const c = map[status]
  return (
    <span
      className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded text-xs font-medium border"
      style={{ backgroundColor: c.bg, color: c.text, borderColor: c.border }}
    >
      {status}
    </span>
  )
}

export function ConfidenceTag({ value }: { value: number }) {
  const color = value >= 90 ? '#7A3117' : value >= 75 ? '#8C5F14' : '#4A5C29'
  return <span className="font-mono text-sm font-medium" style={{ color }}>{value}%</span>
}

export function formatTimestamp(iso: string): string {
  const d = new Date(iso)
  const now = Date.now()
  const diff = Math.floor((now - d.getTime()) / 1000)
  if (diff < 60) return `${diff}s ago`
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`
  return d.toLocaleString('en-IN', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })
}

export function formatCoord(lat: number, lon: number): string {
  const ns = lat >= 0 ? 'N' : 'S'
  const ew = lon >= 0 ? 'E' : 'W'
  return `${Math.abs(lat).toFixed(4)}°${ns}, ${Math.abs(lon).toFixed(4)}°${ew}`
}

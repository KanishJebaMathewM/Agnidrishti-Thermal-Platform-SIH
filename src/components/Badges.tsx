import { AlertTriangle, Flame, Leaf, TreePine, HelpCircle, MapPin } from 'lucide-react'
import { classificationHue, type Classification, type Agency, agencyColor } from '../data/mockData'

const classificationIconMap = {
  'Industrial Incident': AlertTriangle,
  'Persistent Flare/Kiln': Flame,
  'Agricultural Burn': Leaf,
  'Forest Fire': TreePine,
  'Unknown': HelpCircle,
}

export function ClassificationBadge({
  classification,
  size = 'sm',
  showIcon = true,
}: {
  classification: Classification
  size?: 'sm' | 'md'
  showIcon?: boolean
}) {
  const hue = classificationHue[classification] || classificationHue['Unknown']
  const Icon = classificationIconMap[classification] || HelpCircle
  const pad = size === 'md' ? 'px-3 py-1.5 text-xs' : 'px-2.5 py-1 text-[11px]'

  return (
    <span
      className={`inline-flex items-center gap-1.5 ${pad} rounded-lg font-semibold border shadow-2xs`}
      style={{
        backgroundColor: hue.light,
        color: hue.text,
        borderColor: `${hue.mid}40`,
      }}
    >
      {showIcon && <Icon className="w-3 h-3 shrink-0" style={{ color: hue.deep }} />}
      <span>{classification}</span>
    </span>
  )
}

export function AgencyBadge({ agency }: { agency: Agency }) {
  const c = agencyColor[agency]
  return (
    <span
      className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold border"
      style={{ backgroundColor: c.bg, color: c.text, borderColor: c.border }}
    >
      {agency}
    </span>
  )
}

export function StatusBadge({ status }: { status: 'Suppressed' | 'Escalated' | 'Under Review' }) {
  const map = {
    Suppressed: { bg: '#DCFCE7', text: '#15803D', border: '#86EFAC' },
    Escalated: { bg: '#FEE2E2', text: '#991B1B', border: '#FCA5A5' },
    'Under Review': { bg: '#FFEDD5', text: '#C2410C', border: '#FDBA74' },
  }
  const c = map[status]
  return (
    <span
      className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-bold border"
      style={{ backgroundColor: c.bg, color: c.text, borderColor: c.border }}
    >
      {status}
    </span>
  )
}

export function RegistryStatusBadge({ status }: { status: 'Registered' | 'Flagged for Inspection' }) {
  if (status === 'Flagged for Inspection') {
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-bold bg-amber-50 text-amber-800 border border-amber-200">
        Flagged for Inspection
      </span>
    )
  }
  return (
    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-bold bg-emerald-50 text-emerald-800 border border-emerald-200">
      Registered
    </span>
  )
}

export function RegistryTypeBadge({ type }: { type: 'Flare' | 'Kiln' | 'Power Plant' | 'Refinery' | 'Steel Mill' }) {
  const typeStyles = {
    Kiln: 'bg-sky-50 text-sky-700 border-sky-200',
    Flare: 'bg-orange-50 text-orange-700 border-orange-200',
    Refinery: 'bg-sky-50 text-sky-700 border-sky-200',
    'Power Plant': 'bg-purple-50 text-purple-700 border-purple-200',
    'Steel Mill': 'bg-slate-100 text-slate-700 border-slate-200',
  }
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-md text-[11px] font-semibold border ${typeStyles[type]}`}>
      {type}
    </span>
  )
}

export function ConfidenceTag({ value, hasDot = false }: { value: number; hasDot?: boolean }) {
  const color = value >= 85 ? '#DC2626' : value >= 75 ? '#EA580C' : '#166534'
  return (
    <div className="flex items-center gap-1.5">
      {hasDot && <span className="w-1.5 h-1.5 rounded-full bg-rose-600 shrink-0" />}
      <span className="font-bold text-sm" style={{ color }}>{value}%</span>
    </div>
  )
}

export function LocationTag({ place, coords }: { place: string; coords?: { lat: number; lon: number } }) {
  return (
    <div>
      <div className="font-bold text-slate-900 text-sm leading-snug">{place}</div>
      {coords && (
        <div className="flex items-center gap-1 text-[11px] text-slate-500 font-mono mt-0.5">
          <MapPin className="w-3 h-3 text-emerald-600 shrink-0" />
          <span>{formatCoord(coords.lat, coords.lon)}</span>
        </div>
      )}
    </div>
  )
}

export function formatTimestamp(iso: string): string {
  const d = new Date(iso)
  return d.toLocaleString('en-IN', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })
}

export function formatCoord(lat: number, lon: number): string {
  const ns = lat >= 0 ? 'N' : 'S'
  const ew = lon >= 0 ? 'E' : 'W'
  return `${Math.abs(lat).toFixed(4)}°${ns}, ${Math.abs(lon).toFixed(4)}°${ew}`
}

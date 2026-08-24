import { Satellite, Radio, Map, Layers, TreePine, ShieldCheck, Cloud } from 'lucide-react'
import { dataSources } from '../data/mockData'

const iconMap: Record<string, typeof Satellite> = {
  satellite: Satellite,
  radio: Radio,
  map: Map,
  layers: Layers,
  tree: TreePine,
}

export default function DataSources() {
  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold text-ink">Data Sources</h1>
          <p className="text-sm text-muted mt-1">Satellite feeds, infrastructure registries, and land-cover layers powering AGNIDRISHTI</p>
        </div>
        <div className="flex items-center gap-2 panel px-3 py-2">
          <ShieldCheck className="w-4 h-4 text-teal-deep" />
          <span className="text-xs font-medium text-teal-deep">On-premise deployment · NTRO sovereign cloud</span>
        </div>
      </div>

      {/* Source cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {dataSources.map((src) => {
          const Icon = iconMap[src.icon] || Satellite
          const isActive = src.status === 'Active'
          return (
            <div key={src.name} className="card p-4 hover:border-muted/40 transition-colors">
              <div className="flex items-start justify-between mb-3">
                <div className="w-10 h-10 rounded-md bg-teal-light flex items-center justify-center">
                  <Icon className="w-5 h-5 text-teal-deep" />
                </div>
                <span
                  className="badge"
                  style={
                    isActive
                      ? { backgroundColor: '#DCEEEC', color: '#155850', borderColor: '#2C8C82' }
                      : { backgroundColor: '#FBEACD', color: '#8C5F14', borderColor: '#D89B2E' }
                  }
                >
                  <span className={`w-2 h-2 rounded-full ${isActive ? 'bg-teal-mid' : 'bg-amber-mid'}`} />
                  {src.status}
                </span>
              </div>
              <h3 className="font-semibold text-ink text-sm">{src.name}</h3>
              <p className="text-xs text-muted mt-1 leading-relaxed">{src.description}</p>
              <div className="mt-3 pt-3 border-t border-border space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-muted">Last sync</span>
                  <span className="text-xs font-mono text-ink">{src.lastSync}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-muted">Coverage</span>
                  <span className="text-xs text-ink text-right max-w-[60%]">{src.coverage}</span>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Cloud cover map */}
      <div className="card p-4">
        <h2 className="font-semibold text-ink text-sm mb-3 flex items-center gap-2">
          <Cloud className="w-4 h-4 text-muted" />
          Cloud-Cover Gaps — Current Pass
        </h2>
        <p className="text-xs text-muted mb-3">
          Regions with insufficient satellite visibility are shown grayed out. Detections in these zones carry reduced confidence and are held for next-pass confirmation.
        </p>
        <div className="relative w-full bg-panel rounded-md overflow-hidden" style={{ height: 260 }}>
          <svg viewBox="0 0 560 260" className="w-full h-full" preserveAspectRatio="xMidYMid meet">
            <defs>
              <pattern id="cloudGrid" width="20" height="20" patternUnits="userSpaceOnUse">
                <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#DFE3DC" strokeWidth="0.5" />
              </pattern>
            </defs>
            <rect width="560" height="260" fill="url(#cloudGrid)" />
            {/* India outline simplified */}
            <path
              d="M 170 40 L 200 35 L 240 45 L 280 50 L 310 60 L 340 75 L 360 100 L 375 130 L 385 160 L 370 190 L 340 210 L 300 215 L 260 210 L 220 195 L 190 170 L 170 140 L 160 100 Z"
              fill="#DCEEEC"
              stroke="#2C8C82"
              strokeWidth="1"
            />
            {/* Cloud gap regions */}
            <ellipse cx="240" cy="90" rx="45" ry="30" fill="#5B6760" opacity="0.25" />
            <ellipse cx="320" cy="150" rx="50" ry="35" fill="#5B6760" opacity="0.2" />
            <ellipse cx="200" cy="170" rx="30" ry="25" fill="#5B6760" opacity="0.3" />
            {/* Labels */}
            <text x="240" y="92" textAnchor="middle" fontSize="9" fill="#1F2A24" fontFamily="IBM Plex Mono">NE gap</text>
            <text x="320" y="152" textAnchor="middle" fontSize="9" fill="#1F2A24" fontFamily="IBM Plex Mono">E coast gap</text>
            <text x="200" y="172" textAnchor="middle" fontSize="9" fill="#1F2A24" fontFamily="IBM Plex Mono">W gap</text>
          </svg>
        </div>
      </div>
    </div>
  )
}

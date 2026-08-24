import { useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { Flame, Wind, TreePine, Building2, ArrowRight } from 'lucide-react'
import { ClassificationBadge, ConfidenceTag, formatTimestamp } from '../components/Badges'
import { allEvents, agencyColor, type Agency } from '../data/mockData'

const agencyIcons: Record<Agency, typeof Flame> = {
  'Fire Services': Flame,
  'CPCB': Wind,
  'Forest Department': TreePine,
  'State Aggregation': Building2,
}

export default function Alerts() {
  const navigate = useNavigate()

  const grouped = useMemo(() => {
    const map: Record<Agency, typeof allEvents> = {
      'Fire Services': [],
      'CPCB': [],
      'Forest Department': [],
      'State Aggregation': [],
    }
    allEvents.filter((e) => e.isAnomaly).forEach((e) => {
      map[e.routedTo].push(e)
    })
    return map
  }, [])

  const agencyList: Agency[] = ['Fire Services', 'CPCB', 'Forest Department', 'State Aggregation']

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Alerts & Agency Routing</h1>
          <p className="text-xs sm:text-sm font-medium text-slate-500 mt-1">
            Anomalous detections automatically routed to responsible enforcement agencies ·{' '}
            <span className="text-rose-600 font-bold">{allEvents.filter((e) => e.isAnomaly).length} active alerts</span>
          </p>
        </div>
      </div>

      {/* 4 Agency Board Columns */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        {agencyList.map((agency) => {
          const Icon = agencyIcons[agency]
          const c = agencyColor[agency]
          const items = grouped[agency]

          return (
            <div key={agency} className="card overflow-hidden flex flex-col min-h-[520px] bg-slate-50/50">
              {/* Column Header */}
              <div className="p-4 border-b border-slate-200 bg-white" style={{ borderTop: `4px solid ${c.border}` }}>
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-xl flex items-center justify-center shrink-0 shadow-2xs" style={{ backgroundColor: c.bg, color: c.text }}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <div>
                    <h2 className="font-bold text-sm text-slate-900 leading-snug">{agency}</h2>
                    <p className="text-[11px] font-medium text-slate-500">{items.length} routed alerts</p>
                  </div>
                </div>
              </div>

              {/* Column Item Cards */}
              <div className="flex-1 p-3 overflow-y-auto space-y-3">
                {items.map((a) => (
                  <div
                    key={a.id}
                    onClick={() => navigate(`/events?selected=${a.id}`)}
                    className="bg-white border border-slate-200/90 rounded-2xl p-4 shadow-2xs hover:shadow-md hover:border-slate-300 transition-all cursor-pointer space-y-3"
                  >
                    {/* Top Row: Badge + Confidence */}
                    <div className="flex items-center justify-between gap-2">
                      <ClassificationBadge classification={a.classification} />
                      <ConfidenceTag value={a.confidence} />
                    </div>

                    {/* Middle Row: Title & Subtitle */}
                    <div>
                      <div className="font-bold text-slate-900 text-sm leading-snug">{a.placeName}</div>
                      <div className="text-xs text-slate-500 font-medium mt-1">
                        {a.state} <span className="text-slate-300">·</span> {formatTimestamp(a.timestamp)}
                      </div>
                    </div>

                    {/* Bottom Row: Link */}
                    <div className="pt-2 border-t border-slate-100 flex items-center gap-1 text-xs font-bold text-teal-700 hover:text-teal-900 transition-colors">
                      <span>Open detail</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </div>
                  </div>
                ))}

                {items.length === 0 && (
                  <div className="p-8 text-center text-xs font-medium text-slate-400 bg-white/60 rounded-2xl border border-dashed border-slate-200">
                    No active alerts routed to this agency.
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

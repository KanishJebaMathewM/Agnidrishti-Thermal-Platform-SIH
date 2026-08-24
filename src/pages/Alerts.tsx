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
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-semibold text-ink">Alerts & Routing</h1>
        <p className="text-sm text-muted mt-1">
          Anomalous detections routed to responsible agencies · {allEvents.filter((e) => e.isAnomaly).length} active alerts
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        {agencyList.map((agency) => {
          const Icon = agencyIcons[agency]
          const c = agencyColor[agency]
          const items = grouped[agency]
          return (
            <div key={agency} className="card overflow-hidden flex flex-col" style={{ minHeight: 400 }}>
              {/* Column header */}
              <div className="px-4 py-3 border-b border-border" style={{ backgroundColor: c.bg }}>
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-md flex items-center justify-center" style={{ backgroundColor: c.border }}>
                    <Icon className="w-4 h-4 text-white" />
                  </div>
                  <div>
                    <div className="font-semibold text-sm" style={{ color: c.text }}>{agency}</div>
                    <div className="text-xs" style={{ color: c.text, opacity: 0.7 }}>{items.length} routed alerts</div>
                  </div>
                </div>
              </div>

              {/* Cards */}
              <div className="flex-1 overflow-y-auto divide-y divide-border">
                {items.slice(0, 12).map((a) => (
                  <div
                    key={a.id}
                    className="px-4 py-3 hover:bg-panel transition-colors cursor-pointer"
                    onClick={() => navigate(`/events?selected=${a.id}`)}
                  >
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <ClassificationBadge classification={a.classification} />
                      <ConfidenceTag value={a.confidence} />
                    </div>
                    <div className="text-sm font-medium text-ink">{a.placeName}</div>
                    <div className="text-xs text-muted mt-0.5">{a.state} · {formatTimestamp(a.timestamp)}</div>
                    <div className="flex items-center gap-1 mt-2 text-xs text-teal-mid font-medium">
                      Open detail <ArrowRight className="w-3 h-3" />
                    </div>
                  </div>
                ))}
                {items.length === 0 && (
                  <div className="px-4 py-8 text-center text-sm text-muted">No active alerts routed to this agency.</div>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

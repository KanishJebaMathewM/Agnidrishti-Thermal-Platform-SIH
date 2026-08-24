import { useState, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { Flame, Filter, AlertTriangle, Eye, Clock, ArrowRight, Layers } from 'lucide-react'
import IndiaMap from '../components/IndiaMap'
import { ClassificationBadge, StatusBadge, ConfidenceTag, formatTimestamp, formatCoord } from '../components/Badges'
import { allEvents, recentEvents, classificationHue, type ThermalEvent } from '../data/mockData'

export default function Overview() {
  const navigate = useNavigate()
  const [showOnlyAnomalies, setShowOnlyAnomalies] = useState(false)

  const totalToday = allEvents.length
  const suppressed = allEvents.filter((e) => e.status === 'Suppressed').length
  const escalated = allEvents.filter((e) => e.isAnomaly).length
  const pendingResponse = allEvents.filter((e) => e.status === 'Under Review').length
  const activeHighRisk = allEvents.filter((e) => e.isAnomaly && e.classification === 'Industrial Incident').length

  const mapEvents = useMemo(
    () => (showOnlyAnomalies ? allEvents.filter((e) => e.isAnomaly) : allEvents),
    [showOnlyAnomalies],
  )

  const stats = [
    { label: 'Total Detections Today', value: totalToday.toLocaleString('en-IN'), icon: Flame, hue: 'text-ink' },
    { label: 'Suppressed (Known/Expected)', value: suppressed.toLocaleString('en-IN'), icon: Filter, hue: 'text-moss-deep' },
    { label: 'Escalated (Anomalous)', value: escalated.toLocaleString('en-IN'), icon: AlertTriangle, hue: 'text-ember-deep' },
    { label: 'Pending Agency Response', value: pendingResponse.toLocaleString('en-IN'), icon: Clock, hue: 'text-amber-deep' },
    { label: 'Active High-Risk Events', value: activeHighRisk.toLocaleString('en-IN'), icon: Eye, hue: 'text-ember-deep' },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-ink">National Thermal Anomaly Overview</h1>
          <p className="text-sm text-muted mt-1">
            {totalToday.toLocaleString('en-IN')} detections processed today ·{' '}
            <span className="text-ember-deep font-medium">{escalated} escalated as anomalous</span> ·{' '}
            {suppressed} known sources suppressed
          </p>
        </div>

        {/* Anomaly toggle */}
        <div className="flex items-center gap-3 panel px-4 py-3">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-ember-mid" />
            <span className="text-sm font-medium text-ink">Show only anomalies</span>
          </div>
          <button
            onClick={() => setShowOnlyAnomalies(!showOnlyAnomalies)}
            role="switch"
            aria-checked={showOnlyAnomalies}
            className={`relative w-11 h-6 rounded-full transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-teal-mid ${
              showOnlyAnomalies ? 'bg-ember-mid' : 'bg-border'
            }`}
          >
            <span
              className={`absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-white shadow-sm transition-transform ${
                showOnlyAnomalies ? 'translate-x-5' : ''
              }`}
            />
          </button>
        </div>
      </div>

      {/* Stat strip */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
        {stats.map((s) => {
          const Icon = s.icon
          return (
            <div key={s.label} className="card p-4 hover:border-muted/40 transition-colors">
              <div className="flex items-center justify-between mb-2">
                <Icon className={`w-4 h-4 ${s.hue}`} />
              </div>
              <div className={`stat-num ${s.hue}`}>{s.value}</div>
              <div className="text-xs text-muted mt-1 leading-tight">{s.label}</div>
            </div>
          )
        })}
      </div>

      {/* Map + Recent events */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 card overflow-hidden">
          <div className="flex items-center justify-between px-4 py-3 border-b border-border">
            <div className="flex items-center gap-2">
              <Layers className="w-4 h-4 text-teal-mid" />
              <h2 className="font-semibold text-ink text-sm">Detection Map — India</h2>
            </div>
            <span className="text-xs text-muted font-mono">
              {mapEvents.length} markers · {showOnlyAnomalies ? 'anomalies only' : 'all classifications'}
            </span>
          </div>
          <div className="p-2">
            <IndiaMap events={mapEvents} height={440} onMarkerClick={(id) => navigate(`/events?selected=${id}`)} />
          </div>
        </div>

        {/* Recent events */}
        <div className="card overflow-hidden flex flex-col">
          <div className="flex items-center justify-between px-4 py-3 border-b border-border">
            <h2 className="font-semibold text-ink text-sm">Recent Events</h2>
            <button
              onClick={() => navigate('/events')}
              className="flex items-center gap-1 text-xs text-teal-mid hover:text-teal-deep font-medium"
            >
              View all <ArrowRight className="w-3 h-3" />
            </button>
          </div>
          <div className="divide-y divide-border overflow-y-auto" style={{ maxHeight: 440 }}>
            {recentEvents.map((e) => (
              <button
                key={e.id}
                onClick={() => navigate(`/events?selected=${e.id}`)}
                className="w-full text-left px-4 py-3 hover:bg-panel transition-colors focus:outline-none focus-visible:bg-panel"
              >
                <div className="flex items-start justify-between gap-2 mb-1.5">
                  <ClassificationBadge classification={e.classification} />
                  {e.isAnomaly && (
                    <span className="text-[10px] font-semibold text-ember-deep bg-ember-light px-1.5 py-0.5 rounded uppercase tracking-wide">
                      Anomaly
                    </span>
                  )}
                </div>
                <div className="text-sm font-medium text-ink truncate">{e.placeName}</div>
                <div className="flex items-center justify-between mt-1">
                  <span className="text-xs text-muted font-mono">{e.state}</span>
                  <ConfidenceTag value={e.confidence} />
                </div>
                <div className="text-xs text-muted mt-0.5">{formatTimestamp(e.timestamp)}</div>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Classification summary */}
      <div className="card p-4">
        <h2 className="font-semibold text-ink text-sm mb-3">Classification Distribution</h2>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          {Object.entries(classificationHue).map(([key, hue]) => {
            const count = allEvents.filter((e) => e.classification === key).length
            const pct = ((count / totalToday) * 100).toFixed(1)
            return (
              <div key={key} className="panel p-3">
                <div className="flex items-center gap-2 mb-2">
                  <span className="w-3 h-3 rounded" style={{ backgroundColor: hue.mid }} />
                  <span className="text-xs text-muted truncate">{hue.label}</span>
                </div>
                <div className="font-display text-xl font-semibold text-ink">{count}</div>
                <div className="text-xs text-muted font-mono">{pct}%</div>
                <div className="mt-2 h-1.5 rounded-full bg-border overflow-hidden">
                  <div className="h-full rounded-full" style={{ width: `${pct}%`, backgroundColor: hue.mid }} />
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

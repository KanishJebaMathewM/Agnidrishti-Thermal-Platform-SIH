import { useEffect, useState } from 'react'
import { X, Satellite, Flame, Thermometer, Ruler, Activity, Check, AlertCircle, RefreshCw, Calendar } from 'lucide-react'
import { ClassificationBadge, ConfidenceTag, formatTimestamp, formatCoord, AgencyBadge } from './Badges'
import LoadingSkeleton from './shared/LoadingSkeleton'
import { classificationHue, type Classification, type ThermalEvent } from '../data/mockData'
import { useEventDetail } from '../hooks/useEventDetail'

interface Props {
  eventId: string
  onClose: () => void
}

const RECLASSIFY_OPTIONS: Classification[] = [
  'Industrial Incident',
  'Persistent Flare/Kiln',
  'Agricultural Burn',
  'Forest Fire',
  'Unknown',
]

export default function EventDetail({ eventId, onClose }: Props) {
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  const { event, loading, error, actionPending, confirm, markAsFalseAlarm, reclassify } = useEventDetail(eventId)
  const [showReclassify, setShowReclassify] = useState(false)

  return (
    <>
      {/* Backdrop */}
      <div className="fixed inset-0 bg-ink/20 backdrop-blur-[2px] z-40" onClick={onClose} />

      {/* Drawer */}
      <aside className="fixed right-0 top-0 bottom-0 w-full max-w-xl bg-paper border-l border-border z-50 overflow-y-auto shadow-xl">
        {/* Single sticky header — ID/close are always shown; classification/confidence
            fill in once the event loads, matching the original one-piece header so
            nothing else has to guess its height. */}
        <div className="sticky top-0 bg-paper border-b border-border px-5 py-4 z-10">
          <div className="flex items-start justify-between gap-3">
            <div>
              <div className="font-mono text-xs text-muted">{eventId}</div>
              {event && (
                <div className="flex items-center gap-2 mt-2">
                  <ClassificationBadge classification={event.classification} size="md" />
                  {event.isAnomaly && (
                    <span className="text-[10px] font-semibold text-ember-deep bg-ember-light px-2 py-1 rounded uppercase tracking-wide">
                      Anomalous
                    </span>
                  )}
                </div>
              )}
            </div>
            <button onClick={onClose} className="p-2 rounded-md hover:bg-panel transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-teal-mid">
              <X className="w-5 h-5 text-ink" />
            </button>
          </div>
          {event && (
            <div className="flex items-center gap-4 mt-3">
              <div>
                <div className="text-xs text-muted">Confidence</div>
                <ConfidenceTag value={event.confidence} />
              </div>
              <div>
                <div className="text-xs text-muted">Detected</div>
                <div className="text-sm font-medium text-ink">{formatTimestamp(event.timestamp)}</div>
              </div>
            </div>
          )}
        </div>

        {loading && !event && (
          <div className="px-5 py-4">
            <LoadingSkeleton rows={6} />
          </div>
        )}

        {error && !event && (
          <div className="px-5 py-4 text-sm text-ember-deep">Failed to load event details: {error}</div>
        )}

        {event && (
          <EventDetailContent
            event={event}
            actionPending={actionPending}
            showReclassify={showReclassify}
            onToggleReclassify={() => setShowReclassify((v) => !v)}
            onConfirm={() => confirm()}
            onFalseAlarm={() => markAsFalseAlarm()}
            onReclassify={(c) => {
              reclassify(c)
              setShowReclassify(false)
            }}
          />
        )}
      </aside>
    </>
  )
}

function EventDetailContent({
  event,
  actionPending,
  showReclassify,
  onToggleReclassify,
  onConfirm,
  onFalseAlarm,
  onReclassify,
}: {
  event: ThermalEvent
  actionPending: boolean
  showReclassify: boolean
  onToggleReclassify: () => void
  onConfirm: () => void
  onFalseAlarm: () => void
  onReclassify: (c: Classification) => void
}) {
  const hue = classificationHue[event.classification]
  const deviationPct = ((event.current - event.baseline) / event.baseline * 100).toFixed(0)

  const features = [
    { label: 'Fire Radiative Power', value: `${event.frp} MW`, icon: Flame, pct: Math.min(event.frp / 300 * 100, 100) },
    { label: 'Brightness Temp (4µm)', value: `${event.brightnessTemp4} K`, icon: Thermometer, pct: (event.brightnessTemp4 - 290) / 70 * 100 },
    { label: 'Brightness Temp (11µm)', value: `${event.brightnessTemp11} K`, icon: Thermometer, pct: (event.brightnessTemp11 - 280) / 50 * 100 },
    { label: 'Derived Flame Temp', value: `${event.flameTemp} K`, icon: Activity, pct: (event.flameTemp - 700) / 800 * 100 },
    { label: 'Estimated Burn Area', value: `${event.burnArea} km²`, icon: Ruler, pct: Math.min(event.burnArea / 15 * 100, 100) },
  ]

  // 14-day calendar heatmap
  const calendarDays = Array.from({ length: 14 }, (_, i) => {
    const active = i >= 14 - event.persistenceNights
    return { day: i, active }
  })

  return (
    <>
      <div className="px-5 py-4 space-y-5">
        {/* Location */}
        <div className="panel p-3">
          <div className="text-xs text-muted mb-1">Location</div>
          <div className="text-sm font-medium text-ink">
            {event.placeName?.includes(event.state) ? event.placeName : `${event.placeName}, ${event.state}`}
          </div>
          <div className="text-xs text-muted font-mono mt-1">{formatCoord(event.lat, event.lon)}</div>
        </div>

        {/* Feature breakdown */}
        <div>
          <h3 className="text-sm font-semibold text-ink mb-3">Feature Breakdown</h3>
          <div className="space-y-2.5">
            {features.map((f) => {
              const Icon = f.icon
              return (
                <div key={f.label} className="flex items-center gap-3">
                  <Icon className="w-4 h-4 text-muted shrink-0" />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs text-muted">{f.label}</span>
                      <span className="text-xs font-mono font-medium text-ink">{f.value}</span>
                    </div>
                    <div className="h-1.5 rounded-full bg-muted/20 overflow-hidden">
                      <div className="h-full bg-slate-700 rounded-full" style={{ width: `${Math.max(f.pct, 5)}%` }} />
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Deviation from baseline */}
        <div>
          <h3 className="text-sm font-semibold text-ink mb-3">Deviation from Baseline</h3>
          <div className="panel p-4">
            <div className="grid grid-cols-3 gap-2 mb-3">
              <div>
                <div className="text-[11px] text-muted truncate">Baseline (normal)</div>
                <div className="font-mono text-base font-semibold text-muted">{event.baseline}</div>
              </div>
              <div className="text-center">
                <div className="text-[11px] text-muted truncate">Current reading</div>
                <div className="font-mono text-base font-semibold text-ember-deep">{event.current}</div>
              </div>
              <div className="text-right">
                <div className="text-[11px] text-muted truncate">Deviation</div>
                <div className="font-mono text-base font-semibold text-ember-mid">
                  {Number(deviationPct) > 0 ? `+${deviationPct}%` : `${deviationPct}%`}
                </div>
              </div>
            </div>
            <div className="space-y-2">
              <div>
                <div className="text-[10px] text-muted mb-1">Baseline</div>
                <div className="h-3 rounded bg-muted/30 overflow-hidden">
                  <div className="h-full bg-muted/50 rounded" style={{ width: `${Math.min(event.baseline / 120 * 100, 100)}%` }} />
                </div>
              </div>
              <div>
                <div className="text-[10px] text-muted mb-1">Current</div>
                <div className="h-3 rounded bg-ember-light overflow-hidden">
                  <div className="h-full bg-ember-mid rounded" style={{ width: `${Math.min(event.current / 120 * 100, 100)}%` }} />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Historical timeline */}
        <div>
          <h3 className="text-sm font-semibold text-ink mb-3 flex items-center gap-2">
            <Calendar className="w-4 h-4 text-muted" />
            Active Nights (last 14 days)
          </h3>
          <div className="flex gap-1">
            {calendarDays.map((d) => (
              <div
                key={d.day}
                className={`flex-1 h-8 rounded ${d.active ? '' : 'bg-border'}`}
                style={d.active ? { backgroundColor: hue.mid } : undefined}
                title={d.active ? 'Active' : 'No detection'}
              />
            ))}
          </div>
          <div className="flex justify-between mt-1 text-[10px] text-muted font-mono">
            <span>14d ago</span>
            <span>Today</span>
          </div>
        </div>

        {/* Satellite placeholder */}
        <div>
          <h3 className="text-sm font-semibold text-ink mb-3 flex items-center gap-2">
            <Satellite className="w-4 h-4 text-muted" />
            Satellite Imagery
          </h3>
          <div className="relative aspect-video rounded-md border border-border bg-panel overflow-hidden">
            <div className="absolute inset-0 opacity-20" style={{ backgroundImage: 'repeating-linear-gradient(45deg, #DFE3DC 0, #DFE3DC 1px, transparent 1px, transparent 12px)' }} />
            <div className="absolute inset-0 flex flex-col items-center justify-center gap-2">
              <Satellite className="w-8 h-8 text-muted/50" />
              <span className="text-xs text-muted font-mono">Thermal band — {formatCoord(event.lat, event.lon)}</span>
              <span className="text-[10px] text-muted/70">VIIRS · 375m resolution</span>
            </div>
          </div>
        </div>

        {/* Routed agency */}
        <div>
          <h3 className="text-sm font-semibold text-ink mb-3">Routed To</h3>
          <AgencyBadge agency={event.routedTo} />
        </div>

        {/* Feedback buttons */}
        <div className="pt-2 border-t border-border">
          <div className="text-xs text-muted mb-2">Analyst Feedback</div>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={onConfirm}
              disabled={actionPending}
              className={`btn-secondary disabled:opacity-50 disabled:cursor-not-allowed ${event.reviewerFeedback === 'Confirmed' ? 'ring-2 ring-emerald-500' : ''}`}
            >
              <Check className="w-4 h-4" />
              {event.reviewerFeedback === 'Confirmed' ? 'Confirmed ✓' : 'Confirmed'}
            </button>
            <button
              onClick={onFalseAlarm}
              disabled={actionPending}
              className={`btn-secondary disabled:opacity-50 disabled:cursor-not-allowed ${event.reviewerFeedback === 'False Alarm' ? 'ring-2 ring-rose-500' : ''}`}
            >
              <AlertCircle className="w-4 h-4" />
              {event.reviewerFeedback === 'False Alarm' ? 'False Alarm ✓' : 'False Alarm'}
            </button>
            <div className="relative">
              <button onClick={onToggleReclassify} disabled={actionPending} className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed">
                <RefreshCw className="w-4 h-4" />
                Reclassify
              </button>
              {showReclassify && (
                <div className="absolute left-0 top-full mt-1 z-20 bg-paper border border-border rounded-md shadow-lg py-1 w-52">
                  {RECLASSIFY_OPTIONS.map((c) => (
                    <button
                      key={c}
                      onClick={() => onReclassify(c)}
                      className="w-full text-left px-3 py-1.5 text-xs font-medium text-ink hover:bg-panel disabled:opacity-50"
                      disabled={c === event.classification}
                    >
                      {c}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  )
}

import { useState, useMemo, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Search, ChevronUp, ChevronDown } from 'lucide-react'
import { ClassificationBadge, StatusBadge, ConfidenceTag, formatTimestamp, formatCoord, AgencyBadge } from '../components/Badges'
import { allEvents, classificationHue, type Classification, type ThermalEvent } from '../data/mockData'
import EventDetail from '../components/EventDetail'

type SortKey = 'timestamp' | 'confidence' | 'persistenceNights' | 'classification'
type SortDir = 'asc' | 'desc'

export default function Events() {
  const [searchParams, setSearchParams] = useSearchParams()
  const selectedId = searchParams.get('selected')
  const [search, setSearch] = useState('')
  const [classFilter, setClassFilter] = useState<Classification | 'all'>('all')
  const [statusFilter, setStatusFilter] = useState<'all' | 'Suppressed' | 'Escalated' | 'Under Review'>('all')
  const [stateFilter, setStateFilter] = useState('all')
  const [sortKey, setSortKey] = useState<SortKey>('timestamp')
  const [sortDir, setSortDir] = useState<SortDir>('desc')

  const selectedEvent = useMemo(
    () => allEvents.find((e) => e.id === selectedId) || null,
    [selectedId],
  )

  const states = useMemo(() => [...new Set(allEvents.map((e) => e.state))].sort(), [])

  const filtered = useMemo(() => {
    let result = allEvents.filter((e) => {
      if (search && !e.placeName.toLowerCase().includes(search.toLowerCase()) && !e.id.toLowerCase().includes(search.toLowerCase())) return false
      if (classFilter !== 'all' && e.classification !== classFilter) return false
      if (statusFilter !== 'all' && e.status !== statusFilter) return false
      if (stateFilter !== 'all' && e.state !== stateFilter) return false
      return true
    })
    result = [...result].sort((a, b) => {
      let cmp = 0
      if (sortKey === 'timestamp') cmp = +new Date(a.timestamp) - +new Date(b.timestamp)
      else if (sortKey === 'confidence') cmp = a.confidence - b.confidence
      else if (sortKey === 'persistenceNights') cmp = a.persistenceNights - b.persistenceNights
      else if (sortKey === 'classification') cmp = a.classification.localeCompare(b.classification)
      return sortDir === 'asc' ? cmp : -cmp
    })
    return result
  }, [search, classFilter, statusFilter, stateFilter, sortKey, sortDir])

  function toggleSort(key: SortKey) {
    if (sortKey === key) {
      setSortDir(sortDir === 'asc' ? 'desc' : 'asc')
    } else {
      setSortKey(key)
      setSortDir('desc')
    }
  }

  function closeDetail() {
    setSearchParams({})
  }

  const SortIcon = ({ col }: { col: SortKey }) => {
    if (sortKey !== col) return <span className="inline-block w-3" />
    return sortDir === 'asc' ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />
  }

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-semibold text-ink">Thermal Detection Events</h1>
        <p className="text-sm text-muted mt-1">{filtered.length} of {allEvents.length} detections matching current filters</p>
      </div>

      {/* Filter bar */}
      <div className="card p-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
            <input
              type="text"
              placeholder="Search by place or event ID..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="input pl-9"
            />
          </div>
          <select value={classFilter} onChange={(e) => setClassFilter(e.target.value as Classification | 'all')} className="input">
            <option value="all">All classifications</option>
            {Object.keys(classificationHue).map((k) => (
              <option key={k} value={k}>{k}</option>
            ))}
          </select>
          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value as any)} className="input">
            <option value="all">All statuses</option>
            <option value="Suppressed">Suppressed</option>
            <option value="Escalated">Escalated</option>
            <option value="Under Review">Under Review</option>
          </select>
          <select value={stateFilter} onChange={(e) => setStateFilter(e.target.value)} className="input">
            <option value="all">All states</option>
            {states.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-panel border-b border-border">
              <tr>
                <th className="table-header w-32">
                  <button onClick={() => toggleSort('classification')} className="flex items-center gap-1 hover:text-ink">
                    Classification <SortIcon col="classification" />
                  </button>
                </th>
                <th className="table-header">
                  <button onClick={() => toggleSort('confidence')} className="flex items-center gap-1 hover:text-ink">
                    Confidence <SortIcon col="confidence" />
                  </button>
                </th>
                <th className="table-header">Location</th>
                <th className="table-header">
                  <button onClick={() => toggleSort('timestamp')} className="flex items-center gap-1 hover:text-ink">
                    Timestamp <SortIcon col="timestamp" />
                  </button>
                </th>
                <th className="table-header">
                  <button onClick={() => toggleSort('persistenceNights')} className="flex items-center gap-1 hover:text-ink">
                    Persistence <SortIcon col="persistenceNights" />
                  </button>
                </th>
                <th className="table-header">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {filtered.slice(0, 100).map((e) => (
                <tr
                  key={e.id}
                  onClick={() => setSearchParams({ selected: e.id })}
                  className={`cursor-pointer hover:bg-panel transition-colors ${selectedId === e.id ? 'bg-teal-light/50' : ''}`}
                >
                  <td className="table-cell">
                    <div className="flex items-center gap-2">
                      <ClassificationBadge classification={e.classification} />
                      {e.isAnomaly && <span className="w-1.5 h-1.5 rounded-full bg-ember-mid" />}
                    </div>
                  </td>
                  <td className="table-cell"><ConfidenceTag value={e.confidence} /></td>
                  <td className="table-cell">
                    <div className="font-medium text-ink">{e.placeName}</div>
                    <div className="text-xs text-muted font-mono">{formatCoord(e.lat, e.lon)}</div>
                  </td>
                  <td className="table-cell text-muted">{formatTimestamp(e.timestamp)}</td>
                  <td className="table-cell">
                    <span className="font-mono text-sm">{e.persistenceNights} {e.persistenceNights === 1 ? 'night' : 'nights'}</span>
                  </td>
                  <td className="table-cell"><StatusBadge status={e.status} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {filtered.length > 100 && (
          <div className="px-4 py-3 border-t border-border text-xs text-muted text-center">
            Showing first 100 of {filtered.length} results — refine filters to narrow
          </div>
        )}
      </div>

      {selectedEvent && <EventDetail event={selectedEvent} onClose={closeDetail} />}
    </div>
  )
}

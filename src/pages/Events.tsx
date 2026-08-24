import { useState, useMemo } from 'react'
import { useSearchParams } from 'react-router-dom'
import {
  Search, Download, Filter, Calendar, ChevronDown, Eye, BarChart2, MoreVertical,
  TrendingUp, MapPin
} from 'lucide-react'
import { ClassificationBadge, StatusBadge, ConfidenceTag, formatCoord } from '../components/Badges'
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
  const [currentPage, setCurrentPage] = useState(1)

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

  const paginatedEvents = useMemo(() => {
    const start = (currentPage - 1) * 10
    return filtered.slice(start, start + 10)
  }, [filtered, currentPage])

  function closeDetail() {
    setSearchParams({})
  }

  function clearFilters() {
    setSearch('')
    setClassFilter('all')
    setStatusFilter('all')
    setStateFilter('all')
  }

  return (
    <div className="space-y-5">
      {/* Header Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Thermal Detection Events</h1>
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200">
              Live Feed
            </span>
          </div>
          <p className="text-xs sm:text-sm font-medium text-slate-500 mt-1">
            <span className="text-slate-800 font-semibold">{filtered.length} of {allEvents.length} detections matching current filters</span> ·{' '}
            <span className="text-rose-600 font-bold">29 escalated as anomalous</span> ·{' '}
            <span className="text-slate-600 font-medium">79 known sources suppressed</span>
          </p>
        </div>

        {/* Top Right Action Buttons */}
        <div className="flex items-center gap-2.5">
          <button className="btn-secondary">
            <Download className="w-4 h-4 text-slate-600" />
            <span>Export</span>
          </button>
          <button className="btn-primary">
            <Filter className="w-4 h-4 text-white" />
            <span>Filters</span>
            <span className="w-4 h-4 rounded-full bg-teal-800 text-white text-[10px] font-bold flex items-center justify-center">3</span>
          </button>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="card p-3.5">
        <div className="flex flex-col lg:flex-row items-center gap-3">
          {/* Search Box */}
          <div className="relative flex-1 w-full">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              placeholder="Search by place or event ID..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="input pl-10"
            />
          </div>

          {/* Filter Dropdowns */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 w-full lg:w-auto">
            <select
              value={classFilter}
              onChange={(e) => setClassFilter(e.target.value as Classification | 'all')}
              className="input text-xs font-medium"
            >
              <option value="all">All classifications</option>
              {Object.keys(classificationHue).map((k) => (
                <option key={k} value={k}>{k}</option>
              ))}
            </select>

            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as any)}
              className="input text-xs font-medium"
            >
              <option value="all">All statuses</option>
              <option value="Suppressed">Suppressed</option>
              <option value="Escalated">Escalated</option>
              <option value="Under Review">Under Review</option>
            </select>

            <select
              value={stateFilter}
              onChange={(e) => setStateFilter(e.target.value)}
              className="input text-xs font-medium"
            >
              <option value="all">All states</option>
              {states.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>

            <div className="relative">
              <select className="input text-xs font-medium pr-8">
                <option value="7d">Last 7 days</option>
                <option value="24h">Last 24 hours</option>
                <option value="30d">Last 30 days</option>
              </select>
              <Calendar className="absolute right-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-400 pointer-events-none" />
            </div>
          </div>

          {/* Clear Button */}
          <button
            onClick={clearFilters}
            className="text-xs font-bold text-teal-700 hover:text-teal-900 px-2 py-1 shrink-0"
          >
            Clear all
          </button>
        </div>
      </div>

      {/* Events Table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50/80 border-b border-slate-200">
                <th className="table-header">Classification</th>
                <th className="table-header">Confidence</th>
                <th className="table-header">Location</th>
                <th className="table-header">
                  <div className="flex items-center gap-1 cursor-pointer" onClick={() => setSortDir(sortDir === 'asc' ? 'desc' : 'asc')}>
                    <span>Timestamp</span>
                    <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
                  </div>
                </th>
                <th className="table-header">Persistence</th>
                <th className="table-header">Status</th>
                <th className="table-header text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {paginatedEvents.map((e) => (
                <tr
                  key={e.id}
                  onClick={() => setSearchParams({ selected: e.id })}
                  className={`cursor-pointer hover:bg-slate-50/90 transition-colors ${selectedId === e.id ? 'bg-teal-50/60' : ''}`}
                >
                  {/* Classification */}
                  <td className="table-cell">
                    <div className="flex items-center gap-2">
                      <ClassificationBadge classification={e.classification} />
                      {e.isAnomaly && <span className="w-1.5 h-1.5 rounded-full bg-rose-600 shrink-0" />}
                    </div>
                  </td>

                  {/* Confidence */}
                  <td className="table-cell">
                    <ConfidenceTag value={e.confidence} hasDot={e.isAnomaly} />
                  </td>

                  {/* Location */}
                  <td className="table-cell">
                    <div>
                      <div className="font-bold text-slate-900 text-sm">{e.placeName}</div>
                      <div className="flex items-center gap-1 text-[11px] text-slate-500 font-mono mt-0.5">
                        <MapPin className="w-3 h-3 text-emerald-600 shrink-0" />
                        <span>{formatCoord(e.lat, e.lon)}</span>
                      </div>
                    </div>
                  </td>

                  {/* Timestamp */}
                  <td className="table-cell">
                    <div className="font-semibold text-slate-900 text-xs">{e.timeAgo}</div>
                    <div className="text-[11px] text-slate-500 font-mono mt-0.5">{e.formattedTime}</div>
                  </td>

                  {/* Persistence */}
                  <td className="table-cell">
                    <div className="flex items-center gap-1.5">
                      <TrendingUp className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                      <div>
                        <div className="font-bold text-slate-800 text-xs">{e.persistenceText}</div>
                        <div className="text-[10px] text-slate-400 font-medium">{e.persistenceSubtext}</div>
                      </div>
                    </div>
                  </td>

                  {/* Status */}
                  <td className="table-cell">
                    <StatusBadge status={e.status} />
                  </td>

                  {/* Actions */}
                  <td className="table-cell text-right" onClick={(opt) => opt.stopPropagation()}>
                    <div className="flex items-center justify-end gap-1">
                      <button
                        onClick={() => setSearchParams({ selected: e.id })}
                        className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
                        title="View Details"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      <button
                        className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
                        title="Analytics"
                      >
                        <BarChart2 className="w-4 h-4" />
                      </button>
                      <button
                        className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
                        title="More Options"
                      >
                        <MoreVertical className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination Footer */}
        <div className="px-5 py-3.5 border-t border-slate-100 bg-slate-50/50 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-600 font-medium">
          <div className="flex items-center gap-3">
            <span>Rows per page</span>
            <select className="bg-white border border-slate-200 rounded-lg px-2 py-1 text-xs font-semibold">
              <option value="10">10</option>
              <option value="25">25</option>
              <option value="50">50</option>
            </select>
            <span>Showing 1 to 10 of {filtered.length} results</span>
          </div>

          {/* Page buttons */}
          <div className="flex items-center gap-1">
            <button className="px-2 py-1 rounded-lg border border-slate-200 bg-white hover:bg-slate-100 font-mono">
              &laquo;
            </button>
            <button className="px-2.5 py-1 rounded-lg border border-slate-200 bg-white hover:bg-slate-100 font-mono">
              &lt;
            </button>
            <button className="px-3 py-1 rounded-lg bg-teal-700 text-white font-bold">1</button>
            <button className="px-3 py-1 rounded-lg border border-slate-200 bg-white hover:bg-slate-100">2</button>
            <button className="px-3 py-1 rounded-lg border border-slate-200 bg-white hover:bg-slate-100">3</button>
            <span className="px-1 text-slate-400">...</span>
            <button className="px-3 py-1 rounded-lg border border-slate-200 bg-white hover:bg-slate-100">12</button>
            <button className="px-2.5 py-1 rounded-lg border border-slate-200 bg-white hover:bg-slate-100 font-mono">
              &gt;
            </button>
            <button className="px-2 py-1 rounded-lg border border-slate-200 bg-white hover:bg-slate-100 font-mono">
              &raquo;
            </button>
          </div>
        </div>
      </div>

      {selectedEvent && <EventDetail event={selectedEvent} onClose={closeDetail} />}
    </div>
  )
}

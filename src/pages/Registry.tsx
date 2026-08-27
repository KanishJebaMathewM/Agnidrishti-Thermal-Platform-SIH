import { useState, useMemo } from 'react'
import {
  Search, Plus, AlertTriangle, MapPin, Clock, Calendar, Eye, Edit3, MoreVertical,
  Flame, Factory, Zap, Fuel, AlertCircle
} from 'lucide-react'
import { type RegistrySource } from '../data/mockData'
import { formatCoord, RegistryStatusBadge, RegistryTypeBadge } from '../components/Badges'
import LoadingSkeleton from '../components/shared/LoadingSkeleton'
import EmptyState from '../components/shared/EmptyState'
import Pagination from '../components/shared/Pagination'
import { useSourcesList } from '../hooks/useSourcesList'

const typeIconMap = {
  Kiln: Factory,
  Flare: Flame,
  Refinery: Fuel,
  'Power Plant': Zap,
  'Steel Mill': Factory,
}

const typeBgMap = {
  Kiln: 'bg-sky-50 text-sky-600 border-sky-100',
  Flare: 'bg-orange-50 text-orange-600 border-orange-100',
  Refinery: 'bg-sky-50 text-sky-600 border-sky-100',
  'Power Plant': 'bg-purple-50 text-purple-600 border-purple-100',
  'Steel Mill': 'bg-slate-100 text-slate-600 border-slate-200',
}

export default function Registry() {
  const [search, setSearch] = useState('')
  const [typeFilter, setTypeFilter] = useState('all')
  const [statusFilter, setStatusFilter] = useState('all')
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const { sources: registrySources, loading, error } = useSourcesList()

  const types = useMemo(() => [...new Set(registrySources.map((s) => s.type))].sort(), [registrySources])

  const filtered = useMemo(() => {
    return registrySources.filter((s) => {
      if (search && !s.name.toLowerCase().includes(search.toLowerCase()) && !s.id.toLowerCase().includes(search.toLowerCase())) return false
      if (typeFilter !== 'all' && s.type !== typeFilter) return false
      if (statusFilter !== 'all' && s.status !== statusFilter) return false
      return true
    })
  }, [registrySources, search, typeFilter, statusFilter])

  const paginatedSources = useMemo(() => {
    const start = (currentPage - 1) * pageSize
    return filtered.slice(start, start + pageSize)
  }, [filtered, currentPage, pageSize])

  const flaggedCount = registrySources.filter((s) => s.status === 'Flagged for Inspection').length

  function clearFilters() {
    setSearch('')
    setTypeFilter('all')
    setStatusFilter('all')
  }

  return (
    <div className="space-y-5">
      {/* Header Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">National Thermal Source Registry</h1>
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200">
              Live Registry
            </span>
          </div>
          <p className="text-xs sm:text-sm font-medium text-slate-500 mt-1">
            <span className="text-slate-800 font-semibold">{registrySources.length} catalogued known sources</span> ·{' '}
            <span className="text-rose-600 font-bold">{flaggedCount} flagged for inspection</span>
          </p>
        </div>

        {/* Action Button */}
        <button className="btn-primary">
          <Plus className="w-4 h-4" />
          <span>Add New Source</span>
        </button>
      </div>

      {/* Flagged Alert Banner */}
      {flaggedCount > 0 && (
        <div className="card border-rose-200 bg-rose-50/70 p-4 flex flex-col sm:flex-row items-center justify-between gap-3 shadow-2xs">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-xl bg-rose-100 flex items-center justify-center shrink-0 text-rose-600">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <div className="text-sm font-medium text-rose-900">
              <span className="font-bold">{flaggedCount} unregistered persistent sources</span> detected — flagged for field inspection by regional officers.
            </div>
          </div>
          <button className="px-3.5 py-1.5 rounded-xl border border-rose-300 bg-white text-rose-700 font-bold text-xs hover:bg-rose-50 transition-colors shrink-0 shadow-2xs">
            View Flagged Sources
          </button>
        </div>
      )}

      {/* Filter Toolbar */}
      <div className="card p-3.5">
        <div className="flex flex-col lg:flex-row items-center gap-3">
          {/* Search Box */}
          <div className="relative flex-1 w-full">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              placeholder="Search by name or ID..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="input pl-10"
            />
          </div>

          {/* Filter Dropdowns */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5 w-full lg:w-auto">
            <select value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)} className="input text-xs font-medium">
              <option value="all">All types</option>
              {types.map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>

            <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} className="input text-xs font-medium">
              <option value="all">All statuses</option>
              <option value="Registered">Registered</option>
              <option value="Flagged for Inspection">Flagged for Inspection</option>
            </select>

            <select className="input text-xs font-medium">
              <option value="newest">Last updated (Newest)</option>
              <option value="oldest">Last updated (Oldest)</option>
            </select>
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

      {error && (
        <div className="card p-3.5 flex items-center gap-2.5 border-rose-200 bg-rose-50/60">
          <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
          <span className="text-xs font-semibold text-rose-800">{error} — showing offline/demo data.</span>
        </div>
      )}

      {loading ? (
        <div className="card p-5">
          <LoadingSkeleton rows={6} />
        </div>
      ) : filtered.length === 0 ? (
        <div className="card">
          <EmptyState title="No sources match these filters" message="Try clearing filters or adjusting your search." />
        </div>
      ) : (
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50/80 border-b border-slate-200">
                <th className="table-header">Source Name / ID &#x21D5;</th>
                <th className="table-header">Type &#x21D5;</th>
                <th className="table-header">Location &#x21D5;</th>
                <th className="table-header">Expected Active Hours &#x21D5;</th>
                <th className="table-header">Last Deviation &#x21D5;</th>
                <th className="table-header">Status &#x21D5;</th>
                <th className="table-header text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {paginatedSources.map((s: RegistrySource) => {
                const Icon = typeIconMap[s.type] || Factory
                const bgStyle = typeBgMap[s.type] || 'bg-slate-100 text-slate-600 border-slate-200'

                return (
                  <tr key={s.id} className="hover:bg-slate-50/90 transition-colors">
                    {/* Source Name & ID */}
                    <td className="table-cell">
                      <div className="flex items-center gap-3">
                        <div className={`w-9 h-9 rounded-xl border flex items-center justify-center shrink-0 ${bgStyle}`}>
                          <Icon className="w-4 h-4" />
                        </div>
                        <div>
                          <div className="font-bold text-slate-900 text-sm">{s.name}</div>
                          <div className="text-[11px] text-slate-500 font-mono mt-0.5">{s.id}</div>
                        </div>
                      </div>
                    </td>

                    {/* Type */}
                    <td className="table-cell">
                      <RegistryTypeBadge type={s.type} />
                    </td>

                    {/* Location */}
                    <td className="table-cell">
                      <div>
                        <div className="flex items-center gap-1 font-semibold text-slate-900 text-xs">
                          <MapPin className="w-3 h-3 text-emerald-600 shrink-0" />
                          <span>{s.placeName}, {s.state}</span>
                        </div>
                        <div className="text-[11px] text-slate-500 font-mono mt-0.5 pl-4">
                          {formatCoord(s.lat, s.lon)}
                        </div>
                      </div>
                    </td>

                    {/* Expected Active Hours */}
                    <td className="table-cell">
                      <div className="flex items-center gap-1.5 text-xs font-medium text-slate-700">
                        <Clock className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                        <span>{s.expectedHours}</span>
                      </div>
                    </td>

                    {/* Last Deviation */}
                    <td className="table-cell">
                      <div className="flex items-center gap-1.5 text-xs font-medium">
                        <Calendar className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                        {s.lastDeviationPct ? (
                          <div>
                            <div className="text-slate-800 font-semibold">{s.lastDeviationText}</div>
                            <div className="text-rose-600 font-bold text-[11px]">&uarr; {s.lastDeviationPct}</div>
                          </div>
                        ) : (
                          <span className="text-emerald-700 font-semibold">No deviation</span>
                        )}
                      </div>
                    </td>

                    {/* Status */}
                    <td className="table-cell">
                      <RegistryStatusBadge status={s.status} />
                    </td>

                    {/* Actions */}
                    <td className="table-cell text-right">
                      <div className="flex items-center justify-end gap-1">
                        <button className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors" title="View">
                          <Eye className="w-4 h-4" />
                        </button>
                        <button className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors" title="Edit">
                          <Edit3 className="w-4 h-4" />
                        </button>
                        <button className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors" title="More">
                          <MoreVertical className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>

        {/* Pagination Footer */}
        <Pagination
          currentPage={currentPage}
          totalItems={filtered.length}
          pageSize={pageSize}
          onPageChange={setCurrentPage}
          onPageSizeChange={(newSize) => {
            setPageSize(newSize)
            setCurrentPage(1)
          }}
        />
      </div>
      )}
    </div>
  )
}

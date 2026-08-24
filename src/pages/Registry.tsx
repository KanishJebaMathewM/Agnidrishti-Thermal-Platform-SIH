import { useState, useMemo } from 'react'
import { Search, Plus, AlertTriangle, MapPin } from 'lucide-react'
import { registrySources, type RegistrySource } from '../data/mockData'
import { formatCoord, formatTimestamp } from '../components/Badges'

export default function Registry() {
  const [search, setSearch] = useState('')
  const [typeFilter, setTypeFilter] = useState('all')
  const [statusFilter, setStatusFilter] = useState('all')

  const types = useMemo(() => [...new Set(registrySources.map((s) => s.type))].sort(), [])

  const filtered = useMemo(() => {
    return registrySources.filter((s) => {
      if (search && !s.name.toLowerCase().includes(search.toLowerCase()) && !s.id.toLowerCase().includes(search.toLowerCase())) return false
      if (typeFilter !== 'all' && s.type !== typeFilter) return false
      if (statusFilter !== 'all' && s.status !== statusFilter) return false
      return true
    })
  }, [search, typeFilter, statusFilter])

  const flaggedCount = registrySources.filter((s) => s.status === 'Flagged for Inspection').length

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold text-ink">National Thermal Source Registry</h1>
          <p className="text-sm text-muted mt-1">
            {registrySources.length} catalogued known sources ·{' '}
            <span className="text-ember-deep font-medium">{flaggedCount} flagged for inspection</span>
          </p>
        </div>
        <button className="btn-primary">
          <Plus className="w-4 h-4" />
          Add New Source
        </button>
      </div>

      {/* Flagged banner */}
      {flaggedCount > 0 && (
        <div className="card border-ember-mid/40 p-3 flex items-center gap-3" style={{ backgroundColor: '#F7DCD1' }}>
          <AlertTriangle className="w-5 h-5 text-ember-deep shrink-0" />
          <div className="text-sm text-ember-deep">
            <span className="font-semibold">{flaggedCount} unregistered persistent sources</span> detected — flagged for field inspection by regional officers.
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="card p-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
            <input
              type="text"
              placeholder="Search by name or ID..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="input pl-9"
            />
          </div>
          <select value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)} className="input">
            <option value="all">All types</option>
            {types.map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} className="input">
            <option value="all">All statuses</option>
            <option value="Registered">Registered</option>
            <option value="Flagged for Inspection">Flagged for Inspection</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-panel border-b border-border">
              <tr>
                <th className="table-header">Source Name / ID</th>
                <th className="table-header">Type</th>
                <th className="table-header">Location</th>
                <th className="table-header">Expected Active Hours</th>
                <th className="table-header">Last Deviation</th>
                <th className="table-header">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {filtered.map((s: RegistrySource) => (
                <tr key={s.id} className="hover:bg-panel transition-colors">
                  <td className="table-cell">
                    <div className="font-medium text-ink">{s.name}</div>
                    <div className="text-xs text-muted font-mono">{s.id}</div>
                  </td>
                  <td className="table-cell text-muted">{s.type}</td>
                  <td className="table-cell">
                    <div className="flex items-center gap-1.5 text-sm text-ink">
                      <MapPin className="w-3.5 h-3.5 text-muted" />
                      {s.placeName}, {s.state}
                    </div>
                    <div className="text-xs text-muted font-mono mt-0.5">{formatCoord(s.lat, s.lon)}</div>
                  </td>
                  <td className="table-cell text-muted font-mono text-xs">{s.expectedHours}</td>
                  <td className="table-cell text-muted">
                    {s.lastDeviation ? formatTimestamp(s.lastDeviation) : <span className="text-moss-deep">No deviation</span>}
                  </td>
                  <td className="table-cell">
                    {s.status === 'Flagged for Inspection' ? (
                      <span className="badge" style={{ backgroundColor: '#F7DCD1', color: '#7A3117', borderColor: '#C25A34' }}>
                        <AlertTriangle className="w-3 h-3" />
                        Flagged for Inspection
                      </span>
                    ) : (
                      <span className="badge" style={{ backgroundColor: '#DCEEEC', color: '#155850', borderColor: '#2C8C82' }}>
                        Registered
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

import { useState, useMemo, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Settings, ListFilter, Plus, MapPin, ExternalLink, MoreVertical,
  ChevronDown, Flame, TreePine, Building2, Bell, AlertTriangle, Leaf, HelpCircle,
  Wind, Clock, CheckCircle2, AlertCircle
} from 'lucide-react'
import { ClassificationBadge, ConfidenceTag } from '../components/Badges'
import LoadingSkeleton from '../components/shared/LoadingSkeleton'
import Pagination from '../components/shared/Pagination'
import { type Agency, type Classification } from '../data/mockData'
import { useEventsList } from '../hooks/useEventsList'
import { getAuthorities } from '../api/authoritiesApi'

const routedAgencyDetails: Record<string, { agency: Agency; division: string; icon: any }> = {
  'Meerut Bricks Belt': { agency: 'Fire Services', division: 'Meerut Division', icon: Flame },
  'Angul Steel Hub': { agency: 'State Aggregation', division: 'Odisha Control Room', icon: Building2 },
  'Assam Cluster Zone': { agency: 'Forest Department', division: 'Assam Zone', icon: TreePine },
  'Odisha Cluster Zone': { agency: 'State Aggregation', division: 'Odisha Control Room', icon: Building2 },
  'Uttar Pradesh Cluster Zone': { agency: 'State Aggregation', division: 'UP Control Room', icon: Building2 },
  'Karnataka Cluster Zone': { agency: 'CPCB', division: 'Bangalore Regional', icon: Wind },
  'West Bengal Cluster Zone': { agency: 'State Aggregation', division: 'WB Control Room', icon: Building2 },
  'Punjab Cluster Zone': { agency: 'Forest Department', division: 'Punjab Circle', icon: TreePine },
}

export default function Alerts() {
  const navigate = useNavigate()
  const [agencyFilter, setAgencyFilter] = useState('all')
  const [classFilter, setClassFilter] = useState('all')
  const [stateFilter, setStateFilter] = useState('all')
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const { events: allEvents, loading, error } = useEventsList()

  const [agencies, setAgencies] = useState<Agency[]>([])
  useEffect(() => {
    let isMounted = true
    getAuthorities().then((res) => isMounted && setAgencies(res))
    return () => {
      isMounted = false
    }
  }, [])

  const alertsData = useMemo(() => {
    return allEvents.slice(0, 30).map((e, idx) => {
      const routedInfo = routedAgencyDetails[e.placeName] || {
        agency: e.routedTo,
        division: `${e.state} Control Division`,
        icon: e.routedTo === 'Fire Services' ? Flame : e.routedTo === 'Forest Department' ? TreePine : Building2,
      }
      return {
        id: `AGD-2025-08${String(47 - idx).padStart(2, '0')}`,
        isNew: idx === 0,
        classification: e.classification,
        placeName: e.placeName,
        lat: e.lat,
        lon: e.lon,
        state: e.state,
        confidence: e.confidence,
        riskLevel: e.confidence >= 80 ? 'High Risk' : e.confidence >= 70 ? 'Moderate' : 'Low Risk',
        detectedTime: '24 Aug, 08:37 am',
        timeAgo: `${idx * 1 + 2}m ago`,
        status: idx % 3 === 0 ? 'Under Review' : 'Routed',
        routedAgency: routedInfo.agency,
        routedDivision: routedInfo.division,
        AgencyIcon: routedInfo.icon,
        eventId: e.id,
      }
    })
  }, [allEvents])

  const filteredAlerts = useMemo(() => {
    return alertsData.filter((a) => {
      if (agencyFilter !== 'all' && a.routedAgency !== agencyFilter) return false
      if (classFilter !== 'all' && a.classification !== classFilter) return false
      if (stateFilter !== 'all' && a.state !== stateFilter) return false
      return true
    })
  }, [alertsData, agencyFilter, classFilter, stateFilter])

  const paginatedAlerts = useMemo(() => {
    const start = (currentPage - 1) * pageSize
    return filteredAlerts.slice(start, start + pageSize)
  }, [filteredAlerts, currentPage, pageSize])

  return (
    <div className="space-y-5">
      {/* Header Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Alerts & Routing</h1>
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-600 animate-pulse" />
              Live Feed
            </span>
          </div>
          <p className="text-xs sm:text-sm font-medium text-slate-500 mt-1">
            Anomalous detections routed to responsible agencies ·{' '}
            <span className="text-slate-800 font-bold">{filteredAlerts.length} active alerts</span>
          </p>
        </div>

        {/* Top Right Action Buttons */}
        <div className="flex items-center gap-2.5">
          <button className="btn-secondary text-xs">
            <Settings className="w-4 h-4 text-slate-600" />
            <span>Routing Rules</span>
          </button>
          <button className="btn-secondary text-xs">
            <ListFilter className="w-4 h-4 text-slate-600" />
            <span>View All Alerts</span>
          </button>
          <button className="btn-primary text-xs">
            <Plus className="w-4 h-4" />
            <span>Create Alert</span>
          </button>
        </div>
      </div>

      {/* Filter Row */}
      <div className="card p-3.5">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          <select value={agencyFilter} onChange={(e) => setAgencyFilter(e.target.value)} className="input text-xs font-medium">
            <option value="all">🏛️ All Agencies</option>
            {agencies.map((a) => (
              <option key={a} value={a}>{a}</option>
            ))}
          </select>

          <select value={classFilter} onChange={(e) => setClassFilter(e.target.value)} className="input text-xs font-medium">
            <option value="all">🏷️ All Classifications</option>
            <option value="Industrial Incident">Industrial Incident</option>
            <option value="Persistent Flare/Kiln">Persistent Flare/Kiln</option>
            <option value="Agricultural Burn">Agricultural Burn</option>
            <option value="Forest Fire">Forest Fire</option>
            <option value="Unknown">Unknown</option>
          </select>

          <select value={stateFilter} onChange={(e) => setStateFilter(e.target.value)} className="input text-xs font-medium">
            <option value="all">📍 All States</option>
            <option value="Uttar Pradesh">Uttar Pradesh</option>
            <option value="Odisha">Odisha</option>
            <option value="Assam">Assam</option>
            <option value="Punjab">Punjab</option>
            <option value="Karnataka">Karnataka</option>
          </select>

          <div className="relative">
            <select className="input text-xs font-medium pr-8">
              <option value="latest">⇅ Sort: Latest First</option>
              <option value="oldest">⇅ Sort: Oldest First</option>
              <option value="confidence">⇅ Sort: Highest Confidence</option>
            </select>
          </div>
        </div>
      </div>

      {error && (
        <div className="card p-3.5 flex items-center gap-2.5 border-rose-200 bg-rose-50/60">
          <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
          <span className="text-xs font-semibold text-rose-800">{error} — showing offline/demo data.</span>
        </div>
      )}

      {/* Table Section */}
      {loading ? (
        <div className="card p-5">
          <LoadingSkeleton rows={6} />
        </div>
      ) : (
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50/80 border-b border-slate-200">
                <th className="table-header">Alert ID</th>
                <th className="table-header">Classification</th>
                <th className="table-header">Source / Location</th>
                <th className="table-header">State</th>
                <th className="table-header">Confidence</th>
                <th className="table-header">Detected At</th>
                <th className="table-header">Status</th>
                <th className="table-header">Routed To</th>
                <th className="table-header text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-xs">
              {paginatedAlerts.map((a) => {
                const AgencyIcon = a.AgencyIcon
                const dotColor =
                  a.classification === 'Industrial Incident'
                    ? 'bg-rose-500'
                    : a.classification === 'Persistent Flare/Kiln'
                    ? 'bg-orange-500'
                    : a.classification === 'Agricultural Burn'
                    ? 'bg-emerald-500'
                    : a.classification === 'Forest Fire'
                    ? 'bg-purple-500'
                    : 'bg-slate-400'

                return (
                  <tr
                    key={a.id}
                    onClick={() => navigate(`/events?selected=${a.eventId}`)}
                    className="hover:bg-slate-50/90 transition-colors cursor-pointer"
                  >
                    {/* Alert ID */}
                    <td className="table-cell">
                      <div className="flex items-center gap-2">
                        <span className={`w-2 h-2 rounded-full ${dotColor}`} />
                        <span className="font-bold text-slate-900 font-mono">{a.id}</span>
                        {a.isNew && (
                          <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-slate-100 text-slate-600 border border-slate-200">
                            New
                          </span>
                        )}
                      </div>
                    </td>

                    {/* Classification */}
                    <td className="table-cell">
                      <ClassificationBadge classification={a.classification as Classification} />
                    </td>

                    {/* Source / Location */}
                    <td className="table-cell">
                      <div>
                        <div className="font-bold text-slate-900">{a.placeName}</div>
                        <div className="text-[11px] text-slate-500 font-mono mt-0.5">
                          {a.lat.toFixed(4)}°N, {a.lon.toFixed(4)}°E
                        </div>
                      </div>
                    </td>

                    {/* State */}
                    <td className="table-cell font-bold text-slate-800">
                      {a.state}
                    </td>

                    {/* Confidence */}
                    <td className="table-cell">
                      <div className="font-bold text-sm text-rose-600">{a.confidence}%</div>
                      <div className="text-[10px] text-slate-500 font-medium">{a.riskLevel}</div>
                    </td>

                    {/* Detected At */}
                    <td className="table-cell">
                      <div className="font-semibold text-slate-900">{a.detectedTime}</div>
                      <div className="text-[11px] text-slate-500">{a.timeAgo}</div>
                    </td>

                    {/* Status */}
                    <td className="table-cell">
                      {a.status === 'Under Review' ? (
                        <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-bold bg-amber-50 text-amber-800 border border-amber-200">
                          <Clock className="w-3 h-3 text-amber-600" />
                          Under Review
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-bold bg-emerald-50 text-emerald-800 border border-emerald-200">
                          <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                          Routed
                        </span>
                      )}
                    </td>

                    {/* Routed To */}
                    <td className="table-cell">
                      <div className="flex items-center gap-2">
                        <AgencyIcon className="w-4 h-4 text-slate-600 shrink-0" />
                        <div>
                          <div className="font-bold text-slate-900">{a.routedAgency}</div>
                          <div className="text-[11px] text-slate-500">{a.routedDivision}</div>
                        </div>
                      </div>
                    </td>

                    {/* Actions */}
                    <td className="table-cell text-right" onClick={(opt) => opt.stopPropagation()}>
                      <div className="flex items-center justify-end gap-1.5">
                        <button
                          onClick={() => navigate(`/events?selected=${a.eventId}`)}
                          className="px-2.5 py-1 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 font-semibold text-xs inline-flex items-center gap-1 transition-colors"
                        >
                          <span>Open</span>
                          <ExternalLink className="w-3 h-3 text-slate-400" />
                        </button>
                        <button className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors">
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

        {/* Bottom Bar: Stat Summary + Pagination */}
        <div className="p-4 border-t border-slate-100 bg-slate-50/50 flex flex-col xl:flex-row items-center justify-between gap-4 text-xs font-medium">
          {/* Stat Summary Box */}
          <div className="flex flex-wrap items-center gap-4 bg-white border border-slate-200/90 px-4 py-2 rounded-2xl shadow-2xs">
            <div className="flex items-center gap-2">
              <Bell className="w-4 h-4 text-slate-500" />
              <div>
                <span className="font-extrabold text-slate-900 text-sm">30</span>
                <span className="text-[11px] text-slate-500 font-semibold ml-1">Active Alerts <span className="text-slate-400 font-normal">Across 4 agencies</span></span>
              </div>
            </div>

            <div className="h-4 w-[1px] bg-slate-200 hidden sm:block" />

            <div className="flex items-center gap-1.5">
              <AlertTriangle className="w-3.5 h-3.5 text-rose-600" />
              <span className="font-extrabold text-rose-600 text-sm">13</span>
              <span className="text-[11px] text-slate-500 font-semibold">High Risk</span>
            </div>

            <div className="flex items-center gap-1.5">
              <Flame className="w-3.5 h-3.5 text-orange-600" />
              <span className="font-extrabold text-orange-600 text-sm">9</span>
              <span className="text-[11px] text-slate-500 font-semibold">Moderate Risk</span>
            </div>

            <div className="flex items-center gap-1.5">
              <Leaf className="w-3.5 h-3.5 text-emerald-600" />
              <span className="font-extrabold text-emerald-600 text-sm">6</span>
              <span className="text-[11px] text-slate-500 font-semibold">Low Risk</span>
            </div>

            <div className="flex items-center gap-1.5">
              <HelpCircle className="w-3.5 h-3.5 text-slate-500" />
              <span className="font-extrabold text-slate-700 text-sm">2</span>
              <span className="text-[11px] text-slate-500 font-semibold">Unknown</span>
            </div>
          </div>

          {/* Pagination Controls */}
          <Pagination
            className="border-t-0 bg-transparent p-0 w-full xl:w-auto justify-end"
            currentPage={currentPage}
            totalItems={filteredAlerts.length}
            pageSize={pageSize}
            onPageChange={setCurrentPage}
            onPageSizeChange={(newSize) => {
              setPageSize(newSize)
              setCurrentPage(1)
            }}
          />
        </div>
      </div>
      )}
    </div>
  )
}

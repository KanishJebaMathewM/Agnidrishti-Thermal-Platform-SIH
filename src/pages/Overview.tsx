import { useState, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Flame, ShieldCheck, AlertTriangle, Clock, Shield, ArrowRight,
  Info, Calendar, ChevronDown, AlertCircle
} from 'lucide-react'
import { ResponsiveContainer, AreaChart, Area, PieChart, Pie, Cell } from 'recharts'
import IndiaMap from '../components/IndiaMap'
import { ConfidenceTag, formatDistanceToNow } from '../components/Badges'
import { KpiCardSkeleton } from '../components/shared/LoadingSkeleton'
import { useDashboardData } from '../hooks/useDashboardData'
import { trendData } from '../data/mockData'

export default function Overview() {
  const navigate = useNavigate()
  const [showOnlyAnomalies, setShowOnlyAnomalies] = useState(false)
  const { data: summary, mapEvents: liveMapEvents, loading, error, lastSync, refetch } = useDashboardData()

  const mapEvents = useMemo(
    () => (showOnlyAnomalies ? liveMapEvents.filter((e) => e.isAnomaly) : liveMapEvents),
    [showOnlyAnomalies, liveMapEvents],
  )

  // Sparkline generator helper data
  const sparklines = {
    total: [12, 18, 15, 25, 20, 35, 28, 42, 38, 50, 45, 60],
    suppressed: [8, 12, 10, 18, 15, 22, 20, 30, 25, 38, 32, 44],
    escalated: [4, 6, 5, 8, 7, 12, 9, 14, 11, 16, 14, 18],
    pending: [15, 12, 14, 10, 11, 8, 9, 7, 6, 8, 5, 4],
    highRisk: [2, 3, 2, 4, 3, 5, 4, 6, 5, 7, 5, 6],
  }

  const suppressedCount = summary ? summary.total_events_24h - summary.anomaly_events_24h : 0

  const kpiCards = [
    {
      title: 'Total Detections Today',
      value: summary ? String(summary.total_events_24h) : '—',
      change: '↑ 18% vs yesterday',
      changeColor: 'text-emerald-600',
      icon: Flame,
      iconBg: 'bg-teal-50 text-teal-600',
      strokeColor: '#0D9488',
      fillColor: '#E0F2F1',
      sparkline: sparklines.total,
    },
    {
      title: 'Suppressed (Known/Expected)',
      value: summary ? String(suppressedCount) : '—',
      change: '↑ 11% vs yesterday',
      changeColor: 'text-emerald-600',
      icon: ShieldCheck,
      iconBg: 'bg-emerald-50 text-emerald-600',
      strokeColor: '#16A34A',
      fillColor: '#DCFCE7',
      sparkline: sparklines.suppressed,
    },
    {
      title: 'Escalated (Anomalous)',
      value: summary ? String(summary.anomaly_events_24h) : '—',
      change: '↑ 32% vs yesterday',
      changeColor: 'text-rose-600',
      icon: AlertTriangle,
      iconBg: 'bg-rose-50 text-rose-600',
      strokeColor: '#EF4444',
      fillColor: '#FEE2E2',
      sparkline: sparklines.escalated,
    },
    {
      title: 'Active Thermal Sources',
      value: summary ? String(summary.active_sources) : '—',
      change: '↓ 5% vs yesterday',
      changeColor: 'text-emerald-600',
      icon: Clock,
      iconBg: 'bg-amber-50 text-amber-600',
      strokeColor: '#F97316',
      fillColor: '#FFEDD5',
      sparkline: sparklines.pending,
    },
    {
      title: 'Active High-Risk Events',
      value: summary ? String(summary.critical_events) : '—',
      change: '↑ 2 vs yesterday',
      changeColor: 'text-purple-600',
      icon: Shield,
      iconBg: 'bg-purple-50 text-purple-600',
      strokeColor: '#A855F7',
      fillColor: '#F3E8FF',
      sparkline: sparklines.highRisk,
    },
  ]

  const classDist = Array.isArray(summary?.classification_distribution) ? summary.classification_distribution : []
  const riskSummary = Array.isArray(summary?.risk_level_summary) ? summary.risk_level_summary : []

  return (
    <div className="space-y-4">
      {/* Header bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">National Thermal Anomaly Overview</h1>
          <p className="text-sm font-medium text-slate-500 mt-1">
            {summary ? (
              <>
                <span className="text-slate-800 font-semibold">{summary.total_events_24h} detections processed today</span> ·{' '}
                <span className="text-rose-600 font-bold">{summary.anomaly_events_24h} escalated as anomalous</span> ·{' '}
                <span className="text-slate-600 font-medium">{suppressedCount} known sources suppressed</span>
              </>
            ) : (
              <span className="text-slate-400">Loading detection summary…</span>
            )}
          </p>
        </div>

        {/* Anomaly Filter Toggle */}
        <div className="flex items-center gap-3 bg-white border border-slate-200/90 px-4 py-2.5 rounded-2xl shadow-2xs">
          <span className="text-xs font-semibold text-slate-700">Show only anomalies</span>
          <button
            onClick={() => setShowOnlyAnomalies(!showOnlyAnomalies)}
            role="switch"
            aria-checked={showOnlyAnomalies}
            className={`relative w-11 h-6 rounded-full transition-colors focus:outline-none ${
              showOnlyAnomalies ? 'bg-emerald-600' : 'bg-slate-300'
            }`}
          >
            <span
              className={`absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-white shadow-xs transition-transform ${
                showOnlyAnomalies ? 'translate-x-5' : ''
              }`}
            />
          </button>
        </div>
      </div>

      {/* Error banner */}
      {error && (
        <div className="card p-3.5 flex items-center gap-2.5 border-rose-200 bg-rose-50/60">
          <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
          <span className="text-xs font-semibold text-rose-800">{error} — showing offline/demo data.</span>
        </div>
      )}

      {/* 5 KPI Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
        {loading && !summary
          ? Array.from({ length: 5 }, (_, i) => <KpiCardSkeleton key={i} />)
          : kpiCards.map((card, idx) => {
          const Icon = card.icon
          const chartData = card.sparkline.map((v, i) => ({ i, v }))
          return (
            <div key={idx} className="card p-3 flex flex-col justify-between overflow-hidden relative group hover:border-slate-300 transition-all rounded-xl">
              <div className="flex items-start gap-2.5">
                <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${card.iconBg}`}>
                  <Icon className="w-4 h-4" />
                </div>
                <div>
                  <div className="text-2xl font-bold text-slate-900 tracking-tight leading-none">{card.value}</div>
                  <div className="text-[11px] font-medium text-slate-500 leading-tight mt-1">{card.title}</div>
                  <div className={`text-[10px] font-semibold mt-0.5 ${card.changeColor}`}>{card.change}</div>
                </div>
              </div>

              {/* Sparkline Chart Area */}
              <div className="h-6 -mx-3 -mb-3 mt-1.5 opacity-80 group-hover:opacity-100 transition-opacity">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={chartData}>
                    <Area
                      type="monotone"
                      dataKey="v"
                      stroke={card.strokeColor}
                      strokeWidth={1.8}
                      fill={card.fillColor}
                      isAnimationActive={false}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>
          )
        })}
      </div>

      {/* Main Grid: Map & Recent Events */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Detection Map (2 columns) */}
        <div className="lg:col-span-2 card overflow-hidden flex flex-col">
          <div className="flex items-center justify-between px-5 py-3.5 border-b border-slate-100 bg-slate-50/50">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-teal-600" />
              <h2 className="font-bold text-slate-900 text-sm">Detection Map — India</h2>
            </div>
          </div>
          <div className="p-3 flex-1">
            <IndiaMap
              events={mapEvents}
              height={460}
              loading={loading}
              error={error}
              onRetry={refetch}
              onMarkerClick={(id) => navigate(`/events?selected=${id}`)}
            />
          </div>

        </div>

        {/* Recent Events Panel (1 column) */}
        <div className="card flex flex-col overflow-hidden">
          <div className="flex items-center justify-between px-5 py-3.5 border-b border-slate-100 bg-slate-50/50">
            <h2 className="font-bold text-slate-900 text-sm">Recent Events</h2>
            <button
              onClick={() => navigate('/events')}
              className="flex items-center gap-1 text-xs font-bold text-teal-700 hover:text-teal-900 transition-colors"
            >
              View all <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="divide-y divide-slate-100 overflow-y-auto flex-1 max-h-[460px]">
            {(summary?.recent_events ?? []).map((e, idx) => (
              <div
                key={idx}
                onClick={() => navigate(`/events?selected=${e.id}`)}
                className="p-4 hover:bg-slate-50/80 transition-colors cursor-pointer flex items-start gap-3"
              >
                {/* Icon box based on type */}
                <div
                  className={`w-9 h-9 rounded-xl flex items-center justify-center shrink-0 ${
                    e.classification === 'Industrial Incident'
                      ? 'bg-rose-50 text-rose-600'
                      : e.classification === 'Persistent Flare/Kiln'
                      ? 'bg-orange-50 text-orange-600'
                      : e.classification === 'Agricultural Burn'
                      ? 'bg-emerald-50 text-emerald-600'
                      : e.classification === 'Forest Fire'
                      ? 'bg-purple-50 text-purple-600'
                      : 'bg-slate-100 text-slate-600'
                  }`}
                >
                  {e.classification === 'Industrial Incident' ? (
                    <AlertTriangle className="w-4 h-4" />
                  ) : e.classification === 'Persistent Flare/Kiln' ? (
                    <Flame className="w-4 h-4" />
                  ) : e.classification === 'Agricultural Burn' ? (
                    <Shield className="w-4 h-4" />
                  ) : e.classification === 'Forest Fire' ? (
                    <ShieldCheck className="w-4 h-4" />
                  ) : (
                    <Info className="w-4 h-4" />
                  )}
                </div>

                {/* Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2">
                    <span
                      className={`inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-bold border ${
                        e.classification === 'Industrial Incident'
                          ? 'bg-rose-50 text-rose-700 border-rose-200'
                          : e.classification === 'Persistent Flare/Kiln'
                          ? 'bg-orange-50 text-orange-700 border-orange-200'
                          : e.classification === 'Agricultural Burn'
                          ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                          : e.classification === 'Forest Fire'
                          ? 'bg-purple-50 text-purple-700 border-purple-200'
                          : 'bg-slate-100 text-slate-700 border-slate-200'
                      }`}
                    >
                      {e.classification}
                    </span>

                    {e.isAnomaly && (
                      <span className="text-[9px] font-bold text-rose-700 bg-rose-100 px-1.5 py-0.5 rounded tracking-wider uppercase">
                        ANOMALY
                      </span>
                    )}
                  </div>

                  <div className="font-bold text-slate-900 text-sm mt-1 truncate">{e.placeName}</div>
                  <div className="text-xs text-slate-500 font-medium mt-0.5">
                    {e.state} <span className="text-slate-400">·</span> {e.timeAgo}
                  </div>
                </div>

                {/* Confidence */}
                <div className="text-right shrink-0">
                  <ConfidenceTag value={e.confidence} />
                  <div className="text-[10px] text-slate-400 font-medium mt-0.5">Confidence</div>
                </div>
              </div>
            ))}
          </div>

          <div className="p-3 border-t border-slate-100 text-center bg-slate-50/50">
            <button
              onClick={() => navigate('/events')}
              className="text-xs font-bold text-teal-700 hover:text-teal-900"
            >
              +17 more events
            </button>
          </div>
        </div>
      </div>

      {/* Bottom Section: 3 Analytic Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3.5">
        {/* Card 1: Detections Over Time */}
        <div className="card p-3.5 flex flex-col justify-between rounded-xl">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5 text-teal-600" />
              <h3 className="font-bold text-slate-900 text-xs">Detections Over Time</h3>
            </div>
            <div className="flex items-center gap-1 text-[11px] font-semibold text-slate-600 bg-slate-100 px-2 py-0.5 rounded-lg border border-slate-200">
              <span>Today</span>
              <ChevronDown className="w-3 h-3 text-slate-400" />
            </div>
          </div>

          <div className="h-36 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trendData}>
                <defs>
                  <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#0D9488" stopOpacity={0.4} />
                    <stop offset="100%" stopColor="#0D9488" stopOpacity={0.02} />
                  </linearGradient>
                </defs>
                <Area
                  type="monotone"
                  dataKey="industrial"
                  stroke="#0D9488"
                  strokeWidth={2}
                  fill="url(#areaGrad)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Card 2: Classification Distribution */}
        <div className="card p-3.5 flex flex-col justify-between rounded-xl">
          <div className="flex items-center gap-1.5 mb-2">
            <span className="w-2 h-2 rounded-full bg-teal-600" />
            <h3 className="font-bold text-slate-900 text-xs">Classification Distribution</h3>
          </div>

          <div className="flex items-center gap-3">
            {/* Donut Chart */}
            <div className="relative w-28 h-28 shrink-0">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={classDist}
                    cx="50%"
                    cy="50%"
                    innerRadius={32}
                    outerRadius={50}
                    paddingAngle={2}
                    dataKey="value"
                  >
                    {classDist.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
              <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                <span className="font-extrabold text-slate-900 text-sm">{summary?.total_events_24h ?? '—'}</span>
                <span className="text-[9px] text-slate-500 font-semibold">Total</span>
              </div>
            </div>

            {/* Legend list */}
            <div className="flex-1 space-y-1 text-[11px]">
              {classDist.map((item) => (
                <div key={item.name} className="flex items-center justify-between">
                  <div className="flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full shrink-0" style={{ backgroundColor: item.color }} />
                    <span className="text-slate-700 font-medium truncate max-w-[90px]">{item.name}</span>
                  </div>
                  <span className="font-bold text-slate-900">{item.value} <span className="text-slate-400 font-normal">({item.pct})</span></span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Card 3: Risk Level Summary */}
        <div className="card p-3.5 flex flex-col justify-between rounded-xl">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-bold text-slate-900 text-xs">Risk Level Summary</h3>
          </div>

          <div className="flex items-center gap-3">
            {/* Gauge Donut Chart */}
            <div className="relative w-28 h-28 shrink-0">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={riskSummary}
                    cx="50%"
                    cy="50%"
                    innerRadius={32}
                    outerRadius={50}
                    paddingAngle={2}
                    dataKey="count"
                  >
                    {riskSummary.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
              <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                <span className="font-extrabold text-slate-900 text-xs">
                  {summary && summary.total_events_24h > 0
                    ? `${Math.round((summary.critical_events / summary.total_events_24h) * 100)}%`
                    : '—'}
                </span>
                <span className="text-[9px] text-slate-500 font-semibold">High Risk</span>
              </div>
            </div>

            {/* Legend List */}
            <div className="flex-1 space-y-1 text-[11px]">
              {riskSummary.map((item) => (
                <div key={item.name} className="flex items-center justify-between">
                  <div className="flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full shrink-0" style={{ backgroundColor: item.color }} />
                    <span className="text-slate-700 font-medium">{item.name}</span>
                  </div>
                  <span className="font-bold text-slate-900">{item.count} <span className="text-slate-400 font-normal">({item.pct})</span></span>
                </div>
              ))}
            </div>
          </div>

          <div className="text-[10px] text-slate-400 font-medium flex items-center gap-1 mt-2">
            <span>Based on priority scoring model</span>
            <Info className="w-3 h-3 text-slate-400" />
          </div>
        </div>
      </div>

      {/* Overview Footer Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-2 pt-2 text-xs text-slate-500 font-medium border-t border-slate-200/80">
        <div className="flex items-center gap-1.5">
          <Clock className="w-3.5 h-3.5 text-slate-400" />
          <span>Last sync {formatDistanceToNow(lastSync)}</span>
        </div>
        <div className="flex items-center gap-1.5">
          <Info className="w-3.5 h-3.5 text-slate-400" />
          <span>Data Sources: NASA FIRMS · Sentinel-2 · OSM · IMD · MoSPI</span>
        </div>
      </div>
    </div>
  )
}

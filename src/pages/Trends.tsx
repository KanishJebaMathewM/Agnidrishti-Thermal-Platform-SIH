import { useState, useMemo } from 'react'
import {
  Activity, Flame, BarChart3, Calendar, Clock, ShieldCheck, Download, Filter,
  Info, ChevronDown, Lightbulb
} from 'lucide-react'
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar
} from 'recharts'
import { classificationHue } from '../data/mockData'

const stackedData = [
  { date: '23 Apr', industrial: 12, flare: 14, agri: 13, forest: 7, unknown: 6 },
  { date: '27 Apr', industrial: 11, flare: 12, agri: 10, forest: 6, unknown: 5 },
  { date: '01 May', industrial: 15, flare: 18, agri: 18, forest: 10, unknown: 8 },
  { date: '05 May', industrial: 14, flare: 13, agri: 15, forest: 8, unknown: 7 },
  { date: '09 May', industrial: 18, flare: 22, agri: 26, forest: 12, unknown: 10 },
  { date: '13 May', industrial: 25, flare: 27, agri: 38, forest: 14, unknown: 10 },
  { date: '17 May', industrial: 19, flare: 23, agri: 28, forest: 10, unknown: 9 },
  { date: '21 May', industrial: 22, flare: 24, agri: 35, forest: 12, unknown: 11 },
  { date: 'Today', industrial: 24, flare: 26, agri: 36, forest: 14, unknown: 12 },
]

const anomalyByState = [
  { state: 'Odisha', pct: 27.6 },
  { state: 'Chhattisgarh', pct: 21.4 },
  { state: 'Punjab', pct: 16.8 },
  { state: 'Gujarat', pct: 13.2 },
  { state: 'Maharashtra', pct: 11.3 },
  { state: 'Jharkhand', pct: 9.1 },
  { state: 'Madhya Pradesh', pct: 6.7 },
  { state: 'Telangana', pct: 4.8 },
  { state: 'West Bengal', pct: 3.6 },
  { state: 'Assam', pct: 2.4 },
]

const seasonalAgri = [
  { month: 'Jan', count: 28 },
  { month: 'Feb', count: 32 },
  { month: 'Mar', count: 45 },
  { month: 'Apr', count: 62 },
  { month: 'May', count: 78 },
  { month: 'Jun', count: 83 },
  { month: 'Jul', count: 42 },
  { month: 'Aug', count: 35 },
  { month: 'Sep', count: 48 },
  { month: 'Oct', count: 192 },
  { month: 'Nov', count: 215 },
  { month: 'Dec', count: 278 },
]

export default function Trends() {
  const [regionFilter, setRegionFilter] = useState('all')
  const [classFilter, setClassFilter] = useState('all')

  const kpiCards = [
    {
      title: 'Total Detections',
      value: '842',
      change: '↑ 18% vs previous 30 days',
      changeColor: 'text-emerald-600',
      icon: Activity,
      iconBg: 'bg-teal-50 text-teal-600',
    },
    {
      title: 'High Risk Detections',
      value: '312',
      change: '↑ 24% vs previous 30 days',
      changeColor: 'text-emerald-600',
      icon: Flame,
      iconBg: 'bg-rose-50 text-rose-600',
    },
    {
      title: 'Avg. Detections / Day',
      value: '28.6',
      change: '↑ 15% vs previous 30 days',
      changeColor: 'text-emerald-600',
      icon: BarChart3,
      iconBg: 'bg-amber-50 text-amber-600',
    },
    {
      title: 'Peak Day Detections',
      value: '12',
      change: '18 May 2025',
      changeColor: 'text-slate-500 font-medium',
      icon: Calendar,
      iconBg: 'bg-purple-50 text-purple-600',
    },
    {
      title: 'Active Classifications',
      value: '5',
      change: 'of 6 total',
      changeColor: 'text-slate-500 font-medium',
      icon: Clock,
      iconBg: 'bg-sky-50 text-sky-600',
    },
    {
      title: 'Data Coverage',
      value: '96%',
      change: 'Excellent',
      changeColor: 'text-emerald-600 font-semibold',
      icon: ShieldCheck,
      iconBg: 'bg-emerald-50 text-emerald-600',
    },
  ]

  return (
    <div className="space-y-5">
      {/* Header Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-1.5">
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Historical & Seasonal Trends</h1>
            <Info className="w-4 h-4 text-slate-400" />
          </div>
          <p className="text-xs sm:text-sm font-medium text-slate-500 mt-1">
            Detection patterns over time to identify trends, seasonality and emerging risks.
          </p>
        </div>

        <button className="btn-secondary self-start md:self-auto">
          <Download className="w-4 h-4 text-slate-600" />
          <span>Download Report</span>
        </button>
      </div>

      {/* Filter Row */}
      <div className="card p-3.5">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          <select value={regionFilter} onChange={(e) => setRegionFilter(e.target.value)} className="input text-xs font-medium">
            <option value="all">🌐 All Regions</option>
            <option value="north">North India</option>
            <option value="south">South India</option>
            <option value="east">East India</option>
            <option value="west">West India</option>
          </select>

          <select value={classFilter} onChange={(e) => setClassFilter(e.target.value)} className="input text-xs font-medium">
            <option value="all">🏷️ All Classifications</option>
            {Object.keys(classificationHue).map((k) => (
              <option key={k} value={k}>{k}</option>
            ))}
          </select>

          <select className="input text-xs font-medium">
            <option value="30d">📅 Last 30 days</option>
            <option value="90d">Last 90 days</option>
            <option value="1y">Last year</option>
          </select>

          <button className="inline-flex items-center justify-center gap-2 px-4 py-2 rounded-xl bg-teal-50 text-teal-800 font-bold text-xs hover:bg-teal-100 transition-colors border border-teal-200 shadow-2xs">
            <Filter className="w-3.5 h-3.5 text-teal-700" />
            <span>Apply Filters</span>
          </button>
        </div>
      </div>

      {/* 6 KPI Stat Cards Row */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3.5">
        {kpiCards.map((c, idx) => {
          const Icon = c.icon
          return (
            <div key={idx} className="card p-4 flex flex-col justify-between hover:border-slate-300 transition-all">
              <div className="flex items-start gap-3">
                <div className={`w-9 h-9 rounded-xl flex items-center justify-center shrink-0 ${c.iconBg}`}>
                  <Icon className="w-4.5 h-4.5" />
                </div>
                <div>
                  <div className="text-2xl font-extrabold text-slate-900 tracking-tight">{c.value}</div>
                  <div className="text-xs font-medium text-slate-500 leading-snug mt-0.5">{c.title}</div>
                  <div className={`text-[11px] font-semibold mt-1.5 ${c.changeColor}`}>{c.change}</div>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Stacked Area Chart Card: Detections Over Time (by Classification) */}
      <div className="card p-5">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-1.5">
            <h2 className="font-bold text-slate-900 text-sm">Detections Over Time (by Classification)</h2>
            <Info className="w-3.5 h-3.5 text-slate-400" />
          </div>

          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1 text-xs font-semibold text-slate-600 bg-slate-100 px-2.5 py-1 rounded-lg border border-slate-200">
              <span>Daily</span>
              <ChevronDown className="w-3 h-3 text-slate-400" />
            </div>
            <button className="text-xs font-semibold text-slate-600 bg-slate-100 hover:bg-slate-200 px-2.5 py-1 rounded-lg border border-slate-200">
              Show All
            </button>
          </div>
        </div>

        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={stackedData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="colorInd" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#EF4444" stopOpacity={0.4}/>
                  <stop offset="95%" stopColor="#EF4444" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="colorFlare" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#F97316" stopOpacity={0.4}/>
                  <stop offset="95%" stopColor="#F97316" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="colorAgri" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#22C55E" stopOpacity={0.4}/>
                  <stop offset="95%" stopColor="#22C55E" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="colorForest" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#A855F7" stopOpacity={0.4}/>
                  <stop offset="95%" stopColor="#A855F7" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="colorUnknown" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#64748B" stopOpacity={0.4}/>
                  <stop offset="95%" stopColor="#64748B" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" vertical={false} />
              <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#64748B' }} stroke="#CBD5E1" />
              <YAxis tick={{ fontSize: 11, fill: '#64748B' }} stroke="#CBD5E1" />
              <Tooltip />
              <Area type="monotone" dataKey="industrial" stackId="1" stroke="#EF4444" strokeWidth={2} fill="url(#colorInd)" name="Industrial" />
              <Area type="monotone" dataKey="flare" stackId="1" stroke="#F97316" strokeWidth={2} fill="url(#colorFlare)" name="Persistent Flare/Kiln" />
              <Area type="monotone" dataKey="agri" stackId="1" stroke="#22C55E" strokeWidth={2} fill="url(#colorAgri)" name="Agricultural Burn" />
              <Area type="monotone" dataKey="forest" stackId="1" stroke="#A855F7" strokeWidth={2} fill="url(#colorForest)" name="Forest Fire" />
              <Area type="monotone" dataKey="unknown" stackId="1" stroke="#64748B" strokeWidth={2} fill="url(#colorUnknown)" name="Unknown" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Legend Row */}
        <div className="flex flex-wrap items-center justify-center gap-6 mt-4 pt-3 border-t border-slate-100 text-xs font-semibold text-slate-700">
          <div className="flex items-center gap-2"><span className="w-2.5 h-2.5 rounded-full bg-rose-500" /><span>Industrial</span></div>
          <div className="flex items-center gap-2"><span className="w-2.5 h-2.5 rounded-full bg-orange-500" /><span>Persistent Flare/Kiln</span></div>
          <div className="flex items-center gap-2"><span className="w-2.5 h-2.5 rounded-full bg-emerald-500" /><span>Agricultural Burn</span></div>
          <div className="flex items-center gap-2"><span className="w-2.5 h-2.5 rounded-full bg-purple-500" /><span>Forest Fire</span></div>
          <div className="flex items-center gap-2"><span className="w-2.5 h-2.5 rounded-full bg-slate-500" /><span>Unknown</span></div>
        </div>
      </div>

      {/* Bottom 2 Cards Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Left Card: Anomaly Rate by State */}
        <div className="card p-5">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-1.5">
              <h2 className="font-bold text-slate-900 text-sm">Anomaly Rate by State</h2>
              <Info className="w-3.5 h-3.5 text-slate-400" />
            </div>
            <div className="flex items-center gap-1 text-xs font-semibold text-slate-600 bg-slate-100 px-2.5 py-1 rounded-lg border border-slate-200">
              <span>Last 30 days</span>
              <ChevronDown className="w-3 h-3 text-slate-400" />
            </div>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={anomalyByState} layout="vertical" margin={{ top: 0, right: 30, left: 20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" horizontal={false} />
                <XAxis type="number" tick={{ fontSize: 10, fill: '#64748B' }} stroke="#CBD5E1" unit="%" />
                <YAxis type="category" dataKey="state" tick={{ fontSize: 11, fill: '#334155', fontWeight: 600 }} stroke="#CBD5E1" width={90} />
                <Tooltip />
                <Bar dataKey="pct" fill="#EF4444" radius={[0, 6, 6, 0]} barSize={14} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Right Card: Seasonal Pattern — Agricultural Burns */}
        <div className="card p-5 flex flex-col justify-between">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-1.5">
              <h2 className="font-bold text-slate-900 text-sm">Seasonal Pattern — Agricultural Burns</h2>
              <Info className="w-3.5 h-3.5 text-slate-400" />
            </div>
            <div className="flex items-center gap-1 text-xs font-semibold text-slate-600 bg-slate-100 px-2.5 py-1 rounded-lg border border-slate-200">
              <span>Current Year</span>
              <ChevronDown className="w-3 h-3 text-slate-400" />
            </div>
          </div>

          <div className="h-56 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={seasonalAgri} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" vertical={false} />
                <XAxis dataKey="month" tick={{ fontSize: 11, fill: '#64748B' }} stroke="#CBD5E1" />
                <YAxis tick={{ fontSize: 11, fill: '#64748B' }} stroke="#CBD5E1" />
                <Tooltip />
                <Bar dataKey="count" fill="#22C55E" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Light Green Bulb Banner */}
          <div className="mt-4 p-3.5 bg-emerald-50/80 border border-emerald-200 rounded-xl flex items-start gap-2.5 text-xs text-emerald-900 font-medium">
            <Lightbulb className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
            <span>
              <span className="font-bold">Peak burn activity Oct–Dec (harvest residue)</span> and Apr–May (rabi residue). Higher activity observed in Punjab, Haryana, and western UP.
            </span>
          </div>
        </div>
      </div>

      {/* Footer Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-2 pt-2 text-xs text-slate-500 font-medium border-t border-slate-200/80">
        <div className="flex items-center gap-1.5">
          <Clock className="w-3.5 h-3.5 text-slate-400" />
          <span>Last Updated: 24 May 2025, 10:32 AM IST</span>
        </div>
        <div className="flex items-center gap-1.5">
          <Info className="w-3.5 h-3.5 text-slate-400" />
          <span>Data Sources: NASA FIRMS · Sentinel-2 · OSM · IMD · MoSPI</span>
        </div>
      </div>
    </div>
  )
}

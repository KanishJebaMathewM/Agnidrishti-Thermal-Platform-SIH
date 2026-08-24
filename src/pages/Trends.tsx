import { useState, useMemo } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Legend, AreaChart, Area,
} from 'recharts'
import { trendData, stateAnomalyData, classificationHue } from '../data/mockData'

export default function Trends() {
  const [regionFilter, setRegionFilter] = useState('all')
  const [classFilter, setClassFilter] = useState('all')

  const filteredTrend = useMemo(() => trendData, [])

  const seasonalData = useMemo(() => {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    const r = (s: number) => { let x = s; return () => { x = (x * 9301 + 49297) % 233280; return x / 233280 } }
    const rand = r(7)
    return months.map((m, i) => ({
      month: m,
      burns: i >= 9 && i <= 11 ? Math.floor(rand() * 200 + 150) : i >= 3 && i <= 5 ? Math.floor(rand() * 80 + 30) : Math.floor(rand() * 40 + 10),
    }))
  }, [])

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-semibold text-ink">Historical & Seasonal Trends</h1>
        <p className="text-sm text-muted mt-1">Detection patterns over 30 days · anomaly rate by state · seasonal agricultural burn cycle</p>
      </div>

      {/* Filters */}
      <div className="card p-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <select className="input" value={regionFilter} onChange={(e) => setRegionFilter(e.target.value)}>
            <option value="all">All regions</option>
            <option value="north">North India</option>
            <option value="south">South India</option>
            <option value="east">East India</option>
            <option value="west">West India</option>
          </select>
          <select className="input" value={classFilter} onChange={(e) => setClassFilter(e.target.value)}>
            <option value="all">All classifications</option>
            {Object.keys(classificationHue).map((k) => (
              <option key={k} value={k}>{k}</option>
            ))}
          </select>
          <select className="input">
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
            <option value="1y">Last year</option>
          </select>
        </div>
      </div>

      {/* Detections over time */}
      <div className="card p-4">
        <h2 className="font-semibold text-ink text-sm mb-4">Detections Over Time (by classification)</h2>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={filteredTrend}>
            <defs>
              {Object.entries(classificationHue).map(([key, hue], i) => (
                <linearGradient key={key} id={`grad-${i}`} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={hue.mid} stopOpacity={0.3} />
                  <stop offset="100%" stopColor={hue.mid} stopOpacity={0.02} />
                </linearGradient>
              ))}
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#DFE3DC" />
            <XAxis dataKey="date" tick={{ fontSize: 10, fill: '#5B6760', fontFamily: 'IBM Plex Mono' }} tickFormatter={(d) => d.slice(5)} />
            <YAxis tick={{ fontSize: 10, fill: '#5B6760' }} />
            <Tooltip
              contentStyle={{ backgroundColor: '#F7F8F6', border: '1px solid #DFE3DC', borderRadius: 6, fontSize: 12 }}
              labelStyle={{ fontFamily: 'IBM Plex Mono', color: '#1F2A24' }}
            />
            <Legend wrapperStyle={{ fontSize: 11 }} />
            <Area type="monotone" dataKey="industrial" stackId="1" stroke={classificationHue['Industrial Incident'].mid} fill="url(#grad-0)" name="Industrial" />
            <Area type="monotone" dataKey="flare" stackId="1" stroke={classificationHue['Persistent Flare/Kiln'].mid} fill="url(#grad-1)" name="Flare/Kiln" />
            <Area type="monotone" dataKey="agricultural" stackId="1" stroke={classificationHue['Agricultural Burn'].mid} fill="url(#grad-2)" name="Agri Burn" />
            <Area type="monotone" dataKey="forest" stackId="1" stroke={classificationHue['Forest Fire'].mid} fill="url(#grad-3)" name="Forest Fire" />
            <Area type="monotone" dataKey="unknown" stackId="1" stroke={classificationHue['Unknown'].mid} fill="url(#grad-4)" name="Unknown" />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Anomaly rate by state */}
        <div className="card p-4">
          <h2 className="font-semibold text-ink text-sm mb-4">Anomaly Rate by State</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={stateAnomalyData} layout="vertical" margin={{ left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#DFE3DC" horizontal={false} />
              <XAxis type="number" tick={{ fontSize: 10, fill: '#5B6760' }} />
              <YAxis type="category" dataKey="state" tick={{ fontSize: 11, fill: '#1F2A24' }} width={100} />
              <Tooltip
                contentStyle={{ backgroundColor: '#F7F8F6', border: '1px solid #DFE3DC', borderRadius: 6, fontSize: 12 }}
                formatter={(v: any, n: string) => [v, n === 'anomalies' ? 'Anomalies' : 'Total']}
              />
              <Bar dataKey="anomalies" fill={classificationHue['Industrial Incident'].mid} radius={[0, 3, 3, 0]} name="Anomalies" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Seasonal pattern */}
        <div className="card p-4">
          <h2 className="font-semibold text-ink text-sm mb-4">Seasonal Pattern — Agricultural Burns</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={seasonalData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#DFE3DC" />
              <XAxis dataKey="month" tick={{ fontSize: 11, fill: '#5B6760' }} />
              <YAxis tick={{ fontSize: 10, fill: '#5B6760' }} />
              <Tooltip
                contentStyle={{ backgroundColor: '#F7F8F6', border: '1px solid #DFE3DC', borderRadius: 6, fontSize: 12 }}
              />
              <Bar dataKey="burns" fill={classificationHue['Agricultural Burn'].mid} radius={[3, 3, 0, 0]} name="Agri Burns" />
            </BarChart>
          </ResponsiveContainer>
          <p className="text-xs text-muted mt-2">
            Peak burn activity Oct–Nov (kharif stubble) and Apr–May (rabi stubble) — consistent with agricultural calendars in Punjab, Haryana, and western UP.
          </p>
        </div>
      </div>
    </div>
  )
}

import {
  Target, Shield, Zap, Info, Clock, ExternalLink, Brain, ChevronDown, CheckCircle2,
  FileCheck, Lock, TrendingUp
} from 'lucide-react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell,
  AreaChart, Area
} from 'recharts'
import { featureImportance } from '../data/mockData'

const confusionMatrixData = {
  labels: ['Industrial', 'Flare/Kiln', 'Agri', 'Forest', 'Unknown'],
  matrix: [
    [142, 8, 2, 1, 3],
    [6, 168, 4, 0, 2],
    [3, 5, 291, 7, 9],
    [1, 0, 6, 134, 4],
    [4, 3, 11, 5, 87],
  ],
  totalsActual: [156, 180, 315, 145, 110],
  totalsPredicted: [156, 184, 314, 147, 105],
}

const sparklineData = [
  { v: 85 }, { v: 87 }, { v: 86 }, { v: 88 }, { v: 87 }, { v: 89 }, { v: 91 }
]

export default function ModelInsights() {
  const statCards = [
    {
      label: 'Precision',
      value: '91.0%',
      change: '↑ 4.2% vs last 30 days',
      changeColor: 'text-emerald-600',
      icon: Target,
      iconBg: 'bg-teal-50 text-teal-700',
      strokeColor: '#0D9488',
      fillColor: '#E0F2F1',
    },
    {
      label: 'Recall',
      value: '88.0%',
      change: '↑ 2.6% vs last 30 days',
      changeColor: 'text-emerald-600',
      icon: Shield,
      iconBg: 'bg-emerald-50 text-emerald-700',
      strokeColor: '#16A34A',
      fillColor: '#DCFCE7',
    },
    {
      label: 'F1 Score',
      value: '89.0%',
      change: '↑ 3.1% vs last 30 days',
      changeColor: 'text-emerald-600',
      icon: Zap,
      iconBg: 'bg-amber-50 text-amber-700',
      strokeColor: '#F97316',
      fillColor: '#FFEDD5',
    },
    {
      label: 'Accuracy',
      value: '89.0%',
      change: '↑ 3.5% vs last 30 days',
      changeColor: 'text-emerald-600',
      icon: Target,
      iconBg: 'bg-purple-50 text-purple-700',
      strokeColor: '#A855F7',
      fillColor: '#F3E8FF',
    },
  ]

  const featureBarColors = [
    '#00695C', '#0D9488', '#22C55E', '#65A30D', '#84CC16', '#A3E635', '#475569', '#334155'
  ]

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-1.5">
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Model Insights</h1>
            <Info className="w-4 h-4 text-slate-400" />
          </div>
          <p className="text-xs sm:text-sm font-medium text-slate-500 mt-1">
            Explainability, feature importance, and baseline classification performance
          </p>
        </div>
      </div>

      {/* Model Status Banner */}
      <div className="p-3.5 bg-amber-50 border border-amber-200 rounded-xl flex flex-wrap items-center justify-between gap-3 text-xs text-amber-900 shadow-2xs">
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-amber-600 animate-pulse shrink-0" />
          <span className="font-bold">MODEL STATUS: Experimental Candidate (xgb_v2_0.joblib)</span>
          <span className="text-amber-700 hidden lg:inline">• Pipeline mechanics validated | Real-world FIRMS evaluation pending multi-year historical dataset completion</span>
        </div>
        <span className="px-2.5 py-1 rounded-lg bg-amber-200/80 font-mono text-[11px] font-bold text-amber-900 shrink-0">
          EXPERIMENTAL CANDIDATE
        </span>
      </div>

      {/* 4 Top KPI Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((s, idx) => {
          const Icon = s.icon
          return (
            <div key={idx} className="card p-4 flex flex-col justify-between hover:border-slate-300 transition-all overflow-hidden">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${s.iconBg}`}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="text-xs font-semibold text-slate-500">{s.label}</div>
                    <div className="text-2xl font-extrabold text-slate-900 tracking-tight mt-0.5">{s.value}</div>
                    <div className={`text-[11px] font-semibold mt-1 ${s.changeColor}`}>{s.change}</div>
                  </div>
                </div>

                {/* Mini Sparkline Curve */}
                <div className="w-20 h-10 shrink-0">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={sparklineData}>
                      <Area type="monotone" dataKey="v" stroke={s.strokeColor} strokeWidth={2} fill={s.fillColor} />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Middle Grid: Feature Importance & Confusion Matrix */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Left Card: Feature Importance */}
        <div className="card p-5">
          <div className="flex items-center justify-between mb-4">
            <div>
              <div className="flex items-center gap-1.5">
                <h2 className="font-bold text-slate-900 text-sm">Feature Importance</h2>
                <Info className="w-3.5 h-3.5 text-slate-400" />
              </div>
              <p className="text-xs text-slate-500 font-medium mt-0.5">Relative contribution of each feature to classification decisions</p>
            </div>
            <div className="flex items-center gap-1 text-xs font-semibold text-slate-600 bg-slate-100 px-2.5 py-1 rounded-lg border border-slate-200">
              <span>Top 8 Features</span>
              <ChevronDown className="w-3 h-3 text-slate-400" />
            </div>
          </div>

          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={featureImportance} layout="vertical" margin={{ top: 0, right: 30, left: 60, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" horizontal={false} />
                <XAxis type="number" domain={[0, 1.0]} tick={{ fontSize: 10, fill: '#64748B' }} stroke="#CBD5E1" label={{ value: 'Importance Score', position: 'bottom', offset: 0, fontSize: 10, fill: '#64748B' }} />
                <YAxis type="category" dataKey="feature" tick={{ fontSize: 10, fill: '#334155', fontWeight: 600 }} stroke="#CBD5E1" width={140} />
                <Tooltip />
                <Bar dataKey="value" radius={[0, 6, 6, 0]} barSize={16}>
                  {featureImportance.map((_, i) => (
                    <Cell key={i} fill={featureBarColors[i % featureBarColors.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Right Card: Confusion Matrix */}
        <div className="card p-5">
          <div className="flex items-center justify-between mb-4">
            <div>
              <div className="flex items-center gap-1.5">
                <h2 className="font-bold text-slate-900 text-sm">Confusion Matrix</h2>
                <Info className="w-3.5 h-3.5 text-slate-400" />
              </div>
              <p className="text-xs text-slate-500 font-medium mt-0.5">Classification results vs ground truth (last 30 days)</p>
            </div>
            <div className="flex items-center gap-1 text-xs font-semibold text-slate-600 bg-slate-100 px-2.5 py-1 rounded-lg border border-slate-200">
              <span>All Classifications</span>
              <ChevronDown className="w-3 h-3 text-slate-400" />
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-center text-xs border-collapse">
              <thead>
                <tr>
                  <th className="p-2"></th>
                  {confusionMatrixData.labels.map((l) => (
                    <th key={l} className="p-2 font-bold text-slate-700 text-center">{l}</th>
                  ))}
                  <th className="p-2 font-bold text-slate-400">Total (Actual)</th>
                </tr>
              </thead>
              <tbody>
                {confusionMatrixData.matrix.map((row, i) => {
                  const diagonalColors = ['bg-rose-200 text-rose-900 font-bold', 'bg-orange-200 text-orange-900 font-bold', 'bg-emerald-200 text-emerald-900 font-bold', 'bg-purple-200 text-purple-900 font-bold', 'bg-slate-300 text-slate-900 font-bold']
                  return (
                    <tr key={i}>
                      <td className="p-2 font-bold text-slate-700 text-right">{confusionMatrixData.labels[i]}</td>
                      {row.map((cell, j) => {
                        const isDiagonal = i === j
                        return (
                          <td key={j} className="p-1">
                            <div className={`py-2 px-1 rounded-lg text-xs font-semibold ${isDiagonal ? diagonalColors[i] : 'bg-slate-100 text-slate-700'}`}>
                              {cell}
                            </div>
                          </td>
                        )
                      })}
                      <td className="p-2 font-semibold text-slate-500">{confusionMatrixData.totalsActual[i]}</td>
                    </tr>
                  )
                })}
                <tr className="border-t border-slate-200">
                  <td className="p-2 font-bold text-slate-400 text-right">Total (Predicted)</td>
                  {confusionMatrixData.totalsPredicted.map((tot, idx) => (
                    <td key={idx} className="p-2 font-bold text-slate-600">{tot}</td>
                  ))}
                  <td className="p-2 font-extrabold text-slate-900">906</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div className="flex flex-wrap items-center justify-between gap-2 mt-4 pt-3 border-t border-slate-100 text-[11px] font-medium text-slate-500">
            <div className="flex items-center gap-4">
              <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-emerald-500" /> Correct (Diagonal)</span>
              <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-slate-300" /> Misclassified (Off-Diagonal)</span>
            </div>
            <span>Rows = Actual · Cols = Predicted</span>
          </div>
        </div>
      </div>

      {/* Bottom Section: Physics-Based Callout + 4 Benefits */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Left Callout (7 cols) */}
        <div className="lg:col-span-7 card p-5 flex items-start gap-4 bg-slate-50/50">
          <div className="w-12 h-12 rounded-2xl bg-teal-50 text-teal-700 flex items-center justify-center shrink-0 border border-teal-100 shadow-2xs">
            <Brain className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <h2 className="font-bold text-slate-900 text-sm">Why physics-based classification, not deep learning</h2>
              <Info className="w-3.5 h-3.5 text-slate-400" />
            </div>
            <p className="text-xs text-slate-600 font-medium leading-relaxed mt-2">
              AGNIDRISHTI uses physics-based thresholds on fire radiative power, brightness temperature deltas, and persistence patterns rather than a black-box neural network. This means every escalation can be traced to a specific measurable deviation from a known baseline — a requirement for government and defense review.
            </p>
            <p className="text-xs text-slate-500 font-medium leading-relaxed mt-1.5">
              The trade-off is a modest recall ceiling on novel source types, which the Unknown class absorbs honestly rather than guessing.
            </p>
          </div>
        </div>

        {/* Right 4 Benefits Cards Grid (5 cols) */}
        <div className="lg:col-span-5 grid grid-cols-2 gap-3">
          <div className="card p-3.5 flex flex-col justify-between">
            <CheckCircle2 className="w-4 h-4 text-teal-600 mb-2" />
            <div>
              <div className="font-bold text-xs text-slate-900">Transparent</div>
              <div className="text-[11px] text-slate-500 font-medium mt-0.5">Rules are explainable and auditable</div>
            </div>
          </div>

          <div className="card p-3.5 flex flex-col justify-between">
            <FileCheck className="w-4 h-4 text-amber-600 mb-2" />
            <div>
              <div className="font-bold text-xs text-slate-900">Auditable</div>
              <div className="text-[11px] text-slate-500 font-medium mt-0.5">Every decision is traceable</div>
            </div>
          </div>

          <div className="card p-3.5 flex flex-col justify-between">
            <Lock className="w-4 h-4 text-emerald-600 mb-2" />
            <div>
              <div className="font-bold text-xs text-slate-900">Trustworthy</div>
              <div className="text-[11px] text-slate-500 font-medium mt-0.5">Built for defense & government use</div>
            </div>
          </div>

          <div className="card p-3.5 flex flex-col justify-between">
            <TrendingUp className="w-4 h-4 text-purple-600 mb-2" />
            <div>
              <div className="font-bold text-xs text-slate-900">Continuously Improved</div>
              <div className="text-[11px] text-slate-500 font-medium mt-0.5">Thresholds updated from feedback loops</div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-2 pt-2 text-xs text-slate-500 font-medium border-t border-slate-200/80">
        <div className="flex items-center gap-1.5">
          <Clock className="w-3.5 h-3.5 text-slate-400" />
          <span>Last Updated: 24 May 2025, 10:32 AM IST</span>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-slate-600 font-medium">
            Model Version: <span className="font-bold text-slate-800">v2.3.1</span> · Trained on: 12 May 2025 · Next Review: 12 Jun 2025
          </span>
          <button className="text-teal-700 hover:text-teal-900 font-bold inline-flex items-center gap-1">
            <span>View Change Log</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  )
}

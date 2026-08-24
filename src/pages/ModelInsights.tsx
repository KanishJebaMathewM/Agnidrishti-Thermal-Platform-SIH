import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell,
} from 'recharts'
import { featureImportance, confusionMatrix, modelStats, classificationHue } from '../data/mockData'
import { Target, Crosshair, Zap, TrendingUp } from 'lucide-react'

export default function ModelInsights() {
  const statCards = [
    { label: 'Precision', value: modelStats.precision, icon: Target, hue: '#2C8C82' },
    { label: 'Recall', value: modelStats.recall, icon: Crosshair, hue: '#7A9448' },
    { label: 'F1 Score', value: modelStats.f1, icon: Zap, hue: '#D89B2E' },
    { label: 'Accuracy', value: modelStats.accuracy, icon: TrendingUp, hue: '#6C63A6' },
  ]

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-semibold text-ink">Model Insights</h1>
        <p className="text-sm text-muted mt-1">Explainability, feature importance, and classification performance</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {statCards.map((s) => {
          const Icon = s.icon
          return (
            <div key={s.label} className="card p-4">
              <div className="flex items-center gap-2 mb-2">
                <Icon className="w-4 h-4" style={{ color: s.hue }} />
                <span className="text-xs text-muted">{s.label}</span>
              </div>
              <div className="stat-num" style={{ color: s.hue }}>
                {(s.value * 100).toFixed(1)}<span className="text-lg">%</span>
              </div>
            </div>
          )
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Feature importance */}
        <div className="card p-4">
          <h2 className="font-semibold text-ink text-sm mb-1">Feature Importance</h2>
          <p className="text-xs text-muted mb-4">Relative contribution of each feature to classification decisions</p>
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={featureImportance} layout="vertical" margin={{ left: 20, right: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#DFE3DC" horizontal={false} />
              <XAxis type="number" domain={[0, 1]} tick={{ fontSize: 10, fill: '#5B6760' }} />
              <YAxis type="category" dataKey="feature" tick={{ fontSize: 10, fill: '#1F2A24' }} width={160} />
              <Tooltip
                contentStyle={{ backgroundColor: '#F7F8F6', border: '1px solid #DFE3DC', borderRadius: 6, fontSize: 12 }}
                formatter={(v: any) => [(+v).toFixed(2), 'Importance']}
              />
              <Bar dataKey="value" radius={[0, 3, 3, 0]}>
                {featureImportance.map((f, i) => (
                  <Cell key={i} fill={i < 3 ? '#2C8C82' : i < 6 ? '#7A9448' : '#5B6760'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Confusion matrix */}
        <div className="card p-4">
          <h2 className="font-semibold text-ink text-sm mb-1">Confusion Matrix</h2>
          <p className="text-xs text-muted mb-4">Classification results vs ground truth (test set, n=836)</p>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr>
                  <th className="text-xs text-muted p-1.5"></th>
                  {confusionMatrix.labels.map((l) => (
                    <th key={l} className="text-[10px] text-muted p-1.5 text-center font-medium" style={{ writingMode: 'horizontal-tb' }}>
                      {l.split(' ')[0]}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {confusionMatrix.matrix.map((row, i) => {
                  const hue = Object.values(classificationHue)[i]
                  const rowTotal = row.reduce((a, b) => a + b, 0)
                  return (
                    <tr key={i}>
                      <td className="text-[10px] text-muted p-1.5 text-right font-medium whitespace-nowrap">
                        {confusionMatrix.labels[i].split(' ')[0]}
                      </td>
                      {row.map((cell, j) => {
                        const isDiagonal = i === j
                        const intensity = cell / rowTotal
                        return (
                          <td key={j} className="p-1">
                            <div
                              className="w-full h-9 rounded flex items-center justify-center font-mono text-xs"
                              style={{
                                backgroundColor: isDiagonal
                                  ? `${hue.mid}${Math.round(intensity * 80 + 20).toString(16).padStart(2, '0')}`
                                  : `#DFE3DC${Math.round(intensity * 100).toString(16).padStart(2, '0')}`,
                                color: isDiagonal ? '#F7F8F6' : '#1F2A24',
                                fontWeight: isDiagonal ? 600 : 400,
                              }}
                            >
                              {cell}
                            </div>
                          </td>
                        )
                      })}
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
          <div className="flex items-center gap-4 mt-3 text-[10px] text-muted">
            <span>Rows = actual · Cols = predicted</span>
            <span className="flex items-center gap-1">
              <span className="w-3 h-3 rounded bg-teal-mid" /> Correct
            </span>
            <span className="flex items-center gap-1">
              <span className="w-3 h-3 rounded bg-border" /> Misclassified
            </span>
          </div>
        </div>
      </div>

      {/* Explainability narrative */}
      <div className="card p-5">
        <h2 className="font-semibold text-ink text-sm mb-2">Why physics-based classification, not deep learning</h2>
        <p className="text-sm text-muted leading-relaxed max-w-3xl">
          AGNIDRISHTI uses physics-based thresholds on fire radiative power, brightness temperature deltas, and persistence patterns rather than a black-box neural network. This means every escalation can be traced to a specific measurable deviation from a known baseline — a requirement for government and defense review processes where auditability matters as much as accuracy. The trade-off is a modest recall ceiling on novel source types, which the Unknown class absorbs honestly rather than guessing.
        </p>
      </div>
    </div>
  )
}

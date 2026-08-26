import {
  Radio, Map, Layers, TreePine, ShieldCheck, Cloud, Clock, Globe,
  ArrowRight, Maximize2, Target, EyeOff, AlertTriangle, RefreshCw, CheckCircle2,
  Share2
} from 'lucide-react'
import { dataSources } from '../data/mockData'

const iconMap: Record<string, any> = {
  satellite: Share2,
  radio: Radio,
  map: Map,
  layers: Layers,
  tree: TreePine,
}

export default function DataSources() {
  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Data Sources</h1>
          <p className="text-xs sm:text-sm font-medium text-slate-500 mt-1">
            Satellite feeds, infrastructure registries, and land-cover layers powering AGNIDRISHTI
          </p>
        </div>
        <div className="flex items-center gap-2 bg-emerald-50/80 border border-emerald-200 px-3.5 py-2 rounded-2xl shadow-2xs self-start sm:self-auto">
          <ShieldCheck className="w-4 h-4 text-emerald-700" />
          <span className="text-xs font-bold text-emerald-800">On-premise deployment · NTRO sovereign cloud</span>
        </div>
      </div>

      {/* 5 Data Source Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {dataSources.map((src) => {
          const Icon = iconMap[src.icon] || Share2
          const isActive = src.status === 'Active'
          return (
            <div key={src.name} className="card p-5 hover:border-slate-300 transition-all flex flex-col justify-between">
              <div>
                <div className="flex items-start justify-between gap-2 mb-3">
                  <div className="w-10 h-10 rounded-2xl bg-emerald-50 text-emerald-700 flex items-center justify-center border border-emerald-100/80 shrink-0">
                    <Icon className="w-5 h-5" />
                  </div>
                  <span
                    className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold border ${
                      isActive
                        ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                        : 'bg-amber-50 text-amber-800 border-amber-200'
                    }`}
                  >
                    <span className={`w-1.5 h-1.5 rounded-full ${isActive ? 'bg-emerald-600' : 'bg-amber-600'}`} />
                    {src.status}
                  </span>
                </div>
                <h3 className="font-bold text-slate-900 text-sm">{src.name}</h3>
                <p className="text-xs text-slate-500 font-medium mt-1 leading-relaxed">{src.description}</p>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-100 space-y-1.5 text-xs">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1.5 text-slate-400 font-medium">
                    <Clock className="w-3.5 h-3.5" />
                    <span>Last sync</span>
                  </div>
                  <span className="font-semibold text-slate-800 font-mono">{src.lastSync}</span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1.5 text-slate-400 font-medium">
                    <Globe className="w-3.5 h-3.5" />
                    <span>Coverage</span>
                  </div>
                  <span className="font-semibold text-slate-800 text-right max-w-[65%]">{src.coverage}</span>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Cloud-Cover Gaps Card */}
      <div className="card p-5">
        <div className="flex items-center gap-2 mb-1">
          <Cloud className="w-4 h-4 text-teal-600" />
          <h2 className="font-bold text-slate-900 text-sm">Cloud-Cover Gaps — Current Pass</h2>
        </div>
        <p className="text-xs text-slate-500 font-medium mb-4 max-w-3xl">
          Regions with insufficient satellite visibility are shown grayed out. Detections in these zones carry reduced confidence and are held for next-pass confirmation.
        </p>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-center">
          {/* Left 3 Stat Boxes (3 cols) */}
          <div className="lg:col-span-3 space-y-3">
            <div className="panel p-3.5 bg-slate-50 flex items-start gap-3">
              <div className="w-8 h-8 rounded-xl bg-teal-50 text-teal-700 flex items-center justify-center shrink-0 mt-0.5 border border-teal-100">
                <Target className="w-4 h-4" />
              </div>
              <div>
                <div className="text-lg font-extrabold text-slate-900 leading-tight">12.4%</div>
                <div className="text-xs font-semibold text-slate-700 mt-0.5">Area currently under cloud cover</div>
                <div className="text-[11px] font-medium text-slate-400 mt-0.5">– 392K sq km</div>
              </div>
            </div>

            <div className="panel p-3.5 bg-slate-50 flex items-start gap-3">
              <div className="w-8 h-8 rounded-xl bg-teal-50 text-teal-700 flex items-center justify-center shrink-0 mt-0.5 border border-teal-100">
                <EyeOff className="w-4 h-4" />
              </div>
              <div>
                <div className="text-lg font-extrabold text-slate-900 leading-tight">84</div>
                <div className="text-xs font-semibold text-slate-700 mt-0.5">Detections affected</div>
                <div className="text-[11px] font-medium text-slate-400 mt-0.5">Lower confidence</div>
              </div>
            </div>

            <div className="panel p-3.5 bg-slate-50 flex items-start gap-3">
              <div className="w-8 h-8 rounded-xl bg-teal-50 text-teal-700 flex items-center justify-center shrink-0 mt-0.5 border border-teal-100">
                <Clock className="w-4 h-4" />
              </div>
              <div>
                <div className="text-lg font-extrabold text-slate-900 leading-tight">47 min</div>
                <div className="text-xs font-semibold text-slate-700 mt-0.5">Next pass in</div>
                <div className="text-[11px] font-medium text-slate-400 mt-0.5">(Estimated)</div>
              </div>
            </div>
          </div>

          {/* Middle Map Panel (6 cols) */}
          <div className="lg:col-span-6 relative w-full h-[290px] bg-[#E2E8F0] rounded-2xl overflow-hidden border border-slate-200 shadow-2xs">
            <svg viewBox="0 0 500 290" className="w-full h-full" preserveAspectRatio="xMidYMid meet">
              <defs>
                <pattern id="cloudGrid2" width="25" height="25" patternUnits="userSpaceOnUse">
                  <path d="M 25 0 L 0 0 0 25" fill="none" stroke="#CBD5E1" strokeWidth="0.5" opacity="0.6" />
                </pattern>
              </defs>
              <rect width="500" height="290" fill="#DCE6F1" />
              <rect width="500" height="290" fill="url(#cloudGrid2)" />
              {/* India Outline */}
              <path
                d="M 150 30 L 190 25 L 230 35 L 270 45 L 300 55 L 330 70 L 350 95 L 365 125 L 375 155 L 360 185 L 330 205 L 290 210 L 250 205 L 210 190 L 180 165 L 160 135 L 150 95 Z"
                fill="#F8FAFC"
                stroke="#0D9488"
                strokeWidth="1.5"
              />
              {/* Gray Cloud Gap Ellipses */}
              <ellipse cx="270" cy="90" rx="45" ry="28" fill="#475569" opacity="0.3" />
              <ellipse cx="300" cy="160" rx="40" ry="30" fill="#475569" opacity="0.3" />
              <ellipse cx="210" cy="150" rx="30" ry="25" fill="#475569" opacity="0.3" />
              {/* Labels */}
              <text x="270" y="93" textAnchor="middle" fontSize="11" fontWeight="bold" fill="#0F172A" fontFamily="sans-serif">NE gap</text>
              <text x="300" y="163" textAnchor="middle" fontSize="11" fontWeight="bold" fill="#0F172A" fontFamily="sans-serif">E coast gap</text>
              <text x="210" y="153" textAnchor="middle" fontSize="11" fontWeight="bold" fill="#0F172A" fontFamily="sans-serif">W gap</text>
            </svg>

            <div className="absolute top-3 right-3 z-10 flex items-center gap-1.5 bg-white/95 backdrop-blur-md border border-slate-200 p-1 rounded-xl shadow-xs">
              <button className="p-1.5 hover:bg-slate-100 rounded-lg text-slate-700"><Maximize2 className="w-3.5 h-3.5" /></button>
              <button className="p-1.5 hover:bg-slate-100 rounded-lg text-slate-700"><Layers className="w-3.5 h-3.5" /></button>
            </div>
          </div>

          {/* Right Panel Legend & Impact Column (3 cols) */}
          <div className="lg:col-span-3 space-y-4">
            <div>
              <div className="text-[11px] font-bold text-slate-700 uppercase tracking-wider mb-2">Cloud Cover Intensity</div>
              <div className="space-y-1.5 text-xs text-slate-700 font-medium">
                <div className="flex items-center justify-between"><div className="flex items-center gap-2"><span className="w-2.5 h-2.5 rounded-full bg-emerald-400" /><span>&lt; 25%</span></div><span className="text-slate-400 text-[11px]">Low</span></div>
                <div className="flex items-center justify-between"><div className="flex items-center gap-2"><span className="w-2.5 h-2.5 rounded-full bg-amber-400" /><span>25% – 50%</span></div><span className="text-slate-400 text-[11px]">Moderate</span></div>
                <div className="flex items-center justify-between"><div className="flex items-center gap-2"><span className="w-2.5 h-2.5 rounded-full bg-orange-500" /><span>50% – 75%</span></div><span className="text-slate-400 text-[11px]">High</span></div>
                <div className="flex items-center justify-between"><div className="flex items-center gap-2"><span className="w-2.5 h-2.5 rounded-full bg-rose-600" /><span>&gt; 75%</span></div><span className="text-slate-400 text-[11px]">Very High</span></div>
              </div>
            </div>

            <div>
              <div className="text-[11px] font-bold text-slate-700 uppercase tracking-wider mb-2">Impact on Detections</div>
              <div className="space-y-2 text-xs">
                <div className="flex items-start gap-2">
                  <AlertTriangle className="w-3.5 h-3.5 text-teal-600 shrink-0 mt-0.5" />
                  <div><div className="font-bold text-slate-900">Reduced confidence</div><div className="text-[11px] text-slate-500">Detections may be incomplete</div></div>
                </div>
                <div className="flex items-start gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-teal-600 shrink-0 mt-0.5" />
                  <div><div className="font-bold text-slate-900">Held for confirmation</div><div className="text-[11px] text-slate-500">Awaiting next clear pass</div></div>
                </div>
                <div className="flex items-start gap-2">
                  <RefreshCw className="w-3.5 h-3.5 text-teal-600 shrink-0 mt-0.5" />
                  <div><div className="font-bold text-slate-900">Auto-revalidated</div><div className="text-[11px] text-slate-500">Updated automatically on next pass</div></div>
                </div>
              </div>
            </div>

            <button className="w-full btn-secondary justify-center text-xs font-bold">
              <EyeOff className="w-3.5 h-3.5 text-slate-500" />
              <span>View Cloud-Cover History</span>
            </button>
          </div>
        </div>
      </div>

      {/* Footer Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-2 pt-2 text-xs text-slate-500 font-medium border-t border-slate-200/80">
        <div className="flex items-center gap-1.5">
          <Clock className="w-3.5 h-3.5 text-slate-400" />
          <span>All times in IST (UTC +5:30) | Data freshness is continuously monitored</span>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5">
            <span className="text-slate-600 font-bold">Data Sources Online</span>
            <span className="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-[10px] font-extrabold">🟢 5/5 Online</span>
          </div>
          <button className="text-teal-700 hover:text-teal-900 font-bold inline-flex items-center gap-1">
            <span>View Sync Logs</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  )
}

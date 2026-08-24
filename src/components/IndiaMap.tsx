import { useMemo } from 'react'
import { classificationHue, type ThermalEvent } from '../data/mockData'

// Stylized India outline path (simplified cartographic shape)
const INDIA_PATH =
  'M 180 80 L 200 75 L 215 70 L 230 78 L 245 72 L 255 82 L 268 88 L 280 100 L 295 105 L 310 115 L 318 130 L 325 145 L 335 155 L 340 170 L 348 185 L 355 200 L 360 215 L 365 230 L 372 245 L 380 260 L 385 275 L 382 290 L 375 305 L 365 318 L 350 325 L 335 320 L 320 312 L 305 305 L 290 300 L 275 295 L 262 285 L 250 275 L 240 262 L 232 248 L 225 232 L 218 218 L 210 205 L 202 192 L 195 178 L 188 165 L 182 150 L 178 135 L 175 120 L 178 100 Z'

// Map lat/lon to SVG coordinates (approximate India bounds)
function project(lat: number, lon: number): { x: number; y: number } {
  const minLat = 6, maxLat = 37
  const minLon = 68, maxLon = 97
  const x = ((lon - minLon) / (maxLon - minLon)) * 210 + 170
  const y = ((maxLat - lat) / (maxLat - minLat)) * 260 + 60
  return { x, y }
}

interface Props {
  events: ThermalEvent[]
  onMarkerClick?: (id: string) => void
  selectedId?: string
  height?: number
}

export default function IndiaMap({ events, onMarkerClick, selectedId, height = 420 }: Props) {
  const markers = useMemo(
    () =>
      events.map((e) => ({
        ...e,
        pos: project(e.lat, e.lon),
        hue: classificationHue[e.classification],
      })),
    [events],
  )

  return (
    <div className="relative w-full" style={{ height }}>
      <svg viewBox="0 0 560 420" className="w-full h-full" preserveAspectRatio="xMidYMid meet">
        {/* Subtle grid */}
        <defs>
          <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
            <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#DFE3DC" strokeWidth="0.5" opacity="0.5" />
          </pattern>
          <pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
            <line x1="0" y1="0" x2="0" y2="6" stroke="#DFE3DC" strokeWidth="1" />
          </pattern>
        </defs>
        <rect width="560" height="420" fill="url(#grid)" />

        {/* India landmass */}
        <path d={INDIA_PATH} fill="#EDEFEA" stroke="#5B6760" strokeWidth="1.5" strokeLinejoin="round" />
        <path d={INDIA_PATH} fill="url(#hatch)" opacity="0.3" />

        {/* Markers */}
        {markers.map((m) => {
          const isSelected = m.id === selectedId
          const r = m.isAnomaly ? 6 : 4
          return (
            <g key={m.id} onClick={() => onMarkerClick?.(m.id)} className={onMarkerClick ? 'cursor-pointer' : ''}>
              {m.isAnomaly && (
                <circle cx={m.pos.x} cy={m.pos.y} r={r + 4} fill={m.hue.mid} opacity="0.2">
                  <animate attributeName="r" values={`${r + 2};${r + 6};${r + 2}`} dur="2s" repeatCount="indefinite" />
                  <animate attributeName="opacity" values="0.3;0.05;0.3" dur="2s" repeatCount="indefinite" />
                </circle>
              )}
              <circle
                cx={m.pos.x}
                cy={m.pos.y}
                r={r}
                fill={m.hue.mid}
                stroke={isSelected ? '#1F2A24' : m.hue.deep}
                strokeWidth={isSelected ? 2 : 1}
              />
            </g>
          )
        })}

        {/* Compass */}
        <g transform="translate(500, 50)">
          <circle r="18" fill="#F7F8F6" stroke="#DFE3DC" strokeWidth="1" />
          <path d="M 0 -12 L 4 0 L 0 12 L -4 0 Z" fill="#2C8C82" />
          <text x="0" y="-22" textAnchor="middle" fontSize="9" fill="#5B6760" fontFamily="IBM Plex Mono">N</text>
        </g>
      </svg>

      {/* Legend overlay */}
      <div className="absolute bottom-3 left-3 panel px-3 py-2 text-xs">
        <div className="font-semibold text-ink mb-1.5">Classification</div>
        <div className="space-y-1">
          {Object.entries(classificationHue).map(([key, hue]) => (
            <div key={key} className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: hue.mid }} />
              <span className="text-muted">{hue.label}</span>
            </div>
          ))}
        </div>
        <div className="mt-2 pt-2 border-t border-border flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-ember-mid ring-2 ring-ember-light" />
          <span className="text-muted">Pulsing = anomalous</span>
        </div>
      </div>
    </div>
  )
}

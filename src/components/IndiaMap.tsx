import { useEffect, useRef, useState } from 'react'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { Plus, Minus, Target, Maximize2 } from 'lucide-react'
import { classificationHue, type ThermalEvent } from '../data/mockData'

interface Props {
  events: ThermalEvent[]
  onMarkerClick?: (id: string) => void
  selectedId?: string
  height?: number
}

export default function IndiaMap({ events, onMarkerClick, selectedId, height = 480 }: Props) {
  const mapContainerRef = useRef<HTMLDivElement | null>(null)
  const mapInstanceRef = useRef<L.Map | null>(null)
  const layerGroupRef = useRef<L.LayerGroup | null>(null)

  const [layers, setLayers] = useState({
    anomalies: true,
    sources: true,
    industrial: true,
    boundaries: true,
    basemap: true,
  })

  // Initialize Leaflet Map
  useEffect(() => {
    if (!mapContainerRef.current || mapInstanceRef.current) return

    // Center on India
    const map = L.map(mapContainerRef.current, {
      center: [22.5937, 78.9629],
      zoom: 5,
      zoomControl: false,
      attributionControl: false,
    })

    // Standard OpenStreetMap Tile Layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '© OpenStreetMap contributors',
    }).addTo(map)

    const layerGroup = L.layerGroup().addTo(map)
    layerGroupRef.current = layerGroup
    mapInstanceRef.current = map

    return () => {
      map.remove()
      mapInstanceRef.current = null
    }
  }, [])

  // Render Circle Markers for Events on OpenStreetMap
  useEffect(() => {
    if (!mapInstanceRef.current || !layerGroupRef.current) return

    const layerGroup = layerGroupRef.current
    layerGroup.clearLayers()

    events.forEach((e) => {
      if (!layers.anomalies && e.isAnomaly) return

      const hue = classificationHue[e.classification] || classificationHue['Unknown']
      const color = hue.mid
      const radius = e.isAnomaly ? 8 : 6
      const isSelected = e.id === selectedId

      const marker = L.circleMarker([e.lat, e.lon], {
        radius,
        fillColor: color,
        color: isSelected ? '#0F172A' : '#FFFFFF',
        weight: isSelected ? 3 : 1.5,
        opacity: 1,
        fillOpacity: 0.85,
      })

      // Popup Content
      marker.bindPopup(`
        <div style="font-family: Inter, sans-serif; padding: 4px;">
          <div style="font-size: 10px; font-weight: 700; color: ${hue.deep}; background-color: ${hue.light}; padding: 2px 6px; border-radius: 4px; display: inline-block;">
            ${e.classification}
          </div>
          <div style="font-size: 13px; font-weight: 700; color: #0F172A; margin-top: 4px;">
            ${e.placeName}
          </div>
          <div style="font-size: 11px; color: #64748B; margin-top: 2px;">
            ${e.state} · ${e.lat.toFixed(4)}°N, ${e.lon.toFixed(4)}°E
          </div>
          <div style="font-size: 11px; font-weight: 700; color: #0D9488; margin-top: 4px;">
            Confidence: ${e.confidence}% ${e.isAnomaly ? '<span style="color:#EF4444; font-weight:bold;">(ANOMALOUS)</span>' : ''}
          </div>
        </div>
      `)

      if (onMarkerClick) {
        marker.on('click', () => onMarkerClick(e.id))
      }

      marker.addTo(layerGroup)
    })
  }, [events, layers, selectedId, onMarkerClick])

  // Zoom Handlers
  const handleZoomIn = () => mapInstanceRef.current?.zoomIn()
  const handleZoomOut = () => mapInstanceRef.current?.zoomOut()
  const handleCenter = () => mapInstanceRef.current?.setView([22.5937, 78.9629], 5)

  return (
    <div className="relative w-full rounded-2xl overflow-hidden border border-slate-200/90 shadow-2xs" style={{ height }}>
      {/* Real OpenStreetMap Container */}
      <div ref={mapContainerRef} className="w-full h-full z-0" />

      {/* Header Overlay */}
      <div className="absolute top-3 right-4 z-20 flex items-center gap-3 bg-white/95 backdrop-blur-md px-3 py-1.5 rounded-xl border border-slate-200 text-xs font-semibold text-slate-700 shadow-md">
        <span>{events.length} markers · OpenStreetMap</span>
        <button className="p-1 hover:text-slate-900 transition-colors" aria-label="Expand Map">
          <Maximize2 className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Floating Panel: Map Layers (Top-Left) */}
      <div className="absolute top-4 left-4 z-20 bg-white/95 backdrop-blur-md border border-slate-200 p-3 rounded-2xl shadow-md w-44">
        <div className="text-[11px] font-bold text-slate-700 uppercase tracking-wider mb-2">Map Layers</div>
        <div className="space-y-1.5 text-xs text-slate-700">
          {Object.entries({
            anomalies: 'Thermal Anomalies',
            sources: 'Known Sources',
            industrial: 'Industrial Zones',
            boundaries: 'State Boundaries',
            basemap: 'OSM Tile Feed',
          }).map(([key, label]) => (
            <label key={key} className="flex items-center gap-2 cursor-pointer select-none hover:text-slate-900 transition-colors">
              <input
                type="checkbox"
                checked={layers[key as keyof typeof layers]}
                onChange={(e) => setLayers({ ...layers, [key]: e.target.checked })}
                className="w-3.5 h-3.5 rounded bg-slate-100 border-slate-300 text-teal-600 focus:ring-0"
              />
              <span className="text-[11px] font-medium">{label}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Floating Panel: Classification Legend (Bottom-Left) */}
      <div className="absolute bottom-4 left-4 z-20 bg-white/95 backdrop-blur-md border border-slate-200 p-3 rounded-2xl shadow-md w-48">
        <div className="text-[11px] font-bold text-slate-700 uppercase tracking-wider mb-2">Classification Legend</div>
        <div className="space-y-1.5 text-[11px] text-slate-700">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500" />
            <span>Industrial Incident</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-orange-500" />
            <span>Persistent Flare/Kiln</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
            <span>Agricultural Burn</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-purple-500" />
            <span>Forest Fire</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-slate-400" />
            <span>Unknown</span>
          </div>
        </div>
        <div className="mt-2.5 pt-2 border-t border-slate-200 flex items-center gap-2 text-[10px] text-slate-600">
          <span className="w-2.5 h-2.5 rounded-full bg-rose-500 ring-2 ring-rose-300 animate-pulse" />
          <span className="font-semibold text-rose-700">Pulsing = anomalous</span>
        </div>
      </div>

      {/* Floating Controls: Zoom & Target (Bottom-Right) */}
      <div className="absolute bottom-4 right-4 z-20 flex flex-col gap-1 bg-white/95 backdrop-blur-md border border-slate-200 p-1 rounded-xl shadow-md">
        <button onClick={handleZoomIn} className="p-2 hover:bg-slate-100 rounded-lg text-slate-700 transition-colors" aria-label="Zoom In">
          <Plus className="w-4 h-4" />
        </button>
        <button onClick={handleZoomOut} className="p-2 hover:bg-slate-100 rounded-lg text-slate-700 transition-colors" aria-label="Zoom Out">
          <Minus className="w-4 h-4" />
        </button>
        <div className="h-[1px] bg-slate-200 my-0.5" />
        <button onClick={handleCenter} className="p-2 hover:bg-slate-100 rounded-lg text-slate-700 transition-colors" aria-label="Center Map">
          <Target className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}

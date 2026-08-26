import { useEffect, useRef, useState, useMemo } from 'react'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import {
  Plus, Minus, Target, Maximize2, Layers, Flame, Shield, Factory,
  MapPin, Check, AlertTriangle, RefreshCw, Eye
} from 'lucide-react'
import { classificationHue, type ThermalEvent } from '../data/mockData'

interface Props {
  events: ThermalEvent[]
  onMarkerClick?: (id: string) => void
  selectedId?: string
  height?: number
  loading?: boolean
  error?: string | null
  onRetry?: () => void
}

// Known industrial facilities for Known Sources Layer
const KNOWN_SOURCES = [
  { id: 'src-1', name: 'Jamnagar Refinery Complex', lat: 22.4707, lon: 70.0577, state: 'Gujarat', type: 'Refinery' },
  { id: 'src-2', name: 'NTPC Korba Super Thermal Power', lat: 22.3595, lon: 82.7501, state: 'Chhattisgarh', type: 'Power Plant' },
  { id: 'src-3', name: 'Tata Steel Jamshedpur Works', lat: 22.8046, lon: 86.2029, state: 'Jharkhand', type: 'Steel Mill' },
  { id: 'src-4', name: 'Panipat Refinery (IOCL)', lat: 29.3909, lon: 76.9635, state: 'Haryana', type: 'Refinery' },
  { id: 'src-5', name: 'Rourkela Steel Plant (SAIL)', lat: 22.2254, lon: 84.8636, state: 'Odisha', type: 'Steel Mill' },
  { id: 'src-6', name: 'Mathura Refinery Complex', lat: 27.4924, lon: 77.6737, state: 'Uttar Pradesh', type: 'Refinery' },
]

export default function IndiaMap({
  events,
  onMarkerClick,
  selectedId,
  height = 520,
  loading = false,
  error = null,
  onRetry,
}: Props) {
  const mapContainerRef = useRef<HTMLDivElement | null>(null)
  const mapInstanceRef = useRef<L.Map | null>(null)
  const tileLayerRef = useRef<L.TileLayer | null>(null)
  
  // Layer Groups
  const eventLayerGroupRef = useRef<L.LayerGroup | null>(null)
  const sourceLayerGroupRef = useRef<L.LayerGroup | null>(null)
  const industrialLayerGroupRef = useRef<L.LayerGroup | null>(null)

  // Layer Visibility State
  const [layersOpen, setLayersOpen] = useState(false)
  const [layers, setLayers] = useState({
    anomalies: true,
    sources: true,
    industrial: true,
    basemap: true,
    bhuvanContext: false,
  })

  // 1. Initialize Map on Mount
  useEffect(() => {
    if (!mapContainerRef.current || mapInstanceRef.current) return

    // Center on India (approx geographic center)
    const map = L.map(mapContainerRef.current, {
      center: [22.5937, 78.9629],
      zoom: 5,
      minZoom: 4,
      maxZoom: 18,
      zoomControl: false,
      attributionControl: false,
    })

    // OSM Base Tile Layer
    const tileLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '© OpenStreetMap contributors',
    }).addTo(map)
    tileLayerRef.current = tileLayer

    // Initialize Layer Groups
    eventLayerGroupRef.current = L.layerGroup().addTo(map)
    sourceLayerGroupRef.current = L.layerGroup().addTo(map)
    industrialLayerGroupRef.current = L.layerGroup().addTo(map)

    mapInstanceRef.current = map

    return () => {
      map.remove()
      mapInstanceRef.current = null
    }
  }, [])

  // 2. Base Tile Layer Toggle
  useEffect(() => {
    if (!mapInstanceRef.current || !tileLayerRef.current) return
    if (layers.basemap) {
      if (!mapInstanceRef.current.hasLayer(tileLayerRef.current)) {
        tileLayerRef.current.addTo(mapInstanceRef.current)
      }
    } else {
      if (mapInstanceRef.current.hasLayer(tileLayerRef.current)) {
        mapInstanceRef.current.removeLayer(tileLayerRef.current)
      }
    }
  }, [layers.basemap])

  // 3. Render Known Sources Layer
  useEffect(() => {
    if (!sourceLayerGroupRef.current) return
    const group = sourceLayerGroupRef.current
    group.clearLayers()

    if (!layers.sources) return

    KNOWN_SOURCES.forEach((src) => {
      const marker = L.circleMarker([src.lat, src.lon], {
        radius: 7,
        fillColor: '#00695C',
        color: '#FFFFFF',
        weight: 2,
        opacity: 1,
        fillOpacity: 0.9,
      })

      marker.bindPopup(`
        <div style="font-family: Inter, sans-serif; padding: 4px; min-width: 160px;">
          <div style="font-size: 10px; font-weight: 700; color: #004D40; background-color: #E0F2F1; padding: 2px 6px; border-radius: 4px; display: inline-block;">
            REGISTERED SOURCE · ${src.type.toUpperCase()}
          </div>
          <div style="font-size: 12px; font-weight: 700; color: #0F172A; margin-top: 4px;">
            ${src.name}
          </div>
          <div style="font-size: 11px; color: #64748B; margin-top: 2px;">
            ${src.state} · ${src.lat.toFixed(4)}°N, ${src.lon.toFixed(4)}°E
          </div>
          <div style="font-size: 10px; color: #0D9488; font-weight: 600; margin-top: 4px;">
            Baseline: Verified Continuous Facility
          </div>
        </div>
      `)
      marker.addTo(group)
    })
  }, [layers.sources])

  // 4. Render Industrial Zones Layer
  useEffect(() => {
    if (!industrialLayerGroupRef.current) return
    const group = industrialLayerGroupRef.current
    group.clearLayers()

    if (!layers.industrial) return

    // Industrial cluster highlights
    KNOWN_SOURCES.forEach((src) => {
      const zone = L.circle([src.lat, src.lon], {
        radius: 12000, // 12 km cluster buffer
        color: '#F59E0B',
        fillColor: '#FBBF24',
        fillOpacity: 0.12,
        weight: 1.5,
        dashArray: '4, 4',
      })
      zone.bindTooltip(`Industrial Suppression Buffer (${src.name})`, { sticky: true })
      zone.addTo(group)
    })
  }, [layers.industrial])

  // 5. Render Thermal Event Markers
  useEffect(() => {
    if (!eventLayerGroupRef.current) return
    const group = eventLayerGroupRef.current
    group.clearLayers()

    if (!layers.anomalies) return

    events.forEach((e) => {
      const lat = Number(e.lat ?? (e as any).centroid_lat)
      const lon = Number(e.lon ?? (e as any).centroid_lon)
      if (isNaN(lat) || isNaN(lon)) return

      const hue = classificationHue[e.classification] || classificationHue['Unknown']
      const color = hue.mid
      const isSelected = e.id === selectedId
      const radius = e.isAnomaly ? (isSelected ? 10 : 8) : (isSelected ? 8 : 6)

      // Leaflet expects [latitude, longitude]
      const marker = L.circleMarker([lat, lon], {
        radius,
        fillColor: color,
        color: isSelected ? '#0F172A' : (e.isAnomaly ? '#DC2626' : '#FFFFFF'),
        weight: isSelected ? 3 : (e.isAnomaly ? 2 : 1.5),
        opacity: 1,
        fillOpacity: e.isAnomaly ? 0.95 : 0.85,
        className: e.isAnomaly ? 'leaflet-pulsing-marker' : '',
      })

      // Informative Popup
      marker.bindPopup(`
        <div style="font-family: Inter, sans-serif; padding: 4px; min-width: 180px;">
          <div style="display: flex; align-items: center; justify-content: space-between; gap: 6px;">
            <span style="font-size: 10px; font-weight: 700; color: ${hue.deep}; background-color: ${hue.light}; padding: 2px 6px; border-radius: 4px;">
              ${e.classification}
            </span>
            ${e.isAnomaly ? '<span style="font-size: 9px; font-weight: 800; color: #DC2626; background-color: #FEE2E2; padding: 2px 5px; border-radius: 4px;">ANOMALOUS</span>' : ''}
          </div>
          <div style="font-size: 13px; font-weight: 700; color: #0F172A; margin-top: 5px;">
            ${e.placeName || `${e.state} Event`}
          </div>
          <div style="font-size: 11px; color: #64748B; margin-top: 2px; font-family: monospace;">
            ${lat.toFixed(4)}°N, ${lon.toFixed(4)}°E
          </div>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 4px; margin-top: 6px; font-size: 10px; border-top: 1px solid #E2E8F0; padding-top: 4px;">
            <div><span style="color:#64748B;">FRP:</span> <strong>${e.frp} MW</strong></div>
            <div><span style="color:#64748B;">Conf:</span> <strong>${e.confidence}%</strong></div>
          </div>
          <div style="font-size: 10px; color: #94A3B8; margin-top: 4px;">
            ID: <span style="font-family: monospace;">${e.id}</span>
          </div>
        </div>
      `)

      if (onMarkerClick) {
        marker.on('click', () => onMarkerClick(e.id))
      }

      marker.addTo(group)
    })
  }, [events, layers.anomalies, selectedId, onMarkerClick])

  // Center & Zoom Controls
  const handleZoomIn = () => mapInstanceRef.current?.zoomIn()
  const handleZoomOut = () => mapInstanceRef.current?.zoomOut()
  const handleCenter = () => mapInstanceRef.current?.setView([22.5937, 78.9629], 5)

  return (
    <div className="relative w-full rounded-2xl overflow-hidden border border-slate-200 shadow-sm bg-slate-100" style={{ height }}>
      {/* Real Leaflet Map Container */}
      <div ref={mapContainerRef} className="w-full h-full z-0" />

      {/* Loading Overlay */}
      {loading && (
        <div className="absolute inset-0 z-30 bg-white/70 backdrop-blur-xs flex items-center justify-center">
          <div className="bg-white p-4 rounded-2xl shadow-lg border border-slate-200 flex items-center gap-3">
            <RefreshCw className="w-5 h-5 text-teal-600 animate-spin" />
            <span className="text-xs font-bold text-slate-700">Loading thermal events...</span>
          </div>
        </div>
      )}

      {/* Error Overlay */}
      {error && !loading && (
        <div className="absolute inset-0 z-30 bg-white/80 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white p-5 rounded-2xl shadow-lg border border-rose-200 text-center max-w-sm">
            <AlertTriangle className="w-8 h-8 text-rose-600 mx-auto mb-2" />
            <div className="text-sm font-bold text-slate-900 mb-1">Unable to load map events</div>
            <div className="text-xs text-slate-500 mb-3">{error}</div>
            {onRetry && (
              <button onClick={onRetry} className="btn-secondary text-xs mx-auto">
                <RefreshCw className="w-3.5 h-3.5" />
                <span>Retry Connection</span>
              </button>
            )}
          </div>
        </div>
      )}

      {/* Empty State Badge */}
      {!loading && !error && events.length === 0 && (
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-20 bg-white/90 backdrop-blur-md px-4 py-2 rounded-xl border border-slate-200 shadow-md text-xs font-semibold text-slate-600">
          No events in this area or filter selection
        </div>
      )}

      {/* Top Header Badge */}
      <div className="absolute top-3 right-4 z-20 flex items-center gap-2 bg-white/95 backdrop-blur-md px-3 py-1.5 rounded-xl border border-slate-200 text-xs font-semibold text-slate-700 shadow-sm">
        <span className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <span>{events.length} active events</span>
        </span>
        <span className="text-slate-300">|</span>
        <span className="text-[11px] text-slate-500 font-mono">VIIRS 375m & OpenStreetMap</span>
      </div>

      {/* Modern Layer Control Toggle Button & Panel (Top-Left) */}
      <div className="absolute top-3 left-4 z-20">
        <div className="bg-white/95 backdrop-blur-md border border-slate-200 rounded-2xl shadow-md overflow-hidden transition-all duration-200">
          <div
            onClick={() => setLayersOpen(!layersOpen)}
            className="flex items-center justify-between gap-3 px-3 py-2 cursor-pointer hover:bg-slate-50 select-none"
          >
            <div className="flex items-center gap-2 text-xs font-bold text-slate-800">
              <Layers className="w-4 h-4 text-teal-700" />
              <span>Map Layers</span>
            </div>
            <span className="text-[10px] font-mono text-teal-800 font-bold bg-teal-50 px-1.5 py-0.5 rounded">
              {Object.values(layers).filter(Boolean).length}/5 Active
            </span>
          </div>

          {/* Layer Checkboxes */}
          <div className={`px-3 pb-3 pt-1 border-t border-slate-100 space-y-1.5 ${layersOpen ? 'block' : 'hidden sm:block'}`}>
            <label className="flex items-center justify-between gap-2 text-xs text-slate-700 hover:text-slate-900 cursor-pointer">
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={layers.anomalies}
                  onChange={(e) => setLayers({ ...layers, anomalies: e.target.checked })}
                  className="w-3.5 h-3.5 rounded text-teal-600 focus:ring-0 cursor-pointer"
                />
                <span className="text-[11px] font-medium">Thermal Anomalies</span>
              </div>
              <span className="text-[10px] font-mono text-slate-400">{events.length}</span>
            </label>

            <label className="flex items-center justify-between gap-2 text-xs text-slate-700 hover:text-slate-900 cursor-pointer">
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={layers.sources}
                  onChange={(e) => setLayers({ ...layers, sources: e.target.checked })}
                  className="w-3.5 h-3.5 rounded text-teal-600 focus:ring-0 cursor-pointer"
                />
                <span className="text-[11px] font-medium">Known Sources</span>
              </div>
              <span className="text-[10px] font-mono text-slate-400">{KNOWN_SOURCES.length}</span>
            </label>

            <label className="flex items-center justify-between gap-2 text-xs text-slate-700 hover:text-slate-900 cursor-pointer">
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={layers.industrial}
                  onChange={(e) => setLayers({ ...layers, industrial: e.target.checked })}
                  className="w-3.5 h-3.5 rounded text-teal-600 focus:ring-0 cursor-pointer"
                />
                <span className="text-[11px] font-medium">Industrial Buffers</span>
              </div>
              <span className="text-[10px] font-mono text-slate-400">OSM</span>
            </label>

            <label className="flex items-center justify-between gap-2 text-xs text-slate-700 hover:text-slate-900 cursor-pointer">
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={layers.basemap}
                  onChange={(e) => setLayers({ ...layers, basemap: e.target.checked })}
                  className="w-3.5 h-3.5 rounded text-teal-600 focus:ring-0 cursor-pointer"
                />
                <span className="text-[11px] font-medium">OSM Street Tiles</span>
              </div>
              <span className="text-[10px] font-mono text-slate-400">Base</span>
            </label>

            <label className="flex items-center justify-between gap-2 text-xs text-slate-700 hover:text-slate-900 cursor-pointer pt-1 border-t border-slate-100">
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={layers.bhuvanContext}
                  onChange={(e) => setLayers({ ...layers, bhuvanContext: e.target.checked })}
                  className="w-3.5 h-3.5 rounded text-teal-600 focus:ring-0 cursor-pointer"
                />
                <span className="text-[11px] font-medium">ISRO Bhuvan LULC</span>
              </div>
              <span className="text-[9px] font-bold text-emerald-700 bg-emerald-50 px-1 rounded">LIVE API</span>
            </label>
          </div>
        </div>
      </div>

      {/* Floating Classification Legend (Bottom-Left) */}
      <div className="absolute bottom-3 left-4 z-20 bg-white/95 backdrop-blur-md border border-slate-200 p-3 rounded-2xl shadow-md w-48">
        <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-2">Classification Legend</div>
        <div className="space-y-1.5 text-[11px] text-slate-700">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-[#EF4444] shrink-0" />
            <span className="truncate">Industrial Incident</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-[#F97316] shrink-0" />
            <span className="truncate">Persistent Flare/Kiln</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-[#22C55E] shrink-0" />
            <span className="truncate">Agricultural Burn</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-[#A855F7] shrink-0" />
            <span className="truncate">Forest Fire</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-[#64748B] shrink-0" />
            <span className="truncate">Unknown</span>
          </div>
        </div>
        <div className="mt-2.5 pt-2 border-t border-slate-100 flex items-center gap-2 text-[10px] text-slate-600">
          <span className="w-2.5 h-2.5 rounded-full bg-rose-500 ring-2 ring-rose-300 animate-pulse shrink-0" />
          <span className="font-semibold text-rose-700">Pulsing = Anomalous</span>
        </div>
      </div>

      {/* Floating Zoom & Centering Controls (Bottom-Right) */}
      <div className="absolute bottom-3 right-4 z-20 flex flex-col gap-1 bg-white/95 backdrop-blur-md border border-slate-200 p-1 rounded-xl shadow-md">
        <button
          onClick={handleZoomIn}
          className="p-2 hover:bg-slate-100 rounded-lg text-slate-700 transition-colors"
          title="Zoom In"
          aria-label="Zoom In"
        >
          <Plus className="w-4 h-4" />
        </button>
        <button
          onClick={handleZoomOut}
          className="p-2 hover:bg-slate-100 rounded-lg text-slate-700 transition-colors"
          title="Zoom Out"
          aria-label="Zoom Out"
        >
          <Minus className="w-4 h-4" />
        </button>
        <div className="h-[1px] bg-slate-200 my-0.5" />
        <button
          onClick={handleCenter}
          className="p-2 hover:bg-slate-100 rounded-lg text-teal-700 transition-colors"
          title="Center on India"
          aria-label="Center on India"
        >
          <Target className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}

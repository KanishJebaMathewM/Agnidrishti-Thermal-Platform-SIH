export type Classification =
  | 'Industrial Incident'
  | 'Persistent Flare/Kiln'
  | 'Agricultural Burn'
  | 'Forest Fire'
  | 'Unknown'

export type EventStatus = 'Suppressed' | 'Escalated' | 'Under Review'

export type Agency = 'Fire Services' | 'CPCB' | 'Forest Department' | 'State Aggregation'

export interface ThermalEvent {
  id: string
  classification: Classification
  confidence: number
  lat: number
  lon: number
  placeName: string
  state: string
  timestamp: string
  persistenceNights: number
  status: EventStatus
  frp: number
  brightnessTemp4: number
  brightnessTemp11: number
  flameTemp: number
  burnArea: number
  baseline: number
  current: number
  routedTo: Agency
  isAnomaly: boolean
}

export interface RegistrySource {
  id: string
  name: string
  type: 'Flare' | 'Kiln' | 'Power Plant' | 'Refinery' | 'Steel Mill'
  lat: number
  lon: number
  placeName: string
  state: string
  expectedHours: string
  lastDeviation: string | null
  status: 'Registered' | 'Flagged for Inspection'
}

export interface AlertCard {
  id: string
  classification: Classification
  confidence: number
  placeName: string
  state: string
  timestamp: string
  routedTo: Agency
}

export interface DataSourceInfo {
  name: string
  description: string
  status: 'Active' | 'Delayed'
  lastSync: string
  coverage: string
  icon: string
}

export interface TrendPoint {
  date: string
  industrial: number
  flare: number
  agricultural: number
  forest: number
  unknown: number
}

export interface StateAnomaly {
  state: string
  anomalies: number
  total: number
}

export const classificationHue: Record<
  Classification,
  { light: string; mid: string; deep: string; label: string }
> = {
  'Industrial Incident': { light: '#F7DCD1', mid: '#C25A34', deep: '#7A3117', label: 'Industrial Incident' },
  'Persistent Flare/Kiln': { light: '#FBEACD', mid: '#D89B2E', deep: '#8C5F14', label: 'Persistent Flare/Kiln' },
  'Agricultural Burn': { light: '#E4EAD4', mid: '#7A9448', deep: '#4A5C29', label: 'Agricultural Burn' },
  'Forest Fire': { light: '#E4E1EE', mid: '#6C63A6', deep: '#413A6B', label: 'Forest Fire' },
  'Unknown': { light: '#DFE3DC', mid: '#5B6760', deep: '#1F2A24', label: 'Unknown' },
}

export const agencyColor: Record<Agency, { bg: string; text: string; border: string }> = {
  'Fire Services': { bg: '#F7DCD1', text: '#7A3117', border: '#C25A34' },
  'CPCB': { bg: '#DCEEEC', text: '#155850', border: '#2C8C82' },
  'Forest Department': { bg: '#E4E1EE', text: '#413A6B', border: '#6C63A6' },
  'State Aggregation': { bg: '#FBEACD', text: '#8C5F14', border: '#D89B2E' },
}

const states = [
  'Gujarat', 'Maharashtra', 'Punjab', 'Odisha', 'Chhattisgarh',
  'Madhya Pradesh', 'Telangana', 'West Bengal', 'Assam', 'Tamil Nadu',
  'Rajasthan', 'Karnataka', 'Andhra Pradesh', 'Uttar Pradesh', 'Jharkhand',
]

const placeNames: Record<string, string[]> = {
  Gujarat: ['Jamnagar Refinery Zone', 'Kutch Salt Pans', 'Vadodara Industrial Belt'],
  Maharashtra: ['Nagpur Outskirts', 'Mumbai Refinery Cluster', 'Pune Periphery'],
  Punjab: ['Ludhiana Farmlands', 'Bathinda Agri Belt', 'Firozpur Fields'],
  Odisha: ['Angul Steel Hub', 'Jharsuguda Thermal Belt', 'Talcher Mines'],
  Chhattisgarh: ['Raipur Kiln Cluster', 'Bilaspur Coal Belt', 'Durg Bricks Zone'],
  'Madhya Pradesh': ['Singrauli Mines', 'Gwalior Outskirts', 'Jabalpur Farmlands'],
  Telangana: ['Hyderabad Pharma Zone', 'Warangal Agri Belt', 'Nalgonda Fields'],
  'West Bengal': ['Durgapur Industrial Belt', 'Asansol Coal Zone', 'Haldia Refinery'],
  Assam: ['Tinsukia Forest Fringe', 'Digboi Oil Fields', 'Guwahati Outskirts'],
  'Tamil Nadu': ['Chennai Petrochemical Zone', 'Cuddalore Industrial Belt', 'Madurai Farmlands'],
  Rajasthan: ['Barmer Oil Fields', 'Jodhpur Kiln Cluster', 'Udaipur Forest Fringe'],
  Karnataka: ['Bengaluru Outskirts', 'Bellary Mines', 'Chikkamagaluru Forest'],
  'Andhra Pradesh': ['Visakhapatnam Steel Belt', 'Krishna Delta Farms', 'Kurnool Drylands'],
  'Uttar Pradesh': ['Kanpur Leather Zone', 'Meerut Bricks Belt', 'Varanasi Outskirts'],
  Jharkhand: ['Dhanbad Coal Belt', 'Ranchi Forest Fringe', 'Bokaro Steel Zone'],
}

const classifications: Classification[] = [
  'Industrial Incident',
  'Persistent Flare/Kiln',
  'Agricultural Burn',
  'Forest Fire',
  'Unknown',
]

const agencies: Agency[] = ['Fire Services', 'CPCB', 'Forest Department', 'State Aggregation']

function seededRandom(seed: number): () => number {
  let s = seed
  return () => {
    s = (s * 9301 + 49297) % 233280
    return s / 233280
  }
}

const rand = seededRandom(42)

function pick<T>(arr: T[]): T {
  return arr[Math.floor(rand() * arr.length)]
}

function randInt(min: number, max: number): number {
  return Math.floor(rand() * (max - min + 1)) + min
}

function generateEvents(count: number): ThermalEvent[] {
  const events: ThermalEvent[] = []
  for (let i = 0; i < count; i++) {
    const state = pick(states)
    const place = pick(placeNames[state])
    const classification = pick(classifications)
    const isAnomaly = rand() > 0.82
    const status: EventStatus = isAnomaly
      ? rand() > 0.4 ? 'Escalated' : 'Under Review'
      : rand() > 0.15 ? 'Suppressed' : 'Under Review'

    const lat = randInt(8, 36) + rand() * 0.5
    const lon = randInt(68, 97) + rand() * 0.5
    const confidence = randInt(62, 99)
    const nights = randInt(0, 14)
    const frp = +(rand() * 280 + 5).toFixed(1)
    const bt4 = randInt(300, 360)
    const bt11 = randInt(290, 320)
    const flameTemp = randInt(800, 1400)
    const burnArea = +(rand() * 12 + 0.1).toFixed(2)
    const baseline = +(rand() * 40 + 10).toFixed(1)
    const current = +(baseline + rand() * 60 + (isAnomaly ? 40 : 0)).toFixed(1)

    const agencyMap: Record<Classification, Agency> = {
      'Industrial Incident': 'Fire Services',
      'Persistent Flare/Kiln': 'CPCB',
      'Agricultural Burn': 'State Aggregation',
      'Forest Fire': 'Forest Department',
      'Unknown': pick(agencies),
    }

    const hoursAgo = randInt(0, 48)
    const timestamp = new Date(Date.now() - hoursAgo * 3600 * 1000).toISOString()

    events.push({
      id: `AGD-${2026}-${String(1000 + i).padStart(5, '0')}`,
      classification,
      confidence,
      lat: +lat.toFixed(4),
      lon: +lon.toFixed(4),
      placeName: place,
      state,
      timestamp,
      persistenceNights: nights,
      status,
      frp,
      brightnessTemp4: bt4,
      brightnessTemp11: bt11,
      flameTemp,
      burnArea,
      baseline,
      current,
      routedTo: agencyMap[classification],
      isAnomaly,
    })
  }
  return events.sort((a, b) => +new Date(b.timestamp) - +new Date(a.timestamp))
}

export const allEvents: ThermalEvent[] = generateEvents(120)

export const recentEvents: ThermalEvent[] = allEvents.slice(0, 8)

export const escalatedEvents: ThermalEvent[] = allEvents.filter((e) => e.isAnomaly)

export function getEventById(id: string): ThermalEvent | undefined {
  return allEvents.find((e) => e.id === id)
}

export function generateRegistry(count: number): RegistrySource[] {
  const sources: RegistrySource[] = []
  const types: RegistrySource['type'][] = ['Flare', 'Kiln', 'Power Plant', 'Refinery', 'Steel Mill']
  for (let i = 0; i < count; i++) {
    const state = pick(states)
    const place = pick(placeNames[state])
    const type = pick(types)
    const flagged = rand() > 0.78
    const lat = randInt(8, 36) + rand() * 0.5
    const lon = randInt(68, 97) + rand() * 0.5
    sources.push({
      id: `REG-${String(5000 + i).padStart(5, '0')}`,
      name: `${place} ${type}`,
      type,
      lat: +lat.toFixed(4),
      lon: +lon.toFixed(4),
      placeName: place,
      state,
      expectedHours: type === 'Kiln' ? '06:00–18:00 IST (Seasonal)' : type === 'Flare' ? '24/7 (Continuous)' : '08:00–22:00 IST',
      lastDeviation: flagged ? new Date(Date.now() - randInt(1, 20) * 86400000).toISOString() : null,
      status: flagged ? 'Flagged for Inspection' : 'Registered',
    })
  }
  return sources
}

export const registrySources: RegistrySource[] = generateRegistry(60)

export function generateAlerts(): AlertCard[] {
  return escalatedEvents.slice(0, 24).map((e) => ({
    id: e.id,
    classification: e.classification,
    confidence: e.confidence,
    placeName: e.placeName,
    state: e.state,
    timestamp: e.timestamp,
    routedTo: e.routedTo,
  }))
}

export const alerts: AlertCard[] = generateAlerts()

export const dataSources: DataSourceInfo[] = [
  { name: 'NASA FIRMS', description: 'MODIS & VIIRS active fire detections from Aqua/Terra/SNPP satellites.', status: 'Active', lastSync: '4 min ago', coverage: 'Global, 375m resolution, 4x daily overpass', icon: 'satellite' },
  { name: 'ISRO INSAT-3DR', description: 'Imager thermal channel data via MOSDAC for Indian subcontinent.', status: 'Active', lastSync: '12 min ago', coverage: 'India + Indian Ocean, 4km resolution, 30-min cadence', icon: 'radio' },
  { name: 'OpenStreetMap Overpass', description: 'Industrial infrastructure tags for known-source suppression.', status: 'Active', lastSync: '1 hr ago', coverage: 'Global, OSM industrial/landuse polygons', icon: 'map' },
  { name: 'ISRO Bhuvan', description: 'Land use / land cover and administrative boundary layers.', status: 'Delayed', lastSync: '6 hr ago', coverage: 'India, thematic LULC tiles, quarterly refresh', icon: 'layers' },
  { name: 'Forest Survey of India', description: 'Forest cover and fire-prone zone designations.', status: 'Active', lastSync: '2 hr ago', coverage: 'India forest grid, 1:50,000 scale', icon: 'tree' },
]

export const trendData: TrendPoint[] = (() => {
  const points: TrendPoint[] = []
  const r = seededRandom(99)
  for (let d = 29; d >= 0; d--) {
    const date = new Date(Date.now() - d * 86400000).toISOString().slice(0, 10)
    points.push({
      date,
      industrial: Math.floor(r() * 40 + 20),
      flare: Math.floor(r() * 60 + 30),
      agricultural: Math.floor(r() * 120 + 40),
      forest: Math.floor(r() * 25 + 5),
      unknown: Math.floor(r() * 30 + 10),
    })
  }
  return points
})()

export const stateAnomalyData: StateAnomaly[] = [
  { state: 'Odisha', anomalies: 34, total: 412 },
  { state: 'Chhattisgarh', anomalies: 28, total: 356 },
  { state: 'Punjab', anomalies: 22, total: 289 },
  { state: 'Gujarat', anomalies: 19, total: 301 },
  { state: 'Maharashtra', anomalies: 17, total: 264 },
  { state: 'Jharkhand', anomalies: 15, total: 198 },
  { state: 'Madhya Pradesh', anomalies: 12, total: 231 },
  { state: 'Telangana', anomalies: 9, total: 167 },
  { state: 'West Bengal', anomalies: 8, total: 145 },
  { state: 'Assam', anomalies: 7, total: 112 },
]

export const featureImportance = [
  { feature: 'Fire Radiative Power deviation', value: 0.92 },
  { feature: 'Persistence (consecutive nights)', value: 0.85 },
  { feature: 'Brightness temp delta (4µm − 11µm)', value: 0.78 },
  { feature: 'Proximity to registered source', value: 0.71 },
  { feature: 'Land use / land cover class', value: 0.64 },
  { feature: 'Seasonal burn window match', value: 0.58 },
  { feature: 'Cloud-cover confidence', value: 0.41 },
  { feature: 'Elevation / slope', value: 0.33 },
]

export const confusionMatrix = {
  labels: ['Industrial', 'Flare/Kiln', 'Agri Burn', 'Forest Fire', 'Unknown'],
  matrix: [
    [142, 8, 2, 1, 3],
    [6, 168, 4, 0, 2],
    [3, 5, 201, 7, 9],
    [1, 0, 6, 134, 4],
    [4, 3, 11, 5, 87],
  ],
}

export const modelStats = {
  precision: 0.91,
  recall: 0.88,
  f1: 0.89,
  accuracy: 0.89,
}

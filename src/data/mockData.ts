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
  timeAgo: string
  formattedTime: string
  persistenceText: string
  persistenceSubtext: string
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
  /** Set by the analyst feedback actions in EventDetail once a backend/mock mutation lands. */
  reviewerFeedback?: 'Confirmed' | 'False Alarm' | null
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
  lastDeviationText: string
  lastDeviationPct: string | null
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
  { light: string; mid: string; deep: string; text: string; label: string }
> = {
  'Industrial Incident': { light: '#FEE2E2', mid: '#EF4444', deep: '#DC2626', text: '#991B1B', label: 'Industrial Incident' },
  'Persistent Flare/Kiln': { light: '#FFEDD5', mid: '#F97316', deep: '#EA580C', text: '#C2410C', label: 'Persistent Flare/Kiln' },
  'Agricultural Burn': { light: '#DCFCE7', mid: '#22C55E', deep: '#166534', text: '#15803D', label: 'Agricultural Burn' },
  'Forest Fire': { light: '#F3E8FF', mid: '#A855F7', deep: '#7E22CE', text: '#6B21A8', label: 'Forest Fire' },
  'Unknown': { light: '#F1F5F9', mid: '#64748B', deep: '#334155', text: '#475569', label: 'Unknown' },
}

export const agencyColor: Record<Agency, { bg: string; text: string; border: string }> = {
  'Fire Services': { bg: '#FEE2E2', text: '#991B1B', border: '#FCA5A5' },
  'CPCB': { bg: '#E0F2F1', text: '#00695C', border: '#80CBC4' },
  'Forest Department': { bg: '#F3E8FF', text: '#6B21A8', border: '#D8B4FE' },
  'State Aggregation': { bg: '#FFEDD5', text: '#C2410C', border: '#FDBA74' },
}

export const exactEvents: ThermalEvent[] = [
  {
    id: 'AGD-2026-00001',
    classification: 'Industrial Incident',
    confidence: 75,
    lat: 31.2704,
    lon: 83.0934,
    placeName: 'Meerut Bricks Belt',
    state: 'Uttar Pradesh',
    timestamp: '2026-08-23T03:07:00.000Z',
    timeAgo: '6m ago',
    formattedTime: '23 Aug, 03:07 am',
    persistenceText: '2 nights',
    persistenceSubtext: 'Consistent',
    persistenceNights: 2,
    status: 'Under Review',
    frp: 185.4,
    brightnessTemp4: 345,
    brightnessTemp11: 308,
    flameTemp: 1220,
    burnArea: 3.4,
    baseline: 24.0,
    current: 85.0,
    routedTo: 'Fire Services',
    isAnomaly: true,
  },
  {
    id: 'AGD-2026-00002',
    classification: 'Unknown',
    confidence: 91,
    lat: 15.4049,
    lon: 91.4378,
    placeName: 'Meerut Bricks Belt',
    state: 'Uttar Pradesh',
    timestamp: '2026-08-23T02:07:00.000Z',
    timeAgo: '1h ago',
    formattedTime: '23 Aug, 02:07 am',
    persistenceText: '2 nights',
    persistenceSubtext: 'Consistent',
    persistenceNights: 2,
    status: 'Suppressed',
    frp: 120.2,
    brightnessTemp4: 330,
    brightnessTemp11: 302,
    flameTemp: 980,
    burnArea: 1.8,
    baseline: 30.0,
    current: 42.0,
    routedTo: 'State Aggregation',
    isAnomaly: false,
  },
  {
    id: 'AGD-2026-00003',
    classification: 'Persistent Flare/Kiln',
    confidence: 89,
    lat: 9.2731,
    lon: 90.2165,
    placeName: 'Bathinda Agri Belt',
    state: 'Punjab',
    timestamp: '2026-08-23T02:05:00.000Z',
    timeAgo: '1h ago',
    formattedTime: '23 Aug, 02:05 am',
    persistenceText: '1 night',
    persistenceSubtext: 'Low',
    persistenceNights: 1,
    status: 'Suppressed',
    frp: 95.0,
    brightnessTemp4: 325,
    brightnessTemp11: 300,
    flameTemp: 910,
    burnArea: 1.2,
    baseline: 28.0,
    current: 35.0,
    routedTo: 'CPCB',
    isAnomaly: false,
  },
  {
    id: 'AGD-2026-00004',
    classification: 'Agricultural Burn',
    confidence: 68,
    lat: 33.0130,
    lon: 87.4380,
    placeName: 'Chikkamagaluru Forest',
    state: 'Karnataka',
    timestamp: '2026-08-23T01:07:00.000Z',
    timeAgo: '2h ago',
    formattedTime: '23 Aug, 01:07 am',
    persistenceText: '4 nights',
    persistenceSubtext: 'Moderate',
    persistenceNights: 4,
    status: 'Suppressed',
    frp: 62.1,
    brightnessTemp4: 312,
    brightnessTemp11: 295,
    flameTemp: 840,
    burnArea: 0.9,
    baseline: 20.0,
    current: 28.0,
    routedTo: 'Forest Department',
    isAnomaly: false,
  },
  {
    id: 'AGD-2026-00005',
    classification: 'Agricultural Burn',
    confidence: 76,
    lat: 20.1112,
    lon: 90.2686,
    placeName: 'Angul Steel Hub',
    state: 'Odisha',
    timestamp: '2026-08-23T01:01:00.000Z',
    timeAgo: '2h ago',
    formattedTime: '23 Aug, 01:01 am',
    persistenceText: '6 nights',
    persistenceSubtext: 'High',
    persistenceNights: 6,
    status: 'Escalated',
    frp: 210.5,
    brightnessTemp4: 352,
    brightnessTemp11: 312,
    flameTemp: 1350,
    burnArea: 5.2,
    baseline: 35.0,
    current: 110.0,
    routedTo: 'State Aggregation',
    isAnomaly: true,
  },
  {
    id: 'AGD-2026-00006',
    classification: 'Persistent Flare/Kiln',
    confidence: 70,
    lat: 11.4785,
    lon: 76.0063,
    placeName: 'Bellary Mines',
    state: 'Karnataka',
    timestamp: '2026-08-23T00:48:00.000Z',
    timeAgo: '2h ago',
    formattedTime: '23 Aug, 12:48 am',
    persistenceText: '1 night',
    persistenceSubtext: 'Low',
    persistenceNights: 1,
    status: 'Suppressed',
    frp: 140.0,
    brightnessTemp4: 335,
    brightnessTemp11: 305,
    flameTemp: 1050,
    burnArea: 2.1,
    baseline: 40.0,
    current: 48.0,
    routedTo: 'CPCB',
    isAnomaly: false,
  },
  {
    id: 'AGD-2026-00007',
    classification: 'Persistent Flare/Kiln',
    confidence: 82,
    lat: 30.0685,
    lon: 89.2496,
    placeName: 'Durg Bricks Zone',
    state: 'Chhattisgarh',
    timestamp: '2026-08-23T00:32:00.000Z',
    timeAgo: '3h ago',
    formattedTime: '23 Aug, 12:32 am',
    persistenceText: '12 nights',
    persistenceSubtext: 'High',
    persistenceNights: 12,
    status: 'Suppressed',
    frp: 165.0,
    brightnessTemp4: 340,
    brightnessTemp11: 307,
    flameTemp: 1120,
    burnArea: 2.8,
    baseline: 32.0,
    current: 41.0,
    routedTo: 'CPCB',
    isAnomaly: false,
  },
  {
    id: 'AGD-2026-00008',
    classification: 'Industrial Incident',
    confidence: 95,
    lat: 27.2903,
    lon: 83.2142,
    placeName: 'Cuddalore Industrial Belt',
    state: 'Tamil Nadu',
    timestamp: '2026-08-23T00:10:00.000Z',
    timeAgo: '3h ago',
    formattedTime: '23 Aug, 12:10 am',
    persistenceText: '9 nights',
    persistenceSubtext: 'High',
    persistenceNights: 9,
    status: 'Suppressed',
    frp: 240.0,
    brightnessTemp4: 358,
    brightnessTemp11: 315,
    flameTemp: 1390,
    burnArea: 6.0,
    baseline: 50.0,
    current: 62.0,
    routedTo: 'Fire Services',
    isAnomaly: false,
  },
]

function seededRandom(seed: number): () => number {
  let s = seed
  return () => {
    s = (s * 9301 + 49297) % 233280
    return s / 233280
  }
}

const rand = seededRandom(42)
const states = ['Gujarat', 'Maharashtra', 'Punjab', 'Odisha', 'Chhattisgarh', 'Madhya Pradesh', 'Telangana', 'West Bengal', 'Assam', 'Tamil Nadu', 'Rajasthan', 'Karnataka', 'Uttar Pradesh']
const classificationsList: Classification[] = ['Industrial Incident', 'Persistent Flare/Kiln', 'Agricultural Burn', 'Forest Fire', 'Unknown']
const agenciesList: Agency[] = ['Fire Services', 'CPCB', 'Forest Department', 'State Aggregation']

function generateEvents(count: number): ThermalEvent[] {
  const events: ThermalEvent[] = [...exactEvents]
  for (let i = exactEvents.length; i < count; i++) {
    const state = states[i % states.length]
    const classification = classificationsList[i % classificationsList.length]
    const isAnomaly = i % 4 === 0
    const status: EventStatus = isAnomaly ? (i % 2 === 0 ? 'Escalated' : 'Under Review') : 'Suppressed'
    const confidence = 65 + Math.floor(rand() * 32)
    const lat = +(8 + rand() * 26).toFixed(4)
    const lon = +(68 + rand() * 28).toFixed(4)
    const nights = Math.floor(rand() * 14) + 1
    const hoursAgo = Math.floor(i * 0.4) + 3

    events.push({
      id: `AGD-2026-${String(1000 + i).padStart(5, '0')}`,
      classification,
      confidence,
      lat,
      lon,
      placeName: `${state} Cluster Zone`,
      state,
      timestamp: new Date(Date.now() - hoursAgo * 3600 * 1000).toISOString(),
      timeAgo: `${hoursAgo}h ago`,
      formattedTime: `23 Aug, ${String(hoursAgo % 12).padStart(2, '0')}:15 am`,
      persistenceText: `${nights} ${nights === 1 ? 'night' : 'nights'}`,
      persistenceSubtext: nights > 5 ? 'High' : nights > 2 ? 'Moderate' : 'Low',
      persistenceNights: nights,
      status,
      frp: +(50 + rand() * 200).toFixed(1),
      brightnessTemp4: 310 + Math.floor(rand() * 45),
      brightnessTemp11: 295 + Math.floor(rand() * 20),
      flameTemp: 850 + Math.floor(rand() * 500),
      burnArea: +(0.5 + rand() * 8).toFixed(1),
      baseline: +(15 + rand() * 35).toFixed(1),
      current: +(40 + rand() * 80).toFixed(1),
      routedTo: agenciesList[i % agenciesList.length],
      isAnomaly,
    })
  }
  return events
}

export const allEvents: ThermalEvent[] = generateEvents(120)

export const recentEvents: ThermalEvent[] = [
  exactEvents[0],
  exactEvents[1],
  exactEvents[2],
  exactEvents[3],
  {
    ...exactEvents[4],
    placeName: 'Angul Industrial Area',
    classification: 'Forest Fire',
  },
]

export const escalatedEvents: ThermalEvent[] = allEvents.filter((e) => e.isAnomaly)

export const exactRegistrySources: RegistrySource[] = [
  {
    id: 'REG-05000',
    name: 'Vadodara Industrial Belt Kiln',
    type: 'Kiln',
    lat: 17.3471,
    lon: 92.4889,
    placeName: 'Vadodara Industrial Belt',
    state: 'Gujarat',
    expectedHours: '06:00–18:00 IST (Seasonal)',
    lastDeviationText: 'No deviation',
    lastDeviationPct: null,
    status: 'Registered',
  },
  {
    id: 'REG-05001',
    name: 'Chennai Petrochemical Zone Flare',
    type: 'Flare',
    lat: 18.0839,
    lon: 90.1063,
    placeName: 'Chennai Petrochemical Zone',
    state: 'Tamil Nadu',
    expectedHours: '24/7 (Continuous)',
    lastDeviationText: 'No deviation',
    lastDeviationPct: null,
    status: 'Registered',
  },
  {
    id: 'REG-05002',
    name: 'Guwahati Outskirts Flare',
    type: 'Flare',
    lat: 10.0849,
    lon: 97.0118,
    placeName: 'Guwahati Outskirts',
    state: 'Assam',
    expectedHours: '24/7 (Continuous)',
    lastDeviationText: 'No deviation',
    lastDeviationPct: null,
    status: 'Registered',
  },
  {
    id: 'REG-05003',
    name: 'Pune Periphery Flare',
    type: 'Flare',
    lat: 29.2240,
    lon: 96.0078,
    placeName: 'Pune Periphery',
    state: 'Maharashtra',
    expectedHours: '24/7 (Continuous)',
    lastDeviationText: 'No deviation',
    lastDeviationPct: null,
    status: 'Registered',
  },
  {
    id: 'REG-05004',
    name: 'Chikkamagaluru Forest Flare',
    type: 'Flare',
    lat: 13.2509,
    lon: 75.7711,
    placeName: 'Chikkamagaluru Forest',
    state: 'Karnataka',
    expectedHours: '24/7 (Continuous)',
    lastDeviationText: 'No deviation',
    lastDeviationPct: null,
    status: 'Registered',
  },
  {
    id: 'REG-05021',
    name: 'Firozpur Fields Refinery',
    type: 'Refinery',
    lat: 30.4029,
    lon: 76.0912,
    placeName: 'Firozpur Fields',
    state: 'Punjab',
    expectedHours: '08:00–22:00 IST',
    lastDeviationText: 'No deviation',
    lastDeviationPct: null,
    status: 'Registered',
  },
  {
    id: 'REG-05022',
    name: 'Jamnagar Refinery Zone Power Plant',
    type: 'Power Plant',
    lat: 14.0111,
    lon: 97.4195,
    placeName: 'Jamnagar Refinery Zone',
    state: 'Gujarat',
    expectedHours: '08:00–22:00 IST',
    lastDeviationText: '18 Aug, 10:07 pm',
    lastDeviationPct: '+18%',
    status: 'Flagged for Inspection',
  },
  {
    id: 'REG-05023',
    name: 'Asansol Coal Zone Refinery',
    type: 'Refinery',
    lat: 18.2571,
    lon: 87.0661,
    placeName: 'Asansol Coal Zone',
    state: 'West Bengal',
    expectedHours: '08:00–22:00 IST',
    lastDeviationText: '17 Aug, 10:07 pm',
    lastDeviationPct: '+12%',
    status: 'Flagged for Inspection',
  },
  {
    id: 'REG-05024',
    name: 'Nagpur Outskirts Power Plant',
    type: 'Power Plant',
    lat: 29.2428,
    lon: 68.2022,
    placeName: 'Nagpur Outskirts',
    state: 'Maharashtra',
    expectedHours: '08:00–22:00 IST',
    lastDeviationText: '11 Aug, 10:07 pm',
    lastDeviationPct: '+9%',
    status: 'Flagged for Inspection',
  },
  {
    id: 'REG-05025',
    name: 'Jharsuguda Thermal Belt Kiln',
    type: 'Kiln',
    lat: 24.0931,
    lon: 79.4529,
    placeName: 'Jharsuguda Thermal Belt',
    state: 'Odisha',
    expectedHours: '06:00–18:00 IST (Seasonal)',
    lastDeviationText: '15 Aug, 10:07 pm',
    lastDeviationPct: '+6%',
    status: 'Flagged for Inspection',
  },
]

export function generateRegistry(count: number): RegistrySource[] {
  const sources: RegistrySource[] = [...exactRegistrySources]
  const types: RegistrySource['type'][] = ['Flare', 'Kiln', 'Power Plant', 'Refinery', 'Steel Mill']
  for (let i = exactRegistrySources.length; i < count; i++) {
    const type = types[i % types.length]
    const state = states[i % states.length]
    const flagged = i >= 46
    const lat = +(10 + rand() * 22).toFixed(4)
    const lon = +(70 + rand() * 24).toFixed(4)
    sources.push({
      id: `REG-${String(5000 + i).padStart(5, '0')}`,
      name: `${state} ${type} Unit ${i}`,
      type,
      lat,
      lon,
      placeName: `${state} Industrial Zone`,
      state,
      expectedHours: type === 'Kiln' ? '06:00–18:00 IST (Seasonal)' : type === 'Flare' ? '24/7 (Continuous)' : '08:00–22:00 IST',
      lastDeviationText: flagged ? '10 Aug, 08:30 pm' : 'No deviation',
      lastDeviationPct: flagged ? `+${Math.floor(rand() * 15 + 5)}%` : null,
      status: flagged ? 'Flagged for Inspection' : 'Registered',
    })
  }
  return sources
}

export const registrySources: RegistrySource[] = generateRegistry(60)

export const dataSources: DataSourceInfo[] = [
  { name: 'NASA FIRMS', description: 'MODIS & VIIRS active fire detections from Aqua/Terra/SNPP satellites.', status: 'Active', lastSync: '4 min ago', coverage: 'Global, 375m resolution', icon: 'satellite' },
  { name: 'ISRO INSAT-3DR', description: 'Imager thermal channel data via MOSDAC for Indian subcontinent.', status: 'Active', lastSync: '12 min ago', coverage: 'India + Indian Ocean, 4km', icon: 'radio' },
  { name: 'OpenStreetMap Overpass', description: 'Industrial infrastructure tags for known-source suppression.', status: 'Active', lastSync: '1 hr ago', coverage: 'OSM industrial polygons', icon: 'map' },
  { name: 'ISRO Bhuvan', description: 'Land use / land cover and administrative boundary layers.', status: 'Delayed', lastSync: '6 hr ago', coverage: 'Thematic LULC tiles', icon: 'layers' },
  { name: 'Forest Survey of India', description: 'Forest cover and fire-prone zone designations.', status: 'Active', lastSync: '2 hr ago', coverage: 'India forest grid 1:50,000', icon: 'tree' },
]

export const trendData: TrendPoint[] = (() => {
  const points: TrendPoint[] = []
  const times = ['00:00', '02:00', '04:00', '06:00', '08:00', '10:00', '12:00', '14:00', '16:00', '18:00', '20:00']
  const values = [50, 80, 55, 88, 70, 105, 140, 110, 150, 130, 160]
  times.forEach((t, idx) => {
    points.push({
      date: t,
      industrial: Math.floor(values[idx] * 0.2),
      flare: Math.floor(values[idx] * 0.25),
      agricultural: Math.floor(values[idx] * 0.35),
      forest: Math.floor(values[idx] * 0.1),
      unknown: Math.floor(values[idx] * 0.1),
    })
  })
  return points
})()

export const classificationDistributionData = [
  { name: 'Industrial Incident', value: 21, pct: '17.5%', color: '#EF4444' },
  { name: 'Persistent Flare/Kiln', value: 22, pct: '18.3%', color: '#F97316' },
  { name: 'Agricultural Burn', value: 18, pct: '15.0%', color: '#22C55E' },
  { name: 'Forest Fire', value: 27, pct: '22.5%', color: '#A855F7' },
  { name: 'Unknown', value: 32, pct: '26.7%', color: '#64748B' },
]

export const riskLevelSummaryData = [
  { name: 'High Risk', count: 6, pct: '8%', color: '#EF4444' },
  { name: 'Medium Risk', count: 18, pct: '24%', color: '#F97316' },
  { name: 'Low Risk', count: 31, pct: '41%', color: '#22C55E' },
  { name: 'Informational', count: 65, pct: '27%', color: '#0D9488' },
]

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

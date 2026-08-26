import { fetchApi } from './client'
import { getEvents } from './eventsApi'
import {
  allEvents,
  classificationDistributionData,
  riskLevelSummaryData,
  stateAnomalyData,
  recentEvents,
  trendData,
  type ThermalEvent,
  type TrendPoint,
} from '../data/mockData'

export interface ClassificationDistItem {
  name: string
  value: number
  pct: string
  color: string
}

export interface RiskLevelItem {
  name: string
  count: number
  pct: string
  color: string
}

export interface StateAnomalyItem {
  state: string
  anomalies: number
  total: number
}

export interface DashboardSummary {
  total_events_24h: number
  anomaly_events_24h: number
  critical_events: number
  active_sources: number
  classification_distribution: ClassificationDistItem[]
  risk_level_summary: RiskLevelItem[]
  state_anomaly_data: StateAnomalyItem[]
  recent_events: ThermalEvent[]
}

const CLASS_COLORS: Record<string, string> = {
  'Industrial Incident': '#EF4444',
  'Persistent Flare/Kiln': '#F59E0B',
  'Agricultural Burn': '#10B981',
  'Forest Fire': '#059669',
  Unknown: '#6B7280',
}

const RISK_COLORS: Record<string, string> = {
  'Low Risk': '#10B981',
  'Medium Risk': '#F59E0B',
  'High Risk': '#EF4444',
  Critical: '#DC2626',
}

function normalizeDashboardSummary(raw: any): DashboardSummary {
  const total = raw.total_events_24h ?? 1
  const anomaly = raw.anomaly_events_24h ?? 0
  const critical = raw.critical_events ?? 0
  const sources = raw.active_sources ?? 1

  // 1. Classification distribution array normalization
  let classDist: ClassificationDistItem[] = []
  if (Array.isArray(raw.classification_distribution)) {
    classDist = raw.classification_distribution
  } else if (raw.classification_distribution && typeof raw.classification_distribution === 'object') {
    const totalCount = Object.values(raw.classification_distribution).reduce((a: any, b: any) => Number(a) + Number(b), 0) as number || 1
    classDist = Object.entries(raw.classification_distribution).map(([name, count]) => {
      const val = Number(count)
      const pct = Math.round((val / totalCount) * 100)
      return {
        name,
        value: val,
        pct: `${pct}%`,
        color: CLASS_COLORS[name] || '#6B7280',
      }
    })
  }
  if (classDist.length === 0) classDist = classificationDistributionData

  // 2. Risk level summary array normalization
  let riskSummary: RiskLevelItem[] = []
  if (Array.isArray(raw.risk_level_summary)) {
    riskSummary = raw.risk_level_summary
  } else if (raw.risk_level_summary && typeof raw.risk_level_summary === 'object') {
    const totalCount = Object.values(raw.risk_level_summary).reduce((a: any, b: any) => Number(a) + Number(b), 0) as number || 1
    riskSummary = Object.entries(raw.risk_level_summary).map(([name, count]) => {
      const val = Number(count)
      const pct = Math.round((val / totalCount) * 100)
      return {
        name,
        count: val,
        pct: `${pct}%`,
        color: RISK_COLORS[name] || '#6B7280',
      }
    })
  }
  if (riskSummary.length === 0) riskSummary = riskLevelSummaryData

  // 3. State anomaly data array normalization
  let stateAnom: StateAnomalyItem[] = []
  if (Array.isArray(raw.state_anomaly_data)) {
    stateAnom = raw.state_anomaly_data
  } else if (raw.state_anomaly_data && typeof raw.state_anomaly_data === 'object') {
    stateAnom = Object.entries(raw.state_anomaly_data).map(([state, count]) => ({
      state,
      anomalies: Number(count),
      total: Number(count),
    }))
  }
  if (stateAnom.length === 0) stateAnom = stateAnomalyData

  return {
    total_events_24h: total,
    anomaly_events_24h: anomaly,
    critical_events: critical,
    active_sources: sources,
    classification_distribution: classDist,
    risk_level_summary: riskSummary,
    state_anomaly_data: stateAnom,
    recent_events: Array.isArray(raw.recent_events) ? raw.recent_events : recentEvents,
  }
}

function computeMockSummary(): DashboardSummary {
  return {
    total_events_24h: allEvents.length,
    anomaly_events_24h: allEvents.filter((e) => e.isAnomaly).length,
    critical_events: riskLevelSummaryData.find((r) => r.name === 'High Risk')?.count ?? 0,
    active_sources: allEvents.length,
    classification_distribution: classificationDistributionData,
    risk_level_summary: riskLevelSummaryData,
    state_anomaly_data: stateAnomalyData,
    recent_events: recentEvents,
  }
}

export async function getDashboardSummary(): Promise<DashboardSummary> {
  try {
    const raw = await fetchApi<any>('/dashboard/summary')
    return normalizeDashboardSummary(raw)
  } catch {
    return computeMockSummary()
  }
}

export async function getMapEvents(): Promise<{ events: ThermalEvent[] }> {
  const page = await getEvents({ limit: 200 })
  return { events: page.items }
}

export interface TrendsResponse {
  summary: {
    total_events: number
    total_observations: number
    total_anomalies: number
    avg_daily_events: number
    peak_day: string
    peak_count: number
    data_coverage_pct: number
  }
  yearly: Array<{
    year: string
    events: number
    observations: number
    anomalies: number
  }>
  monthly_2026: Array<{
    month: string
    events: number
    industrial: number
    flare: number
    agri: number
    forest: number
    unknown: number
  }>
  state_anomalies: Array<{
    state: string
    pct: number
  }>
  points: TrendPoint[]
}

export async function getDashboardTrends(): Promise<TrendsResponse> {
  return await fetchApi<TrendsResponse>('/dashboard/trends')
}


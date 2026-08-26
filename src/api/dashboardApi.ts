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

/** Mirrors backend/app/schemas/dashboard_schemas.py::DashboardSummary exactly. */
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
    return await fetchApi<DashboardSummary>('/dashboard/summary')
  } catch {
    return computeMockSummary()
  }
}

/**
 * The real `/dashboard/map` endpoint returns a lean per-event shape
 * (id/lat/lon/classification/severity/confidence/anomaly_flag) that can't
 * populate IndiaMap's popups (placeName, state, frp, etc.), so this sources
 * the map from `/events` instead — same full ThermalEvent shape used
 * everywhere else, capped at the API's max page size for a national map.
 */
export async function getMapEvents(): Promise<{ events: ThermalEvent[] }> {
  const page = await getEvents({ limit: 200 })
  return { events: page.items }
}

export async function getDashboardTrends(): Promise<{ points: TrendPoint[] }> {
  try {
    const res = await fetchApi<{ points: TrendPoint[] }>('/dashboard/trends')
    // The real endpoint exists but isn't implemented yet (always returns an
    // empty list) — fall back to mock data rather than rendering an empty chart.
    return res.points.length > 0 ? res : { points: trendData }
  } catch {
    return { points: trendData }
  }
}

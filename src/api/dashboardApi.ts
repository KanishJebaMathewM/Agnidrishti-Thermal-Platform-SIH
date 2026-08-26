import { fetchApi } from './client'
import { allEvents, riskLevelSummaryData, trendData, type ThermalEvent, type TrendPoint } from '../data/mockData'

export interface DashboardSummary {
  totalDetections: number
  suppressedCount: number
  escalatedCount: number
  pendingCount: number
  highRiskCount: number
}

function computeMockSummary(): DashboardSummary {
  return {
    totalDetections: allEvents.length,
    suppressedCount: allEvents.filter((e) => e.status === 'Suppressed').length,
    escalatedCount: allEvents.filter((e) => e.isAnomaly).length,
    pendingCount: allEvents.filter((e) => e.status === 'Under Review').length,
    highRiskCount: riskLevelSummaryData.find((r) => r.name === 'High Risk')?.count ?? 0,
  }
}

export async function getDashboardSummary(): Promise<DashboardSummary> {
  try {
    return await fetchApi<DashboardSummary>('/dashboard/summary')
  } catch {
    return computeMockSummary()
  }
}

export async function getMapEvents(): Promise<{ events: ThermalEvent[] }> {
  try {
    return await fetchApi<{ events: ThermalEvent[] }>('/dashboard/map')
  } catch {
    return { events: allEvents }
  }
}

export async function getDashboardTrends(): Promise<{ points: TrendPoint[] }> {
  try {
    return await fetchApi<{ points: TrendPoint[] }>('/dashboard/trends')
  } catch {
    return { points: trendData }
  }
}

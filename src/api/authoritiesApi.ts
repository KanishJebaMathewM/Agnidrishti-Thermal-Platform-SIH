import { fetchApi } from './client'
import { agencyColor, type Agency, type Classification } from '../data/mockData'

export interface RoutingResolution {
  agency: Agency
  division: string
  source: 'api' | 'heuristic'
}

// Offline stand-in for the PostGIS jurisdiction-routing lookup: the same
// classification -> agency mapping already used across Alerts.tsx today.
const CLASSIFICATION_AGENCY_FALLBACK: Record<Classification, Agency> = {
  'Industrial Incident': 'Fire Services',
  'Persistent Flare/Kiln': 'CPCB',
  'Agricultural Burn': 'State Aggregation',
  'Forest Fire': 'Forest Department',
  Unknown: 'State Aggregation',
}

export async function getAuthorities(): Promise<Agency[]> {
  try {
    return await fetchApi<Agency[]>('/authorities')
  } catch {
    return Object.keys(agencyColor) as Agency[]
  }
}

export async function resolveRouting(
  lat: number,
  lon: number,
  classification: Classification,
): Promise<RoutingResolution> {
  try {
    return await fetchApi<RoutingResolution>(
      `/authorities/resolve?lat=${lat}&lon=${lon}&classification=${encodeURIComponent(classification)}`,
    )
  } catch {
    return {
      agency: CLASSIFICATION_AGENCY_FALLBACK[classification],
      division: 'Regional Control Room',
      source: 'heuristic',
    }
  }
}

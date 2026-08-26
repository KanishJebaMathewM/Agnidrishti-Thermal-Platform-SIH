import { fetchApi } from './client'
import { agencyColor, type Agency, type Classification } from '../data/mockData'

export interface RoutingResolution {
  agency: Agency
  division: string
  source: 'api' | 'heuristic'
}

/** Mirrors backend/app/schemas/authority_schemas.py::AuthorityDetail. */
interface AuthorityRecord {
  id: string
  state: string
  district: string
  authority_type: string
  department: string
  role: string | null
  official_email: string
  official_phone: string | null
  portal_url: string | null
  active: boolean
}

/** Mirrors backend/app/schemas/authority_schemas.py::RoutingResult. */
interface RoutingResult {
  state: string
  district: string
  routing_profile: string | null
  primary_authority: AuthorityRecord | null
  secondary_authorities: AuthorityRecord[]
}

// The backend's authority_type values (PLANT_EMERGENCY, FIRE_RESPONSE,
// FOREST_RESPONSE, POLLUTION_CONTROL, DISTRICT_EMERGENCY) are richer than
// the UI's 4-bucket Agency concept — this maps one onto the other so the
// approved Alerts.tsx design doesn't need to be rebuilt around raw records.
const AUTHORITY_TYPE_TO_AGENCY: Record<string, Agency> = {
  PLANT_EMERGENCY: 'Fire Services',
  FIRE_RESPONSE: 'Fire Services',
  FOREST_RESPONSE: 'Forest Department',
  POLLUTION_CONTROL: 'CPCB',
  DISTRICT_EMERGENCY: 'State Aggregation',
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
    const records = await fetchApi<AuthorityRecord[]>('/authorities')
    const agencies = new Set<Agency>()
    for (const record of records) {
      const agency = AUTHORITY_TYPE_TO_AGENCY[record.authority_type]
      if (agency) agencies.add(agency)
    }
    return agencies.size > 0 ? Array.from(agencies) : (Object.keys(agencyColor) as Agency[])
  } catch {
    return Object.keys(agencyColor) as Agency[]
  }
}

export async function resolveRouting(
  lat: number,
  lon: number,
  classification: Classification,
  severity?: string,
): Promise<RoutingResolution> {
  try {
    const query = new URLSearchParams({ lat: String(lat), lon: String(lon), classification })
    if (severity) query.set('severity', severity)
    const result = await fetchApi<RoutingResult>(`/authorities/routing/resolve?${query.toString()}`)
    const primary = result.primary_authority
    return {
      agency: primary ? AUTHORITY_TYPE_TO_AGENCY[primary.authority_type] ?? CLASSIFICATION_AGENCY_FALLBACK[classification] : CLASSIFICATION_AGENCY_FALLBACK[classification],
      division: primary?.department ?? 'Regional Control Room',
      source: 'api',
    }
  } catch {
    return {
      agency: CLASSIFICATION_AGENCY_FALLBACK[classification],
      division: 'Regional Control Room',
      source: 'heuristic',
    }
  }
}

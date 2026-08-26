import { fetchApi } from './client'
import { registrySources, type RegistrySource } from '../data/mockData'

/** Mirrors backend/app/schemas/observation_schemas.py::ObservationDetail. */
export interface SourceHistoryEntry {
  id: string
  source_type: string
  source_product: string | null
  satellite: string | null
  timestamp_utc: string
  latitude: number
  longitude: number
  h3_cell: string | null
  frp: number | null
  bright_ti4: number | null
  bright_ti5: number | null
  confidence: string | null
  ingested_at: string
  source_id: string | null
}

interface SourcesPage {
  items: RegistrySource[]
  total: number
  page: number
  pages: number
}

interface SourceHistoryPage {
  items: SourceHistoryEntry[]
  total: number
  page: number
  pages: number
}

export async function getSources(): Promise<RegistrySource[]> {
  try {
    const page = await fetchApi<SourcesPage>('/sources?limit=200')
    return page.items
  } catch {
    return registrySources
  }
}

export async function getSourceById(id: string): Promise<RegistrySource | null> {
  try {
    return await fetchApi<RegistrySource>(`/sources/${id}`)
  } catch {
    return registrySources.find((s) => s.id === id) ?? null
  }
}

export async function getSourceHistory(id: string): Promise<SourceHistoryEntry[]> {
  try {
    const page = await fetchApi<SourceHistoryPage>(`/sources/${id}/history`)
    return page.items
  } catch {
    // No historical observation series exists in mock data yet — an honest
    // empty result rather than a fabricated trend.
    return []
  }
}

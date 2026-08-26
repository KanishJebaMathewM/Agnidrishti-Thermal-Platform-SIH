import { fetchApi } from './client'
import { registrySources, type RegistrySource } from '../data/mockData'

export interface SourceHistoryEntry {
  timestamp: string
  observedValue: number
  expectedValue: number
}

export async function getSources(): Promise<RegistrySource[]> {
  try {
    return await fetchApi<RegistrySource[]>('/sources')
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
    return await fetchApi<SourceHistoryEntry[]>(`/sources/${id}/history`)
  } catch {
    // No historical deviation series exists in mock data yet — an honest
    // empty result rather than a fabricated trend.
    return []
  }
}

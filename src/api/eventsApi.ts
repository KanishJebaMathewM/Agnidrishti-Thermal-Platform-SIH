import { fetchApi } from './client'
import { allEvents, type Classification, type ThermalEvent } from '../data/mockData'

export interface EventFilterParams {
  page?: number
  limit?: number
  state?: string
  classification?: Classification
  status?: ThermalEvent['status']
  anomaly_only?: boolean
}

export interface EventsPage {
  items: ThermalEvent[]
  total: number
  page: number
  pages: number
}

function filterMockEvents(params?: EventFilterParams): ThermalEvent[] {
  return allEvents.filter((e) => {
    if (params?.state && e.state !== params.state) return false
    if (params?.classification && e.classification !== params.classification) return false
    if (params?.status && e.status !== params.status) return false
    if (params?.anomaly_only && !e.isAnomaly) return false
    return true
  })
}

export async function getEvents(params?: EventFilterParams): Promise<EventsPage> {
  const query = new URLSearchParams()
  if (params?.page) query.append('page', params.page.toString())
  if (params?.limit) query.append('limit', params.limit.toString())
  if (params?.state) query.append('state', params.state)
  if (params?.classification) query.append('classification', params.classification)
  if (params?.status) query.append('status', params.status)
  if (params?.anomaly_only) query.append('anomaly_only', 'true')

  try {
    return await fetchApi<EventsPage>(`/events?${query.toString()}`)
  } catch {
    const items = filterMockEvents(params)
    return { items, total: items.length, page: 1, pages: 1 }
  }
}

export async function getEventById(id: string): Promise<ThermalEvent> {
  try {
    return await fetchApi<ThermalEvent>(`/events/${id}`)
  } catch {
    const found = allEvents.find((e) => e.id === id)
    if (!found) throw new Error(`Event ${id} not found`)
    return found
  }
}

/**
 * Mutating actions fall back to updating the in-memory mock array so the demo
 * UI keeps working end-to-end without a live backend. `reviewerFeedback` is
 * the one field added to ThermalEvent to carry this — see src/data/mockData.ts.
 */
function applyMockMutation(id: string, fields: Partial<ThermalEvent>): void {
  const idx = allEvents.findIndex((e) => e.id === id)
  if (idx >= 0) {
    allEvents[idx] = { ...allEvents[idx], ...fields }
  }
}

export async function confirmEvent(id: string, reviewer: string, comment: string) {
  try {
    return await fetchApi(`/events/${id}/confirm`, {
      method: 'POST',
      body: JSON.stringify({ reviewer, comment }),
    })
  } catch {
    applyMockMutation(id, { reviewerFeedback: 'Confirmed' })
    return { ok: true, mode: 'mock' as const }
  }
}

export async function markFalseAlarm(id: string, reviewer: string, comment: string) {
  try {
    return await fetchApi(`/events/${id}/false-alarm`, {
      method: 'POST',
      body: JSON.stringify({ reviewer, comment }),
    })
  } catch {
    applyMockMutation(id, { reviewerFeedback: 'False Alarm' })
    return { ok: true, mode: 'mock' as const }
  }
}

export async function reclassifyEvent(
  id: string,
  newClassification: Classification,
  reviewer: string,
  comment: string,
) {
  try {
    return await fetchApi(`/events/${id}/reclassify`, {
      method: 'POST',
      body: JSON.stringify({ new_classification: newClassification, reviewer, comment }),
    })
  } catch {
    applyMockMutation(id, { classification: newClassification })
    return { ok: true, mode: 'mock' as const }
  }
}

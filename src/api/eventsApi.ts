import { fetchApi } from './client'
import { allEvents, type Classification, type ThermalEvent, type EventStatus, type Agency } from '../data/mockData'

export interface EventFilterParams {
  page?: number
  limit?: number
  state?: string
  classification?: Classification
  status?: EventStatus
  anomaly_only?: boolean
}

export interface EventsPage {
  items: ThermalEvent[]
  total: number
  page: number
  pages: number
}

function normalizeRawEventItem(item: any): ThermalEvent {
  const lat = item.lat ?? item.centroid_lat ?? 28.6139
  const lon = item.lon ?? item.centroid_lon ?? 77.2090
  const state = item.state || 'Delhi'
  const district = item.district || 'New Delhi'
  const frp = item.frp ?? item.max_frp ?? 42.1
  const isAnomaly = Boolean(item.isAnomaly ?? item.anomaly_flag ?? false)
  const confidence = item.confidence ?? (item.classification_confidence ? Math.round(item.classification_confidence * 100) : 58)

  return {
    id: String(item.id),
    classification: (item.classification || 'Unknown') as Classification,
    confidence: typeof confidence === 'number' ? confidence : 58,
    lat: Number(lat),
    lon: Number(lon),
    placeName: item.placeName || `${district}, ${state}`,
    state: state,
    timestamp: item.timestamp || item.first_seen || '2026-08-25T03:15:00Z',
    timeAgo: item.timeAgo || 'Just now',
    formattedTime: item.formattedTime || 'Today, 03:15 UTC',
    persistenceText: item.persistenceText || '1 observation',
    persistenceSubtext: item.persistenceSubtext || 'Single VIIRS Pass',
    persistenceNights: item.persistenceNights ?? 1,
    status: (item.status === 'CONFIRMED' ? 'Escalated' : item.status === 'FALSE_ALARM' ? 'Suppressed' : item.status || 'Under Review') as EventStatus,
    frp: Number(frp),
    brightnessTemp4: item.brightnessTemp4 ?? 365.2,
    brightnessTemp11: item.brightnessTemp11 ?? 305.1,
    flameTemp: item.flameTemp ?? 950,
    burnArea: item.burnArea ?? 0.35,
    baseline: item.baseline ?? 160.0,
    current: Number(frp),
    routedTo: (item.routedTo || 'State Aggregation') as Agency,
    isAnomaly: isAnomaly,
    reviewerFeedback: item.reviewerFeedback || null,
  }
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
    const raw = await fetchApi<any>(`/events?${query.toString()}`)
    const items = Array.isArray(raw.items) ? raw.items.map(normalizeRawEventItem) : []
    return {
      items,
      total: raw.total ?? items.length,
      page: raw.page ?? 1,
      pages: raw.pages ?? 1,
    }
  } catch {
    const items = filterMockEvents(params)
    return { items, total: items.length, page: 1, pages: 1 }
  }
}

export async function getEventById(id: string): Promise<ThermalEvent> {
  try {
    const raw = await fetchApi<any>(`/events/${id}`)
    return normalizeRawEventItem(raw)
  } catch {
    const found = allEvents.find((e) => e.id === id)
    if (!found) throw new Error(`Event ${id} not found`)
    return found
  }
}

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

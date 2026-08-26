import { describe, it, expect, vi, afterEach } from 'vitest'
import { getDashboardSummary, getMapEvents } from '../../src/api/dashboardApi'
import { getSources, getSourceHistory } from '../../src/api/sourcesApi'
import { getAuthorities, resolveRouting } from '../../src/api/authoritiesApi'
import { allEvents, registrySources } from '../../src/data/mockData'

describe('frontend API contracts vs the real backend shapes', () => {
  const originalFetch = global.fetch

  afterEach(() => {
    global.fetch = originalFetch
    vi.restoreAllMocks()
  })

  describe('dashboardApi', () => {
    it('getDashboardSummary matches backend/app/schemas/dashboard_schemas.py::DashboardSummary', async () => {
      const summaryPayload = {
        total_events_24h: 10,
        anomaly_events_24h: 3,
        critical_events: 2,
        active_sources: 5,
        classification_distribution: [{ name: 'Forest Fire', value: 3, pct: '30%', color: '#A855F7' }],
        risk_level_summary: [{ name: 'High Risk', count: 2, pct: '20%', color: '#EF4444' }],
        state_anomaly_data: [{ state: 'Odisha', anomalies: 1, total: 10 }],
        recent_events: [],
      }
      global.fetch = vi.fn().mockResolvedValue({ ok: true, status: 200, statusText: 'OK', json: async () => summaryPayload }) as any

      const result = await getDashboardSummary()
      expect(result).toEqual(summaryPayload)
    })

    it('getDashboardSummary falls back to a shape-compatible mock summary when offline', async () => {
      global.fetch = vi.fn().mockRejectedValue(new Error('offline')) as any
      const result = await getDashboardSummary()
      expect(result.total_events_24h).toBe(allEvents.length)
      expect(Array.isArray(result.classification_distribution)).toBe(true)
      expect(Array.isArray(result.risk_level_summary)).toBe(true)
      expect(Array.isArray(result.state_anomaly_data)).toBe(true)
      expect(Array.isArray(result.recent_events)).toBe(true)
    })

    it('getMapEvents sources from /events (full ThermalEvent shape), not the lean /dashboard/map shape', async () => {
      global.fetch = vi.fn().mockRejectedValue(new Error('offline')) as any
      const result = await getMapEvents()
      // Falls back through eventsApi's own mock fallback, so we get full events.
      expect(result.events.length).toBeGreaterThan(0)
      expect(result.events[0]).toHaveProperty('placeName')
      expect(result.events[0]).toHaveProperty('frp')
    })
  })

  describe('sourcesApi', () => {
    it('getSources unwraps the paginated {items,total,page,pages} response', async () => {
      const items = [registrySources[0]]
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        statusText: 'OK',
        json: async () => ({ items, total: 1, page: 1, pages: 1 }),
      }) as any

      const result = await getSources()
      expect(result).toEqual(items)
    })

    it('getSourceHistory unwraps the paginated ObservationDetail[] response', async () => {
      const historyItem = {
        id: 'obs-1',
        source_type: 'FIRMS_VIIRS',
        source_product: null,
        satellite: 'N',
        timestamp_utc: '2026-08-25T03:15:00Z',
        latitude: 28.6139,
        longitude: 77.209,
        h3_cell: null,
        frp: 42.1,
        bright_ti4: null,
        bright_ti5: null,
        confidence: 'nominal',
        ingested_at: '2026-08-25T03:16:00Z',
        source_id: null,
      }
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        statusText: 'OK',
        json: async () => ({ items: [historyItem], total: 1, page: 1, pages: 1 }),
      }) as any

      const result = await getSourceHistory('some-id')
      expect(result).toEqual([historyItem])
    })

    it('getSourceHistory falls back to an empty (honest) list when offline', async () => {
      global.fetch = vi.fn().mockRejectedValue(new Error('offline')) as any
      const result = await getSourceHistory('some-id')
      expect(result).toEqual([])
    })
  })

  describe('authoritiesApi', () => {
    it('getAuthorities maps real authority_type records onto the 4-bucket Agency type', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        statusText: 'OK',
        json: async () => [
          { id: '1', state: 'Odisha', district: 'X', authority_type: 'FIRE_RESPONSE', department: 'Fire Dept', role: null, official_email: 'a@example.gov.in', official_phone: null, portal_url: null, active: true },
          { id: '2', state: 'Odisha', district: 'X', authority_type: 'POLLUTION_CONTROL', department: 'CPCB', role: null, official_email: 'b@example.gov.in', official_phone: null, portal_url: null, active: true },
        ],
      }) as any

      const result = await getAuthorities()
      expect(result).toContain('Fire Services')
      expect(result).toContain('CPCB')
    })

    it('resolveRouting calls the real /authorities/routing/resolve path and maps RoutingResult correctly', async () => {
      let requestedUrl = ''
      global.fetch = vi.fn().mockImplementation((url: string) => {
        requestedUrl = url
        return Promise.resolve({
          ok: true,
          status: 200,
          statusText: 'OK',
          json: async () => ({
            state: 'Odisha',
            district: 'Angul',
            routing_profile: 'industrial_incident_odisha_rule',
            primary_authority: { id: '1', state: 'Odisha', district: 'Angul', authority_type: 'FIRE_RESPONSE', department: 'Angul Fire Dept', role: null, official_email: 'a@example.gov.in', official_phone: null, portal_url: null, active: true },
            secondary_authorities: [],
          }),
        })
      }) as any

      const result = await resolveRouting(20.84, 85.1, 'Industrial Incident')

      expect(requestedUrl).toContain('/authorities/routing/resolve')
      expect(requestedUrl).toContain('lat=20.84')
      expect(result).toEqual({ agency: 'Fire Services', division: 'Angul Fire Dept', source: 'api' })
    })

    it('resolveRouting falls back to the classification heuristic when offline', async () => {
      global.fetch = vi.fn().mockRejectedValue(new Error('offline')) as any
      const result = await resolveRouting(20.84, 85.1, 'Forest Fire')
      expect(result).toEqual({ agency: 'Forest Department', division: 'Regional Control Room', source: 'heuristic' })
    })
  })
})

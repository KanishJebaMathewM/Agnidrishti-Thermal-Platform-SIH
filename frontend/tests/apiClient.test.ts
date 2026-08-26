import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { fetchApi, pingApi, ApiError } from '../../src/api/client'

describe('fetchApi', () => {
  const originalFetch = global.fetch

  afterEach(() => {
    global.fetch = originalFetch
    vi.restoreAllMocks()
  })

  it('returns parsed JSON on a 200 OK response', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      statusText: 'OK',
      json: async () => ({ hello: 'world' }),
    }) as any

    const result = await fetchApi<{ hello: string }>('/dashboard/summary')
    expect(result).toEqual({ hello: 'world' })
    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/dashboard/summary',
      expect.objectContaining({ headers: expect.objectContaining({ 'Content-Type': 'application/json' }) }),
    )
  })

  it('throws an ApiError on a 500 response instead of returning data', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 500,
      statusText: 'Internal Server Error',
      json: async () => ({}),
    }) as any

    await expect(fetchApi('/dashboard/summary')).rejects.toBeInstanceOf(ApiError)
    await expect(fetchApi('/dashboard/summary')).rejects.toMatchObject({ status: 500 })
  })

  it('propagates network failures (e.g. backend unreachable)', async () => {
    global.fetch = vi.fn().mockRejectedValue(new TypeError('Failed to fetch')) as any
    await expect(fetchApi('/dashboard/summary')).rejects.toThrow('Failed to fetch')
  })

  it('normalizes endpoints without a leading slash', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      statusText: 'OK',
      json: async () => ({}),
    }) as any

    await fetchApi('events')
    expect(global.fetch).toHaveBeenCalledWith('http://localhost:8000/events', expect.anything())
  })
})

describe('pingApi', () => {
  const originalFetch = global.fetch

  afterEach(() => {
    global.fetch = originalFetch
    vi.restoreAllMocks()
  })

  it('returns true when the health endpoint responds ok', async () => {
    global.fetch = vi.fn().mockResolvedValue({ ok: true }) as any
    expect(await pingApi()).toBe(true)
  })

  it('returns false (never throws) when the backend is unreachable', async () => {
    global.fetch = vi.fn().mockRejectedValue(new Error('network down')) as any
    expect(await pingApi()).toBe(false)
  })
})

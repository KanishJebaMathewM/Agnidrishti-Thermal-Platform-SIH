import { describe, it, expect, vi, afterEach } from 'vitest'
import { renderHook, waitFor, act } from '@testing-library/react'
import { useEventsList } from '../../src/hooks/useEventsList'
import { allEvents } from '../../src/data/mockData'

describe('useEventsList', () => {
  const originalFetch = global.fetch

  afterEach(() => {
    global.fetch = originalFetch
    vi.restoreAllMocks()
  })

  it('falls back to mock data when the backend is unreachable', async () => {
    global.fetch = vi.fn().mockRejectedValue(new Error('offline')) as any

    const { result } = renderHook(() => useEventsList())

    await waitFor(() => expect(result.current.loading).toBe(false))
    expect(result.current.events.length).toBe(allEvents.length)
    expect(result.current.error).toBeNull()
  })

  it('re-fetches and narrows results when filter params change', async () => {
    global.fetch = vi.fn().mockRejectedValue(new Error('offline')) as any

    const targetState = allEvents[0].state
    const { result } = renderHook(() => useEventsList())
    await waitFor(() => expect(result.current.loading).toBe(false))

    act(() => {
      result.current.setParams({ state: targetState })
    })

    await waitFor(() => expect(result.current.loading).toBe(false))
    expect(result.current.events.length).toBeGreaterThan(0)
    expect(result.current.events.every((e) => e.state === targetState)).toBe(true)
    expect(result.current.total).toBe(result.current.events.length)
  })

  it('narrows by classification filter', async () => {
    global.fetch = vi.fn().mockRejectedValue(new Error('offline')) as any

    const { result } = renderHook(() => useEventsList({ classification: 'Forest Fire' }))
    await waitFor(() => expect(result.current.loading).toBe(false))

    expect(result.current.events.length).toBeGreaterThan(0)
    expect(result.current.events.every((e) => e.classification === 'Forest Fire')).toBe(true)
  })

  it('reacts when the caller passes a new params object on rerender (e.g. from dropdown state), not just via setParams', async () => {
    global.fetch = vi.fn().mockRejectedValue(new Error('offline')) as any

    // Mirrors how Events.tsx calls this hook: a fresh object literal built
    // from local component state on every render, never touching setParams.
    const { result, rerender } = renderHook(
      ({ classification }: { classification?: 'Forest Fire' | 'Agricultural Burn' }) =>
        useEventsList({ classification }),
      { initialProps: { classification: undefined } },
    )
    await waitFor(() => expect(result.current.loading).toBe(false))
    const unfilteredCount = result.current.events.length

    rerender({ classification: 'Agricultural Burn' })

    await waitFor(() => expect(result.current.loading).toBe(false))
    await waitFor(() => expect(result.current.events.length).toBeLessThan(unfilteredCount))
    expect(result.current.events.every((e) => e.classification === 'Agricultural Burn')).toBe(true)
  })
})

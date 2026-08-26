import { describe, it, expect, vi, afterEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import EventDetail from '../../src/components/EventDetail'
import { allEvents } from '../../src/data/mockData'

describe('EventDetail — analyst feedback actions', () => {
  const originalFetch = global.fetch
  const targetEvent = allEvents[0]

  afterEach(() => {
    global.fetch = originalFetch
    vi.restoreAllMocks()
    // Reset any mock mutation applied to the shared in-memory array by a previous test.
    const idx = allEvents.findIndex((e) => e.id === targetEvent.id)
    if (idx >= 0) allEvents[idx] = { ...allEvents[idx], reviewerFeedback: null, classification: targetEvent.classification }
  })

  it('clicking "Confirmed" calls the backend confirm endpoint', async () => {
    global.fetch = vi.fn().mockRejectedValue(new Error('offline')) as any
    const user = userEvent.setup()

    render(<EventDetail eventId={targetEvent.id} onClose={() => {}} />)

    const confirmButton = await screen.findByRole('button', { name: /^confirmed$/i })
    await user.click(confirmButton)

    await waitFor(() => {
      const calledUrls = (global.fetch as any).mock.calls.map((c: any[]) => String(c[0]))
      expect(calledUrls.some((u: string) => u.includes(`/events/${targetEvent.id}/confirm`))).toBe(true)
    })

    const [, confirmCallOptions] = (global.fetch as any).mock.calls.find((c: any[]) =>
      String(c[0]).includes('/confirm'),
    )
    expect(confirmCallOptions.method).toBe('POST')
  })

  it('optimistically reflects the confirmation in the UI when the backend is unreachable', async () => {
    global.fetch = vi.fn().mockRejectedValue(new Error('offline')) as any
    const user = userEvent.setup()

    render(<EventDetail eventId={targetEvent.id} onClose={() => {}} />)

    const confirmButton = await screen.findByRole('button', { name: /^confirmed$/i })
    await user.click(confirmButton)

    await screen.findByRole('button', { name: /confirmed ✓/i })
  })

  it('disables action buttons while a confirm request is pending', async () => {
    let resolveConfirmFetch: (v: any) => void
    let callCount = 0
    global.fetch = vi.fn().mockImplementation(() => {
      callCount += 1
      if (callCount === 1) {
        // Initial getEventById fetch — reject immediately so it falls back to mock data.
        return Promise.reject(new Error('offline'))
      }
      // The confirm POST — held open so we can assert the pending/disabled state.
      return new Promise((resolve) => {
        resolveConfirmFetch = resolve
      })
    }) as any
    const user = userEvent.setup()

    render(<EventDetail eventId={targetEvent.id} onClose={() => {}} />)

    const confirmButton = await screen.findByRole('button', { name: /^confirmed$/i })
    await user.click(confirmButton)

    expect(confirmButton).toBeDisabled()
    resolveConfirmFetch!({ ok: false, status: 500, statusText: 'err', json: async () => ({}) })
  })
})

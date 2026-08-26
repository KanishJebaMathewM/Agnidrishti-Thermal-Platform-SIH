import { useEffect, useState } from 'react'
import { getEvents, type EventFilterParams } from '../api/eventsApi'
import type { ThermalEvent } from '../data/mockData'

export function useEventsList(initialParams?: EventFilterParams) {
  const [events, setEvents] = useState<ThermalEvent[]>([])
  const [total, setTotal] = useState<number>(0)
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  const [params, setParams] = useState<EventFilterParams>(initialParams || {})

  // useState only reads its initializer once, so a caller passing filters as
  // a fresh object literal on every render (e.g. built from local dropdown
  // state) would otherwise be frozen to whatever it passed on first mount.
  // Re-sync internal params whenever the caller's params actually change.
  const initialParamsKey = JSON.stringify(initialParams || {})
  useEffect(() => {
    setParams(initialParams || {})
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialParamsKey])

  useEffect(() => {
    let isMounted = true
    setLoading(true)
    getEvents(params)
      .then((res) => {
        if (isMounted) {
          setEvents(res.items)
          setTotal(res.total)
          setError(null)
        }
      })
      .catch((err) => {
        if (isMounted) setError(err.message)
      })
      .finally(() => {
        if (isMounted) setLoading(false)
      })

    return () => {
      isMounted = false
    }
  }, [JSON.stringify(params)])

  return { events, total, loading, error, params, setParams }
}

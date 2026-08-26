import { useCallback, useEffect, useState } from 'react'
import { getDashboardSummary, getMapEvents, type DashboardSummary } from '../api/dashboardApi'
import type { ThermalEvent } from '../data/mockData'

export function useDashboardData() {
  const [data, setData] = useState<DashboardSummary | null>(null)
  const [mapEvents, setMapEvents] = useState<ThermalEvent[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  const [lastSync, setLastSync] = useState<Date>(new Date())

  const refetch = useCallback(async () => {
    setLoading(true)
    try {
      const [summary, mapRes] = await Promise.all([getDashboardSummary(), getMapEvents()])
      setData(summary)
      setMapEvents(mapRes.events)
      setLastSync(new Date())
      setError(null)
    } catch (err: any) {
      setError(err?.message || 'Failed to fetch dashboard summary')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    refetch()
    const interval = setInterval(refetch, 60000)
    return () => clearInterval(interval)
  }, [refetch])

  return { data, mapEvents, loading, error, lastSync, refetch }
}

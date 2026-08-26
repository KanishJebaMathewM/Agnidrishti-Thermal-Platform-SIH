import { useEffect, useState } from 'react'
import { getSources } from '../api/sourcesApi'
import type { RegistrySource } from '../data/mockData'

export function useSourcesList() {
  const [sources, setSources] = useState<RegistrySource[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let isMounted = true
    setLoading(true)
    getSources()
      .then((res) => {
        if (isMounted) {
          setSources(res)
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
  }, [])

  return { sources, loading, error }
}

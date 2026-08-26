import { useCallback, useEffect, useState } from 'react'
import {
  confirmEvent,
  getEventById,
  markFalseAlarm,
  reclassifyEvent,
} from '../api/eventsApi'
import type { Classification, ThermalEvent } from '../data/mockData'

const REVIEWER = 'Operator'

export function useEventDetail(eventId: string | null) {
  const [event, setEvent] = useState<ThermalEvent | null>(null)
  const [loading, setLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)
  const [actionPending, setActionPending] = useState<boolean>(false)

  useEffect(() => {
    if (!eventId) {
      setEvent(null)
      return
    }
    let isMounted = true
    setLoading(true)
    getEventById(eventId)
      .then((res) => {
        if (isMounted) {
          setEvent(res)
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
  }, [eventId])

  const confirm = useCallback(
    async (comment = '') => {
      if (!eventId) return
      setActionPending(true)
      try {
        await confirmEvent(eventId, REVIEWER, comment)
        setEvent((prev) => (prev ? { ...prev, reviewerFeedback: 'Confirmed' } : prev))
      } finally {
        setActionPending(false)
      }
    },
    [eventId],
  )

  const markAsFalseAlarm = useCallback(
    async (comment = '') => {
      if (!eventId) return
      setActionPending(true)
      try {
        await markFalseAlarm(eventId, REVIEWER, comment)
        setEvent((prev) => (prev ? { ...prev, reviewerFeedback: 'False Alarm' } : prev))
      } finally {
        setActionPending(false)
      }
    },
    [eventId],
  )

  const reclassify = useCallback(
    async (newClassification: Classification, comment = '') => {
      if (!eventId) return
      setActionPending(true)
      try {
        await reclassifyEvent(eventId, newClassification, REVIEWER, comment)
        setEvent((prev) => (prev ? { ...prev, classification: newClassification } : prev))
      } finally {
        setActionPending(false)
      }
    },
    [eventId],
  )

  return { event, loading, error, actionPending, confirm, markAsFalseAlarm, reclassify }
}

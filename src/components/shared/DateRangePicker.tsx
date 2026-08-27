import React, { useState, useRef, useEffect } from 'react'
import { Calendar as CalendarIcon, ChevronDown, Check, X } from 'lucide-react'

export interface DateRangePickerProps {
  startDate: string
  endDate: string
  onChange: (startDate: string, endDate: string) => void
  className?: string
}

export const DateRangePicker: React.FC<DateRangePickerProps> = ({
  startDate,
  endDate,
  onChange,
  className = '',
}) => {
  const [isOpen, setIsOpen] = useState(false)
  const [tempStart, setTempStart] = useState(startDate)
  const [tempEnd, setTempEnd] = useState(endDate)
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    setTempStart(startDate)
    setTempEnd(endDate)
  }, [startDate, endDate])

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isOpen])

  const formatDateLabel = (isoDate: string) => {
    if (!isoDate) return ''
    try {
      const d = new Date(isoDate)
      return d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })
    } catch {
      return isoDate
    }
  }

  const applyPreset = (daysAgo: number) => {
    const end = new Date(2026, 7, 27) // 27 Aug 2026 (current demo timestamp)
    const start = new Date(end)
    start.setDate(end.getDate() - daysAgo)
    const startStr = start.toISOString().split('T')[0]
    const endStr = end.toISOString().split('T')[0]
    setTempStart(startStr)
    setTempEnd(endStr)
    onChange(startStr, endStr)
    setIsOpen(false)
  }

  const applyYearPreset = (year: number) => {
    const startStr = `${year}-01-01`
    const endStr = year === 2026 ? '2026-08-27' : `${year}-12-31`
    setTempStart(startStr)
    setTempEnd(endStr)
    onChange(startStr, endStr)
    setIsOpen(false)
  }

  const handleApplyCustom = (e: React.FormEvent) => {
    e.preventDefault()
    if (tempStart && tempEnd) {
      if (new Date(tempStart) > new Date(tempEnd)) {
        onChange(tempEnd, tempStart)
      } else {
        onChange(tempStart, tempEnd)
      }
    }
    setIsOpen(false)
  }

  return (
    <div className={`relative inline-block ${className}`} ref={containerRef}>
      {/* Trigger Button */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 bg-white border border-slate-200 hover:border-slate-300 rounded-xl text-xs font-semibold text-slate-700 shadow-2xs transition-all focus:outline-none focus:ring-2 focus:ring-teal-500/20"
      >
        <CalendarIcon className="w-4 h-4 text-teal-600 shrink-0" />
        <span>
          {formatDateLabel(startDate)} — {formatDateLabel(endDate)}
        </span>
        <ChevronDown className={`w-3.5 h-3.5 text-slate-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {/* Popover Card */}
      {isOpen && (
        <div className="absolute right-0 mt-2 z-50 w-80 sm:w-96 bg-white rounded-2xl shadow-xl border border-slate-200 p-4 animate-in fade-in zoom-in-95 duration-100">
          <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-100">
            <div className="flex items-center gap-2">
              <CalendarIcon className="w-4 h-4 text-teal-600" />
              <span className="font-bold text-slate-900 text-xs">Select Date Range</span>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Quick Preset Buttons */}
          <div className="mb-4">
            <label className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-2">
              Quick Presets
            </label>
            <div className="grid grid-cols-2 gap-1.5">
              <button
                type="button"
                onClick={() => applyPreset(7)}
                className="px-2.5 py-1.5 rounded-lg text-xs font-medium text-slate-700 bg-slate-50 hover:bg-teal-50 hover:text-teal-800 border border-slate-200/80 transition-colors text-left"
              >
                Last 7 Days
              </button>
              <button
                type="button"
                onClick={() => applyPreset(30)}
                className="px-2.5 py-1.5 rounded-lg text-xs font-medium text-slate-700 bg-slate-50 hover:bg-teal-50 hover:text-teal-800 border border-slate-200/80 transition-colors text-left"
              >
                Last 30 Days
              </button>
              <button
                type="button"
                onClick={() => applyPreset(90)}
                className="px-2.5 py-1.5 rounded-lg text-xs font-medium text-slate-700 bg-slate-50 hover:bg-teal-50 hover:text-teal-800 border border-slate-200/80 transition-colors text-left"
              >
                Last 90 Days
              </button>
              <button
                type="button"
                onClick={() => applyYearPreset(2026)}
                className="px-2.5 py-1.5 rounded-lg text-xs font-medium text-slate-700 bg-slate-50 hover:bg-teal-50 hover:text-teal-800 border border-slate-200/80 transition-colors text-left"
              >
                2026 Year-to-Date
              </button>
              <button
                type="button"
                onClick={() => applyYearPreset(2025)}
                className="px-2.5 py-1.5 rounded-lg text-xs font-medium text-slate-700 bg-slate-50 hover:bg-teal-50 hover:text-teal-800 border border-slate-200/80 transition-colors text-left"
              >
                Full Year 2025
              </button>
              <button
                type="button"
                onClick={() => {
                  setTempStart('2020-01-01')
                  setTempEnd('2026-08-27')
                  onChange('2020-01-01', '2026-08-27')
                  setIsOpen(false)
                }}
                className="px-2.5 py-1.5 rounded-lg text-xs font-medium text-slate-700 bg-slate-50 hover:bg-teal-50 hover:text-teal-800 border border-slate-200/80 transition-colors text-left"
              >
                All 7-Yr Archive
              </button>
            </div>
          </div>

          {/* Custom Date Range Form */}
          <form onSubmit={handleApplyCustom} className="space-y-3">
            <label className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">
              Custom Calendar Range
            </label>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <span className="text-[10px] font-semibold text-slate-500 block mb-1">Start Date</span>
                <input
                  type="date"
                  value={tempStart}
                  min="2020-01-01"
                  max="2026-12-31"
                  onChange={(e) => setTempStart(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-xs font-semibold text-slate-800 focus:outline-none focus:ring-1 focus:ring-teal-500"
                />
              </div>
              <div>
                <span className="text-[10px] font-semibold text-slate-500 block mb-1">End Date</span>
                <input
                  type="date"
                  value={tempEnd}
                  min="2020-01-01"
                  max="2026-12-31"
                  onChange={(e) => setTempEnd(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-xs font-semibold text-slate-800 focus:outline-none focus:ring-1 focus:ring-teal-500"
                />
              </div>
            </div>

            <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setIsOpen(false)}
                className="px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-600 hover:bg-slate-100 transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-teal-700 hover:bg-teal-800 text-white text-xs font-bold shadow-2xs transition-colors"
              >
                <Check className="w-3.5 h-3.5" />
                <span>Apply Date Range</span>
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  )
}

export default DateRangePicker

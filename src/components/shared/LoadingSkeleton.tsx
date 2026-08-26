interface Props {
  rows?: number
  className?: string
}

export default function LoadingSkeleton({ rows = 3, className = '' }: Props) {
  return (
    <div className={`animate-pulse space-y-2.5 ${className}`} role="status" aria-label="Loading">
      {Array.from({ length: rows }, (_, i) => (
        <div key={i} className="h-4 rounded-lg bg-slate-200/80" style={{ width: `${85 - i * 8}%` }} />
      ))}
    </div>
  )
}

export function KpiCardSkeleton() {
  return (
    <div className="card p-3 flex flex-col justify-between overflow-hidden rounded-xl animate-pulse">
      <div className="flex items-start gap-2.5">
        <div className="w-8 h-8 rounded-lg bg-slate-200/80 shrink-0" />
        <div className="flex-1 space-y-1.5">
          <div className="h-5 w-12 rounded bg-slate-200/80" />
          <div className="h-3 w-24 rounded bg-slate-200/60" />
        </div>
      </div>
    </div>
  )
}

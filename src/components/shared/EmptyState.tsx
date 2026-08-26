import { Inbox, type LucideIcon } from 'lucide-react'

interface Props {
  title?: string
  message?: string
  icon?: LucideIcon
  action?: { label: string; onClick: () => void }
}

export default function EmptyState({
  title = 'No results found',
  message = 'Try adjusting your filters or search terms.',
  icon: Icon = Inbox,
  action,
}: Props) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16 text-center">
      <div className="w-12 h-12 rounded-2xl bg-slate-100 text-slate-400 flex items-center justify-center">
        <Icon className="w-6 h-6" />
      </div>
      <div>
        <div className="font-bold text-slate-800 text-sm">{title}</div>
        <div className="text-xs text-slate-500 mt-1">{message}</div>
      </div>
      {action && (
        <button onClick={action.onClick} className="text-xs font-bold text-teal-700 hover:text-teal-900 mt-1">
          {action.label}
        </button>
      )}
    </div>
  )
}

import React from 'react'

export interface PaginationProps {
  currentPage: number
  totalItems: number
  pageSize: number
  onPageChange: (page: number) => void
  onPageSizeChange?: (size: number) => void
  pageSizeOptions?: number[]
  className?: string
}

export const Pagination: React.FC<PaginationProps> = ({
  currentPage,
  totalItems,
  pageSize,
  onPageChange,
  onPageSizeChange,
  pageSizeOptions = [10, 25, 50],
  className = '',
}) => {
  const totalPages = Math.max(1, Math.ceil(totalItems / pageSize))
  const startItem = totalItems === 0 ? 0 : (currentPage - 1) * pageSize + 1
  const endItem = Math.min(currentPage * pageSize, totalItems)

  const getPageNumbers = () => {
    const pages: (number | string)[] = []
    if (totalPages <= 7) {
      for (let i = 1; i <= totalPages; i++) pages.push(i)
    } else {
      pages.push(1)
      if (currentPage > 3) {
        pages.push('...')
      }
      const start = Math.max(2, currentPage - 1)
      const end = Math.min(totalPages - 1, currentPage + 1)
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      if (currentPage < totalPages - 2) {
        pages.push('...')
      }
      pages.push(totalPages)
    }
    return pages
  }

  const pageNumbers = getPageNumbers()

  return (
    <div
      className={`px-5 py-3.5 border-t border-slate-100 bg-slate-50/50 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-600 font-medium ${className}`}
    >
      <div className="flex items-center gap-3">
        {onPageSizeChange && (
          <>
            <span>Rows per page</span>
            <select
              value={pageSize}
              onChange={(e) => {
                const newSize = Number(e.target.value)
                onPageSizeChange(newSize)
              }}
              className="bg-white border border-slate-200 rounded-lg px-2 py-1 text-xs font-semibold focus:outline-none focus:ring-1 focus:ring-teal-500 cursor-pointer shadow-2xs"
            >
              {pageSizeOptions.map((opt) => (
                <option key={opt} value={opt}>
                  {opt}
                </option>
              ))}
            </select>
          </>
        )}
        <span>
          Showing {startItem} to {endItem} of {totalItems.toLocaleString()} results
        </span>
      </div>

      {/* Page buttons */}
      <div className="flex items-center gap-1">
        {/* First Page */}
        <button
          onClick={() => onPageChange(1)}
          disabled={currentPage === 1}
          title="First Page"
          className="px-2 py-1 rounded-lg border border-slate-200 bg-white hover:bg-slate-100 font-mono disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        >
          &laquo;
        </button>

        {/* Previous Page */}
        <button
          onClick={() => onPageChange(Math.max(1, currentPage - 1))}
          disabled={currentPage === 1}
          title="Previous Page"
          className="px-2.5 py-1 rounded-lg border border-slate-200 bg-white hover:bg-slate-100 font-mono disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        >
          &lt;
        </button>

        {/* Dynamic Pages */}
        {pageNumbers.map((p, idx) => {
          if (p === '...') {
            return (
              <span key={`ellipsis-${idx}`} className="px-1 text-slate-400">
                ...
              </span>
            )
          }
          const pageNum = Number(p)
          const isActive = pageNum === currentPage
          return (
            <button
              key={`page-${pageNum}`}
              onClick={() => onPageChange(pageNum)}
              className={`px-3 py-1 rounded-lg transition-colors font-semibold ${
                isActive
                  ? 'bg-teal-700 text-white font-bold shadow-2xs'
                  : 'border border-slate-200 bg-white hover:bg-slate-100 text-slate-700'
              }`}
            >
              {pageNum}
            </button>
          )
        })}

        {/* Next Page */}
        <button
          onClick={() => onPageChange(Math.min(totalPages, currentPage + 1))}
          disabled={currentPage === totalPages}
          title="Next Page"
          className="px-2.5 py-1 rounded-lg border border-slate-200 bg-white hover:bg-slate-100 font-mono disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        >
          &gt;
        </button>

        {/* Last Page */}
        <button
          onClick={() => onPageChange(totalPages)}
          disabled={currentPage === totalPages}
          title="Last Page"
          className="px-2 py-1 rounded-lg border border-slate-200 bg-white hover:bg-slate-100 font-mono disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        >
          &raquo;
        </button>
      </div>
    </div>
  )
}

export default Pagination

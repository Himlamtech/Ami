import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { ChevronLeft, ChevronRight } from 'lucide-react'

interface Column<T> {
    key: string
    header: string
    render?: (item: T, index: number) => React.ReactNode
    className?: string
}

interface DataTableProps<T> {
    columns: Column<T>[]
    data: T[]
    keyExtractor: (item: T) => string
    onRowClick?: (item: T) => void
    currentPage?: number
    totalPages?: number
    onPageChange?: (page: number) => void
    emptyMessage?: string
    loading?: boolean
}

export default function DataTable<T>({
    columns,
    data,
    keyExtractor,
    onRowClick,
    currentPage = 1,
    totalPages = 1,
    onPageChange,
    emptyMessage = 'No data available',
    loading = false,
}: DataTableProps<T>) {
    return (
        <div className="w-full">
            <div className="overflow-x-auto">
                <table className="w-full">
                    <thead>
                        <tr className="border-b bg-neutral-50">
                            {columns.map((col) => (
                                <th
                                    key={col.key}
                                    className={cn(
                                        'text-left py-3 px-4 text-sm font-medium text-neutral-500',
                                        col.className
                                    )}
                                >
                                    {col.header}
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {loading ? (
                            <tr>
                                <td colSpan={columns.length} className="py-12 text-center">
                                    <div className="flex items-center justify-center gap-2">
                                        <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                                        <span className="text-neutral-500">Loading...</span>
                                    </div>
                                </td>
                            </tr>
                        ) : data.length === 0 ? (
                            <tr>
                                <td colSpan={columns.length} className="py-12 text-center text-neutral-500">
                                    {emptyMessage}
                                </td>
                            </tr>
                        ) : (
                            data.map((item, index) => (
                                <tr
                                    key={keyExtractor(item)}
                                    className={cn(
                                        'border-b last:border-0 hover:bg-neutral-50 transition-colors',
                                        onRowClick && 'cursor-pointer'
                                    )}
                                    onClick={() => onRowClick?.(item)}
                                >
                                    {columns.map((col) => (
                                        <td key={col.key} className={cn('py-3 px-4', col.className)}>
                                            {col.render
                                                ? col.render(item, index)
                                                : (item as Record<string, unknown>)[col.key]?.toString()}
                                        </td>
                                    ))}
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
                <div className="flex items-center justify-between px-4 py-3 border-t">
                    <p className="text-sm text-neutral-500">
                        Page {currentPage} of {totalPages}
                    </p>
                    <div className="flex items-center gap-2">
                        <Button
                            variant="outline"
                            size="sm"
                            disabled={currentPage <= 1}
                            onClick={() => onPageChange?.(currentPage - 1)}
                        >
                            <ChevronLeft className="w-4 h-4" />
                            Prev
                        </Button>
                        <div className="flex gap-1">
                            {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                                const page = i + 1
                                return (
                                    <Button
                                        key={page}
                                        variant={page === currentPage ? 'default' : 'outline'}
                                        size="sm"
                                        className="w-9"
                                        onClick={() => onPageChange?.(page)}
                                    >
                                        {page}
                                    </Button>
                                )
                            })}
                        </div>
                        <Button
                            variant="outline"
                            size="sm"
                            disabled={currentPage >= totalPages}
                            onClick={() => onPageChange?.(currentPage + 1)}
                        >
                            Next
                            <ChevronRight className="w-4 h-4" />
                        </Button>
                    </div>
                </div>
            )}
        </div>
    )
}

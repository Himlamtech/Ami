import { Search, Filter, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'


interface FilterOption {
    key: string
    label: string
    options?: { value: string; label: string }[]
    type?: 'select' | 'toggle' | 'date'
}

interface ActiveFilter {
    key: string
    value: string
    label: string
}

interface FilterBarProps {
    searchPlaceholder?: string
    searchValue?: string
    onSearchChange?: (value: string) => void
    filters?: FilterOption[]
    activeFilters?: ActiveFilter[]
    onFilterChange?: (key: string, value: string | null) => void
    onClearFilters?: () => void
    resultCount?: number
    className?: string
}

export default function FilterBar({
    searchPlaceholder = 'Search...',
    searchValue = '',
    onSearchChange,
    filters = [],
    activeFilters = [],
    onFilterChange,
    onClearFilters,
    resultCount,
    className,
}: FilterBarProps) {
    return (
        <Card className={className}>
            <CardContent className="p-4">
                <div className="flex flex-wrap items-center gap-4">
                    {/* Search */}
                    <div className="relative flex-1 min-w-[200px]">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
                        <Input
                            placeholder={searchPlaceholder}
                            value={searchValue}
                            onChange={(e) => onSearchChange?.(e.target.value)}
                            className="pl-9"
                        />
                    </div>

                    {/* Filter buttons */}
                    {filters.map((filter) => (
                        <Button key={filter.key} variant="outline" size="sm">
                            <Filter className="w-4 h-4 mr-2" />
                            {filter.label}
                        </Button>
                    ))}

                    {/* Result count */}
                    {resultCount !== undefined && (
                        <span className="text-sm text-neutral-500">
                            Showing {resultCount} items
                        </span>
                    )}
                </div>

                {/* Active filters */}
                {activeFilters.length > 0 && (
                    <div className="flex flex-wrap items-center gap-2 mt-3 pt-3 border-t">
                        <span className="text-sm text-neutral-500">Active filters:</span>
                        {activeFilters.map((filter) => (
                            <Badge
                                key={filter.key}
                                variant="secondary"
                                className="flex items-center gap-1"
                            >
                                {filter.label}
                                <button
                                    onClick={() => onFilterChange?.(filter.key, null)}
                                    className="ml-1 hover:bg-neutral-300 rounded-full p-0.5"
                                >
                                    <X className="w-3 h-3" />
                                </button>
                            </Badge>
                        ))}
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={onClearFilters}
                            className="text-xs text-neutral-500"
                        >
                            Clear all
                        </Button>
                    </div>
                )}
            </CardContent>
        </Card>
    )
}

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { cn } from '@/lib/utils'

interface ChartData {
    label: string
    value: number
    color?: string
}

interface ChartCardProps {
    title: string
    subtitle?: string
    data: ChartData[]
    type?: 'bar' | 'horizontal' | 'donut'
    showLegend?: boolean
    className?: string
}

export default function ChartCard({
    title,
    subtitle,
    data,
    type = 'bar',
    showLegend = true,
    className,
}: ChartCardProps) {
    const maxValue = Math.max(...data.map((d) => d.value))
    const total = data.reduce((acc, d) => acc + d.value, 0)

    const defaultColors = [
        'bg-primary',
        'bg-secondary',
        'bg-success',
        'bg-warning',
        'bg-error',
        'bg-info',
    ]

    return (
        <Card className={className}>
            <CardHeader>
                <CardTitle className="text-base">{title}</CardTitle>
                {subtitle && <p className="text-sm text-neutral-500">{subtitle}</p>}
            </CardHeader>
            <CardContent>
                {type === 'bar' && (
                    <div className="h-48 flex items-end justify-between gap-2">
                        {data.map((item, index) => {
                            const height = maxValue > 0 ? (item.value / maxValue) * 100 : 0
                            return (
                                <div key={item.label} className="flex-1 flex flex-col items-center gap-1">
                                    <div
                                        className={cn(
                                            'w-full rounded-t transition-all hover:opacity-80',
                                            item.color || defaultColors[index % defaultColors.length]
                                        )}
                                        style={{ height: `${height}%`, minHeight: height > 0 ? '4px' : '0' }}
                                        title={`${item.label}: ${item.value}`}
                                    />
                                    <span className="text-xs text-neutral-500 truncate max-w-full">
                                        {item.label}
                                    </span>
                                </div>
                            )
                        })}
                    </div>
                )}

                {type === 'horizontal' && (
                    <div className="space-y-4">
                        {data.map((item, index) => {
                            const percentage = total > 0 ? (item.value / total) * 100 : 0
                            return (
                                <div key={item.label} className="space-y-2">
                                    <div className="flex justify-between text-sm">
                                        <span>{item.label}</span>
                                        <span className="font-medium">
                                            {typeof item.value === 'number' && item.value >= 1
                                                ? `$${item.value.toFixed(2)}`
                                                : item.value}
                                            {' '}({percentage.toFixed(0)}%)
                                        </span>
                                    </div>
                                    <div className="h-2 bg-neutral-100 rounded-full overflow-hidden">
                                        <div
                                            className={cn(
                                                'h-full rounded-full transition-all',
                                                item.color || defaultColors[index % defaultColors.length]
                                            )}
                                            style={{ width: `${percentage}%` }}
                                        />
                                    </div>
                                </div>
                            )
                        })}
                    </div>
                )}

                {type === 'donut' && (
                    <div className="flex items-center gap-6">
                        <div className="relative w-32 h-32">
                            <svg className="w-full h-full transform -rotate-90">
                                {data.map((item, index) => {
                                    const percentage = total > 0 ? (item.value / total) * 100 : 0
                                    const offset = data
                                        .slice(0, index)
                                        .reduce((acc, d) => acc + (d.value / total) * 100, 0)
                                    return (
                                        <circle
                                            key={item.label}
                                            cx="64"
                                            cy="64"
                                            r="48"
                                            fill="none"
                                            stroke="currentColor"
                                            strokeWidth="16"
                                            strokeDasharray={`${percentage * 3.01} 301`}
                                            strokeDashoffset={-offset * 3.01}
                                            className={cn(
                                                item.color?.replace('bg-', 'text-') ||
                                                defaultColors[index % defaultColors.length].replace('bg-', 'text-')
                                            )}
                                        />
                                    )
                                })}
                            </svg>
                            <div className="absolute inset-0 flex items-center justify-center">
                                <span className="text-lg font-bold">{total}</span>
                            </div>
                        </div>
                        {showLegend && (
                            <div className="flex-1 space-y-2">
                                {data.map((item, index) => (
                                    <div key={item.label} className="flex items-center gap-2">
                                        <div
                                            className={cn(
                                                'w-3 h-3 rounded-full',
                                                item.color || defaultColors[index % defaultColors.length]
                                            )}
                                        />
                                        <span className="text-sm flex-1">{item.label}</span>
                                        <span className="text-sm font-medium">{item.value}</span>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )}
            </CardContent>
        </Card>
    )
}

import { LucideIcon, TrendingUp, TrendingDown } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { cn, formatNumber } from '@/lib/utils'

interface StatCardProps {
    title: string
    value: number | string
    change?: number
    changeType?: 'increase' | 'decrease'
    icon: LucideIcon
    iconColor?: string
}

export default function StatCard({
    title,
    value,
    change,
    changeType,
    icon: Icon,
    iconColor = 'text-primary',
}: StatCardProps) {
    return (
        <Card>
            <CardContent className="p-6">
                <div className="flex items-center justify-between">
                    <div className={cn('p-2 rounded-lg bg-primary/10', iconColor.replace('text-', 'bg-') + '/10')}>
                        <Icon className={cn('w-5 h-5', iconColor)} />
                    </div>
                    {change !== undefined && changeType && (
                        <div
                            className={cn(
                                'flex items-center gap-1 text-sm font-medium',
                                changeType === 'increase' ? 'text-success' : 'text-error'
                            )}
                        >
                            {changeType === 'increase' ? (
                                <TrendingUp className="w-4 h-4" />
                            ) : (
                                <TrendingDown className="w-4 h-4" />
                            )}
                            {change}%
                        </div>
                    )}
                </div>
                <div className="mt-4">
                    <p className="text-2xl font-bold text-neutral-900">
                        {typeof value === 'number' ? formatNumber(value) : value}
                    </p>
                    <p className="text-sm text-neutral-500">{title}</p>
                </div>
            </CardContent>
        </Card>
    )
}

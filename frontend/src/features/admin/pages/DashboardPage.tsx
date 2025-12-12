import { useQuery } from '@tanstack/react-query'
import { BarChart3, Users, Zap, AlertCircle, RefreshCw, FileText, MessageSquare, Database } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import adminApi from '@/services/adminApi'

export default function DashboardPage() {
    const { data: overview, isLoading, refetch } = useQuery({
        queryKey: ['admin', 'overview'],
        queryFn: () => adminApi.getAnalyticsOverview('today'),
    })

    const { data: stats } = useQuery({
        queryKey: ['admin', 'stats'],
        queryFn: () => adminApi.getStats(),
    })

    return (
        <div className="p-6 space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold">Dashboard</h1>
                <Button variant="outline" size="sm" onClick={() => refetch()} disabled={isLoading}>
                    <RefreshCw className={cn('w-4 h-4 mr-2', isLoading && 'animate-spin')} />
                    Refresh
                </Button>
            </div>

            {/* Analytics Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <StatCard
                    title="Requests"
                    value={overview?.requests ?? '-'}
                    icon={BarChart3}
                    loading={isLoading}
                />
                <StatCard
                    title="Active Users"
                    value={overview?.active_users ?? '-'}
                    icon={Users}
                    loading={isLoading}
                />
                <StatCard
                    title="Avg Latency"
                    value={overview ? `${overview.avg_latency_ms.toFixed(0)}ms` : '-'}
                    icon={Zap}
                    loading={isLoading}
                />
                <StatCard
                    title="Error Rate"
                    value={overview ? `${(overview.error_rate * 100).toFixed(1)}%` : '-'}
                    icon={AlertCircle}
                    loading={isLoading}
                />
            </div>

            {/* System Stats */}
            <Card>
                <CardHeader>
                    <CardTitle>System Stats</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="text-center p-4 bg-blue-50 rounded-lg">
                            <FileText className="w-6 h-6 mx-auto mb-2 text-blue-600" />
                            <p className="text-2xl font-bold">{stats?.documents_count ?? '-'}</p>
                            <p className="text-sm text-neutral-500">Documents</p>
                        </div>
                        <div className="text-center p-4 bg-green-50 rounded-lg">
                            <Database className="w-6 h-6 mx-auto mb-2 text-green-600" />
                            <p className="text-2xl font-bold">{stats?.chunks_count ?? '-'}</p>
                            <p className="text-sm text-neutral-500">Chunks</p>
                        </div>
                        <div className="text-center p-4 bg-purple-50 rounded-lg">
                            <MessageSquare className="w-6 h-6 mx-auto mb-2 text-purple-600" />
                            <p className="text-2xl font-bold">{stats?.sessions_count ?? '-'}</p>
                            <p className="text-sm text-neutral-500">Sessions</p>
                        </div>
                        <div className="text-center p-4 bg-orange-50 rounded-lg">
                            <Users className="w-6 h-6 mx-auto mb-2 text-orange-600" />
                            <p className="text-2xl font-bold">{stats?.users_count ?? '-'}</p>
                            <p className="text-sm text-neutral-500">Users</p>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    )
}

function StatCard({ title, value, icon: Icon, loading }: {
    title: string
    value: string | number
    icon: React.ElementType
    loading?: boolean
}) {
    return (
        <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-neutral-500">{title}</CardTitle>
                <Icon className="w-4 h-4 text-neutral-400" />
            </CardHeader>
            <CardContent>
                {loading ? (
                    <div className="h-8 w-16 bg-neutral-200 animate-pulse rounded" />
                ) : (
                    <p className="text-2xl font-bold">{value}</p>
                )}
            </CardContent>
        </Card>
    )
}

import { useQuery } from '@tanstack/react-query'
import { BarChart3, Users, Zap, AlertCircle, RefreshCw, FileText, MessageSquare, Database, ArrowRight } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { adminApi } from '../api/adminApi'
import { Link } from 'react-router-dom'

export default function DashboardPage() {
    const { data: stats, isLoading, refetch } = useQuery({
        queryKey: ['admin', 'dashboard'],
        queryFn: adminApi.getDashboardStats,
    })

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
                    <p className="text-sm text-[var(--muted)] mt-1">Overview of AMI usage and system health.</p>
                </div>
                <Button variant="outline" size="sm" onClick={() => refetch()} disabled={isLoading}>
                    <RefreshCw className={cn('w-4 h-4 mr-2', isLoading && 'animate-spin')} />
                    Refresh
                </Button>
            </div>

            {/* Analytics Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <StatCard
                    title="Requests"
                    value={stats?.totalRequests ?? '-'}
                    icon={BarChart3}
                    loading={isLoading}
                />
                <StatCard
                    title="Active Users"
                    value={stats?.activeUsers ?? '-'}
                    icon={Users}
                    loading={isLoading}
                />
                <StatCard
                    title="Avg Latency"
                    value={stats ? `${Math.round(stats.avgLatency)}ms` : '0ms'}
                    icon={Zap}
                    loading={isLoading}
                />
                <StatCard
                    title="Error Rate"
                    value={stats ? `${(stats.errorRate * 100).toFixed(1)}%` : '-'}
                    icon={AlertCircle}
                    loading={isLoading}
                />
            </div>

            {/* Quick actions */}
            <Card>
                <CardHeader className="pb-3">
                    <CardTitle className="text-base">Quick actions</CardTitle>
                </CardHeader>
                <CardContent className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
                    <QuickLink title="Conversations" description="Review sessions & issues" to="/admin/conversations" />
                    <QuickLink title="Knowledge gaps" description="Fix low-confidence queries" to="/admin/knowledge" />
                    <QuickLink title="Datasources" description="Manage crawlers & feeds" to="/admin/datasources" />
                    <QuickLink title="Vector store" description="Monitor embeddings health" to="/admin/vector-store" />
                </CardContent>
            </Card>

            {/* System Stats */}
            <Card>
                <CardHeader>
                    <CardTitle>System Stats</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="text-center p-4 bg-[var(--surface2)] rounded-[var(--radius)]">
                            <FileText className="w-6 h-6 mx-auto mb-2 text-neutral-500" />
                            <p className="text-2xl font-semibold">{stats?.totalDocuments ?? '-'}*</p>
                            <p className="text-sm text-[var(--muted)]">Documents</p>
                        </div>
                        <div className="text-center p-4 bg-[var(--surface2)] rounded-[var(--radius)]">
                            <Database className="w-6 h-6 mx-auto mb-2 text-neutral-500" />
                            <p className="text-2xl font-semibold">{stats?.totalChunks ?? '-'}</p>
                            <p className="text-sm text-[var(--muted)]">Chunks</p>
                        </div>
                        <div className="text-center p-4 bg-[var(--surface2)] rounded-[var(--radius)]">
                            <MessageSquare className="w-6 h-6 mx-auto mb-2 text-neutral-500" />
                            <p className="text-2xl font-semibold">{stats?.totalSessions ?? '-'}</p>
                            <p className="text-sm text-[var(--muted)]">Sessions</p>
                        </div>
                        <div className="text-center p-4 bg-[var(--surface2)] rounded-[var(--radius)]">
                            <Users className="w-6 h-6 mx-auto mb-2 text-neutral-500" />
                            <p className="text-2xl font-semibold">{stats?.activeUsers ?? '-'}</p>
                            <p className="text-sm text-[var(--muted)]">Users</p>
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

function QuickLink({
    title,
    description,
    to,
}: {
    title: string
    description: string
    to: string
}) {
    return (
        <Button
            asChild
            variant="ghost"
            className="h-auto p-4 rounded-[var(--radius)] bg-[var(--surface2)] hover:bg-[var(--surface)] hover:shadow-sm transition-all justify-between"
        >
            <Link to={to}>
                <div className="text-left">
                    <div className="font-medium">{title}</div>
                    <div className="text-xs text-[var(--muted)] mt-1">{description}</div>
                </div>
                <ArrowRight className="w-4 h-4 text-neutral-400" />
            </Link>
        </Button>
    )
}

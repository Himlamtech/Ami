import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Database, Plus, Globe, FileText, Server, AlertCircle, CheckCircle, Clock, XCircle, Play } from "lucide-react"
import { adminApi } from '../api/adminApi'
import { DataSource } from '@/types/admin'
import { formatDistanceToNow } from 'date-fns'

const sourceTypeIcons = {
    web_crawler: Globe,
    api: Server,
    file_upload: FileText,
    database: Database,
}

const statusIcons = {
    active: CheckCircle,
    inactive: Clock,
    error: XCircle,
    pending: AlertCircle,
}

export default function DatasourcesPage() {
    const { data: stats, isLoading: statsLoading } = useQuery({
        queryKey: ['dataSourceStats'],
        queryFn: adminApi.getDataSourceStats,
    })

    const { data: sourcesData, isLoading: sourcesLoading } = useQuery({
        queryKey: ['dataSources'],
        queryFn: () => adminApi.getDataSources({ skip: 0, limit: 100 }),
    })

    const sources = sourcesData?.items || []

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-semibold tracking-tight">Datasources</h2>
                    <p className="text-sm text-[var(--muted)] mt-1">Manage knowledge sources for the chatbot.</p>
                </div>
                <Button>
                    <Plus className="w-4 h-4 mr-2" />
                    Add Source
                </Button>
            </div>

            {/* Stats Grid */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Total Sources</CardTitle>
                        <Database className="h-4 w-4 text-neutral-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{statsLoading ? '...' : stats?.total || 0}</div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Active</CardTitle>
                        <CheckCircle className="h-4 w-4 text-green-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{statsLoading ? '...' : stats?.active || 0}</div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Inactive</CardTitle>
                        <Clock className="h-4 w-4 text-gray-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{statsLoading ? '...' : stats?.inactive || 0}</div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Errors</CardTitle>
                        <XCircle className="h-4 w-4 text-red-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{statsLoading ? '...' : stats?.error || 0}</div>
                    </CardContent>
                </Card>
            </div>

            {/* Active Sources List */}
            <Card>
                <CardHeader>
                    <CardTitle>Active Sources</CardTitle>
                </CardHeader>
                <CardContent>
                    {sourcesLoading ? (
                        <div className="text-sm text-neutral-500 text-center py-8">
                            Loading sources...
                        </div>
                    ) : sources.length === 0 ? (
                        <div className="text-sm text-neutral-500 text-center py-8">
                            No data sources configured yet.
                        </div>
                    ) : (
                        <div className="space-y-3">
                            {sources.map((source: DataSource) => {
                                const TypeIcon = sourceTypeIcons[source.source_type] || Database
                                const StatusIcon = statusIcons[source.status] || AlertCircle
                                const badgeVariant =
                                    source.status === 'active'
                                        ? 'softSuccess'
                                        : source.status === 'pending'
                                            ? 'softWarning'
                                            : source.status === 'error'
                                                ? 'softError'
                                                : 'softNeutral'

                                return (
                                    <div key={source.id} className="flex items-center justify-between p-4 bg-[var(--surface2)] rounded-[var(--radius)] hover:bg-[var(--surface)] hover:shadow-sm transition-all">
                                        <div className="flex items-center gap-4 flex-1">
                                            <div className="p-2 bg-[var(--surface)] rounded-lg shadow-sm">
                                                <TypeIcon className="h-5 w-5 text-neutral-600" />
                                            </div>
                                            <div className="flex-1">
                                                <div className="flex items-center gap-2">
                                                    <h3 className="font-medium">{source.name}</h3>
                                                    <Badge variant={badgeVariant as any}>
                                                        <StatusIcon className="h-3 w-3 mr-1" />
                                                        {source.status}
                                                    </Badge>
                                                </div>
                                                <p className="text-sm text-[var(--muted)]">{source.description || source.base_url}</p>
                                                <div className="flex items-center gap-4 mt-2 text-xs text-[var(--muted)]">
                                                    <span>Crawls: {source.crawl_count}</span>
                                                    <span>Success: {source.success_count}</span>
                                                    {source.error_count > 0 && (
                                                        <span className="text-error">Errors: {source.error_count}</span>
                                                    )}
                                                    {source.last_crawl_at && (
                                                        <span>Last: {formatDistanceToNow(new Date(source.last_crawl_at), { addSuffix: true })}</span>
                                                    )}
                                                </div>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-2">
                                            <Button variant="ghost" size="sm">
                                                <Play className="h-4 w-4" />
                                            </Button>
                                        </div>
                                    </div>
                                )
                            })}
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    )
}

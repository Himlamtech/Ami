import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
    Search,
    Filter,
    RefreshCw,
    History,
    MessageSquare,
    LogIn,
    LogOut,
    FileText,
    Download,
    Calendar,
    User,
    AlertCircle,
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select'
import { cn, formatDate } from '@/lib/utils'
import { api } from '@/lib/api'

interface ActivityLog {
    id: string
    user_id: string
    user_name: string
    user_email: string
    action: string
    action_type: 'login' | 'logout' | 'chat' | 'feedback' | 'profile' | 'bookmark' | 'export' | 'error'
    details: string
    metadata?: Record<string, unknown>
    ip_address?: string
    user_agent?: string
    session_id?: string
    created_at: string
}

interface ActivityStats {
    total_today: number
    total_week: number
    unique_users_today: number
    errors_today: number
}

const actionTypeConfig: Record<string, { icon: typeof History; label: string; color: string }> = {
    login: { icon: LogIn, label: 'Đăng nhập', color: 'text-success' },
    logout: { icon: LogOut, label: 'Đăng xuất', color: 'text-neutral-500' },
    chat: { icon: MessageSquare, label: 'Chat', color: 'text-primary' },
    feedback: { icon: FileText, label: 'Feedback', color: 'text-warning' },
    profile: { icon: User, label: 'Profile', color: 'text-secondary' },
    bookmark: { icon: FileText, label: 'Bookmark', color: 'text-purple-500' },
    export: { icon: Download, label: 'Export', color: 'text-blue-500' },
    error: { icon: AlertCircle, label: 'Error', color: 'text-error' },
}

export default function ActivityLogPage() {
    const [searchParams] = useSearchParams()
    const userIdFromUrl = searchParams.get('userId')

    const [searchQuery, setSearchQuery] = useState('')
    const [debouncedSearch, setDebouncedSearch] = useState('')
    const [filters, setFilters] = useState({
        actionType: 'all',
        dateRange: 'today',
        userId: userIdFromUrl || '',
    })

    // Update filter when URL param changes
    useEffect(() => {
        if (userIdFromUrl) {
            setFilters((prev) => ({ ...prev, userId: userIdFromUrl }))
        }
    }, [userIdFromUrl])

    // Debounce search
    useEffect(() => {
        const timer = setTimeout(() => {
            setDebouncedSearch(searchQuery)
        }, 300)
        return () => clearTimeout(timer)
    }, [searchQuery])

    // Fetch activity logs
    const { data, isLoading, refetch } = useQuery({
        queryKey: ['admin', 'activity-log', debouncedSearch, filters],
        queryFn: async () => {
            const params: Record<string, string> = {}
            if (debouncedSearch) params.search = debouncedSearch
            if (filters.actionType !== 'all') params.action_type = filters.actionType
            if (filters.dateRange !== 'all') params.date_range = filters.dateRange
            if (filters.userId) params.user_id = filters.userId

            return api.get<{ data: ActivityLog[]; stats: ActivityStats }>('/admin/activity-logs', params)
        },
    })

    const logs = data?.data || []
    const stats = data?.stats || {
        total_today: 0,
        total_week: 0,
        unique_users_today: 0,
        errors_today: 0,
    }

    const getActionIcon = (actionType: string) => {
        const config = actionTypeConfig[actionType] || actionTypeConfig.chat
        const Icon = config.icon
        return <Icon className={cn('w-4 h-4', config.color)} />
    }

    const getActionBadge = (actionType: string) => {
        const config = actionTypeConfig[actionType] || actionTypeConfig.chat
        return (
            <Badge variant="outline" className="gap-1 text-xs">
                {getActionIcon(actionType)}
                {config.label}
            </Badge>
        )
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-semibold text-neutral-900">Activity Log</h1>
                    <p className="text-sm text-neutral-500 mt-1">
                        Theo dõi hoạt động của sinh viên trên hệ thống
                    </p>
                </div>
                <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm" onClick={() => refetch()}>
                        <RefreshCw className="w-4 h-4 mr-2" />
                        Làm mới
                    </Button>
                    <Button variant="outline" size="sm">
                        <Download className="w-4 h-4 mr-2" />
                        Export
                    </Button>
                </div>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Card>
                    <CardContent className="p-4">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                                <History className="w-5 h-5 text-primary" />
                            </div>
                            <div>
                                <p className="text-2xl font-semibold">{stats.total_today}</p>
                                <p className="text-xs text-neutral-500">Hoạt động hôm nay</p>
                            </div>
                        </div>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="p-4">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-lg bg-secondary/10 flex items-center justify-center">
                                <Calendar className="w-5 h-5 text-secondary" />
                            </div>
                            <div>
                                <p className="text-2xl font-semibold">{stats.total_week}</p>
                                <p className="text-xs text-neutral-500">Tuần này</p>
                            </div>
                        </div>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="p-4">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-lg bg-success/10 flex items-center justify-center">
                                <User className="w-5 h-5 text-success" />
                            </div>
                            <div>
                                <p className="text-2xl font-semibold">{stats.unique_users_today}</p>
                                <p className="text-xs text-neutral-500">Users hôm nay</p>
                            </div>
                        </div>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="p-4">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-lg bg-error/10 flex items-center justify-center">
                                <AlertCircle className="w-5 h-5 text-error" />
                            </div>
                            <div>
                                <p className="text-2xl font-semibold">{stats.errors_today}</p>
                                <p className="text-xs text-neutral-500">Lỗi hôm nay</p>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Filters */}
            <Card>
                <CardContent className="p-4">
                    <div className="flex flex-wrap items-center gap-4">
                        <div className="relative flex-1 min-w-[200px] max-w-md">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
                            <Input
                                placeholder="Tìm theo user, action..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="pl-10"
                            />
                        </div>
                        <Select
                            value={filters.actionType}
                            onValueChange={(value) => setFilters({ ...filters, actionType: value })}
                        >
                            <SelectTrigger className="w-[150px]">
                                <SelectValue placeholder="Loại action" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="all">Tất cả</SelectItem>
                                <SelectItem value="login">Đăng nhập</SelectItem>
                                <SelectItem value="logout">Đăng xuất</SelectItem>
                                <SelectItem value="chat">Chat</SelectItem>
                                <SelectItem value="feedback">Feedback</SelectItem>
                                <SelectItem value="profile">Profile</SelectItem>
                                <SelectItem value="error">Error</SelectItem>
                            </SelectContent>
                        </Select>
                        <Select
                            value={filters.dateRange}
                            onValueChange={(value) => setFilters({ ...filters, dateRange: value })}
                        >
                            <SelectTrigger className="w-[150px]">
                                <SelectValue placeholder="Thời gian" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="today">Hôm nay</SelectItem>
                                <SelectItem value="yesterday">Hôm qua</SelectItem>
                                <SelectItem value="week">7 ngày qua</SelectItem>
                                <SelectItem value="month">30 ngày qua</SelectItem>
                                <SelectItem value="all">Tất cả</SelectItem>
                            </SelectContent>
                        </Select>
                        {filters.userId && (
                            <Badge variant="secondary" className="gap-1">
                                User: {filters.userId.slice(0, 8)}...
                                <button
                                    onClick={() => setFilters({ ...filters, userId: '' })}
                                    className="ml-1 hover:text-error"
                                >
                                    ×
                                </button>
                            </Badge>
                        )}
                        <Button variant="ghost" size="sm">
                            <Filter className="w-4 h-4 mr-2" />
                            Bộ lọc khác
                        </Button>
                    </div>
                </CardContent>
            </Card>

            {/* Activity Timeline */}
            <Card>
                <CardHeader className="pb-3">
                    <CardTitle className="text-base">
                        Activity Timeline ({logs.length})
                    </CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                    {isLoading ? (
                        <div className="flex items-center justify-center py-12">
                            <RefreshCw className="w-6 h-6 animate-spin text-neutral-400" />
                        </div>
                    ) : logs.length === 0 ? (
                        <div className="text-center py-12 text-neutral-500">
                            <History className="w-12 h-12 mx-auto mb-3 text-neutral-300" />
                            <p>Không có hoạt động nào</p>
                        </div>
                    ) : (
                        <div className="divide-y divide-[color:var(--border)]">
                            {logs.map((log) => (
                                <div
                                    key={log.id}
                                    className="flex items-start gap-4 p-4 hover:bg-[var(--surface2)] transition-colors"
                                >
                                    {/* Icon */}
                                    <div className="w-10 h-10 rounded-full bg-[var(--surface2)] flex items-center justify-center flex-shrink-0">
                                        {getActionIcon(log.action_type)}
                                    </div>

                                    {/* Content */}
                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-center gap-2 flex-wrap">
                                            <span className="font-medium text-sm">
                                                {log.user_name || 'Unknown User'}
                                            </span>
                                            {getActionBadge(log.action_type)}
                                        </div>
                                        <p className="text-sm text-neutral-600 mt-1">{log.details}</p>
                                        <div className="flex items-center gap-4 mt-2 text-xs text-neutral-400">
                                            <span>{log.user_email}</span>
                                            {log.ip_address && <span>IP: {log.ip_address}</span>}
                                            {log.session_id && (
                                                <span>Session: {log.session_id.slice(0, 8)}...</span>
                                            )}
                                        </div>
                                    </div>

                                    {/* Timestamp */}
                                    <div className="text-xs text-neutral-400 flex-shrink-0">
                                        {formatDate(log.created_at)}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* Pagination */}
            {logs.length > 0 && (
                <div className="flex items-center justify-between">
                    <p className="text-sm text-neutral-500">
                        Hiển thị {logs.length} hoạt động
                    </p>
                    <div className="flex items-center gap-2">
                        <Button variant="outline" size="sm" disabled>
                            Trang trước
                        </Button>
                        <Button variant="outline" size="sm">
                            Trang sau
                        </Button>
                    </div>
                </div>
            )}
        </div>
    )
}

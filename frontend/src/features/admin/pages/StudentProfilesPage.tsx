import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
    Search,
    Filter,
    RefreshCw,
    MoreHorizontal,
    Eye,
    MessageSquare,
    Ban,
    Download,
    GraduationCap,
    TrendingUp,
    Users,
    Clock,
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
} from '@/components/ui/dialog'
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select'
import { cn, formatDate } from '@/lib/utils'
import { api } from '@/lib/api'

interface StudentProfile {
    id: string
    user_id: string
    name: string
    email: string
    student_id: string
    major: string
    level: string
    class_name?: string
    status: 'active' | 'inactive' | 'suspended' | 'banned'
    total_sessions: number
    total_queries: number
    avg_rating: number
    engagement_score: number
    last_active: string
    created_at: string
}

interface StudentStats {
    total_students: number
    active_today: number
    avg_engagement: number
    new_this_month: number
}

const statusStyles = {
    active: 'bg-success/10 text-success border-success/20',
    inactive: 'bg-neutral-100 text-neutral-500 border-neutral-200',
    suspended: 'bg-warning/10 text-warning border-warning/20',
    banned: 'bg-error/10 text-error border-error/20',
}

const statusLabels = {
    active: 'Hoạt động',
    inactive: 'Không hoạt động',
    suspended: 'Tạm khóa',
    banned: 'Bị cấm',
}

export default function StudentProfilesPage() {
    const navigate = useNavigate()
    const [searchQuery, setSearchQuery] = useState('')
    const [debouncedSearch, setDebouncedSearch] = useState('')
    const [selectedStudent, setSelectedStudent] = useState<StudentProfile | null>(null)
    const [filters, setFilters] = useState({
        status: 'all',
        major: 'all',
        engagement: 'all',
    })

    // Debounce search
    useEffect(() => {
        const timer = setTimeout(() => {
            setDebouncedSearch(searchQuery)
        }, 300)
        return () => clearTimeout(timer)
    }, [searchQuery])

    // Fetch students
    const { data, isLoading, refetch } = useQuery({
        queryKey: ['admin', 'students', debouncedSearch, filters],
        queryFn: async () => {
            const params: Record<string, string> = {}
            if (debouncedSearch) params.search = debouncedSearch
            if (filters.status !== 'all') params.status = filters.status
            if (filters.major !== 'all') params.major = filters.major
            if (filters.engagement !== 'all') params.engagement = filters.engagement

            return api.get<{ data: StudentProfile[]; stats: StudentStats }>('/admin/students', params)
        },
    })

    const students = data?.data || []
    const stats = data?.stats || {
        total_students: 0,
        active_today: 0,
        avg_engagement: 0,
        new_this_month: 0,
    }

    const getEngagementBadge = (score: number) => {
        if (score >= 0.7) return <Badge className="bg-success/10 text-success">Cao</Badge>
        if (score >= 0.4) return <Badge className="bg-warning/10 text-warning">TB</Badge>
        return <Badge className="bg-neutral-100 text-neutral-500">Thấp</Badge>
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-semibold text-neutral-900">Student Profiles</h1>
                    <p className="text-sm text-neutral-500 mt-1">
                        Quản lý hồ sơ sinh viên, engagement và activity
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
                                <GraduationCap className="w-5 h-5 text-primary" />
                            </div>
                            <div>
                                <p className="text-2xl font-semibold">{stats.total_students}</p>
                                <p className="text-xs text-neutral-500">Tổng sinh viên</p>
                            </div>
                        </div>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="p-4">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-lg bg-success/10 flex items-center justify-center">
                                <Users className="w-5 h-5 text-success" />
                            </div>
                            <div>
                                <p className="text-2xl font-semibold">{stats.active_today}</p>
                                <p className="text-xs text-neutral-500">Hoạt động hôm nay</p>
                            </div>
                        </div>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="p-4">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-lg bg-warning/10 flex items-center justify-center">
                                <TrendingUp className="w-5 h-5 text-warning" />
                            </div>
                            <div>
                                <p className="text-2xl font-semibold">
                                    {(stats.avg_engagement * 100).toFixed(0)}%
                                </p>
                                <p className="text-xs text-neutral-500">Engagement TB</p>
                            </div>
                        </div>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="p-4">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-lg bg-secondary/10 flex items-center justify-center">
                                <Clock className="w-5 h-5 text-secondary" />
                            </div>
                            <div>
                                <p className="text-2xl font-semibold">{stats.new_this_month}</p>
                                <p className="text-xs text-neutral-500">Mới tháng này</p>
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
                                placeholder="Tìm theo tên, email, MSSV..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="pl-10"
                            />
                        </div>
                        <Select
                            value={filters.status}
                            onValueChange={(value) => setFilters({ ...filters, status: value })}
                        >
                            <SelectTrigger className="w-[150px]">
                                <SelectValue placeholder="Trạng thái" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="all">Tất cả</SelectItem>
                                <SelectItem value="active">Hoạt động</SelectItem>
                                <SelectItem value="inactive">Không hoạt động</SelectItem>
                                <SelectItem value="suspended">Tạm khóa</SelectItem>
                                <SelectItem value="banned">Bị cấm</SelectItem>
                            </SelectContent>
                        </Select>
                        <Select
                            value={filters.major}
                            onValueChange={(value) => setFilters({ ...filters, major: value })}
                        >
                            <SelectTrigger className="w-[180px]">
                                <SelectValue placeholder="Ngành học" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="all">Tất cả ngành</SelectItem>
                                <SelectItem value="cntt">Công nghệ thông tin</SelectItem>
                                <SelectItem value="attt">An toàn thông tin</SelectItem>
                                <SelectItem value="dtvt">Điện tử viễn thông</SelectItem>
                                <SelectItem value="qtkd">Quản trị kinh doanh</SelectItem>
                            </SelectContent>
                        </Select>
                        <Select
                            value={filters.engagement}
                            onValueChange={(value) => setFilters({ ...filters, engagement: value })}
                        >
                            <SelectTrigger className="w-[150px]">
                                <SelectValue placeholder="Engagement" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="all">Tất cả</SelectItem>
                                <SelectItem value="high">Cao (&gt;70%)</SelectItem>
                                <SelectItem value="medium">TB (40-70%)</SelectItem>
                                <SelectItem value="low">Thấp (&lt;40%)</SelectItem>
                            </SelectContent>
                        </Select>
                        <Button variant="ghost" size="sm">
                            <Filter className="w-4 h-4 mr-2" />
                            Bộ lọc khác
                        </Button>
                    </div>
                </CardContent>
            </Card>

            {/* Students Table */}
            <Card>
                <CardHeader className="pb-3">
                    <CardTitle className="text-base">
                        Danh sách sinh viên ({students.length})
                    </CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                    {isLoading ? (
                        <div className="flex items-center justify-center py-12">
                            <RefreshCw className="w-6 h-6 animate-spin text-neutral-400" />
                        </div>
                    ) : students.length === 0 ? (
                        <div className="text-center py-12 text-neutral-500">
                            <GraduationCap className="w-12 h-12 mx-auto mb-3 text-neutral-300" />
                            <p>Không tìm thấy sinh viên nào</p>
                        </div>
                    ) : (
                        <div className="overflow-x-auto">
                            <table className="w-full">
                                <thead>
                                    <tr className="border-b border-[color:var(--border)] bg-neutral-50/50">
                                        <th className="text-left py-3 px-4 text-xs font-medium text-neutral-500 uppercase">
                                            Sinh viên
                                        </th>
                                        <th className="text-left py-3 px-4 text-xs font-medium text-neutral-500 uppercase">
                                            Ngành / Lớp
                                        </th>
                                        <th className="text-left py-3 px-4 text-xs font-medium text-neutral-500 uppercase">
                                            Trạng thái
                                        </th>
                                        <th className="text-left py-3 px-4 text-xs font-medium text-neutral-500 uppercase">
                                            Sessions
                                        </th>
                                        <th className="text-left py-3 px-4 text-xs font-medium text-neutral-500 uppercase">
                                            Engagement
                                        </th>
                                        <th className="text-left py-3 px-4 text-xs font-medium text-neutral-500 uppercase">
                                            Hoạt động
                                        </th>
                                        <th className="text-right py-3 px-4 text-xs font-medium text-neutral-500 uppercase">
                                            Actions
                                        </th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {students.map((student) => (
                                        <tr
                                            key={student.id}
                                            className="border-b border-[color:var(--border)] last:border-0 hover:bg-[var(--surface2)] cursor-pointer transition-colors"
                                            onClick={() => setSelectedStudent(student)}
                                        >
                                            <td className="py-3 px-4">
                                                <div className="flex items-center gap-3">
                                                    <div className="w-9 h-9 rounded-full bg-primary/10 flex items-center justify-center text-primary font-medium text-sm">
                                                        {student.name?.charAt(0)?.toUpperCase() || 'S'}
                                                    </div>
                                                    <div>
                                                        <p className="text-sm font-medium">{student.name}</p>
                                                        <p className="text-xs text-neutral-500">
                                                            {student.student_id} · {student.email}
                                                        </p>
                                                    </div>
                                                </div>
                                            </td>
                                            <td className="py-3 px-4">
                                                <p className="text-sm">{student.major || '-'}</p>
                                                <p className="text-xs text-neutral-500">
                                                    {student.class_name || student.level || '-'}
                                                </p>
                                            </td>
                                            <td className="py-3 px-4">
                                                <Badge
                                                    className={cn(
                                                        'border',
                                                        statusStyles[student.status]
                                                    )}
                                                >
                                                    {statusLabels[student.status]}
                                                </Badge>
                                            </td>
                                            <td className="py-3 px-4">
                                                <p className="text-sm">{student.total_sessions}</p>
                                                <p className="text-xs text-neutral-500">
                                                    {student.total_queries} queries
                                                </p>
                                            </td>
                                            <td className="py-3 px-4">
                                                {getEngagementBadge(student.engagement_score)}
                                            </td>
                                            <td className="py-3 px-4">
                                                <p className="text-sm text-neutral-600">
                                                    {formatDate(student.last_active)}
                                                </p>
                                            </td>
                                            <td className="py-3 px-4 text-right">
                                                <DropdownMenu>
                                                    <DropdownMenuTrigger asChild>
                                                        <Button
                                                            variant="ghost"
                                                            size="icon"
                                                            className="h-8 w-8"
                                                            onClick={(e) => e.stopPropagation()}
                                                        >
                                                            <MoreHorizontal className="w-4 h-4" />
                                                        </Button>
                                                    </DropdownMenuTrigger>
                                                    <DropdownMenuContent align="end">
                                                        <DropdownMenuItem
                                                            onClick={(e) => {
                                                                e.stopPropagation()
                                                                setSelectedStudent(student)
                                                            }}
                                                        >
                                                            <Eye className="w-4 h-4 mr-2" />
                                                            Xem chi tiết
                                                        </DropdownMenuItem>
                                                        <DropdownMenuItem
                                                            onClick={(e) => {
                                                                e.stopPropagation()
                                                                navigate(
                                                                    `/admin/conversations?userId=${student.user_id}`
                                                                )
                                                            }}
                                                        >
                                                            <MessageSquare className="w-4 h-4 mr-2" />
                                                            Xem conversations
                                                        </DropdownMenuItem>
                                                        <DropdownMenuItem
                                                            className="text-error"
                                                            onClick={(e) => e.stopPropagation()}
                                                        >
                                                            <Ban className="w-4 h-4 mr-2" />
                                                            {student.status === 'banned'
                                                                ? 'Gỡ cấm'
                                                                : 'Cấm tài khoản'}
                                                        </DropdownMenuItem>
                                                    </DropdownMenuContent>
                                                </DropdownMenu>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* Student Detail Dialog */}
            <Dialog open={!!selectedStudent} onOpenChange={() => setSelectedStudent(null)}>
                <DialogContent className="max-w-2xl">
                    <DialogHeader>
                        <DialogTitle className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary font-semibold">
                                {selectedStudent?.name?.charAt(0)?.toUpperCase() || 'S'}
                            </div>
                            <div>
                                <p>{selectedStudent?.name}</p>
                                <p className="text-sm font-normal text-neutral-500">
                                    {selectedStudent?.student_id}
                                </p>
                            </div>
                        </DialogTitle>
                        <DialogDescription className="sr-only">
                            Chi tiết hồ sơ sinh viên
                        </DialogDescription>
                    </DialogHeader>
                    {selectedStudent && (
                        <div className="space-y-6">
                            {/* Basic Info */}
                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-1">
                                    <p className="text-xs text-neutral-500">Email</p>
                                    <p className="text-sm font-medium">{selectedStudent.email}</p>
                                </div>
                                <div className="space-y-1">
                                    <p className="text-xs text-neutral-500">Trạng thái</p>
                                    <Badge
                                        className={cn('border', statusStyles[selectedStudent.status])}
                                    >
                                        {statusLabels[selectedStudent.status]}
                                    </Badge>
                                </div>
                                <div className="space-y-1">
                                    <p className="text-xs text-neutral-500">Ngành học</p>
                                    <p className="text-sm font-medium">
                                        {selectedStudent.major || 'Chưa cập nhật'}
                                    </p>
                                </div>
                                <div className="space-y-1">
                                    <p className="text-xs text-neutral-500">Lớp / Năm</p>
                                    <p className="text-sm font-medium">
                                        {selectedStudent.class_name || selectedStudent.level || '-'}
                                    </p>
                                </div>
                            </div>

                            {/* Engagement Stats */}
                            <div className="p-4 bg-neutral-50 rounded-lg">
                                <h4 className="text-sm font-medium mb-3">Engagement Metrics</h4>
                                <div className="grid grid-cols-4 gap-4">
                                    <div className="text-center">
                                        <p className="text-2xl font-semibold text-primary">
                                            {selectedStudent.total_sessions}
                                        </p>
                                        <p className="text-xs text-neutral-500">Sessions</p>
                                    </div>
                                    <div className="text-center">
                                        <p className="text-2xl font-semibold text-secondary">
                                            {selectedStudent.total_queries}
                                        </p>
                                        <p className="text-xs text-neutral-500">Queries</p>
                                    </div>
                                    <div className="text-center">
                                        <p className="text-2xl font-semibold text-warning">
                                            {selectedStudent.avg_rating.toFixed(1)}
                                        </p>
                                        <p className="text-xs text-neutral-500">Avg Rating</p>
                                    </div>
                                    <div className="text-center">
                                        <p className="text-2xl font-semibold text-success">
                                            {(selectedStudent.engagement_score * 100).toFixed(0)}%
                                        </p>
                                        <p className="text-xs text-neutral-500">Engagement</p>
                                    </div>
                                </div>
                            </div>

                            {/* Actions */}
                            <div className="flex justify-end gap-2 pt-4 border-t">
                                <Button
                                    variant="outline"
                                    onClick={() =>
                                        navigate(
                                            `/admin/conversations?userId=${selectedStudent.user_id}`
                                        )
                                    }
                                >
                                    <MessageSquare className="w-4 h-4 mr-2" />
                                    Xem Conversations
                                </Button>
                                <Button
                                    variant="outline"
                                    onClick={() =>
                                        navigate(
                                            `/admin/activity-log?userId=${selectedStudent.user_id}`
                                        )
                                    }
                                >
                                    <History className="w-4 h-4 mr-2" />
                                    Activity Log
                                </Button>
                            </div>
                        </div>
                    )}
                </DialogContent>
            </Dialog>
        </div>
    )
}

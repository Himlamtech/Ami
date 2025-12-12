import { useState } from 'react'
import {
    Search,
    Filter,
    Download,
    RefreshCw,
    MoreHorizontal,
    Eye,
    Archive,
    Trash2,
    ChevronLeft,
    ChevronRight,
    X,
} from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
} from '@/components/ui/dialog'
import { cn, formatDate } from '@/lib/utils'
import type { AdminConversation } from '@/types/admin'

// Mock data
const mockConversations: AdminConversation[] = [
    {
        id: '1',
        userId: 'u1',
        userName: 'Nguyen Van A',
        studentId: 'B21DCCN001',
        title: 'Học phí kỳ 1',
        preview: 'Học phí cho sinh viên CNTT là...',
        messageCount: 5,
        lastActive: new Date().toISOString(),
        status: 'active',
        hasNegativeFeedback: false,
    },
    {
        id: '2',
        userId: 'u2',
        userName: 'Tran Thi B',
        studentId: 'B21DCCN045',
        title: 'Đăng ký môn học',
        preview: 'Cách đăng ký môn học online...',
        messageCount: 8,
        lastActive: new Date(Date.now() - 3600000).toISOString(),
        status: 'active',
        hasNegativeFeedback: false,
    },
    {
        id: '3',
        userId: 'u3',
        userName: 'Le Van C',
        studentId: 'B20DCCN102',
        title: 'Mẫu đơn xin nghỉ',
        preview: 'Cho tôi mẫu đơn xin nghỉ...',
        messageCount: 3,
        lastActive: new Date(Date.now() - 7200000).toISOString(),
        status: 'issues',
        hasNegativeFeedback: true,
    },
    {
        id: '4',
        userId: 'u4',
        userName: 'Pham D',
        studentId: 'B21DCCN078',
        title: 'Học bổng KKHT',
        preview: 'Điều kiện để được học bổng...',
        messageCount: 12,
        lastActive: new Date(Date.now() - 86400000).toISOString(),
        status: 'multiple_issues',
        hasNegativeFeedback: true,
    },
]

export default function ConversationsPage() {
    const [searchQuery, setSearchQuery] = useState('')
    const [selectedConversation, setSelectedConversation] = useState<AdminConversation | null>(null)
    const [filters, setFilters] = useState({
        hasNegativeFeedback: false,
    })

    const filteredConversations = mockConversations.filter((conv) => {
        if (searchQuery && !conv.title.toLowerCase().includes(searchQuery.toLowerCase())) {
            return false
        }
        if (filters.hasNegativeFeedback && !conv.hasNegativeFeedback) {
            return false
        }
        return true
    })

    const getStatusBadge = (status: AdminConversation['status']) => {
        const styles = {
            active: 'bg-success/10 text-success',
            issues: 'bg-warning/10 text-warning',
            multiple_issues: 'bg-error/10 text-error',
            archived: 'bg-neutral-100 text-neutral-500',
        }
        const labels = {
            active: '🟢',
            issues: '🟡 👎',
            multiple_issues: '🔴 👎👎',
            archived: '⚫',
        }
        return (
            <span className={cn('px-2 py-1 rounded-full text-xs font-medium', styles[status])}>
                {labels[status]}
            </span>
        )
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-neutral-900">Conversations</h2>
                <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm">
                        <Download className="w-4 h-4 mr-2" />
                        Export
                    </Button>
                    <Button variant="outline" size="sm">
                        <RefreshCw className="w-4 h-4 mr-2" />
                        Refresh
                    </Button>
                </div>
            </div>

            {/* Filters */}
            <Card>
                <CardContent className="p-4">
                    <div className="flex flex-wrap items-center gap-4">
                        <div className="relative flex-1 min-w-[200px]">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
                            <Input
                                placeholder="Search conversations..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="pl-9"
                            />
                        </div>
                        <Button variant="outline" size="sm">
                            <Filter className="w-4 h-4 mr-2" />
                            User
                        </Button>
                        <Button variant="outline" size="sm">
                            <Filter className="w-4 h-4 mr-2" />
                            Status
                        </Button>
                        <Button variant="outline" size="sm">
                            📅 Date Range
                        </Button>
                    </div>
                    <div className="flex items-center gap-4 mt-4">
                        <label className="flex items-center gap-2 text-sm">
                            <input
                                type="checkbox"
                                checked={filters.hasNegativeFeedback}
                                onChange={(e) =>
                                    setFilters({ ...filters, hasNegativeFeedback: e.target.checked })
                                }
                                className="rounded border-neutral-300"
                            />
                            Has negative feedback
                        </label>
                        {(searchQuery || filters.hasNegativeFeedback) && (
                            <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => {
                                    setSearchQuery('')
                                    setFilters({ hasNegativeFeedback: false })
                                }}
                            >
                                <X className="w-4 h-4 mr-1" />
                                Clear filters
                            </Button>
                        )}
                    </div>
                </CardContent>
            </Card>

            {/* Table */}
            <Card>
                <CardContent className="p-0">
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead>
                                <tr className="border-b bg-neutral-50">
                                    <th className="text-left py-3 px-4 text-sm font-medium text-neutral-500">
                                        <input type="checkbox" className="rounded border-neutral-300" />
                                    </th>
                                    <th className="text-left py-3 px-4 text-sm font-medium text-neutral-500">
                                        User
                                    </th>
                                    <th className="text-left py-3 px-4 text-sm font-medium text-neutral-500">
                                        Title
                                    </th>
                                    <th className="text-left py-3 px-4 text-sm font-medium text-neutral-500">
                                        Msgs
                                    </th>
                                    <th className="text-left py-3 px-4 text-sm font-medium text-neutral-500">
                                        Last Active
                                    </th>
                                    <th className="text-left py-3 px-4 text-sm font-medium text-neutral-500">
                                        Status
                                    </th>
                                    <th className="text-left py-3 px-4 text-sm font-medium text-neutral-500"></th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredConversations.map((conv) => (
                                    <tr
                                        key={conv.id}
                                        className="border-b last:border-0 hover:bg-neutral-50 cursor-pointer"
                                        onClick={() => setSelectedConversation(conv)}
                                    >
                                        <td className="py-3 px-4" onClick={(e) => e.stopPropagation()}>
                                            <input type="checkbox" className="rounded border-neutral-300" />
                                        </td>
                                        <td className="py-3 px-4">
                                            <div>
                                                <p className="text-sm font-medium">👤 {conv.userName}</p>
                                                <p className="text-xs text-neutral-500">{conv.studentId}</p>
                                            </div>
                                        </td>
                                        <td className="py-3 px-4">
                                            <div>
                                                <p className="text-sm font-medium">{conv.title}</p>
                                                <p className="text-xs text-neutral-500 truncate max-w-[200px]">
                                                    "{conv.preview}"
                                                </p>
                                            </div>
                                        </td>
                                        <td className="py-3 px-4 text-sm">{conv.messageCount}</td>
                                        <td className="py-3 px-4 text-sm text-neutral-500">
                                            {formatDate(conv.lastActive)}
                                        </td>
                                        <td className="py-3 px-4">{getStatusBadge(conv.status)}</td>
                                        <td className="py-3 px-4" onClick={(e) => e.stopPropagation()}>
                                            <DropdownMenu>
                                                <DropdownMenuTrigger asChild>
                                                    <Button variant="ghost" size="icon">
                                                        <MoreHorizontal className="w-4 h-4" />
                                                    </Button>
                                                </DropdownMenuTrigger>
                                                <DropdownMenuContent align="end">
                                                    <DropdownMenuItem onClick={() => setSelectedConversation(conv)}>
                                                        <Eye className="w-4 h-4 mr-2" />
                                                        View
                                                    </DropdownMenuItem>
                                                    <DropdownMenuItem>
                                                        <Archive className="w-4 h-4 mr-2" />
                                                        Archive
                                                    </DropdownMenuItem>
                                                    <DropdownMenuItem className="text-error">
                                                        <Trash2 className="w-4 h-4 mr-2" />
                                                        Delete
                                                    </DropdownMenuItem>
                                                </DropdownMenuContent>
                                            </DropdownMenu>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>

                    {/* Pagination */}
                    <div className="flex items-center justify-between p-4 border-t">
                        <p className="text-sm text-neutral-500">
                            Showing 1-{filteredConversations.length} of 1,234 conversations
                        </p>
                        <div className="flex items-center gap-2">
                            <Button variant="outline" size="sm" disabled>
                                <ChevronLeft className="w-4 h-4" />
                                Prev
                            </Button>
                            <Button variant="outline" size="sm" className="bg-primary text-white">
                                1
                            </Button>
                            <Button variant="outline" size="sm">
                                2
                            </Button>
                            <Button variant="outline" size="sm">
                                3
                            </Button>
                            <Button variant="outline" size="sm">
                                Next
                                <ChevronRight className="w-4 h-4" />
                            </Button>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Status Legend */}
            <div className="flex items-center gap-4 text-sm text-neutral-500">
                <span>Status:</span>
                <span>🟢 Active</span>
                <span>🟡 Has Issues</span>
                <span>🔴 Multiple Issues</span>
                <span>⚫ Archived</span>
            </div>

            {/* Conversation Detail Modal */}
            <Dialog open={!!selectedConversation} onOpenChange={() => setSelectedConversation(null)}>
                <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
                    <DialogHeader>
                        <DialogTitle className="flex items-center gap-2">
                            💬 {selectedConversation?.title}
                        </DialogTitle>
                    </DialogHeader>
                    {selectedConversation && (
                        <div className="grid grid-cols-3 gap-6">
                            {/* Messages */}
                            <div className="col-span-2 space-y-4">
                                <div className="p-4 bg-neutral-50 rounded-lg">
                                    <p className="text-sm text-neutral-500 mb-2">Session: sess_abc123</p>
                                    <div className="space-y-4">
                                        <div className="flex justify-end">
                                            <div className="bg-primary text-white rounded-2xl rounded-br-md px-4 py-2 max-w-[80%]">
                                                <p className="text-sm">Học phí kỳ này bao nhiêu?</p>
                                                <p className="text-xs opacity-70 mt-1">10:30 AM</p>
                                            </div>
                                        </div>
                                        <div className="flex gap-3">
                                            <div className="w-8 h-8 rounded-full bg-primary text-white flex items-center justify-center text-sm">
                                                🤖
                                            </div>
                                            <div className="bg-white border rounded-2xl rounded-bl-md px-4 py-2 max-w-[80%]">
                                                <p className="text-sm">Chào bạn! Học phí kỳ 1 năm 2024-2025...</p>
                                                <div className="flex items-center gap-2 mt-2 text-xs text-neutral-500">
                                                    <span>👍 Helpful ✓</span>
                                                </div>
                                                <p className="text-xs text-neutral-400 mt-1">10:31 AM</p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* User Info */}
                            <div className="space-y-4">
                                <div className="p-4 bg-neutral-50 rounded-lg">
                                    <h4 className="font-medium mb-3">👤 User Info</h4>
                                    <div className="space-y-2 text-sm">
                                        <p>
                                            <span className="text-neutral-500">Name:</span>{' '}
                                            {selectedConversation.userName}
                                        </p>
                                        <p>
                                            <span className="text-neutral-500">ID:</span>{' '}
                                            {selectedConversation.studentId}
                                        </p>
                                        <p>
                                            <span className="text-neutral-500">Major:</span> CNTT - K66
                                        </p>
                                    </div>
                                </div>

                                <div className="p-4 bg-neutral-50 rounded-lg">
                                    <h4 className="font-medium mb-3">📈 Stats</h4>
                                    <div className="space-y-2 text-sm">
                                        <p>Total sessions: 45</p>
                                        <p>Avg rating: 4.5 ⭐</p>
                                        <p>Last active: {formatDate(selectedConversation.lastActive)}</p>
                                    </div>
                                </div>

                                <div className="flex flex-col gap-2">
                                    <Button variant="outline" size="sm">
                                        View Full Profile
                                    </Button>
                                    <Button variant="outline" size="sm">
                                        View All Sessions
                                    </Button>
                                </div>
                            </div>
                        </div>
                    )}
                    <div className="flex gap-2 mt-4 pt-4 border-t">
                        <Button variant="outline" size="sm">
                            Archive
                        </Button>
                        <Button variant="outline" size="sm" className="text-error">
                            Delete
                        </Button>
                        <Button variant="outline" size="sm">
                            Export JSON
                        </Button>
                        <Button variant="outline" size="sm">
                            Export PDF
                        </Button>
                    </div>
                </DialogContent>
            </Dialog>
        </div>
    )
}

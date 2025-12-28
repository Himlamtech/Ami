import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import { adminApi } from '../api/adminApi'
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
    DialogDescription,
} from '@/components/ui/dialog'
import { cn, formatDate } from '@/lib/utils'
import type { AdminConversation } from '@/types/admin'


export default function ConversationsPage() {
    const navigate = useNavigate()
    const [searchQuery, setSearchQuery] = useState('')
    const [debouncedSearch, setDebouncedSearch] = useState('')
    const [selectedSessionId, setSelectedSessionId] = useState<string | null>(null)
    const [filters, setFilters] = useState({
        hasNegativeFeedback: false,
    })

    // Debounce search
    useEffect(() => {
        const timer = setTimeout(() => {
            setDebouncedSearch(searchQuery)
        }, 300)
        return () => clearTimeout(timer)
    }, [searchQuery])

    const { data, isLoading, refetch } = useQuery({
        queryKey: ['admin', 'conversations', debouncedSearch, filters],
        queryFn: () => adminApi.getConversations({
            search: debouncedSearch || undefined,
            hasNegativeFeedback: filters.hasNegativeFeedback || undefined
        }),
    })

    // Load conversation detail when selected
    const { data: conversationDetail, isLoading: isLoadingDetail } = useQuery({
        queryKey: ['admin', 'conversation-detail', selectedSessionId],
        queryFn: () => adminApi.getConversationDetail(selectedSessionId!),
        enabled: !!selectedSessionId,
    })

    const filteredConversations = data?.data || []

    const getStatusBadge = (status: AdminConversation['status']) => {
        const styles = {
            active: 'bg-success/10 text-success border border-success/20',
            issues: 'bg-warning/10 text-warning border border-warning/20',
            multiple_issues: 'bg-error/10 text-error border border-error/20',
            archived: 'bg-neutral-100 text-neutral-500 border border-neutral-200',
        }
        const labels = {
            active: 'Active',
            issues: 'Has Issues',
            multiple_issues: 'Multiple Issues',
            archived: 'Archived',
        }
        return (
            <span className={cn('px-2.5 py-1 rounded-md text-xs font-medium', styles[status])}>
                {labels[status]}
            </span>
        )
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-semibold tracking-tight text-neutral-900">Conversations</h2>
                    <p className="text-sm text-[var(--muted)] mt-1">Browse and manage chat sessions.</p>
                </div>
                <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm">
                        <Download className="w-4 h-4 mr-2" />
                        Export
                    </Button>
                    <Button variant="outline" size="sm" onClick={() => refetch()} disabled={isLoading}>
                        <RefreshCw className={cn("w-4 h-4 mr-2", isLoading && "animate-spin")} />
                        Refresh
                    </Button>
                </div>
            </div>

            {/* Filters */}
            <Card>
                <CardContent className="p-4">
                    <div className="flex flex-wrap items-center gap-3">
                        <div className="relative flex-1 min-w-[200px]">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
                            <Input
                                placeholder="Search conversations..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="pl-9 h-9 bg-[var(--surface2)]"
                            />
                        </div>
                        <Button variant="ghost" size="sm" className="h-9 rounded-full bg-[var(--surface2)] shadow-sm">
                            <Filter className="w-4 h-4 mr-2" />
                            User
                        </Button>
                        <Button variant="ghost" size="sm" className="h-9 rounded-full bg-[var(--surface2)] shadow-sm">
                            <Filter className="w-4 h-4 mr-2" />
                            Status
                        </Button>
                        <Button variant="ghost" size="sm" className="h-9 rounded-full bg-[var(--surface2)] shadow-sm">
                            <Filter className="w-4 h-4 mr-2" />
                            Date Range
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
                                className="h-4 w-4 rounded border-[color:var(--border)] text-primary focus:ring-2 focus:ring-[var(--ring)]"
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
                    <div className="overflow-x-auto rounded-[var(--radius)] bg-[var(--surface)] shadow-sm">
                        <table className="w-full text-sm">
                            <thead className="sticky top-0 bg-[var(--surface)] shadow-[var(--shadow-sm)]">
                                <tr>
                                    <th className="text-left py-3 px-4 font-medium text-[var(--muted)] w-10">
                                        <input type="checkbox" className="h-4 w-4 rounded border-[color:var(--border)]" />
                                    </th>
                                    <th className="text-left py-3 px-4 font-medium text-[var(--muted)]">
                                        User
                                    </th>
                                    <th className="text-left py-3 px-4 font-medium text-[var(--muted)]">
                                        Title
                                    </th>
                                    <th className="text-left py-3 px-4 font-medium text-[var(--muted)]">
                                        Msgs
                                    </th>
                                    <th className="text-left py-3 px-4 font-medium text-[var(--muted)]">
                                        Last Active
                                    </th>
                                    <th className="text-left py-3 px-4 font-medium text-[var(--muted)]">
                                        Status
                                    </th>
                                    <th className="text-left py-3 px-4 font-medium text-[var(--muted)] w-14"></th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredConversations.map((conv) => (
                                    <tr
                                        key={conv.id}
                                        className="border-b border-[color:var(--border)] last:border-0 hover:bg-[var(--surface2)] cursor-pointer transition-colors"
                                        onClick={() => setSelectedSessionId(conv.id)}
                                    >
                                        <td className="py-3 px-4" onClick={(e) => e.stopPropagation()}>
                                            <input type="checkbox" className="h-4 w-4 rounded border-[color:var(--border)]" />
                                        </td>
                                        <td className="py-3 px-4">
                                            <div className="flex items-center gap-2">
                                                <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-primary font-medium text-sm">
                                                    {conv.userName?.charAt(0)?.toUpperCase() || 'U'}
                                                </div>
                                                <div>
                                                    <p className="text-sm font-medium">{conv.userName}</p>
                                                    <p className="text-xs text-neutral-500">{conv.studentId}</p>
                                                </div>
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
                                                    <DropdownMenuItem onClick={() => setSelectedSessionId(conv.id)}>
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
                    <div className="flex items-center justify-between p-4">
                        <p className="text-sm text-[var(--muted)]">
                            Showing 1-{filteredConversations.length} of {data?.total || 0} conversations
                        </p>
                        <div className="flex items-center gap-2">
                            <Button variant="outline" size="sm" disabled>
                                <ChevronLeft className="w-4 h-4" />
                                Prev
                            </Button>
                            <Button variant="outline" size="sm" className="bg-primary text-white border-transparent">
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
            <div className="flex items-center gap-4 text-sm">
                <span className="text-neutral-500">Status:</span>
                <div className="flex items-center gap-2">
                    <span className="inline-block w-2 h-2 rounded-full bg-success"></span>
                    <span className="text-neutral-600">Active</span>
                </div>
                <div className="flex items-center gap-2">
                    <span className="inline-block w-2 h-2 rounded-full bg-warning"></span>
                    <span className="text-neutral-600">Has Issues</span>
                </div>
                <div className="flex items-center gap-2">
                    <span className="inline-block w-2 h-2 rounded-full bg-error"></span>
                    <span className="text-neutral-600">Multiple Issues</span>
                </div>
                <div className="flex items-center gap-2">
                    <span className="inline-block w-2 h-2 rounded-full bg-neutral-400"></span>
                    <span className="text-neutral-600">Archived</span>
                </div>
            </div>

            {/* Conversation Detail Modal */}
            <Dialog open={!!selectedSessionId} onOpenChange={() => setSelectedSessionId(null)}>
                <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
                    <DialogHeader>
                        <DialogTitle className="flex items-center gap-2">
                            {conversationDetail?.session.title || 'Loading...'}
                        </DialogTitle>
                        <DialogDescription className="sr-only">
                            Chi tiết cuộc trò chuyện và thông tin người dùng liên quan.
                        </DialogDescription>
                    </DialogHeader>
                    {isLoadingDetail ? (
                        <div className="flex items-center justify-center py-8">
                            <RefreshCw className="w-6 h-6 animate-spin text-neutral-400" />
                        </div>
                    ) : conversationDetail && (
                        <div className="grid grid-cols-3 gap-6">
                            {/* Messages */}
                            <div className="col-span-2 space-y-4">
                                <div className="p-4 bg-[var(--surface2)] rounded-[var(--radius)]">
                                    <p className="text-sm text-neutral-500 mb-4">Session: {conversationDetail.session.id}</p>
                                    <div className="space-y-4 max-h-[400px] overflow-y-auto">
                                        {conversationDetail.messages.map((msg) => (
                                            <div key={msg.id} className={cn(
                                                "flex",
                                                msg.role === 'user' ? 'justify-end' : 'justify-start'
                                            )}>
                                                <div className={cn(
                                                    "rounded-2xl px-4 py-2 max-w-[80%]",
                                                    msg.role === 'user'
                                                        ? 'bg-primary text-white rounded-br-md'
                                                        : 'bg-[var(--surface)] shadow-sm rounded-bl-md'
                                                )}>
                                                    <div className="text-sm whitespace-pre-wrap prose prose-sm max-w-none">
                                                        <ReactMarkdown>{msg.content}</ReactMarkdown>
                                                    </div>
                                                    {msg.feedback && (
                                                        <div className="mt-2 pt-2 border-t border-neutral-200 flex items-center gap-2">
                                                            {msg.feedback.type === 'helpful' ? (
                                                                <span className="text-xs text-success flex items-center gap-1">
                                                                    👍 Helpful
                                                                </span>
                                                            ) : (
                                                                <span className="text-xs text-error flex items-center gap-1">
                                                                    👎 Not helpful
                                                                    {msg.feedback.comment && (
                                                                        <span className="text-neutral-500">: {msg.feedback.comment}</span>
                                                                    )}
                                                                </span>
                                                            )}
                                                        </div>
                                                    )}
                                                    <p className="text-xs opacity-70 mt-1">{formatDate(msg.created_at)}</p>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>

                            {/* User Info */}
                            <div className="space-y-4">
                                <div className="p-4 bg-[var(--surface2)] rounded-[var(--radius)]">
                                    <div className="flex items-center gap-3 mb-4">
                                        <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center text-primary font-semibold text-lg">
                                            {conversationDetail.user_profile?.name?.charAt(0)?.toUpperCase() ||
                                                conversationDetail.session.user_name?.charAt(0)?.toUpperCase() || 'U'}
                                        </div>
                                        <div>
                                            <h4 className="font-medium">User Info</h4>
                                            <p className="text-xs text-neutral-500">Student Profile</p>
                                        </div>
                                    </div>
                                    <div className="space-y-2 text-sm">
                                        <div className="flex justify-between">
                                            <span className="text-neutral-500">Name:</span>
                                            <span className="font-medium">
                                                {conversationDetail.user_profile?.name || conversationDetail.session.user_name || 'N/A'}
                                            </span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-neutral-500">Student ID:</span>
                                            <span className="font-medium">
                                                {conversationDetail.user_profile?.student_id || 'N/A'}
                                            </span>
                                        </div>
                                        {conversationDetail.user_profile?.major && (
                                            <div className="flex justify-between">
                                                <span className="text-neutral-500">Major:</span>
                                                <span className="font-medium">{conversationDetail.user_profile.major}</span>
                                            </div>
                                        )}
                                        {conversationDetail.user_profile?.level && (
                                            <div className="flex justify-between">
                                                <span className="text-neutral-500">Level:</span>
                                                <span className="font-medium">{conversationDetail.user_profile.level}</span>
                                            </div>
                                        )}
                                        <div className="flex justify-between">
                                            <span className="text-neutral-500">Messages:</span>
                                            <span className="font-medium">{conversationDetail.session.message_count}</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-neutral-500">Last Active:</span>
                                            <span className="font-medium text-xs">{formatDate(conversationDetail.session.last_activity)}</span>
                                        </div>
                                    </div>
                                </div>

                                <div className="flex flex-col gap-2">
                                    <Button
                                        variant="outline"
                                        size="sm"
                                        onClick={() => {
                                            if (conversationDetail.session.user_id) {
                                                navigate(`/admin/users/${conversationDetail.session.user_id}`)
                                                setSelectedSessionId(null)
                                            }
                                        }}
                                        disabled={!conversationDetail.session.user_id}
                                    >
                                        View Full Profile
                                    </Button>
                                    <Button
                                        variant="outline"
                                        size="sm"
                                        onClick={() => {
                                            if (conversationDetail.session.user_id) {
                                                navigate(`/admin/conversations?userId=${conversationDetail.session.user_id}`)
                                                setSelectedSessionId(null)
                                            }
                                        }}
                                        disabled={!conversationDetail.session.user_id}
                                    >
                                        View All Sessions
                                    </Button>
                                </div>
                            </div>
                        </div>
                    )}
                    <div className="flex gap-2 mt-4 pt-4">
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

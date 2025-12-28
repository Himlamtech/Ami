import { useState } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import {
    Bot,
    Sparkles,
    Search,
    MessageSquareText,
    User,
    MoreHorizontal,
    Trash2,
    X,
    Shield,
    LogOut,
    Bookmark,
    PenLine,
} from 'lucide-react'
import { chatApi, type Session } from '@/features/chat/api/chatApi'

import { useAuthStore } from '@/stores/authStore'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { cn } from '@/lib/utils'

interface ChatSidebarProps {
    onClose?: () => void
}

export default function ChatSidebar({ onClose }: ChatSidebarProps) {
    const [searchQuery, setSearchQuery] = useState('')
    const [isCreatingSession, setIsCreatingSession] = useState(false)
    const navigate = useNavigate()
    const queryClient = useQueryClient()
    const { logout } = useAuthStore()

    // Fetch sessions from backend
    const { data: sessions = [], isLoading } = useQuery({
        queryKey: ['sessions'],
        queryFn: chatApi.getSessions,
        staleTime: 30000, // 30 seconds
    })

    const filteredSessions = sessions.filter((session) =>
        (session.title || '').toLowerCase().includes(searchQuery.toLowerCase())
    )

    const groupedSessions = {
        today: filteredSessions.filter((s) => {
            const date = new Date(s.updated_at || s.created_at)
            const today = new Date()
            return date.toDateString() === today.toDateString()
        }),
        yesterday: filteredSessions.filter((s) => {
            const date = new Date(s.updated_at || s.created_at)
            const yesterday = new Date(Date.now() - 86400000)
            return date.toDateString() === yesterday.toDateString()
        }),
        older: filteredSessions.filter((s) => {
            const date = new Date(s.updated_at || s.created_at)
            const yesterday = new Date(Date.now() - 86400000)
            return date < yesterday
        }),
    }

    const handleNewChat = async () => {
        if (isCreatingSession) return
        setIsCreatingSession(true)
        try {
            const session = await chatApi.createSession()
            queryClient.invalidateQueries({ queryKey: ['sessions'] })
            navigate(`/chat/${session.id}`)
            onClose?.()
        } catch (error) {
            console.error('[ChatSidebar] Failed to create new chat', error)
        } finally {
            setIsCreatingSession(false)
        }
    }

    return (
        <div className="flex flex-col h-full bg-[var(--panel)]">
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-3 shadow-sm">
                <div className="flex items-center gap-3">
                    <div>
                        <span className="font-bold text-2xl text-red-600 block leading-none">AMI</span>
                        <span className="text-xs text-neutral-500 mt-0.5 block">AI Assistant</span>
                    </div>
                </div>
                <Button variant="ghost" size="icon" className="lg:hidden" onClick={onClose}>
                    <X className="w-5 h-5" />
                </Button>
            </div>

            {/* New Chat Button */}
            <div className="px-4 py-3">
                <Button
                    onClick={handleNewChat}
                    className="w-full gap-2 h-10 font-medium bg-[var(--surface)] border-[color:var(--border)] hover:bg-[var(--surface2)] shadow-sm"
                    variant="outline"
                    disabled={isCreatingSession}
                >
                    <Sparkles className="w-4 h-4" />
                    Cuộc trò chuyện mới
                </Button>
            </div>

            {/* Search */}
            <div className="px-4 py-2">
                <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
                    <Input
                        placeholder="Tìm kiếm..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="pl-9 bg-[var(--surface)] border-[color:var(--border)] focus-visible:ring-[var(--ring)]"
                    />
                </div>
            </div>

            {/* Bookmarks Link */}
            <div className="px-4 pb-2">
                <NavLink
                    to="/chat/saved"
                    className={({ isActive }) =>
                        cn(
                            'flex items-center gap-2 px-3 py-2 rounded-xl text-sm font-medium transition-colors bg-[var(--surface)] shadow-sm hover:bg-[var(--surface2)]',
                            isActive ? 'bg-primary/5 text-primary' : 'text-neutral-700'
                        )
                    }
                >
                    <Bookmark className="w-4 h-4" />
                    <span>Đã lưu</span>
                </NavLink>
            </div>

            {/* Conversations List */}
            <ScrollArea className="flex-1 px-2">
                {isLoading ? (
                    <div className="flex items-center justify-center py-8">
                        <div className="animate-spin rounded-full h-6 w-6 border-2 border-primary border-t-transparent" />
                    </div>
                ) : (
                    <>
                        {groupedSessions.today.length > 0 && (
                            <SessionGroup title="Hôm nay" sessions={groupedSessions.today} />
                        )}
                        {groupedSessions.yesterday.length > 0 && (
                            <SessionGroup title="Hôm qua" sessions={groupedSessions.yesterday} />
                        )}
                        {groupedSessions.older.length > 0 && (
                            <SessionGroup title="Trước đó" sessions={groupedSessions.older} />
                        )}
                        {filteredSessions.length === 0 && (
                            <p className="text-center text-sm text-neutral-500 py-8">
                                Chưa có cuộc trò chuyện nào
                            </p>
                        )}
                    </>
                )}
            </ScrollArea>

            <Separator />

            {/* Footer */}
            <div className="p-3 space-y-1">
                {/* Show admin link for all users - simplified for now */}
                <NavLink
                    to="/admin"
                    className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-neutral-600 hover:bg-[var(--surface)] hover:text-neutral-900 transition-colors"
                >
                    <Shield className="w-5 h-5" />
                    <span>Admin Panel</span>
                </NavLink>
                <NavLink
                    to="/chat/profile"
                    className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-neutral-600 hover:bg-[var(--surface)] hover:text-neutral-900 transition-colors"
                >
                    <User className="w-5 h-5" />
                    <span>Hồ sơ</span>
                </NavLink>
                <button
                    onClick={() => {
                        logout()
                        navigate('/login')
                    }}
                    className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-red-600 hover:bg-red-50 transition-colors"
                >
                    <LogOut className="w-5 h-5" />
                    <span>Đăng xuất</span>
                </button>
            </div>
        </div>
    )
}

function SessionGroup({
    title,
    sessions,
}: {
    title: string
    sessions: Session[]
}) {
    return (
        <div className="mb-4">
            <p className="px-3 py-2 text-[10px] font-semibold tracking-wider uppercase text-neutral-500">{title}</p>
            <div className="space-y-1">
                {sessions.map((session) => (
                    <SessionItem key={session.id} session={session} />
                ))}
            </div>
        </div>
    )
}

function SessionItem({ session }: { session: Session }) {
    const [isRenaming, setIsRenaming] = useState(false)
    const [newTitle, setNewTitle] = useState(session.title || 'Cuộc trò chuyện mới')
    const queryClient = useQueryClient()

    const handleRename = async () => {
        if (!newTitle.trim()) return
        try {
            // TODO: Call API to update session title
            // await chatApi.updateSession(session.id, { title: newTitle })
            queryClient.invalidateQueries({ queryKey: ['sessions'] })
            setIsRenaming(false)
        } catch (error) {
            console.error('Failed to rename session', error)
        }
    }

    const handleDelete = async () => {
        if (!confirm('Bạn có chắc muốn xóa cuộc trò chuyện này?')) return
        try {
            await chatApi.deleteConversation(session.id)
            queryClient.invalidateQueries({ queryKey: ['sessions'] })
        } catch (error) {
            console.error('Failed to delete session', error)
        }
    }

    const handleBookmark = async () => {
        try {
            // TODO: Call API to bookmark session
            console.log('Bookmark session:', session.id)
        } catch (error) {
            console.error('Failed to bookmark session', error)
        }
    }

    if (isRenaming) {
        return (
            <div className="px-3 py-2.5">
                <Input
                    value={newTitle}
                    onChange={(e) => setNewTitle(e.target.value)}
                    onBlur={handleRename}
                    onKeyDown={(e) => {
                        if (e.key === 'Enter') handleRename()
                        if (e.key === 'Escape') setIsRenaming(false)
                    }}
                    autoFocus
                    className="h-8 text-sm"
                />
            </div>
        )
    }

    return (
        <NavLink
            to={`/chat/${session.id}`}
            className={({ isActive }) =>
                cn(
                    'group relative flex items-center gap-3 px-3 py-2 rounded-xl transition-colors',
                    isActive
                        ? 'bg-primary/10 text-neutral-900 before:absolute before:left-0 before:top-1.5 before:bottom-1.5 before:w-0.5 before:rounded-full before:bg-primary'
                        : 'hover:bg-[var(--surface)] text-neutral-700'
                )
            }
        >
            <MessageSquareText className="w-5 h-5 mt-0.5 flex-shrink-0 text-neutral-400 group-hover:text-neutral-600" />
            <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{session.title || 'Cuộc trò chuyện mới'}</p>
                <p className="text-xs text-neutral-500">
                    {session.message_count || 0} tin nhắn
                </p>
            </div>
            <DropdownMenu>
                <DropdownMenuTrigger asChild>
                    <Button
                        variant="ghost"
                        size="icon"
                        className="w-7 h-7 flex-shrink-0 text-neutral-400 hover:text-neutral-600"
                        onClick={(e) => e.preventDefault()}
                    >
                        <MoreHorizontal className="w-4 h-4" />
                    </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-48">
                    <DropdownMenuLabel className="text-xs text-neutral-500">Actions</DropdownMenuLabel>
                    <DropdownMenuItem onClick={(e) => {
                        e.preventDefault()
                        handleBookmark()
                    }}>
                        <Bookmark className="w-4 h-4 mr-2" />
                        Bookmark
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={(e) => {
                        e.preventDefault()
                        setIsRenaming(true)
                    }}>
                        <PenLine className="w-4 h-4 mr-2" />
                        Rename
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem>
                        <Shield className="w-4 h-4 mr-2" />
                        Archive
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem
                        className="text-red-600 focus:text-red-600"
                        onClick={(e) => {
                            e.preventDefault()
                            handleDelete()
                        }}
                    >
                        <Trash2 className="w-4 h-4 mr-2" />
                        Delete
                    </DropdownMenuItem>
                </DropdownMenuContent>
            </DropdownMenu>
        </NavLink>
    )
}

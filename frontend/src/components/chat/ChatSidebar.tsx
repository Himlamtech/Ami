import { useState } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
    Bot,
    Plus,
    Search,
    MessageSquare,
    Settings,
    User,
    MoreHorizontal,
    Trash2,
    Archive,
    X,
    Shield,
    LogOut,
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
    DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { cn } from '@/lib/utils'

interface ChatSidebarProps {
    onClose?: () => void
}

export default function ChatSidebar({ onClose }: ChatSidebarProps) {
    const [searchQuery, setSearchQuery] = useState('')
    const navigate = useNavigate()
    const { user, logout } = useAuthStore()

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

    const handleNewChat = () => {
        navigate('/')
        onClose?.()
    }

    return (
        <div className="flex flex-col h-full">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-neutral-200">
                <div className="flex items-center gap-3">
                    <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-primary text-white">
                        <Bot className="w-6 h-6" />
                    </div>
                    <span className="font-bold text-lg text-neutral-900">AMI</span>
                </div>
                <Button variant="ghost" size="icon" className="lg:hidden" onClick={onClose}>
                    <X className="w-5 h-5" />
                </Button>
            </div>

            {/* New Chat Button */}
            <div className="p-4">
                <Button onClick={handleNewChat} className="w-full gap-2">
                    <Plus className="w-4 h-4" />
                    Cuộc trò chuyện mới
                </Button>
            </div>

            {/* Search */}
            <div className="px-4 pb-4">
                <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
                    <Input
                        placeholder="Tìm kiếm..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="pl-9"
                    />
                </div>
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
                {/* Show admin link only for admin users */}
                {user?.email?.toLowerCase().includes('admin') && (
                    <NavLink
                        to="/admin"
                        className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900 transition-colors"
                    >
                        <Shield className="w-5 h-5" />
                        <span>Admin Panel</span>
                    </NavLink>
                )}
                <NavLink
                    to="/settings"
                    className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900 transition-colors"
                >
                    <Settings className="w-5 h-5" />
                    <span>Cài đặt</span>
                </NavLink>
                <NavLink
                    to="/profile"
                    className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900 transition-colors"
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
            <p className="px-3 py-2 text-xs font-medium text-neutral-500 uppercase">{title}</p>
            <div className="space-y-1">
                {sessions.map((session) => (
                    <SessionItem key={session.id} session={session} />
                ))}
            </div>
        </div>
    )
}

function SessionItem({ session }: { session: Session }) {
    return (
        <NavLink
            to={`/chat/${session.id}`}
            className={({ isActive }) =>
                cn(
                    'group flex items-start gap-3 px-3 py-2.5 rounded-lg transition-colors',
                    isActive ? 'bg-primary/10 text-primary' : 'hover:bg-neutral-100'
                )
            }
        >
            <MessageSquare className="w-5 h-5 mt-0.5 flex-shrink-0" />
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
                        className="w-6 h-6 opacity-0 group-hover:opacity-100 transition-opacity"
                        onClick={(e) => e.preventDefault()}
                    >
                        <MoreHorizontal className="w-4 h-4" />
                    </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                    <DropdownMenuItem>
                        <Archive className="w-4 h-4 mr-2" />
                        Lưu trữ
                    </DropdownMenuItem>
                    <DropdownMenuItem className="text-error">
                        <Trash2 className="w-4 h-4 mr-2" />
                        Xóa
                    </DropdownMenuItem>
                </DropdownMenuContent>
            </DropdownMenu>
        </NavLink>
    )
}

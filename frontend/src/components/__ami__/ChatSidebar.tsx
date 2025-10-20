import { useEffect, useState } from 'react'
import { Plus, Search, Trash2 } from 'lucide-react'
import { useChatStore } from '../../store/chatStore'
import { apiClient } from '../../api/client'
import '@styles/__ami__/ChatSidebar.css'

interface ChatSidebarProps {
    isOpen: boolean
    onNewChat: () => void
    onLoadSession: (sessionId: string) => void
}

export default function ChatSidebar({
    isOpen,
    onNewChat,
    onLoadSession,
}: ChatSidebarProps) {
    const { sessions, setSessions, currentSession } = useChatStore()
    const [isLoading, setIsLoading] = useState(false)
    const [searchTerm, setSearchTerm] = useState('')

    useEffect(() => {
        loadSessions()
    }, [])

    const loadSessions = async () => {
        try {
            setIsLoading(true)
            const result = await apiClient.listSessions(0, 50)
            setSessions(result.sessions)
        } catch (error) {
            console.error('Failed to load sessions:', error)
        } finally {
            setIsLoading(false)
        }
    }

    const handleDeleteSession = async (sessionId: string, e: React.MouseEvent) => {
        e.stopPropagation()
        if (confirm('Are you sure you want to delete this chat?')) {
            try {
                await apiClient.deleteSession(sessionId)
                setSessions(sessions.filter((s) => s.id !== sessionId))
            } catch (error) {
                console.error('Failed to delete session:', error)
            }
        }
    }

    const filteredSessions = sessions.filter((s: any) =>
        s.title.toLowerCase().includes(searchTerm.toLowerCase())
    )

    return (
        <aside className={`chat-sidebar ${!isOpen ? 'collapsed' : ''}`}>
            <div className="sidebar-header">
                <button className="btn-new-chat" onClick={onNewChat}>
                    <Plus size={18} />
                    <span>New Chat</span>
                </button>
            </div>

            <div className="sidebar-search">
                <Search size={16} className="search-icon" />
                <input
                    type="text"
                    placeholder="Search chats..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="search-input"
                />
            </div>

            <div className="sessions-list">
                {isLoading ? (
                    <div className="loading-skeleton">
                        {[1, 2, 3].map((i) => (
                            <div key={i} className="skeleton-item"></div>
                        ))}
                    </div>
                ) : filteredSessions.length > 0 ? (
                    filteredSessions.map((session: any) => (
                        <div
                            key={session.id}
                            className={`session-item ${currentSession?.id === session.id ? 'active' : ''}`}
                            onClick={() => onLoadSession(session.id)}
                        >
                            <div className="session-content">
                                <div className="session-title">{session.title}</div>
                                {session.summary && <div className="session-summary">{session.summary}</div>}
                            </div>
                            <button
                                className="btn-delete"
                                onClick={(e) => handleDeleteSession(session.id, e)}
                                title="Delete chat"
                            >
                                <Trash2 size={14} />
                            </button>
                        </div>
                    ))
                ) : (
                    <div className="empty-state">
                        <p>No chats yet</p>
                        <p className="text-hint">Start a new chat to begin</p>
                    </div>
                )}
            </div>
        </aside>
    )
}

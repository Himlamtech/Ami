import { Menu, Settings } from 'lucide-react'
import { useChatStore } from '../../store/chatStore'
import '@styles/__ami__/ChatHeader.css'

interface ChatHeaderProps {
    onToggleSidebar: () => void
    onToggleSettings: () => void
}

export default function ChatHeader({ onToggleSidebar, onToggleSettings }: ChatHeaderProps) {
    const { currentSession } = useChatStore()

    return (
        <header className="chat-header">
            <div className="header-left">
                <button className="btn-icon" onClick={onToggleSidebar} title="Toggle sidebar">
                    <Menu size={20} />
                </button>
                <div className="header-title">
                    {currentSession ? (
                        <>
                            <span className="title-main">{currentSession.title}</span>
                            {currentSession.message_count > 0 && (
                                <span className="title-meta">({currentSession.message_count} messages)</span>
                            )}
                        </>
                    ) : (
                        <span className="title-main">New Chat</span>
                    )}
                </div>
            </div>

            <div className="header-right">
                <button className="btn-icon" onClick={onToggleSettings} title="Settings">
                    <Settings size={20} />
                </button>
            </div>
        </header>
    )
}

// CSS will be imported via global index.css

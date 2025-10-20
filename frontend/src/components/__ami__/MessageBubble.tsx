import { ChatMessage } from '../../api/client'
import '@styles/__ami__/MessageBubble.css'

interface MessageBubbleProps {
    message: ChatMessage
}

export default function MessageBubble({ message }: MessageBubbleProps) {
    const isUser = message.role === 'user'

    return (
        <div className={`message ${isUser ? 'user' : 'assistant'}`}>
            <div className={`message-bubble ${isUser ? 'user-bubble' : 'assistant-bubble'}`}>
                <div className="message-content">
                    {message.content}
                </div>
                <div className="message-time">
                    {new Date(message.created_at).toLocaleTimeString([], {
                        hour: '2-digit',
                        minute: '2-digit',
                    })}
                </div>
            </div>
        </div>
    )
}

// CSS will be imported via global index.css

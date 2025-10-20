import { forwardRef } from 'react'
import { MessageSquare } from 'lucide-react'
import { ChatMessage } from '../../api/client'
import MessageBubble from './MessageBubble'
import '@styles/__ami__/MessageList.css'

interface MessageListProps {
    messages: ChatMessage[]
    isLoading: boolean
}

const MessageList = forwardRef<HTMLDivElement, MessageListProps>(
    ({ messages, isLoading }, ref) => {
        return (
            <div className="message-list">
                {messages.length === 0 ? (
                    <div className="message-empty-state">
                        <div className="empty-icon">
                            <MessageSquare size={64} strokeWidth={1.5} />
                        </div>
                        <h2>Start Your Conversation</h2>
                        <p>Ask anything and get instant answers powered by AI</p>
                    </div>
                ) : (
                    messages.map((message) => (
                        <MessageBubble key={message.id} message={message} />
                    ))
                )}

                {isLoading && (
                    <div className="message loading">
                        <div className="message-bubble assistant-bubble">
                            <div className="typing-indicator">
                                <span></span>
                                <span></span>
                                <span></span>
                            </div>
                        </div>
                    </div>
                )}

                <div ref={ref} />
            </div>
        )
    }
)

MessageList.displayName = 'MessageList'
export default MessageList

// CSS will be imported via global index.css

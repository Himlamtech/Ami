import { ChatMessage } from '../../api/client'
import { FileText, ExternalLink } from 'lucide-react'
import '@styles/__ami__/MessageBubble.css'

interface MessageBubbleProps {
    message: ChatMessage
}

export default function MessageBubble({ message }: MessageBubbleProps) {
    const isUser = message.role === 'user'
    const sources = message.metadata?.sources as Array<{ title: string; url?: string; page?: number }> | undefined
    const webSources = message.metadata?.web_sources as Array<{ title: string; url: string }> | undefined

    return (
        <div className={`message ${isUser ? 'user' : 'assistant'}`}>
            <div className={`message-bubble ${isUser ? 'user-bubble' : 'assistant-bubble'}`}>
                <div className="message-content">
                    {message.content}
                </div>

                {(sources?.length || webSources?.length) ? (
                    <div className="message-sources">
                        <div className="sources-title">Sources:</div>
                        <div className="sources-list">
                            {sources?.map((source, i) => (
                                <div key={`doc-${i}`} className="source-item" title={source.title}>
                                    <FileText size={12} />
                                    <span className="source-name">
                                        {source.title}
                                        {source.page && ` (p.${source.page})`}
                                    </span>
                                </div>
                            ))}
                            {webSources?.map((source, i) => (
                                <a
                                    key={`web-${i}`}
                                    href={source.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="source-item link"
                                >
                                    <ExternalLink size={12} />
                                    <span className="source-name">{source.title}</span>
                                </a>
                            ))}
                        </div>
                    </div>
                ) : null}

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

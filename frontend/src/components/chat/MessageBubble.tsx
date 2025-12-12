import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism'
import {
    Bot,
    ThumbsUp,
    ThumbsDown,
    Copy,
    Bookmark,
    Check,
    ExternalLink,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from '@/components/ui/tooltip'
import { cn, formatTime } from '@/lib/utils'
import type { Message, Source } from '@/types/chat'

interface MessageBubbleProps {
    message: Message
    onFeedback?: (type: 'helpful' | 'not_helpful') => void
}

export default function MessageBubble({ message, onFeedback }: MessageBubbleProps) {
    const [copied, setCopied] = useState(false)
    const isUser = message.role === 'user'

    const handleCopy = async () => {
        await navigator.clipboard.writeText(message.content)
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
    }

    return (
        <div className={cn('flex gap-3', isUser ? 'flex-row-reverse' : 'flex-row')}>
            {/* Avatar */}
            {!isUser && (
                <Avatar className="w-10 h-10 flex-shrink-0">
                    <AvatarFallback className="bg-primary text-white">
                        <Bot className="w-5 h-5" />
                    </AvatarFallback>
                </Avatar>
            )}

            {/* Message content */}
            <div className={cn('flex flex-col max-w-[80%]', isUser ? 'items-end' : 'items-start')}>
                <div
                    className={cn(
                        'rounded-2xl px-4 py-3 text-sm leading-relaxed',
                        isUser
                            ? 'bg-[var(--surface)] text-neutral-900 rounded-br-md shadow-sm'
                            : 'bg-[var(--surface2)] text-neutral-900 rounded-bl-md shadow-sm'
                    )}
                >
                    {message.isStreaming ? (
                        <div className="flex items-center gap-2">
                            <span className="text-sm">AMI đang suy nghĩ</span>
                            <div className="flex gap-1">
                                <span className="w-1.5 h-1.5 bg-current rounded-full animate-pulse-dot" />
                                <span className="w-1.5 h-1.5 bg-current rounded-full animate-pulse-dot" />
                                <span className="w-1.5 h-1.5 bg-current rounded-full animate-pulse-dot" />
                            </div>
                        </div>
                    ) : (
                        <div className="text-[15px] leading-7 text-neutral-900 space-y-2 [&_ul]:list-disc [&_ul]:pl-5 [&_ol]:list-decimal [&_ol]:pl-5 [&_li]:my-1 [&_a]:text-primary hover:[&_a]:underline [&_a]:underline-offset-2">
                            <ReactMarkdown
                                components={{
                                    code({ className, children, ...props }) {
                                        const match = /language-(\w+)/.exec(className || '')
                                        const isInline = !match
                                        return isInline ? (
                                            <code
                                                className={cn(
                                                    'px-1.5 py-0.5 rounded text-sm font-mono',
                                                    'bg-[var(--surface)]'
                                                )}
                                                {...props}
                                            >
                                                {children}
                                            </code>
                                        ) : (
                                            <SyntaxHighlighter
                                                style={oneDark}
                                                language={match[1]}
                                                PreTag="div"
                                                className="rounded-lg !mt-2 !mb-2"
                                            >
                                                {String(children).replace(/\n$/, '')}
                                            </SyntaxHighlighter>
                                        )
                                    },
                                    table({ children }) {
                                        return (
                                            <div className="overflow-x-auto my-2">
                                                <table className="min-w-full border-collapse border border-[color:var(--border)]">
                                                    {children}
                                                </table>
                                            </div>
                                        )
                                    },
                                    th({ children }) {
                                        return (
                                            <th className="border border-[color:var(--border)] px-3 py-2 bg-[var(--surface2)] text-left font-medium">
                                                {children}
                                            </th>
                                        )
                                    },
                                    td({ children }) {
                                        return (
                                            <td className="border border-[color:var(--border)] px-3 py-2">{children}</td>
                                        )
                                    },
                                }}
                            >
                                {message.content}
                            </ReactMarkdown>
                        </div>
                    )}
                </div>

                {/* Sources */}
                {!isUser && message.sources && message.sources.length > 0 && (
                    <div className="mt-2 p-2.5 bg-[var(--surface2)] rounded-xl shadow-sm w-full">
                        <p className="text-xs font-medium text-neutral-400 mb-1.5">📄 Nguồn:</p>
                        <div className="space-y-1">
                            {message.sources.map((source, index) => (
                                <SourceItem key={source.id} source={source} index={index + 1} />
                            ))}
                        </div>
                    </div>
                )}

                {/* Actions */}
                {!isUser && !message.isStreaming && (
                    <div className="flex items-center gap-1 mt-2">
                        <TooltipProvider>
                            <Tooltip>
                                <TooltipTrigger asChild>
                                    <Button
                                        variant="ghost"
                                        size="sm"
                                        className={cn(
                                            'h-8 px-2 text-neutral-500 hover:text-success',
                                            message.feedback?.type === 'helpful' && 'text-success bg-success/10'
                                        )}
                                        onClick={() => onFeedback?.('helpful')}
                                    >
                                        <ThumbsUp className="w-4 h-4" />
                                    </Button>
                                </TooltipTrigger>
                                <TooltipContent>Hữu ích</TooltipContent>
                            </Tooltip>

                            <Tooltip>
                                <TooltipTrigger asChild>
                                    <Button
                                        variant="ghost"
                                        size="sm"
                                        className={cn(
                                            'h-8 px-2 text-neutral-500 hover:text-error',
                                            message.feedback?.type === 'not_helpful' && 'text-error bg-error/10'
                                        )}
                                        onClick={() => onFeedback?.('not_helpful')}
                                    >
                                        <ThumbsDown className="w-4 h-4" />
                                    </Button>
                                </TooltipTrigger>
                                <TooltipContent>Không hữu ích</TooltipContent>
                            </Tooltip>

                            <Tooltip>
                                <TooltipTrigger asChild>
                                    <Button
                                        variant="ghost"
                                        size="sm"
                                        className="h-8 px-2 text-neutral-500"
                                        onClick={handleCopy}
                                    >
                                        {copied ? (
                                            <Check className="w-4 h-4 text-success" />
                                        ) : (
                                            <Copy className="w-4 h-4" />
                                        )}
                                    </Button>
                                </TooltipTrigger>
                                <TooltipContent>{copied ? 'Đã sao chép' : 'Sao chép'}</TooltipContent>
                            </Tooltip>

                            <Tooltip>
                                <TooltipTrigger asChild>
                                    <Button variant="ghost" size="sm" className="h-8 px-2 text-neutral-500">
                                        <Bookmark className="w-4 h-4" />
                                    </Button>
                                </TooltipTrigger>
                                <TooltipContent>Lưu lại</TooltipContent>
                            </Tooltip>
                        </TooltipProvider>
                    </div>
                )}

                {/* Timestamp */}
                <span className="text-xs text-neutral-400 mt-1">{formatTime(message.timestamp)}</span>
            </div>
        </div>
    )
}

function SourceItem({ source, index }: { source: Source; index: number }) {
    return (
        <a
            href={source.url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 text-xs text-neutral-600 hover:text-primary transition-colors"
        >
            <span className="text-neutral-400">[{index}]</span>
            <span className="flex-1 truncate">{source.title}</span>
            {source.score !== undefined && (
                <span className="text-neutral-400">(score: {source.score.toFixed(2)})</span>
            )}
            <ExternalLink className="w-3 h-3" />
        </a>
    )
}

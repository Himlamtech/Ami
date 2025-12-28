import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism'
import {
    Bot,
    Copy,
    Bookmark,
    Check,
    ExternalLink,
    ThumbsUp,
    ThumbsDown,
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
import type { Attachment, Message, Source, ToolProgress } from '@/types/chat'
import { FileText } from 'lucide-react'

interface MessageBubbleProps {
    message: Message
    onFeedback?: (messageId: string, type: 'helpful' | 'not_helpful') => void
}

export default function MessageBubble({ message, onFeedback }: MessageBubbleProps) {
    const [copied, setCopied] = useState(false)
    const [feedbackGiven, setFeedbackGiven] = useState<'helpful' | 'not_helpful' | null>(
        message.feedback?.type || null
    )
    const isUser = message.role === 'user'

    const handleCopy = async () => {
        await navigator.clipboard.writeText(message.content)
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
    }

    const handleFeedback = (type: 'helpful' | 'not_helpful') => {
        if (feedbackGiven === type) return
        setFeedbackGiven(type)
        onFeedback?.(message.id, type)
    }

    const markdownContent = (
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
                {message.content || ''}
            </ReactMarkdown>
        </div>
    )

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
                {!isUser && (message.toolStage || (message.tools && message.tools.length > 0)) && (
                    <div className="mb-2 rounded-xl border border-[color:var(--border)] bg-[var(--surface)]/80 px-3 py-2 text-xs text-neutral-600 w-full">
                        {message.toolStage && (
                            <div className="font-medium text-neutral-700">
                                Trạng thái: {renderStageLabel(message.toolStage)}
                            </div>
                        )}
                        {message.tools && message.tools.length > 0 && (
                            <div className="mt-1 space-y-1">
                                {message.tools.map((tool) => (
                                    <div key={tool.id} className="flex items-center justify-between gap-3">
                                        <div className="truncate">
                                            <span className="font-medium text-neutral-700">
                                                {renderToolLabel(tool.type)}
                                            </span>
                                            {tool.reasoning && (
                                                <span className="text-neutral-400"> · {tool.reasoning}</span>
                                            )}
                                        </div>
                                        <span className="shrink-0 text-neutral-500">
                                            {renderToolStatus(tool.status)}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )}
                <div
                    className={cn(
                        'rounded-2xl px-4 py-3 text-sm leading-relaxed',
                        isUser
                            ? 'bg-[var(--surface)] text-neutral-900 rounded-br-md shadow-sm'
                            : 'bg-[var(--surface2)] text-neutral-900 rounded-bl-md shadow-sm'
                    )}
                >
                    {message.attachments && message.attachments.length > 0 && (
                        <AttachmentGallery attachments={message.attachments} />
                    )}
                    {message.isStreaming ? (
                        <div className="space-y-3">
                            {message.content ? (
                                markdownContent
                            ) : (
                                <div className="space-y-2">
                                    <div className="h-3 w-40 rounded-full bg-[var(--surface2)] animate-pulse" />
                                    <div className="h-3 w-72 rounded-full bg-[var(--surface2)] animate-pulse" />
                                    <div className="h-3 w-60 rounded-full bg-[var(--surface2)] animate-pulse" />
                                </div>
                            )}
                            {message.content ? null : (
                                <span className="text-xs text-neutral-500">Đang tạo phản hồi…</span>
                            )}
                        </div>
                    ) : (
                        markdownContent
                    )}
                </div>

                {!isUser && message.steps && message.steps.length > 0 && (
                    <div className="mt-2 w-full rounded-xl border border-[color:var(--border)] bg-[var(--surface)]/70 px-3 py-2 text-xs text-neutral-600">
                        <p className="text-[11px] font-medium uppercase text-neutral-400 mb-1">
                            Quy trình xử lý
                        </p>
                        <ol className="space-y-1 list-decimal list-inside">
                            {message.steps.map((step, index) => (
                                <li key={`${step}-${index}`}>{step}</li>
                            ))}
                        </ol>
                    </div>
                )}

                {/* Sources */}
                {!isUser && !message.isStreaming && message.sources && message.sources.length > 0 && (
                    <div className="mt-2 p-2.5 bg-[var(--surface2)] rounded-xl shadow-sm w-full">
                        <p className="text-xs font-medium text-neutral-400 mb-1.5">📄 Nguồn:</p>
                        <div className="space-y-1">
                            {message.sources.map((source, index) => (
                                <SourceItem key={source.id} source={source} index={index + 1} />
                            ))}
                        </div>
                    </div>
                )}

                {!isUser && !message.isStreaming && message.webSources && message.webSources.length > 0 && (
                    <div className="mt-2 p-2.5 bg-[var(--surface2)] rounded-xl shadow-sm w-full">
                        <p className="text-xs font-medium text-neutral-400 mb-1.5">🌐 Web đã tham chiếu:</p>
                        <div className="space-y-1">
                            {message.webSources.map((url, index) => (
                                <a
                                    key={`${url}-${index}`}
                                    href={url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="flex items-center gap-2 text-xs text-neutral-600 hover:text-primary transition-colors"
                                >
                                    <span className="text-neutral-400">[{index + 1}]</span>
                                    <span className="flex-1 truncate">{url}</span>
                                    <ExternalLink className="w-3 h-3" />
                                </a>
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
                                    <Button
                                        variant="ghost"
                                        size="sm"
                                        className={cn(
                                            "h-8 px-2",
                                            feedbackGiven === 'helpful' ? 'text-success' : 'text-neutral-500'
                                        )}
                                        onClick={() => handleFeedback('helpful')}
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
                                            "h-8 px-2",
                                            feedbackGiven === 'not_helpful' ? 'text-error' : 'text-neutral-500'
                                        )}
                                        onClick={() => handleFeedback('not_helpful')}
                                    >
                                        <ThumbsDown className="w-4 h-4" />
                                    </Button>
                                </TooltipTrigger>
                                <TooltipContent>Không hữu ích</TooltipContent>
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
    if (!source.url) {
        return (
            <div className="flex items-center gap-2 text-xs text-neutral-600">
                <span className="text-neutral-400">[{index}]</span>
                <span className="flex-1 truncate">{source.title}</span>
                {source.score !== undefined && (
                    <span className="text-neutral-400">(score: {source.score.toFixed(2)})</span>
                )}
            </div>
        )
    }
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

const renderToolLabel = (toolType: ToolProgress['type']) => {
    const mapping: Record<string, string> = {
        use_rag_context: 'RAG Context',
        search_web: 'Tìm kiếm web',
        answer_directly: 'Trả lời trực tiếp',
        fill_form: 'Tạo biểu mẫu',
        clarify_question: 'Làm rõ câu hỏi',
        analyze_image: 'Phân tích ảnh',
    }
    return mapping[toolType] || toolType
}

const renderToolStatus = (status: ToolProgress['status']) => {
    const mapping: Record<ToolProgress['status'], string> = {
        pending: 'Chờ',
        running: 'Đang chạy',
        success: 'Hoàn tất',
        failed: 'Lỗi',
        skipped: 'Bỏ qua',
    }
    return mapping[status]
}

const renderStageLabel = (stage: string) => {
    const mapping: Record<string, string> = {
        starting: 'Khởi tạo',
        deciding_tools: 'Đang suy luận',
        executing_tools: 'Đang chạy tool',
        synthesizing: 'Đang tổng hợp',
        completed: 'Hoàn tất',
    }
    return mapping[stage] || stage
}

function AttachmentGallery({ attachments }: { attachments: Attachment[] }) {
    return (
        <div className="mb-3 flex flex-wrap gap-3">
            {attachments.map((attachment, idx) => {
                const isImage = attachment.type === 'image'
                if (isImage) {
                    return (
                        <a
                            key={idx}
                            href={attachment.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="relative block w-32 h-32 overflow-hidden rounded-xl border border-[color:var(--border)] bg-white shadow-sm"
                        >
                            <img
                                src={attachment.url}
                                alt={attachment.name}
                                className="w-full h-full object-cover"
                            />
                            <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/60 to-transparent p-1.5">
                                <p className="text-[11px] text-white truncate" title={attachment.name}>
                                    {attachment.name}
                                </p>
                            </div>
                        </a>
                    )
                }

                return (
                    <div
                        key={idx}
                        className="flex items-center gap-2 px-3 py-2 rounded-xl border border-[color:var(--border)] bg-white shadow-sm min-w-[200px]"
                    >
                        <div className="p-2 rounded-lg bg-blue-50 text-blue-600">
                            <FileText className="w-4 h-4" />
                        </div>
                        <div className="flex-1 min-w-0">
                            <p className="text-sm text-neutral-800 truncate" title={attachment.name}>
                                {attachment.name}
                            </p>
                            <p className="text-[11px] text-neutral-500">Tài liệu đính kèm</p>
                        </div>
                    </div>
                )
            })}
        </div>
    )
}

import { useState, useRef, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { MoreHorizontal, Bookmark, Share2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import MessageBubble from '@/components/chat/MessageBubble'
import ChatInput from '@/components/chat/ChatInput'
import SuggestionChips from '@/components/chat/SuggestionChips'
import WelcomeScreen from '@/components/chat/WelcomeScreen'
import { generateId } from '@/lib/utils'
import type { Message, SuggestedQuestion, Attachment } from '@/types/chat'

// Mock suggestions
const mockSuggestions: SuggestedQuestion[] = [
    { id: '1', text: 'Học bổng KKHT' },
    { id: '2', text: 'Đóng học phí online' },
    { id: '3', text: 'Miễn giảm học phí' },
]

export default function ChatPage() {
    const { sessionId } = useParams()
    const [messages, setMessages] = useState<Message[]>([])
    const [isLoading, setIsLoading] = useState(false)
    const [suggestions, setSuggestions] = useState<SuggestedQuestion[]>([])
    const scrollRef = useRef<HTMLDivElement>(null)

    // Load conversation if sessionId exists
    useEffect(() => {
        if (sessionId) {
            // TODO: Load conversation from API
            // For now, use mock data
            setMessages([
                {
                    id: '1',
                    role: 'user',
                    content: 'Học phí kỳ này bao nhiêu?',
                    timestamp: new Date(Date.now() - 60000).toISOString(),
                },
                {
                    id: '2',
                    role: 'assistant',
                    content: `Chào bạn! 👋

Học phí kỳ 1 năm học 2024-2025 cho sinh viên ngành **CNTT** như sau:

| Hệ đào tạo | Học phí/kỳ |
|------------|------------|
| Đại trà | 15,500,000 VNĐ |
| Chất lượng cao | 25,000,000 VNĐ |

📎 **Lưu ý:**
- Hạn đóng: 15/12/2024
- Đóng online qua cổng thanh toán PTIT`,
                    timestamp: new Date(Date.now() - 30000).toISOString(),
                    sources: [
                        { id: '1', title: 'Thông báo học phí 2024-2025', score: 0.92 },
                        { id: '2', title: 'Quy định thu học phí PTIT', score: 0.78 },
                    ],
                },
            ])
            setSuggestions(mockSuggestions)
        }
    }, [sessionId])

    // Auto scroll to bottom
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight
        }
    }, [messages])

    const handleSend = async (content: string, _attachments?: Attachment[]) => {
        // Add user message
        const userMessage: Message = {
            id: generateId(),
            role: 'user',
            content,
            timestamp: new Date().toISOString(),
        }
        setMessages((prev) => [...prev, userMessage])
        setIsLoading(true)
        setSuggestions([])

        // Add streaming placeholder
        const assistantId = generateId()
        setMessages((prev) => [
            ...prev,
            {
                id: assistantId,
                role: 'assistant',
                content: '',
                timestamp: new Date().toISOString(),
                isStreaming: true,
            },
        ])

        // Simulate API response
        setTimeout(() => {
            setMessages((prev) =>
                prev.map((msg) =>
                    msg.id === assistantId
                        ? {
                            ...msg,
                            content: `Cảm ơn bạn đã hỏi về "${content}"! 

Đây là câu trả lời mẫu từ AMI. Trong thực tế, nội dung này sẽ được tạo từ API backend sử dụng RAG và LLM.

**Một số thông tin hữu ích:**
- Điểm 1
- Điểm 2
- Điểm 3`,
                            isStreaming: false,
                            sources: [
                                { id: '1', title: 'Tài liệu tham khảo 1', score: 0.85 },
                            ],
                        }
                        : msg
                )
            )
            setIsLoading(false)
            setSuggestions(mockSuggestions)
        }, 2000)
    }

    const handleStop = () => {
        setIsLoading(false)
        setMessages((prev) =>
            prev.map((msg) =>
                msg.isStreaming ? { ...msg, isStreaming: false, content: msg.content || '(Đã dừng)' } : msg
            )
        )
    }

    const handleFeedback = (messageId: string, type: 'helpful' | 'not_helpful') => {
        setMessages((prev) =>
            prev.map((msg) =>
                msg.id === messageId ? { ...msg, feedback: { type } } : msg
            )
        )
        // TODO: Send feedback to API
    }

    const handleSuggestionSelect = (question: string) => {
        handleSend(question)
    }

    const conversationTitle = sessionId ? 'Học phí kỳ 1 2024' : 'Cuộc trò chuyện mới'

    return (
        <div className="flex flex-col h-full">
            {/* Header */}
            {messages.length > 0 && (
                <header className="flex items-center justify-between h-16 px-4 border-b border-neutral-200 bg-white">
                    <div className="flex items-center gap-3">
                        <span className="text-lg">💬</span>
                        <h1 className="font-semibold text-neutral-900 truncate">{conversationTitle}</h1>
                    </div>
                    <div className="flex items-center gap-1">
                        <Button variant="ghost" size="icon">
                            <Bookmark className="w-5 h-5" />
                        </Button>
                        <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                                <Button variant="ghost" size="icon">
                                    <MoreHorizontal className="w-5 h-5" />
                                </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                                <DropdownMenuItem>
                                    <Share2 className="w-4 h-4 mr-2" />
                                    Chia sẻ
                                </DropdownMenuItem>
                                <DropdownMenuItem>Xuất PDF</DropdownMenuItem>
                                <DropdownMenuItem className="text-error">Xóa cuộc trò chuyện</DropdownMenuItem>
                            </DropdownMenuContent>
                        </DropdownMenu>
                    </div>
                </header>
            )}

            {/* Messages area */}
            {messages.length === 0 ? (
                <WelcomeScreen onQuestionSelect={handleSend} />
            ) : (
                <ScrollArea className="flex-1 p-4" ref={scrollRef}>
                    <div className="max-w-3xl mx-auto space-y-6">
                        {messages.map((message) => (
                            <MessageBubble
                                key={message.id}
                                message={message}
                                onFeedback={(type) => handleFeedback(message.id, type)}
                            />
                        ))}

                        {/* Suggestions after last AI message */}
                        {!isLoading && suggestions.length > 0 && (
                            <SuggestionChips
                                suggestions={suggestions}
                                onSelect={handleSuggestionSelect}
                            />
                        )}
                    </div>
                </ScrollArea>
            )}

            {/* Input area */}
            <ChatInput onSend={handleSend} isLoading={isLoading} onStop={handleStop} />
        </div>
    )
}

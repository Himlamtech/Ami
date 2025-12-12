import { useRef, useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { MoreHorizontal, Share2, Sparkles } from 'lucide-react'
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
import { useChat } from '../hooks/useChat'
import { chatApi } from '../api/chatApi'
import type { SuggestedQuestion, Attachment, ThinkingMode } from '@/types/chat'

export default function ChatPage() {

    const { sessionId } = useParams()
    const navigate = useNavigate()
    const creatingSessionRef = useRef(false)
    const {
        messages,
        isLoading,
        isStreaming,
        suggestions: chatSuggestions,
        sendMessage,
        stopStreaming,
        submitFeedback
    } = useChat(sessionId)
    const [initialSuggestions, setInitialSuggestions] = useState<SuggestedQuestion[]>([])
    const scrollRef = useRef<HTMLDivElement>(null)
    const [mode, setMode] = useState<ThinkingMode>('fast')

    useEffect(() => {
        if (sessionId || creatingSessionRef.current) return
        creatingSessionRef.current = true
        chatApi.createSession()
            .then((session) => {
                navigate(`/chat/${session.id}`, { replace: true })
            })
            .catch((error) => {
                console.error('[ChatPage] Failed to auto-create session', error)
            })
            .finally(() => {
                creatingSessionRef.current = false
            })
    }, [sessionId, navigate])

    // Load initial suggestions
    useEffect(() => {
        chatApi.getSuggestions().then(setInitialSuggestions).catch(() => { })
    }, [])

    const suggestions = chatSuggestions.length > 0 ? chatSuggestions : initialSuggestions

    // Auto scroll to bottom
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight
        }
    }, [messages])

    const handleSend = async (content: string, attachments?: Attachment[], sendMode?: ThinkingMode) => {
        await sendMessage(content, attachments, sendMode ?? mode)
    }

    const handleStop = () => {
        stopStreaming()
    }

    const handleFeedback = (messageId: string, type: 'helpful' | 'not_helpful') => {
        submitFeedback(messageId, type)
    }

    const handleSuggestionSelect = (question: string) => {
        handleSend(question)
    }

    const conversationTitle = 'Cuộc trò chuyện' // TODO: Get from session

    return (
        <div className="flex flex-col h-full">
            {/* Topbar */}
            <header className="flex items-center justify-between h-[52px] px-4 lg:px-6 bg-[var(--surface)]/90 backdrop-blur-sm shadow-sm">
                <div className="flex items-center gap-3 min-w-0">
                    <div className="w-8 h-8 rounded-full bg-primary/10 text-primary flex items-center justify-center">
                        <Sparkles className="w-4 h-4" />
                    </div>
                    <h1 className="font-semibold text-neutral-900 truncate">
                        {messages.length > 0 ? conversationTitle : 'AMI / AI Assistant'}
                    </h1>
                </div>
                <div className="flex items-center gap-1.5">
                    {messages.length > 0 && (
                        <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                                <Button variant="ghost" size="icon" className="text-neutral-600 hover:text-neutral-900">
                                    <MoreHorizontal className="w-5 h-5" />
                                </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end" className="w-48">
                                <DropdownMenuItem>
                                    <Share2 className="w-4 h-4 mr-2" />
                                    Chia sẻ
                                </DropdownMenuItem>
                                <DropdownMenuItem>Xuất PDF</DropdownMenuItem>
                                <DropdownMenuItem className="text-error">Xóa cuộc trò chuyện</DropdownMenuItem>
                            </DropdownMenuContent>
                        </DropdownMenu>
                    )}
                </div>
            </header>

            {/* Messages area */}
            {messages.length === 0 ? (
                <WelcomeScreen onQuestionSelect={handleSend} />
            ) : (
                <ScrollArea className="flex-1 px-4 lg:px-8 pt-8 pb-28" ref={scrollRef}>
                    <div className="max-w-[820px] mx-auto space-y-6">
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
            <ChatInput
                onSend={handleSend}
                isLoading={isLoading || isStreaming}
                onStop={handleStop}
                mode={mode}
                onModeChange={setMode}
            />
        </div>
    )
}

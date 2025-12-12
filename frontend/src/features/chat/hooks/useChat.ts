import { useState, useCallback, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { chatApi } from '../api/chatApi'
import { generateId } from '@/lib/utils'
import type { Message, Attachment, SuggestedQuestion } from '@/types/chat'

export function useChat(sessionId?: string) {
    const queryClient = useQueryClient()
    const [messages, setMessages] = useState<Message[]>([])
    const [isStreaming, setIsStreaming] = useState(false)
    const [suggestions, setSuggestions] = useState<SuggestedQuestion[]>([])

    // Load conversation
    const { data: conversationData, isLoading: isLoadingConversation } = useQuery({
        queryKey: ['conversation', sessionId],
        queryFn: () => chatApi.getConversation(sessionId!),
        enabled: !!sessionId,
    })

    // Update messages when conversation data changes
    useEffect(() => {
        if (conversationData?.messages) {
            setMessages(conversationData.messages)
        }
    }, [conversationData])

    // Send message mutation
    const sendMessageMutation = useMutation({
        mutationFn: chatApi.sendMessage,
        onSuccess: (data) => {
            setMessages((prev) =>
                prev.map((msg) =>
                    msg.isStreaming
                        ? { ...data.message, isStreaming: false }
                        : msg
                )
            )
            setSuggestions(data.suggestions)
        },
    })

    // Send message with streaming
    const sendMessage = useCallback(
        async (content: string, _attachments?: Attachment[]) => {
            // Add user message
            const userMessage: Message = {
                id: generateId(),
                role: 'user',
                content,
                timestamp: new Date().toISOString(),
            }
            setMessages((prev) => [...prev, userMessage])

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

            setIsStreaming(true)
            setSuggestions([])

            let fullContent = ''

            // Use streaming API
            const cancel = chatApi.smartQueryStream(
                { query: content, session_id: sessionId },
                (chunk: string) => {
                    try {
                        const data = JSON.parse(chunk)
                        if (data.content) {
                            fullContent += data.content
                            setMessages((prev) =>
                                prev.map((msg) =>
                                    msg.id === assistantId
                                        ? { ...msg, content: fullContent }
                                        : msg
                                )
                            )
                        }
                        if (data.sources) {
                            setMessages((prev) =>
                                prev.map((msg) =>
                                    msg.id === assistantId
                                        ? { ...msg, sources: data.sources }
                                        : msg
                                )
                            )
                        }
                        if (data.suggestions) {
                            setSuggestions(data.suggestions)
                        }
                    } catch {
                        // Plain text chunk
                        fullContent += chunk
                        setMessages((prev) =>
                            prev.map((msg) =>
                                msg.id === assistantId
                                    ? { ...msg, content: fullContent }
                                    : msg
                            )
                        )
                    }
                },
                () => {
                    setIsStreaming(false)
                    setMessages((prev) =>
                        prev.map((msg) =>
                            msg.id === assistantId
                                ? { ...msg, isStreaming: false }
                                : msg
                        )
                    )
                    // Invalidate conversations list
                    queryClient.invalidateQueries({ queryKey: ['conversations'] })
                }
            )

            return cancel
        },
        [sessionId, queryClient]
    )

    // Stop streaming
    const stopStreaming = useCallback(() => {
        setIsStreaming(false)
        setMessages((prev) =>
            prev.map((msg) =>
                msg.isStreaming
                    ? { ...msg, isStreaming: false, content: msg.content || '(Đã dừng)' }
                    : msg
            )
        )
    }, [])

    // Submit feedback
    const submitFeedback = useCallback(
        async (messageId: string, type: 'helpful' | 'not_helpful', comment?: string) => {
            await chatApi.submitFeedback(messageId, { type, comment })
            setMessages((prev) =>
                prev.map((msg) =>
                    msg.id === messageId
                        ? { ...msg, feedback: { type, comment } }
                        : msg
                )
            )
        },
        []
    )

    return {
        messages,
        isLoading: isLoadingConversation || sendMessageMutation.isPending,
        isStreaming,
        suggestions,
        sendMessage,
        stopStreaming,
        submitFeedback,
    }
}

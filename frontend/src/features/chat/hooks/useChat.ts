import { useState, useCallback, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { chatApi } from '../api/chatApi'
import { generateId } from '@/lib/utils'
import { useAuthStore } from '@/stores/authStore'
import type { Message, Attachment, SuggestedQuestion, ThinkingMode, Source } from '@/types/chat'

const MODE_CONFIG: Record<ThinkingMode, { temperature: number; maxTokens: number }> = {
    fast: { temperature: 0.3, maxTokens: 1024 },
    thinking: { temperature: 0.8, maxTokens: 4096 },
}

export function useChat(sessionId?: string) {
    const queryClient = useQueryClient()
    const [messages, setMessages] = useState<Message[]>([])
    const [isStreaming, setIsStreaming] = useState(false)
    const [suggestions, setSuggestions] = useState<SuggestedQuestion[]>([])
    const user = useAuthStore((state) => state.user)

    // Load conversation
    const { data: conversationData, isLoading: isLoadingConversation } = useQuery({
        queryKey: ['conversation', sessionId],
        queryFn: () => chatApi.getConversation(sessionId!),
        enabled: !!sessionId,
    })

    // Clear messages when sessionId changes
    useEffect(() => {
        setMessages([])
    }, [sessionId])

    // Update messages when conversation data changes
    useEffect(() => {
        if (!conversationData?.messages) return
        setMessages((prev) => {
            const hasStreaming = prev.some((msg) => msg.isStreaming)
            if (hasStreaming) {
                return prev
            }
            if (prev.length === 0) {
                return conversationData.messages
            }
            const prevById = new Map(prev.map((msg) => [msg.id, msg]))
            const merged = conversationData.messages.map((message) => {
                const existing = prevById.get(message.id)
                if (!existing) {
                    return message
                }
                return {
                    ...existing,
                    ...message,
                    sources: message.sources || existing.sources,
                    feedback: message.feedback || existing.feedback,
                }
            })
            const serverIds = new Set(conversationData.messages.map((m) => m.id))
            const remaining = prev.filter((msg) => !serverIds.has(msg.id))
            return [...merged, ...remaining]
        })
    }, [conversationData])

    // (Legacy) Send message mutation - kept for compatibility
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

    const persistMessage = useCallback(
        async (
            tempId: string,
            role: 'user' | 'assistant',
            content: string,
            metadata?: Record<string, any>
        ) => {
            if (!sessionId) return
            try {
                const saved = await chatApi.logMessage({
                    sessionId,
                    role,
                    content,
                    metadata,
                })
                setMessages((prev) =>
                    prev.map((msg) =>
                        msg.id === tempId
                            ? {
                                ...msg,
                                ...saved,
                                isStreaming: false,
                            }
                            : msg
                    )
                )
            } catch (error) {
                console.error(`[useChat] Failed to log ${role} message`, error)
            }
        },
        [sessionId]
    )

    // Send message with streaming
    const sendMessage = useCallback(
        async (content: string, attachments?: Attachment[], mode: ThinkingMode = 'fast') => {
            if (!sessionId) {
                console.warn('[useChat] Cannot send message without a session')
                return
            }
            const { temperature, maxTokens } = MODE_CONFIG[mode] ?? MODE_CONFIG.fast

            // Check for image attachments
            const imageAttachment = attachments && attachments.length > 0
                ? attachments.find(a => a.type === 'image')
                : undefined

            let queryContent = content

            // If there's an image, process it first
            if (imageAttachment) {
                try {
                    // Fetch the image file from the blob URL
                    const response = await fetch(imageAttachment.url)
                    const blob = await response.blob()
                    const file = new File([blob], imageAttachment.name, { type: 'image/jpeg' })

                    // Send image query
                    const imageResult = await chatApi.sendImageQuery(file, content)

                    // Enhance query with image analysis
                    queryContent = `[Image analyzed: ${imageResult.description}]\n${content}\n\nImage details: ${imageResult.response}`
                } catch (error) {
                    console.error('Image processing error:', error)
                }
            }

            // Add user message and streaming placeholder
            const userMessage: Message = {
                id: generateId(),
                role: 'user',
                content,
                timestamp: new Date().toISOString(),
                attachments,
            }
            const assistantId = generateId()
            const streamingMessage: Message = {
                id: assistantId,
                role: 'assistant',
                content: '',
                timestamp: new Date().toISOString(),
                isStreaming: true,
            }
            setMessages((prev) => [...prev, userMessage, streamingMessage])
            persistMessage(userMessage.id, 'user', content)

            setIsStreaming(true)
            setSuggestions([])

            let fullContent = ''
            let rafId: number | null = null
            let pendingUpdate = false
            let latestSources: Source[] = []

            const updateContent = (content: string) => {
                fullContent = content

                if (!pendingUpdate) {
                    pendingUpdate = true
                    rafId = requestAnimationFrame(() => {
                        setMessages((prev) =>
                            prev.map((msg) =>
                                msg.id === assistantId
                                    ? { ...msg, content: fullContent }
                                    : msg
                            )
                        )
                        pendingUpdate = false
                    })
                }
            }

            // Use streaming API
            console.log('[useChat] Starting stream for:', queryContent)
            const cancel = chatApi.smartQueryStream(
                {
                    query: queryContent,
                    session_id: sessionId,
                    temperature,
                    max_tokens: maxTokens,
                },
                (chunk: string) => {
                    console.log('[useChat] Received chunk:', chunk)
                    try {
                        const data = JSON.parse(chunk)
                        console.log('[useChat] Parsed data:', data)
                        if (data.content) {
                            const newContent = fullContent + data.content
                            console.log('[useChat] New accumulated:', newContent)
                            updateContent(newContent)
                        }
                        if (data.sources) {
                            console.log('[useChat] Received sources:', data.sources.length)
                            // Map backend sources to frontend Source format
                            const mappedSources = data.sources.map((s: any, idx: number) => ({
                                id: s.document_id || `source-${idx}`,
                                title: s.title || 'Unknown',
                                score: s.relevance_score,
                                url: s.url
                            }))
                            latestSources = mappedSources
                            setMessages((prev) =>
                                prev.map((msg) =>
                                    msg.id === assistantId
                                        ? { ...msg, sources: mappedSources }
                                        : msg
                                )
                            )
                        }
                        if (data.suggestions) {
                            setSuggestions(data.suggestions)
                        }
                    } catch (e) {
                        console.error('[useChat] JSON parse failed, treating as plain text:', e)
                        // Plain text chunk
                        const newContent = fullContent + chunk
                        updateContent(newContent)
                    }
                },
                () => {
                    // Cancel any pending RAF
                    if (rafId !== null) {
                        cancelAnimationFrame(rafId)
                    }

                    // Final update with complete content
                    setIsStreaming(false)
                    setMessages((prev) =>
                        prev.map((msg) =>
                            msg.id === assistantId
                                ? { ...msg, content: fullContent, isStreaming: false }
                                : msg
                        )
                    )
                    const metadata = latestSources.length ? { sources: latestSources } : undefined
                    persistMessage(assistantId, 'assistant', fullContent, metadata)
                    // Invalidate conversations list
                    queryClient.invalidateQueries({ queryKey: ['sessions'] })
                    queryClient.invalidateQueries({ queryKey: ['conversation', sessionId] })
                }
            )

            return cancel
        },
        [sessionId, queryClient, persistMessage]
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
            if (!sessionId || !user?.id) return
            await chatApi.submitFeedback(messageId, { type, comment, sessionId, userId: user.id })
            setMessages((prev) =>
                prev.map((msg) =>
                    msg.id === messageId
                        ? { ...msg, feedback: { type, comment } }
                        : msg
                )
            )
        },
        [sessionId, user]
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

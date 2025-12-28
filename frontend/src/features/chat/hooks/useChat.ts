import { useState, useCallback, useEffect, useRef } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { chatApi, type OrchestrateResponse } from '../api/chatApi'
import { generateId } from '@/lib/utils'
import { useAuthStore } from '@/stores/authStore'
import type { Message, Attachment, SuggestedQuestion, ThinkingMode, Source, ToolProgress } from '@/types/chat'

const TOOL_LABELS: Record<string, string> = {
    use_rag_context: 'dùng RAG',
    search_web: 'search web',
    answer_directly: 'trả lời trực tiếp',
    fill_form: 'tạo biểu mẫu',
    clarify_question: 'làm rõ câu hỏi',
    analyze_image: 'phân tích ảnh',
}

const extractSources = (response: OrchestrateResponse): Source[] | undefined => {
    const tools = response.tools ?? []
    const ragTool = tools.find((tool) => tool.type === 'use_rag_context')
    const rawSources = ragTool?.result?.sources
    if (!Array.isArray(rawSources) || rawSources.length === 0) {
        return undefined
    }
    return rawSources.map((source, idx) => ({
        id: source.id || source.document_id || `source-${idx}`,
        title: source.title || 'Unknown',
        url: source.url,
        score: source.score ?? source.relevance_score ?? 0,
    }))
}

export function useChat(sessionId?: string) {
    const queryClient = useQueryClient()
    const navigate = useNavigate()
    const [messages, setMessages] = useState<Message[]>([])
    const [isStreaming, setIsStreaming] = useState(false)
    const [suggestions, setSuggestions] = useState<SuggestedQuestion[]>([])
    const [currentSessionId, setCurrentSessionId] = useState<string | undefined>(sessionId)
    const [isSending, setIsSending] = useState(false)
    const streamCancelRef = useRef<(() => void) | null>(null)
    const user = useAuthStore((state) => state.user)

    const { data: conversationData, isLoading: isLoadingConversation } = useQuery({
        queryKey: ['conversation', sessionId],
        queryFn: () => chatApi.getConversation(sessionId!),
        enabled: !!sessionId,
    })

    useEffect(() => {
        setMessages([])
        setCurrentSessionId(sessionId)
    }, [sessionId])

    useEffect(() => {
        if (!conversationData?.messages) return
        setMessages((prev) => {
            const hasPending = prev.some((msg) => msg.isStreaming)
            if (hasPending) {
                return prev
            }
            if (prev.length === 0) {
                return conversationData.messages
            }
            const serverIds = new Set(conversationData.messages.map((msg) => msg.id))
            const tempMessages = prev.filter(
                (msg) => !serverIds.has(msg.id) && msg.id.startsWith('temp-')
            )
            return [...conversationData.messages, ...tempMessages]
        })
    }, [conversationData])

    const appendStep = useCallback((messageId: string, step: string) => {
        setMessages((prev) =>
            prev.map((msg) => {
                if (msg.id !== messageId) return msg
                const currentSteps = msg.steps ?? []
                const lastStep = currentSteps[currentSteps.length - 1]
                if (lastStep === step) return msg
                return { ...msg, steps: [...currentSteps, step] }
            })
        )
    }, [])

    const sendMessage = useCallback(
        async (content: string, attachments?: Attachment[], _mode: ThinkingMode = 'fast') => {
            if (!content.trim()) return false

            const imageAttachment =
                attachments && attachments.length > 0
                    ? attachments.find((attachment) => attachment.type === 'image')
                    : undefined

            let queryContent = content

            if (imageAttachment) {
                try {
                    const response = await fetch(imageAttachment.url)
                    const blob = await response.blob()
                    const file = new File([blob], imageAttachment.name, { type: 'image/jpeg' })
                    const imageResult = await chatApi.sendImageQuery(file, content)
                    queryContent = `[Image analyzed: ${imageResult.description}]\n${content}\n\nImage details: ${imageResult.response}`
                } catch (error) {
                    console.error('[useChat] Image processing error', error)
                }
            }

            const userMessage: Message = {
                id: `temp-${generateId()}`,
                role: 'user',
                content,
                timestamp: new Date().toISOString(),
                attachments,
            }
            const assistantId = `temp-${generateId()}`
            const streamingMessage: Message = {
                id: assistantId,
                role: 'assistant',
                content: '',
                timestamp: new Date().toISOString(),
                isStreaming: true,
                steps: [],
            }

            setMessages((prev) => [...prev, userMessage, streamingMessage])
            setIsStreaming(true)
            setSuggestions([])
            setIsSending(true)

            try {
                const cancel = chatApi.orchestrateStream(
                    {
                        query: queryContent,
                        session_id: currentSessionId,
                        user_id: user?.id,
                    },
                    (chunk: string) => {
                        try {
                            const data = JSON.parse(chunk)
                            if (data.type === 'status') {
                                if (data.stage === 'deciding_tools') {
                                    appendStep(assistantId, 'Đang suy luận')
                                }
                                if (data.stage === 'synthesizing') {
                                    appendStep(assistantId, 'Đang sinh câu trả lời')
                                }
                                if (data.stage === 'completed') {
                                    appendStep(assistantId, 'Hoàn tất')
                                }
                                setMessages((prev) =>
                                    prev.map((msg) =>
                                        msg.id === assistantId
                                            ? { ...msg, toolStage: data.stage }
                                            : msg
                                    )
                                )
                                return
                            }

                            if (data.type === 'tools_decided' && Array.isArray(data.tools)) {
                                const tools: ToolProgress[] = data.tools.map((tool: any) => ({
                                    id: tool.id,
                                    type: tool.type,
                                    status: 'pending',
                                    reasoning: tool.reasoning,
                                }))
                                setMessages((prev) =>
                                    prev.map((msg) =>
                                        msg.id === assistantId
                                            ? { ...msg, tools }
                                            : msg
                                    )
                                )
                                return
                            }

                            if (data.type === 'tool_start' && data.tool) {
                                const label = TOOL_LABELS[data.tool.type] || data.tool.type
                                appendStep(assistantId, `Đang ${label}`)
                                setMessages((prev) =>
                                    prev.map((msg) => {
                                        if (msg.id !== assistantId) return msg
                                        const updatedTools = (msg.tools || []).map((tool) =>
                                            tool.id === data.tool.id
                                                ? { ...tool, status: 'running' }
                                                : tool
                                        )
                                        return { ...msg, tools: updatedTools }
                                    })
                                )
                                return
                            }

                            if (data.type === 'tool_end' && data.tool) {
                                appendStep(assistantId, 'Đang suy luận')
                                setMessages((prev) =>
                                    prev.map((msg) => {
                                        if (msg.id !== assistantId) return msg
                                        const updatedTools = (msg.tools || []).map((tool) =>
                                            tool.id === data.tool.id
                                                ? {
                                                    ...tool,
                                                    status: data.tool.status,
                                                    error: data.tool.error,
                                                }
                                                : tool
                                        )
                                        const sources = Array.isArray(data.result?.sources)
                                            ? data.result.sources.map((source: any, idx: number) => ({
                                                  id: source.id || source.document_id || `source-${idx}`,
                                                  title: source.title || 'Unknown',
                                                  url: source.url,
                                                  score: source.score ?? source.relevance_score ?? 0,
                                              }))
                                            : msg.sources
                                        const webSources = Array.isArray(data.result?.source_urls)
                                            ? data.result.source_urls
                                            : msg.webSources
                                        return { ...msg, tools: updatedTools, sources, webSources }
                                    })
                                )
                                return
                            }

                            if (data.type === 'answer_chunk' && data.content) {
                                setMessages((prev) =>
                                    prev.map((msg) =>
                                        msg.id === assistantId
                                            ? {
                                                  ...msg,
                                                  content: `${msg.content || ''}${data.content}`,
                                              }
                                            : msg
                                    )
                                )
                                return
                            }

                            if (data.type === 'final') {
                                const nextSessionId = data.session_id || currentSessionId
                                if (!currentSessionId && nextSessionId) {
                                    setCurrentSessionId(nextSessionId)
                                    navigate(`/chat/${nextSessionId}`, { replace: true })
                                }
                                const sources = extractSources({
                                    tools: data.tools,
                                } as OrchestrateResponse)
                                appendStep(assistantId, 'Hoàn tất')
                                setMessages((prev) =>
                                    prev.map((msg) =>
                                        msg.id === assistantId
                                            ? {
                                                  ...msg,
                                                  content: data.answer || msg.content || '',
                                                  isStreaming: false,
                                                  sources: sources || msg.sources,
                                                  toolStage: 'completed',
                                              }
                                            : msg
                                    )
                                )
                                setIsStreaming(false)
                                setIsSending(false)
                                queryClient.invalidateQueries({ queryKey: ['sessions'] })
                                if (nextSessionId) {
                                    queryClient.invalidateQueries({ queryKey: ['conversation', nextSessionId] })
                                }
                                return
                            }

                            if (data.type === 'error') {
                                appendStep(assistantId, 'Hoàn tất')
                                setMessages((prev) =>
                                    prev.map((msg) =>
                                        msg.id === assistantId
                                            ? {
                                                  ...msg,
                                                content: 'Xin lỗi, hệ thống đang bận. Vui lòng thử lại.',
                                                isStreaming: false,
                                                toolStage: 'completed',
                                            }
                                            : msg
                                    )
                                )
                                setIsStreaming(false)
                                setIsSending(false)
                            }
                        } catch (error) {
                            console.error('[useChat] Stream parse failed', error)
                        }
                    },
                    () => {
                        setIsStreaming(false)
                        setIsSending(false)
                    }
                )
                streamCancelRef.current = cancel
                return true
            } catch (error) {
                console.error('[useChat] Orchestrate failed', error)
                setMessages((prev) =>
                    prev.map((msg) =>
                        msg.id === assistantId
                            ? {
                                ...msg,
                                content: 'Xin lỗi, hệ thống đang bận. Vui lòng thử lại.',
                                isStreaming: false,
                            }
                            : msg
                    )
                )
                setIsStreaming(false)
                setIsSending(false)
                return false
            }
        },
        [appendStep, currentSessionId, navigate, queryClient, user?.id]
    )

    const stopStreaming = useCallback(() => {
        if (streamCancelRef.current) {
            streamCancelRef.current()
            streamCancelRef.current = null
        }
        setIsStreaming(false)
        setMessages((prev) =>
            prev.map((msg) =>
                msg.isStreaming
                    ? { ...msg, isStreaming: false, content: msg.content || '(Đã dừng)' }
                    : msg
            )
        )
    }, [])

    const submitFeedback = useCallback(
        async (messageId: string, type: 'helpful' | 'not_helpful', comment?: string) => {
            if (!currentSessionId || !user?.id) return
            try {
                await chatApi.submitFeedback({
                    sessionId: currentSessionId,
                    messageId,
                    userId: user.id,
                    feedbackType: type,
                })
                setMessages((prev) =>
                    prev.map((msg) =>
                        msg.id === messageId
                            ? { ...msg, feedback: { type, comment } }
                            : msg
                    )
                )
            } catch (error) {
                console.error('[useChat] Feedback error', error)
            }
        },
        [currentSessionId, user?.id]
    )

    return {
        messages,
        isLoading: isLoadingConversation || isSending,
        isStreaming,
        suggestions,
        sendMessage,
        stopStreaming,
        submitFeedback,
    }
}

import { useEffect, useState, useRef } from 'react'
import { useChatStore } from '../store/chatStore'
import { apiClient } from '../api/client'
import ChatSidebar from '../components/__ami__/ChatSidebar'
import ChatHeader from '../components/__ami__/ChatHeader'
import MessageList from '../components/__ami__/MessageList'
import MessageInput from '../components/__ami__/MessageInput'
import SettingsPanel from '../components/__ami__/SettingsPanel'
import { Square } from 'lucide-react'
import '../styles/__ami__/Chat.css'

export default function Chat() {
    const {
        currentSession,
        currentMessages,
        loading,
        config,
        isStreaming,
        abortController,
        setCurrentSession,
        setCurrentMessages,
        setLoading,
        setError,
        addMessage,
        updateLastMessage,
        setIsStreaming,
        setAbortController,
    } = useChatStore()

    const [showSettings, setShowSettings] = useState(false)
    const [showSidebar, setShowSidebar] = useState(true)
    const messagesEndRef = useRef<HTMLDivElement>(null)

    // Load sessions on mount
    useEffect(() => {
        loadSessions()
    }, [])

    // Scroll to bottom when messages change
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [currentMessages, isStreaming])

    const loadSessions = async () => {
        try {
            const result = await apiClient.listSessions(0, 50)
            // First session will be loaded if available
            if (result.sessions.length > 0) {
                loadSession(result.sessions[0].id)
            }
        } catch (error) {
            setError('Failed to load sessions')
        }
    }

    const loadSession = async (sessionId: string) => {
        try {
            setLoading(true)
            const session = await apiClient.getSession(sessionId)
            setCurrentSession(session as any)
            if ((session as any).messages) {
                setCurrentMessages((session as any).messages)
            }
        } catch (error) {
            setError('Failed to load session')
        } finally {
            setLoading(false)
        }
    }

    const handleNewChat = async () => {
        try {
            setLoading(true)
            const session = await apiClient.createSession('New Chat')
            setCurrentSession(session)
            setCurrentMessages([])
        } catch (error) {
            setError('Failed to create new chat')
        } finally {
            setLoading(false)
        }
    }

    const handleStopGeneration = () => {
        if (abortController) {
            abortController.abort()
            setAbortController(null)
            setIsStreaming(false)
            setLoading(false)
        }
    }

    const handleSendMessage = async (message: string, files: File[] = []) => {
        if (!message.trim() && files.length === 0) return

        try {
            setLoading(true)
            setIsStreaming(true)
            setError(null)

            // Create session if needed
            let sessionId = currentSession?.id
            if (!sessionId) {
                const session = await apiClient.createSession()
                setCurrentSession(session)
                sessionId = session.id
            }

            // Upload files if any
            if (files.length > 0) {
                for (const file of files) {
                    await apiClient.uploadFile(file, config.collection)
                }
            }

            // Add user message
            const userMsg = await apiClient.addMessage(sessionId, 'user', message)
            addMessage(userMsg)

            // Create placeholder for assistant message
            const assistantMsgPlaceholder = {
                id: 'streaming-placeholder',
                session_id: sessionId,
                role: 'assistant' as const,
                content: '',
                created_at: new Date().toISOString(),
                is_deleted: false,
            }
            addMessage(assistantMsgPlaceholder)

            // Create AbortController
            const controller = new AbortController()
            setAbortController(controller)

            // Stream response
            let fullContent = ''
            const currentSessionId = sessionId // Capture sessionId for callback

            console.log('[Chat] Starting stream with sessionId:', currentSessionId)

            await apiClient.streamChat(
                {
                    messages: [...currentMessages, { role: 'user', content: message }].map((m: any) => ({
                        role: m.role as 'user' | 'assistant',
                        content: m.content,
                    })),
                    thinking_mode: config.thinkingMode as any,
                    rag_config: {
                        enabled: config.enableRAG,
                        top_k: config.topK,
                        similarity_threshold: config.similarityThreshold,
                        include_sources: true,
                    },
                    web_search_config: {
                        enabled: config.enableWebSearch,
                        max_results: 5,
                        timeout: 30000,
                    },
                    generation_config: {
                        temperature: config.temperature,
                        max_tokens: config.maxTokens,
                        top_p: 1.0,
                        frequency_penalty: 0,
                        presence_penalty: 0,
                    },
                    collection: config.collection,
                    session_id: currentSessionId,
                    auto_generate_title: true,
                    stream: true,
                },
                (chunk) => {
                    fullContent += chunk
                    updateLastMessage(fullContent)
                },
                () => {
                    // Done - stream completed successfully
                    console.log('[Chat] Stream completed. Full content length:', fullContent.length)
                    setIsStreaming(false)
                    setLoading(false)
                    setAbortController(null)

                    // DON'T reload session - it will overwrite the streaming message!
                    // The message is already in currentMessages from updateLastMessage()
                    // Backend auto-saves it, so it's persisted
                    console.log('[Chat] Stream done. Message already in state, no reload needed.')
                },
                (error) => {
                    console.error('[Chat] Streaming error:', error)
                    setError('Failed to generate response: ' + error.message)
                    setIsStreaming(false)
                    setLoading(false)
                    setAbortController(null)
                },
                controller.signal
            )

        } catch (error) {
            console.error('[Chat] Send message error:', error)
            setError('Failed to send message: ' + (error as Error).message)
            setLoading(false)
            setIsStreaming(false)
            setAbortController(null)
        }
    }

    return (
        <div className="chat-layout">
            <ChatSidebar
                isOpen={showSidebar}
                onNewChat={handleNewChat}
                onLoadSession={loadSession}
            />

            <div className="chat-main">
                <ChatHeader
                    onToggleSidebar={() => setShowSidebar(!showSidebar)}
                    onToggleSettings={() => setShowSettings(!showSettings)}
                />

                <MessageList messages={currentMessages} isLoading={loading && !isStreaming} ref={messagesEndRef} />

                <div className="input-area-container">
                    <MessageInput
                        onSendMessage={handleSendMessage}
                        disabled={loading && !isStreaming}
                        isStreaming={isStreaming}
                        onStopGeneration={handleStopGeneration}
                    />
                </div>
            </div>

            {showSettings && (
                <SettingsPanel onClose={() => setShowSettings(false)} />
            )}
        </div>
    )
}

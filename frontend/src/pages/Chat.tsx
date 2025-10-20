import { useEffect, useState, useRef } from 'react'
import { useChatStore } from '../store/chatStore'
import { apiClient } from '../api/client'
import ChatSidebar from '../components/__ami__/ChatSidebar'
import ChatHeader from '../components/__ami__/ChatHeader'
import MessageList from '../components/__ami__/MessageList'
import MessageInput from '../components/__ami__/MessageInput'
import SettingsPanel from '../components/__ami__/SettingsPanel'
import '../styles/__ami__/Chat.css'

export default function Chat() {
    const {
        currentSession,
        currentMessages,
        loading,
        config,
        setCurrentSession,
        setCurrentMessages,
        setLoading,
        setError,
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
    }, [currentMessages])

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

    const handleSendMessage = async (message: string, files: File[] = []) => {
        if (!message.trim() && files.length === 0) return

        try {
            setLoading(true)

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
            setCurrentMessages([...currentMessages, userMsg] as any)

            // Generate response
            const response = await apiClient.generateChat({
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
                session_id: sessionId,
                auto_generate_title: true,
            })

            // Add assistant response
            const assistantMsg = await apiClient.addMessage(
                sessionId,
                'assistant',
                response.message.content,
                response.metadata
            )
            setCurrentMessages([...currentMessages, userMsg, assistantMsg] as any)
        } catch (error) {
            setError('Failed to send message')
        } finally {
            setLoading(false)
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

                <MessageList messages={currentMessages} isLoading={loading} ref={messagesEndRef} />

                <MessageInput
                    onSendMessage={handleSendMessage}
                    disabled={loading}
                />
            </div>

            {showSettings && (
                <SettingsPanel onClose={() => setShowSettings(false)} />
            )}
        </div>
    )
}

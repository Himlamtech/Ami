import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { ChatSession, ChatMessage } from '../api/client'

interface ChatConfig {
    thinkingMode: 'fast' | 'balance' | 'thinking'
    enableRAG: boolean
    enableWebSearch: boolean
    temperature: number
    maxTokens?: number
    topK: number
    similarityThreshold: number
    collection: string
}

interface ChatState {
    currentSession: ChatSession | null
    sessions: ChatSession[]
    currentMessages: ChatMessage[]
    loading: boolean
    error: string | null
    config: ChatConfig
    isUploadingFile: boolean
    isStreaming: boolean
    abortController: AbortController | null

    setCurrentSession: (session: ChatSession | null) => void
    setSessions: (sessions: ChatSession[]) => void
    addMessage: (message: ChatMessage) => void
    setCurrentMessages: (messages: ChatMessage[]) => void
    setLoading: (loading: boolean) => void
    setError: (error: string | null) => void
    updateConfig: (config: Partial<ChatConfig>) => void
    setIsUploadingFile: (loading: boolean) => void
    clearState: () => void

    // Streaming actions
    setIsStreaming: (isStreaming: boolean) => void
    setAbortController: (controller: AbortController | null) => void
    updateLastMessage: (content: string) => void
}

const defaultConfig: ChatConfig = {
    thinkingMode: 'balance',
    enableRAG: true,
    enableWebSearch: false,
    temperature: 0.7,
    topK: 5,
    similarityThreshold: 0.0,
    collection: 'default',
}

export const useChatStore = create<ChatState>()(
    persist(
        (set) => ({
            currentSession: null,
            sessions: [],
            currentMessages: [],
            loading: false,
            error: null,
            config: defaultConfig,
            isUploadingFile: false,
            isStreaming: false,
            abortController: null,

            setCurrentSession: (session) => set({ currentSession: session }),
            setSessions: (sessions) => set({ sessions }),
            addMessage: (message) =>
                set((state) => ({
                    currentMessages: [...state.currentMessages, message],
                })),
            setCurrentMessages: (messages) => set({ currentMessages: messages }),
            setLoading: (loading) => set({ loading }),
            setError: (error) => set({ error }),
            updateConfig: (config) =>
                set((state) => ({
                    config: { ...state.config, ...config },
                })),
            setIsUploadingFile: (loading) => set({ isUploadingFile: loading }),
            clearState: () =>
                set({
                    currentSession: null,
                    sessions: [],
                    currentMessages: [],
                    loading: false,
                    error: null,
                }),

            setIsStreaming: (isStreaming) => set({ isStreaming }),
            setAbortController: (controller) => set({ abortController: controller }),
            updateLastMessage: (content) =>
                set((state) => {
                    const messages = [...state.currentMessages]
                    if (messages.length > 0) {
                        const lastMsg = messages[messages.length - 1]
                        if (lastMsg.role === 'assistant') {
                            lastMsg.content = content
                        }
                    }
                    return { currentMessages: messages }
                }),
        }),
        {
            name: 'ami-chat-storage',
            partialize: (state) => ({ config: state.config }), // Only persist config
        }
    )
)

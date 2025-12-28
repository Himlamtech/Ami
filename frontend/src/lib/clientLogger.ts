type ClientLogPayload = {
    level: 'error' | 'warn' | 'info'
    message: string
    stack?: string
    url?: string
    user_agent?: string
    metadata?: Record<string, unknown>
}

let initialized = false
let lastSentAt = 0
const MIN_INTERVAL_MS = 2000

const getUserId = () => {
    try {
        const authStorage = localStorage.getItem('ami-auth')
        if (!authStorage) return null
        const { state } = JSON.parse(authStorage)
        return state?.user?.id || null
    } catch {
        return null
    }
}

const sendLog = async (payload: ClientLogPayload) => {
    const now = Date.now()
    if (now - lastSentAt < MIN_INTERVAL_MS) return
    lastSentAt = now

    const headers: Record<string, string> = {
        'Content-Type': 'application/json',
    }
    const apiKey = import.meta.env.VITE_AMI_API_KEY
    if (apiKey) {
        headers['X-AMI-API-Key'] = apiKey
    }
    const userId = getUserId()
    if (userId) {
        headers['X-User-ID'] = userId
    }

    await fetch('/api/v1/logs/client', {
        method: 'POST',
        headers,
        body: JSON.stringify(payload),
        keepalive: true,
    }).catch(() => {
        // ignore logging errors
    })
}

export const initClientLogging = () => {
    if (initialized) return
    initialized = true

    window.addEventListener('error', (event) => {
        sendLog({
            level: 'error',
            message: event.message,
            stack: event.error?.stack,
            url: window.location.href,
            user_agent: navigator.userAgent,
        })
    })

    window.addEventListener('unhandledrejection', (event) => {
        const reason = event.reason instanceof Error ? event.reason : new Error(String(event.reason))
        sendLog({
            level: 'error',
            message: reason.message || 'Unhandled promise rejection',
            stack: reason.stack,
            url: window.location.href,
            user_agent: navigator.userAgent,
            metadata: { type: 'unhandledrejection' },
        })
    })
}

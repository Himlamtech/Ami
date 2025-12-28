const API_BASE = '/api/v1'

interface RequestOptions extends RequestInit {
    params?: Record<string, string | number | boolean | undefined>
}

class ApiClient {
    private baseUrl: string

    constructor(baseUrl: string) {
        this.baseUrl = baseUrl
    }

    private buildUrl(endpoint: string, params?: Record<string, string | number | boolean | undefined>): string {
        const url = new URL(`${this.baseUrl}${endpoint}`, window.location.origin)
        if (params) {
            Object.entries(params).forEach(([key, value]) => {
                if (value !== undefined) {
                    url.searchParams.append(key, String(value))
                }
            })
        }
        return url.toString()
    }

    async request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
        const { params, ...fetchOptions } = options
        const url = this.buildUrl(endpoint, params)

        // Get auth headers
        const headers: Record<string, string> = {
            ...(fetchOptions.headers as Record<string, string>),
        }

        const amiApiKey = import.meta.env.VITE_AMI_API_KEY
        if (amiApiKey) {
            headers['X-AMI-API-Key'] = amiApiKey
        }

        // Set Content-Type to json if not FormData
        if (!(fetchOptions.body instanceof FormData)) {
            headers['Content-Type'] = 'application/json'
        }

        // Auto-inject auth headers
        try {
            const authStorage = localStorage.getItem('ami-auth')
            if (authStorage) {
                const { state } = JSON.parse(authStorage)
                if (state?.user?.id) {
                    headers['X-User-ID'] = state.user.id
                }
                // For admin routes, send token as admin key (temporary)
                // TODO: Implement proper role-based auth
                if (state?.token && endpoint.includes('/admin')) {
                    headers['X-Admin-API-Key'] = state.token
                }
            }
        } catch (e) {
            // ignore
        }

        const response = await fetch(url, {
            ...fetchOptions,
            headers,
        })

        if (!response.ok) {
            const error = await response.json().catch(() => ({ message: 'Request failed' }))
            throw new Error(error.detail || error.message || `HTTP ${response.status}`)
        }

        return response.json()
    }

    get<T>(endpoint: string, params?: Record<string, string | number | boolean | undefined>): Promise<T> {
        return this.request<T>(endpoint, { method: 'GET', params })
    }

    post<T>(endpoint: string, data?: unknown): Promise<T> {
        return this.request<T>(endpoint, {
            method: 'POST',
            body: data ? JSON.stringify(data) : undefined,
        })
    }

    put<T>(endpoint: string, data?: unknown): Promise<T> {
        return this.request<T>(endpoint, {
            method: 'PUT',
            body: data ? JSON.stringify(data) : undefined,
        })
    }

    delete<T>(endpoint: string): Promise<T> {
        return this.request<T>(endpoint, { method: 'DELETE' })
    }

    postFormData<T>(endpoint: string, formData: FormData): Promise<T> {
        return this.request<T>(endpoint, {
            method: 'POST',
            body: formData,
        })
    }

    // SSE for streaming responses
    stream(endpoint: string, data: unknown, onMessage: (data: string) => void, onDone?: () => void): () => void {
        const controller = new AbortController()
        let doneSignaled = false

        const signalDone = () => {
            if (!doneSignaled) {
                doneSignaled = true
                onDone?.()
            }
        }

        // Get auth headers for stream
        const headers: Record<string, string> = {
            'Content-Type': 'application/json',
        }
        const amiApiKey = import.meta.env.VITE_AMI_API_KEY
        if (amiApiKey) {
            headers['X-AMI-API-Key'] = amiApiKey
        }
        try {
            const authStorage = localStorage.getItem('ami-auth')
            if (authStorage) {
                const { state } = JSON.parse(authStorage)
                if (state?.user?.id) {
                    headers['X-User-ID'] = state.user.id
                }
                if (state?.token && state?.user?.role === 'admin') {
                    headers['X-Admin-API-Key'] = state.token
                }
            }
        } catch (e) { }

        fetch(`${this.baseUrl}${endpoint}`, {
            method: 'POST',
            headers,
            body: JSON.stringify(data),
            signal: controller.signal,
        }).then(async (response) => {
            if (!response.ok) {
                const errorText = await response.text().catch(() => '')
                signalDone()
                return
            }
            const reader = response.body?.getReader()
            if (!reader) {
                signalDone()
                return
            }

            const decoder = new TextDecoder()
            let chunkCount = 0
            let buffer = ''
            while (true) {
                const { done, value } = await reader.read()
                if (done) {
                    signalDone()
                    break
                }

                const chunk = decoder.decode(value, { stream: true })
                chunkCount++
                buffer += chunk.replace(/\r/g, '')

                let boundaryIndex = buffer.indexOf('\n\n')
                while (boundaryIndex !== -1) {
                    const event = buffer.slice(0, boundaryIndex)
                    buffer = buffer.slice(boundaryIndex + 2)

                    const lines = event.split('\n')
                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            const payload = line.slice(6)
                            if (payload === '[DONE]') {
                                signalDone()
                                controller.abort()
                                return
                            }
                            onMessage(payload)
                        }
                    }

                    boundaryIndex = buffer.indexOf('\n\n')
                }
            }
        }).catch((err) => {
            if (err.name === 'AbortError') {
                signalDone()
            }
        })

        return () => controller.abort()
    }
}

export const api = new ApiClient(API_BASE)

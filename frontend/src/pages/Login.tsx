import { useState } from 'react'
import { Zap, BookOpen, Search, Save, FolderUp, Globe, FolderOpen, TrendingUp, Bot, BarChart3 } from 'lucide-react'
import { useAuthStore } from '../store/authStore'
import '../styles/__ami__/Login.css'

export default function Login() {
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState('')
    const [isLoading, setIsLoading] = useState(false)
    const { setToken, setUser } = useAuthStore()

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault()
        setError('')
        setIsLoading(true)

        try {
            const apiUrl = import.meta.env.VITE_API_URL || '/v2/api'
            const response = await fetch(
                `${apiUrl}/auth/login`,
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password }),
                }
            )

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}))
                throw new Error(errorData.detail || errorData.message || `Login failed: ${response.status} ${response.statusText}`)
            }

            const data = await response.json()
            
            if (!data.access_token) {
                throw new Error('No access token received from server')
            }

            setToken(data.access_token)
            setUser({
                id: data.user.id,
                username: data.user.username,
                email: data.user.email,
                role: data.user.role,
            })

            // Force re-render by reloading the page (App component will detect token)
            window.location.reload()
        } catch (err) {
            console.error('Login error:', err)
            setError(err instanceof Error ? err.message : 'Login failed. Please check your credentials.')
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <div className="login-container">
            <div className="login-info-panel">

                <div className="info-content">
                    <div className="feature-section">
                        <h2>
                            <Bot size={24} strokeWidth={2} />
                            Intelligent Chat Assistant
                        </h2>
                        <ul className="feature-list">
                            <li>
                                <span className="feature-icon">
                                    <Zap size={22} strokeWidth={2} />
                                </span>
                                <div>
                                    <strong>Multiple Thinking Modes</strong>
                                    <span>Fast, Balanced, or Deep reasoning for different needs</span>
                                </div>
                            </li>
                            <li>
                                <span className="feature-icon">
                                    <BookOpen size={22} strokeWidth={2} />
                                </span>
                                <div>
                                    <strong>RAG-Powered Responses</strong>
                                    <span>Context-aware answers from your knowledge base</span>
                                </div>
                            </li>
                            <li>
                                <span className="feature-icon">
                                    <Search size={22} strokeWidth={2} />
                                </span>
                                <div>
                                    <strong>Web Search Integration</strong>
                                    <span>Real-time information from the web when needed</span>
                                </div>
                            </li>
                            <li>
                                <span className="feature-icon">
                                    <Save size={22} strokeWidth={2} />
                                </span>
                                <div>
                                    <strong>Session History</strong>
                                    <span>Save and continue conversations seamlessly</span>
                                </div>
                            </li>
                        </ul>
                    </div>

                    <div className="feature-section">
                        <h2>
                            <BarChart3 size={24} strokeWidth={2} />
                            Data Management
                        </h2>
                        <ul className="feature-list">
                            <li>
                                <span className="feature-icon">
                                    <FolderUp size={22} strokeWidth={2} />
                                </span>
                                <div>
                                    <strong>Document Upload</strong>
                                    <span>Support for PDF, DOCX, TXT, Markdown, and more</span>
                                </div>
                            </li>
                            <li>
                                <span className="feature-icon">
                                    <Globe size={22} strokeWidth={2} />
                                </span>
                                <div>
                                    <strong>Web Crawling</strong>
                                    <span>Extract and ingest content from websites</span>
                                </div>
                            </li>
                            <li>
                                <span className="feature-icon">
                                    <FolderOpen size={22} strokeWidth={2} />
                                </span>
                                <div>
                                    <strong>Collection Management</strong>
                                    <span>Organize documents into logical collections</span>
                                </div>
                            </li>
                            <li>
                                <span className="feature-icon">
                                    <TrendingUp size={22} strokeWidth={2} />
                                </span>
                                <div>
                                    <strong>Analytics & Stats</strong>
                                    <span>Monitor your data and system performance</span>
                                </div>
                            </li>
                        </ul>
                    </div>
                </div>

                <div className="info-footer">
                    <p>© 2025 PTIT - Posts and Telecommunications Institute of Technology</p>
                </div>
            </div>

            <div className="login-form-panel">
                <div className="login-form-content">
                    <div className="form-header">
                        <h2>Welcome Back</h2>
                        <p>Sign in to continue</p>
                    </div>

                    {error && <div className="error-message">{error}</div>}

                    <form onSubmit={handleLogin}>
                        <div className="form-group">
                            <label htmlFor="username">Username</label>
                            <input
                                id="username"
                                type="text"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                placeholder="Enter your username"
                                disabled={isLoading}
                                autoFocus
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="password">Password</label>
                            <input
                                id="password"
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                placeholder="Enter your password"
                                disabled={isLoading}
                            />
                        </div>

                        <button type="submit" className="btn-login" disabled={isLoading || !username || !password}>
                            {isLoading ? 'Signing in...' : 'Sign In'}
                        </button>
                    </form>
                </div>
            </div>
        </div>
    )
}


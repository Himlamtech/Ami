import { useEffect, useState } from 'react'
import { MessageSquare, BarChart3, Users, FileText, LogOut } from 'lucide-react'
import { useAuthStore } from './store/authStore'
import Login from './pages/Login'
import Chat from './pages/Chat'
import DataManagement from './pages/DataManagement'
import UserManagement from './pages/UserManagement'
import LogManagement from './pages/LogManagement'
import './App.css'

type AppView = 'chat' | 'data' | 'users' | 'logs'

function App() {
    const { token, user, logout, initialize } = useAuthStore()
    const [isInitialized, setIsInitialized] = useState(false)
    const [currentView, setCurrentView] = useState<AppView>('chat')

    useEffect(() => {
        const init = async () => {
            await initialize()
            setIsInitialized(true)
        }
        init()
    }, [])

    if (!isInitialized) {
        return (
            <div className="app-loading">
                <div className="loader"></div>
            </div>
        )
    }

    if (!token) {
        return <Login />
    }

    return (
        <div className="app-container">
            <nav className="app-nav">
                <div className="nav-brand">
                    <img src="/assets/logo_ptit.png" alt="PTIT Logo" className="nav-logo" />
                    <span className="nav-title">Ami System</span>
                </div>

                <div className="nav-menu">
                    <button
                        className={`nav-item ${currentView === 'chat' ? 'active' : ''}`}
                        onClick={() => setCurrentView('chat')}
                    >
                        <MessageSquare size={18} />
                        <span>Chat</span>
                    </button>
                    <button
                        className={`nav-item ${currentView === 'data' ? 'active' : ''}`}
                        onClick={() => setCurrentView('data')}
                    >
                        <BarChart3 size={18} />
                        <span>Data Management</span>
                    </button>

                    {user?.role === 'admin' && (
                        <>
                            <button
                                className={`nav-item ${currentView === 'users' ? 'active' : ''}`}
                                onClick={() => setCurrentView('users')}
                            >
                                <Users size={18} />
                                <span>User Management</span>
                            </button>
                            <button
                                className={`nav-item ${currentView === 'logs' ? 'active' : ''}`}
                                onClick={() => setCurrentView('logs')}
                            >
                                <FileText size={18} />
                                <span>Log Management</span>
                            </button>
                        </>
                    )}
                </div>

                <div className="nav-user">
                    <span className="user-name">{user?.username || 'User'}</span>
                    <button className="btn-logout" onClick={logout}>
                        <LogOut size={16} />
                        <span>Logout</span>
                    </button>
                </div>
            </nav>

            <div className="app-content">
                {currentView === 'chat' && <Chat />}
                {currentView === 'data' && <DataManagement />}
                {currentView === 'users' && user?.role === 'admin' && <UserManagement />}
                {currentView === 'logs' && user?.role === 'admin' && <LogManagement />}
            </div>
        </div>
    )
}

export default App


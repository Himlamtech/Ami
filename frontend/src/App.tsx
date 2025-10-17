import { Navigate, Route, Routes } from 'react-router-dom'
import { Box } from '@mui/material'
import { useAuthStore } from './store/authStore'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Documents from './pages/Documents'
import Layout from './components/Layout'

function App() {
    const token = useAuthStore((state) => state.token)

    if (!token) {
        return <Login />
    }

    return (
        <Layout>
            <Routes>
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/documents" element={<Documents />} />
                <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
        </Layout>
    )
}

export default App


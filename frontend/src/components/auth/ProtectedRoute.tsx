import { Navigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'

interface ProtectedRouteProps {
    children: React.ReactNode
    requireAdmin?: boolean
}

export default function ProtectedRoute({ children, requireAdmin = false }: ProtectedRouteProps) {
    const { isAuthenticated, user } = useAuthStore()
    const location = useLocation()

    if (!isAuthenticated) {
        return <Navigate to="/login" state={{ from: location.pathname }} replace />
    }

    if (requireAdmin) {
        const isAdmin = user?.role === 'admin' || user?.email?.toLowerCase().includes('admin')
        if (!isAdmin) {
            return <Navigate to="/chat" replace />
        }
    }

    return <>{children}</>
}

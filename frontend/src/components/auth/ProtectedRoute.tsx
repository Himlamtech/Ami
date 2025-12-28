import { Navigate, useLocation } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { useAuthStore } from '@/stores/authStore'
import LoadingSpinner from '@/components/shared/LoadingSpinner'
import { profileApi } from '@/features/profile/api/profileApi'

interface ProtectedRouteProps {
    children: React.ReactNode
    requireAdmin?: boolean
}

export default function ProtectedRoute({ children, requireAdmin = false }: ProtectedRouteProps) {
    const { isAuthenticated, user } = useAuthStore()
    const location = useLocation()
    const [profileStatus, setProfileStatus] = useState<'unknown' | 'complete' | 'incomplete'>('unknown')

    useEffect(() => {
        let isActive = true
        if (!isAuthenticated || !user?.id) {
            setProfileStatus('unknown')
            return
        }

        profileApi.get(user.id)
            .then((profile) => {
                if (!isActive) return
                const isComplete = Boolean(profile.name?.trim()) && Boolean(profile.major?.trim())
                setProfileStatus(isComplete ? 'complete' : 'incomplete')
            })
            .catch(() => {
                if (!isActive) return
                setProfileStatus('incomplete')
            })

        return () => {
            isActive = false
        }
    }, [isAuthenticated, user?.id])

    if (!isAuthenticated) {
        return <Navigate to="/login" state={{ from: location.pathname }} replace />
    }

    if (profileStatus === 'unknown') {
        return (
            <div className="flex items-center justify-center h-full min-h-[200px]">
                <LoadingSpinner size="lg" />
            </div>
        )
    }

    const isProfileRoute = location.pathname.startsWith('/chat/profile')
    if (profileStatus === 'incomplete' && !isProfileRoute) {
        return <Navigate to="/chat/profile" replace />
    }

    if (requireAdmin) {
        const canAccessAdmin = user?.role === 'admin' || user?.role === 'manager'
        if (!canAccessAdmin) {
            return <Navigate to="/chat" replace />
        }
    }

    return <>{children}</>
}

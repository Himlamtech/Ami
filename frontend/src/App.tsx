import { lazy, Suspense } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from '@/components/ui/toaster'
import LoadingSpinner from '@/components/shared/LoadingSpinner'
import ProtectedRoute from '@/components/auth/ProtectedRoute'

// Layouts
import ChatLayout from '@/layouts/ChatLayout'
import AdminLayout from '@/layouts/AdminLayout'

// Lazy load pages - Auth
const LoginPage = lazy(() => import('@/features/auth/pages/LoginPage'))
const RegisterPage = lazy(() => import('@/features/auth/pages/RegisterPage'))
const ForgotPasswordPage = lazy(() => import('@/features/auth/pages/ForgotPasswordPage'))

// Lazy load pages - Chat/User
const ChatPage = lazy(() => import('@/features/chat/pages/ChatPage'))
const ProfilePage = lazy(() => import('@/features/profile/pages/ProfilePage'))
const SavedPage = lazy(() => import('@/features/bookmarks/pages/SavedPage'))
const DocsPage = lazy(() => import('@/features/docs/pages/DocsPage'))
const LandingPage = lazy(() => import('@/features/landing/pages/LandingPage'))

// Lazy load pages - Admin
const DashboardPage = lazy(() => import('@/features/admin/pages/DashboardPage'))
const ConversationsPage = lazy(() => import('@/features/admin/pages/ConversationsPage'))
const FeedbackPage = lazy(() => import('@/features/admin/pages/FeedbackPage'))
const AnalyticsPage = lazy(() => import('@/features/admin/pages/AnalyticsPage'))
const KnowledgePage = lazy(() => import('@/features/admin/pages/KnowledgePage'))
const DatasourcesPage = lazy(() => import('@/features/admin/pages/DatasourcesPage'))
const VectorStorePage = lazy(() => import('@/features/admin/pages/VectorStorePage'))
const UsersPage = lazy(() => import('@/features/admin/pages/UsersPage'))
const SettingsPage = lazy(() => import('@/features/admin/pages/SettingsPage'))

function PageLoader() {
    return (
        <div className="flex items-center justify-center h-full min-h-[400px]">
            <LoadingSpinner size="lg" />
        </div>
    )
}

function App() {
    return (
        <BrowserRouter>
            <Suspense fallback={<PageLoader />}>
                <Routes>
                    {/* Auth Routes */}
                    <Route path="/login" element={<LoginPage />} />
                    <Route path="/register" element={<RegisterPage />} />
                    <Route path="/forgot-password" element={<ForgotPasswordPage />} />

                    {/* Chat Routes - Protected */}
                    {/* Public Routes */}
                    <Route path="/" element={<LandingPage />} />

                    {/* Chat Routes - Protected */}
                    <Route path="/chat" element={
                        <ProtectedRoute>
                            <ChatLayout />
                        </ProtectedRoute>
                    }>
                        <Route index element={<ChatPage />} />
                        <Route path=":sessionId" element={<ChatPage />} />
                        <Route path="saved" element={<SavedPage />} />
                        <Route path="docs" element={<DocsPage />} />
                        <Route path="profile" element={<ProfilePage />} />
                    </Route>

                    {/* Admin Routes - Protected & Admin Only */}
                    <Route path="/admin" element={
                        <ProtectedRoute requireAdmin>
                            <AdminLayout />
                        </ProtectedRoute>
                    }>
                        <Route index element={<DashboardPage />} />
                        <Route path="conversations" element={<ConversationsPage />} />
                        <Route path="feedback" element={<FeedbackPage />} />
                        <Route path="analytics" element={<AnalyticsPage />} />
                        <Route path="knowledge" element={<KnowledgePage />} />
                        <Route path="datasources" element={<DatasourcesPage />} />
                        <Route path="vector-store" element={<VectorStorePage />} />
                        <Route path="users" element={<UsersPage />} />
                        <Route path="settings" element={<SettingsPage />} />
                    </Route>

                    {/* Fallback */}
                    <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
            </Suspense>
            <Toaster />
        </BrowserRouter>
    )
}

export default App

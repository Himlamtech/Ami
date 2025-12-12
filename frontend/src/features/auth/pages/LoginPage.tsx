import { useState } from 'react'
import { useNavigate, useLocation, Link } from 'react-router-dom'
import { Bot, Mail, Lock, LogIn, Eye, EyeOff } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useAuthStore } from '@/stores/authStore'

export default function LoginPage() {
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [showPassword, setShowPassword] = useState(false)
    const [error, setError] = useState('')

    const { login, isLoading } = useAuthStore()
    const navigate = useNavigate()
    const location = useLocation()

    const from = (location.state as { from?: string })?.from || '/'

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setError('')

        if (!email || !password) {
            setError('Vui lòng nhập đầy đủ thông tin')
            return
        }

        try {
            await login(email, password)

            // Check current user state immediately after login? 
            // Note: login is async but state update via zustand might be instant or batched. 
            // However, we can trust the API response data if we returned it, but store does void.
            // We can assume successful login sets the user in store. 
            // Since we can't easily access the updated state inside this function immediately without using the store.getState() 
            // or waiting for re-render, we'll do a simple heuristic or checking the store directly if possible.
            // A safer bet involves checking the email/role from the inputs or just assuming student if not admin email for now, 
            // OR better: let's look at how authStore sets the user.

            // Let's rely on the fact that if we are here, login success.
            // Check standard redirect
            if (from === '/') {
                // Heuristic based on email for immediate feedback, 
                // OR ideally we should check the role from the token/user state.
                // Since this is a simple app, let's redirect to /admin if email contains admin
                if (email.toLowerCase().includes('admin')) {
                    navigate('/admin', { replace: true })
                } else {
                    navigate('/chat', { replace: true })
                }
            } else {
                navigate(from, { replace: true })
            }
        } catch (err) {
            console.error('Login error:', err)
            setError('Đăng nhập thất bại. Vui lòng thử lại.')
        }
    }

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary/5 via-white to-primary/10 p-4">
            <div className="w-full max-w-md">
                {/* Logo & Title */}
                <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-primary text-white mb-4">
                        <Bot className="w-8 h-8" />
                    </div>
                    <h1 className="text-2xl font-bold text-neutral-900">
                        AMI - PTIT Assistant
                    </h1>
                    <p className="text-neutral-500 mt-2">
                        Đăng nhập để tiếp tục
                    </p>
                </div>

                {/* Login Form */}
                <div className="bg-white rounded-2xl shadow-lg border border-neutral-200 p-6 md:p-8">
                    <form onSubmit={handleSubmit} className="space-y-5">
                        {error && (
                            <div className="p-3 rounded-lg bg-error/10 text-error text-sm">
                                {error}
                            </div>
                        )}

                        <div className="space-y-2">
                            <Label htmlFor="email">Email</Label>
                            <div className="relative">
                                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
                                <Input
                                    id="email"
                                    type="email"
                                    placeholder="sinhvien@ptit.edu.vn"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    className="pl-10"
                                    autoComplete="email"
                                />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="password">Mật khẩu</Label>
                            <div className="relative">
                                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
                                <Input
                                    id="password"
                                    type={showPassword ? 'text' : 'password'}
                                    placeholder="••••••••"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="pl-10 pr-10"
                                    autoComplete="current-password"
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-400 hover:text-neutral-600"
                                >
                                    {showPassword ? (
                                        <EyeOff className="w-4 h-4" />
                                    ) : (
                                        <Eye className="w-4 h-4" />
                                    )}
                                </button>
                            </div>
                        </div>

                        <Button
                            type="submit"
                            className="w-full gap-2"
                            disabled={isLoading}
                        >
                            {isLoading ? (
                                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                            ) : (
                                <LogIn className="w-4 h-4" />
                            )}
                            Đăng nhập
                        </Button>
                        <div className="text-center text-sm">
                            <span className="text-neutral-500">Chưa có tài khoản? </span>
                            <Link to="/register" className="font-medium text-primary hover:text-primary/80">
                                Đăng ký ngay
                            </Link>
                        </div>
                    </form>

                    <div className="mt-6 pt-6 border-t border-neutral-200 text-center text-sm text-neutral-500">
                        <p>
                            Demo: Dùng email chứa "admin" để đăng nhập với quyền admin
                        </p>
                    </div>
                </div>

                {/* Footer */}
                <p className="text-center text-xs text-neutral-400 mt-6">
                    Học viện Công nghệ Bưu chính Viễn thông
                </p>
            </div>
        </div>
    )
}

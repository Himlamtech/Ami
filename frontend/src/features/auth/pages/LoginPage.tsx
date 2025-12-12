import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
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
            navigate(from, { replace: true })
        } catch (err) {
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

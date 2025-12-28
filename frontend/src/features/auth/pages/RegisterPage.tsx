import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Eye, EyeOff, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useAuthStore } from '@/stores/authStore'
import { useToast } from '@/hooks/useToast'

const registerSchema = z.object({
    fullName: z.string().min(2, 'Họ tên phải có ít nhất 2 ký tự'),
    email: z.string().email('Email không hợp lệ').endsWith('@ptit.edu.vn', 'Vui lòng sử dụng email PTIT (@ptit.edu.vn)'),
    password: z.string().min(6, 'Mật khẩu phải có ít nhất 6 ký tự'),
    confirmPassword: z.string()
}).refine((data) => data.password === data.confirmPassword, {
    message: "Mật khẩu không khớp",
    path: ["confirmPassword"],
})

type RegisterForm = z.infer<typeof registerSchema>

export default function RegisterPage() {
    const registrationDisabled = true
    const [showPassword, setShowPassword] = useState(false)
    const [isLoading, setIsLoading] = useState(false)
    const navigate = useNavigate()
    const { toast } = useToast()
    const registerUser = useAuthStore((state) => state.register)

    const {
        register,
        handleSubmit,
        formState: { errors },
    } = useForm<RegisterForm>({
        resolver: zodResolver(registerSchema),
    })

    const onSubmit = async (data: RegisterForm) => {
        if (registrationDisabled) {
            toast({
                variant: 'destructive',
                title: 'Đăng ký bị vô hiệu hóa',
                description: 'Vui lòng liên hệ admin để tạo tài khoản.',
            })
            return
        }
        setIsLoading(true)
        try {
            await registerUser({
                email: data.email,
                password: data.password,
                full_name: data.fullName
            })
            toast({
                title: 'Đăng ký thành công',
                description: 'Vui lòng kiểm tra email để xác thực tài khoản.',
            })
            navigate('/login')
        } catch (error) {
            toast({
                variant: 'destructive',
                title: 'Đăng ký thất bại',
                description: 'Email này có thể đã được sử dụng.',
            })
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4 py-12 sm:px-6 lg:px-8">
            <div className="w-full max-w-md space-y-8 bg-white p-8 rounded-xl shadow-lg">
                <div className="text-center">
                    <h2 className="text-3xl font-bold tracking-tight text-gray-900">Đăng ký tài khoản</h2>
                    <p className="mt-2 text-sm text-gray-600">
                        Dành cho sinh viên PTIT
                    </p>
                </div>

                <form className="mt-8 space-y-6" onSubmit={handleSubmit(onSubmit)}>
                    {registrationDisabled && (
                        <div className="rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800">
                            Đăng ký tài khoản đang tạm khóa. Vui lòng liên hệ admin để được tạo tài khoản.
                        </div>
                    )}
                    <div className="space-y-4">
                        <div className="space-y-2">
                            <Label htmlFor="fullName">Họ và tên</Label>
                            <Input
                                id="fullName"
                                placeholder="Nguyễn Văn A"
                                {...register('fullName')}
                                disabled={registrationDisabled}
                                className={errors.fullName ? 'border-red-500' : ''}
                            />
                            {errors.fullName && (
                                <p className="text-sm text-red-500">{errors.fullName.message}</p>
                            )}
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="email">Email PTIT</Label>
                            <Input
                                id="email"
                                type="email"
                                placeholder="example@ptit.edu.vn"
                                {...register('email')}
                                disabled={registrationDisabled}
                                className={errors.email ? 'border-red-500' : ''}
                            />
                            {errors.email && (
                                <p className="text-sm text-red-500">{errors.email.message}</p>
                            )}
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="password">Mật khẩu</Label>
                            <div className="relative">
                                <Input
                                    id="password"
                                    type={showPassword ? 'text' : 'password'}
                                    {...register('password')}
                                    disabled={registrationDisabled}
                                    className={errors.password ? 'border-red-500' : ''}
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                                >
                                    {showPassword ? (
                                        <EyeOff className="h-4 w-4" />
                                    ) : (
                                        <Eye className="h-4 w-4" />
                                    )}
                                </button>
                            </div>
                            {errors.password && (
                                <p className="text-sm text-red-500">{errors.password.message}</p>
                            )}
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="confirmPassword">Xác nhận mật khẩu</Label>
                            <Input
                                id="confirmPassword"
                                type="password"
                                {...register('confirmPassword')}
                                disabled={registrationDisabled}
                                className={errors.confirmPassword ? 'border-red-500' : ''}
                            />
                            {errors.confirmPassword && (
                                <p className="text-sm text-red-500">{errors.confirmPassword.message}</p>
                            )}
                        </div>
                    </div>

                    <Button
                        type="submit"
                        className="w-full"
                        disabled={isLoading || registrationDisabled}
                    >
                        {isLoading ? (
                            <>
                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                Đang xử lý...
                            </>
                        ) : (
                            'Đăng ký'
                        )}
                    </Button>

                    <div className="text-center text-sm">
                        <span className="text-gray-500">Đã có tài khoản? </span>
                        <Link to="/login" className="font-medium text-primary hover:text-primary/80">
                            Đăng nhập
                        </Link>
                    </div>
                </form>
            </div>
        </div>
    )
}

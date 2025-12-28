import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
    Search,
    RefreshCw,
    Plus,
    MoreHorizontal,
    Eye,
    Edit,
    Trash2,
    Shield,
    UserCog,
    Mail,
    Calendar,
    Key,
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
    DialogFooter,
} from '@/components/ui/dialog'
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select'
import { cn, formatDate } from '@/lib/utils'
import { useToast } from '@/hooks/useToast'
import { api } from '@/lib/api'
import { useAuthStore } from '@/stores/authStore'

interface SystemUser {
    id: string
    username: string
    email: string
    name: string
    role: 'admin' | 'manager'
    status: 'active' | 'inactive' | 'suspended'
    last_login: string | null
    created_at: string
    created_by?: string
}

interface CreateUserPayload {
    username: string
    email: string
    name: string
    password: string
    role: 'admin' | 'manager'
}

const roleConfig = {
    admin: { label: 'Admin', color: 'bg-error/10 text-error border-error/20' },
    manager: { label: 'Manager', color: 'bg-warning/10 text-warning border-warning/20' },
}

const statusConfig = {
    active: { label: 'Hoạt động', color: 'bg-success/10 text-success border-success/20' },
    inactive: { label: 'Chưa kích hoạt', color: 'bg-neutral-100 text-neutral-500 border-neutral-200' },
    suspended: { label: 'Tạm khóa', color: 'bg-warning/10 text-warning border-warning/20' },
}

export default function SystemUsersPage() {
    const { user: currentUser } = useAuthStore()
    const queryClient = useQueryClient()
    const { toast } = useToast()

    const [searchQuery, setSearchQuery] = useState('')
    const [debouncedSearch, setDebouncedSearch] = useState('')
    const [showCreateDialog, setShowCreateDialog] = useState(false)
    const [selectedUser, setSelectedUser] = useState<SystemUser | null>(null)
    const [showDeleteDialog, setShowDeleteDialog] = useState(false)
    const [newUser, setNewUser] = useState<CreateUserPayload>({
        username: '',
        email: '',
        name: '',
        password: '',
        role: 'manager',
    })

    // Debounce search
    useEffect(() => {
        const timer = setTimeout(() => {
            setDebouncedSearch(searchQuery)
        }, 300)
        return () => clearTimeout(timer)
    }, [searchQuery])

    // Fetch system users
    const { data, isLoading, refetch } = useQuery({
        queryKey: ['admin', 'system-users', debouncedSearch],
        queryFn: async () => {
            const params: Record<string, string> = { type: 'system' }
            if (debouncedSearch) params.search = debouncedSearch
            return api.get<{ data: SystemUser[]; total: number }>('/admin/users', params)
        },
    })

    const users = data?.data || []

    // Create user mutation
    const createUserMutation = useMutation({
        mutationFn: (payload: CreateUserPayload) => api.post('/admin/users', payload),
        onSuccess: () => {
            toast({ title: 'Tạo tài khoản thành công' })
            setShowCreateDialog(false)
            setNewUser({ username: '', email: '', name: '', password: '', role: 'manager' })
            queryClient.invalidateQueries({ queryKey: ['admin', 'system-users'] })
        },
        onError: () => {
            toast({ title: 'Lỗi tạo tài khoản', variant: 'destructive' })
        },
    })

    // Delete user mutation
    const deleteUserMutation = useMutation({
        mutationFn: (userId: string) => api.delete(`/admin/users/${userId}`),
        onSuccess: () => {
            toast({ title: 'Xóa tài khoản thành công' })
            setShowDeleteDialog(false)
            setSelectedUser(null)
            queryClient.invalidateQueries({ queryKey: ['admin', 'system-users'] })
        },
        onError: () => {
            toast({ title: 'Lỗi xóa tài khoản', variant: 'destructive' })
        },
    })

    const handleCreateUser = () => {
        if (!newUser.username || !newUser.email || !newUser.password) {
            toast({ title: 'Vui lòng điền đầy đủ thông tin', variant: 'destructive' })
            return
        }
        createUserMutation.mutate(newUser)
    }

    const handleDeleteUser = () => {
        if (!selectedUser) return
        deleteUserMutation.mutate(selectedUser.id)
    }

    const isAdmin = currentUser?.role === 'admin'

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-semibold text-neutral-900">System Users</h1>
                    <p className="text-sm text-neutral-500 mt-1">
                        Quản lý tài khoản Admin và Manager của hệ thống
                    </p>
                </div>
                <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm" onClick={() => refetch()}>
                        <RefreshCw className="w-4 h-4 mr-2" />
                        Làm mới
                    </Button>
                    {isAdmin && (
                        <Button size="sm" onClick={() => setShowCreateDialog(true)}>
                            <Plus className="w-4 h-4 mr-2" />
                            Tạo tài khoản
                        </Button>
                    )}
                </div>
            </div>

            {/* Info Banner */}
            <Card className="border-primary/20 bg-primary/5">
                <CardContent className="p-4">
                    <div className="flex items-start gap-3">
                        <Shield className="w-5 h-5 text-primary mt-0.5" />
                        <div className="text-sm">
                            <p className="font-medium text-primary">Về System Users</p>
                            <p className="text-neutral-600 mt-1">
                                System Users là các tài khoản có quyền truy cập Admin Panel.
                                <strong> Admin</strong> có toàn quyền quản lý hệ thống.
                                <strong> Manager</strong> có thể xem và quản lý nội dung nhưng không thể tạo admin mới.
                            </p>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Search */}
            <Card>
                <CardContent className="p-4">
                    <div className="relative max-w-md">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
                        <Input
                            placeholder="Tìm theo tên, email, username..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="pl-10"
                        />
                    </div>
                </CardContent>
            </Card>

            {/* Users Table */}
            <Card>
                <CardHeader className="pb-3">
                    <CardTitle className="text-base">
                        Danh sách tài khoản ({users.length})
                    </CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                    {isLoading ? (
                        <div className="flex items-center justify-center py-12">
                            <RefreshCw className="w-6 h-6 animate-spin text-neutral-400" />
                        </div>
                    ) : users.length === 0 ? (
                        <div className="text-center py-12 text-neutral-500">
                            <UserCog className="w-12 h-12 mx-auto mb-3 text-neutral-300" />
                            <p>Không có tài khoản nào</p>
                        </div>
                    ) : (
                        <div className="overflow-x-auto">
                            <table className="w-full">
                                <thead>
                                    <tr className="border-b border-[color:var(--border)] bg-neutral-50/50">
                                        <th className="text-left py-3 px-4 text-xs font-medium text-neutral-500 uppercase">
                                            Tài khoản
                                        </th>
                                        <th className="text-left py-3 px-4 text-xs font-medium text-neutral-500 uppercase">
                                            Vai trò
                                        </th>
                                        <th className="text-left py-3 px-4 text-xs font-medium text-neutral-500 uppercase">
                                            Trạng thái
                                        </th>
                                        <th className="text-left py-3 px-4 text-xs font-medium text-neutral-500 uppercase">
                                            Đăng nhập cuối
                                        </th>
                                        <th className="text-left py-3 px-4 text-xs font-medium text-neutral-500 uppercase">
                                            Ngày tạo
                                        </th>
                                        <th className="text-right py-3 px-4 text-xs font-medium text-neutral-500 uppercase">
                                            Actions
                                        </th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {users.map((user) => (
                                        <tr
                                            key={user.id}
                                            className="border-b border-[color:var(--border)] last:border-0 hover:bg-[var(--surface2)] transition-colors"
                                        >
                                            <td className="py-3 px-4">
                                                <div className="flex items-center gap-3">
                                                    <div className="w-9 h-9 rounded-full bg-primary/10 flex items-center justify-center">
                                                        <UserCog className="w-4 h-4 text-primary" />
                                                    </div>
                                                    <div>
                                                        <p className="text-sm font-medium">{user.name}</p>
                                                        <p className="text-xs text-neutral-500">
                                                            @{user.username} · {user.email}
                                                        </p>
                                                    </div>
                                                </div>
                                            </td>
                                            <td className="py-3 px-4">
                                                <Badge className={cn('border', roleConfig[user.role].color)}>
                                                    {roleConfig[user.role].label}
                                                </Badge>
                                            </td>
                                            <td className="py-3 px-4">
                                                <Badge className={cn('border', statusConfig[user.status].color)}>
                                                    {statusConfig[user.status].label}
                                                </Badge>
                                            </td>
                                            <td className="py-3 px-4 text-sm text-neutral-600">
                                                {user.last_login ? formatDate(user.last_login) : 'Chưa đăng nhập'}
                                            </td>
                                            <td className="py-3 px-4 text-sm text-neutral-600">
                                                {formatDate(user.created_at)}
                                            </td>
                                            <td className="py-3 px-4 text-right">
                                                <DropdownMenu>
                                                    <DropdownMenuTrigger asChild>
                                                        <Button variant="ghost" size="icon" className="h-8 w-8">
                                                            <MoreHorizontal className="w-4 h-4" />
                                                        </Button>
                                                    </DropdownMenuTrigger>
                                                    <DropdownMenuContent align="end">
                                                        <DropdownMenuItem>
                                                            <Eye className="w-4 h-4 mr-2" />
                                                            Xem chi tiết
                                                        </DropdownMenuItem>
                                                        {isAdmin && (
                                                            <>
                                                                <DropdownMenuItem>
                                                                    <Edit className="w-4 h-4 mr-2" />
                                                                    Chỉnh sửa
                                                                </DropdownMenuItem>
                                                                <DropdownMenuItem>
                                                                    <Key className="w-4 h-4 mr-2" />
                                                                    Reset mật khẩu
                                                                </DropdownMenuItem>
                                                                <DropdownMenuSeparator />
                                                                <DropdownMenuItem
                                                                    className="text-error"
                                                                    disabled={user.id === currentUser?.id}
                                                                    onClick={() => {
                                                                        setSelectedUser(user)
                                                                        setShowDeleteDialog(true)
                                                                    }}
                                                                >
                                                                    <Trash2 className="w-4 h-4 mr-2" />
                                                                    Xóa tài khoản
                                                                </DropdownMenuItem>
                                                            </>
                                                        )}
                                                    </DropdownMenuContent>
                                                </DropdownMenu>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* Create User Dialog */}
            <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Tạo tài khoản mới</DialogTitle>
                        <DialogDescription>
                            Tạo tài khoản Admin hoặc Manager để truy cập Admin Panel
                        </DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <Label htmlFor="username">Username *</Label>
                                <Input
                                    id="username"
                                    placeholder="admin_username"
                                    value={newUser.username}
                                    onChange={(e) => setNewUser({ ...newUser, username: e.target.value })}
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="email">Email *</Label>
                                <Input
                                    id="email"
                                    type="email"
                                    placeholder="admin@ami.edu.vn"
                                    value={newUser.email}
                                    onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                                />
                            </div>
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="name">Họ tên</Label>
                            <Input
                                id="name"
                                placeholder="Nguyễn Văn A"
                                value={newUser.name}
                                onChange={(e) => setNewUser({ ...newUser, name: e.target.value })}
                            />
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="password">Mật khẩu *</Label>
                            <Input
                                id="password"
                                type="password"
                                placeholder="••••••••"
                                value={newUser.password}
                                onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                            />
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="role">Vai trò</Label>
                            <Select
                                value={newUser.role}
                                onValueChange={(value: 'admin' | 'manager') =>
                                    setNewUser({ ...newUser, role: value })
                                }
                            >
                                <SelectTrigger>
                                    <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="manager">Manager</SelectItem>
                                    <SelectItem value="admin">Admin</SelectItem>
                                </SelectContent>
                            </Select>
                            <p className="text-xs text-neutral-500">
                                Manager có quyền xem và quản lý nội dung. Admin có toàn quyền.
                            </p>
                        </div>
                    </div>
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
                            Hủy
                        </Button>
                        <Button
                            onClick={handleCreateUser}
                            disabled={createUserMutation.isPending}
                        >
                            {createUserMutation.isPending ? (
                                <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                            ) : (
                                <Plus className="w-4 h-4 mr-2" />
                            )}
                            Tạo tài khoản
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>

            {/* Delete Confirmation Dialog */}
            <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Xác nhận xóa tài khoản</DialogTitle>
                        <DialogDescription>
                            Bạn có chắc chắn muốn xóa tài khoản{' '}
                            <strong>{selectedUser?.name}</strong> (@{selectedUser?.username})?
                            Hành động này không thể hoàn tác.
                        </DialogDescription>
                    </DialogHeader>
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setShowDeleteDialog(false)}>
                            Hủy
                        </Button>
                        <Button
                            variant="destructive"
                            onClick={handleDeleteUser}
                            disabled={deleteUserMutation.isPending}
                        >
                            {deleteUserMutation.isPending ? (
                                <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                            ) : (
                                <Trash2 className="w-4 h-4 mr-2" />
                            )}
                            Xóa tài khoản
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    )
}

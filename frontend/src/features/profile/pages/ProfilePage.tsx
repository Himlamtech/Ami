import { useState, useEffect } from 'react'
import { User, Settings, LogOut, Save } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { useAuthStore } from '@/stores/authStore'
import { Link } from 'react-router-dom'

import { profileApi } from '../api/profileApi'

interface UserProfileState {
    name: string
    studentId: string
    major: string
    year: string
    email: string
    class_name?: string
}

export default function ProfilePage() {
    const { user } = useAuthStore()

    const [profile, setProfile] = useState<UserProfileState>({
        name: user?.displayName || '',
        studentId: '',
        major: 'Công nghệ thông tin', // Default
        year: 'K6x',
        email: user?.email || '',
        class_name: ''
    })

    // Load profile
    useEffect(() => {
        if (!user?.id) return
        profileApi.get(user.id).then(data => {
            setProfile({
                name: data.name || '',
                studentId: data.student_id || '',
                major: data.major || '',
                year: data.level || '',
                email: data.email || '',
                class_name: data.class_name || ''
            })
        }).catch((error) => {
            console.error('[ProfilePage] Failed to load profile', error)
        })
    }, [user?.id])

    const [isEditing, setIsEditing] = useState(false)
    const levelLabel = (() => {
        const match = profile.studentId.match(/\D*(\d{2})/)
        if (match) {
            const intakeYear = 2000 + Number(match[1])
            const now = new Date()
            const isAfterJuly = now.getMonth() >= 6
            const rawYear = now.getFullYear() - intakeYear + (isAfterJuly ? 1 : 0)
            if (rawYear <= 1) return 'Năm 1'
            if (rawYear === 2) return 'Năm 2'
            if (rawYear === 3) return 'Năm 3'
            if (rawYear === 4) return 'Năm 4'
            return 'Cuối'
        }

        const value = (profile.year || '').toLowerCase()
        const mapping: Record<string, string> = {
            freshman: 'Năm 1',
            sophomore: 'Năm 2',
            junior: 'Năm 3',
            senior: 'Năm 4',
            graduate: 'Cuối',
            alumni: 'Cuối',
        }
        return mapping[value] || 'Chưa xác định'
    })()

    const handleSave = async () => {
        if (!user?.id) return
        try {
            await profileApi.update(user.id, {
                name: profile.name,
                student_id: profile.studentId,
                email: profile.email,
                major: profile.major,
                class_name: profile.class_name
            })
            setIsEditing(false)
        } catch (e) {
            console.error(e)
        }
    }

    return (
        <div className="flex-1 overflow-y-auto p-4 lg:p-6">
            <div className="max-w-2xl mx-auto space-y-6">
                {/* Profile Header */}
                <Card>
                    <CardContent className="p-6">
                        <div className="flex items-center gap-4">
                            <Avatar className="w-20 h-20">
                            <AvatarFallback className="bg-primary text-white text-2xl">
                                    {(profile.name || 'U').charAt(0)}
                                </AvatarFallback>
                            </Avatar>
                            <div className="flex-1">
                                <h2 className="text-xl font-bold text-neutral-900">{profile.name}</h2>
                                <p className="text-neutral-500">{profile.studentId}</p>
                                <p className="text-sm text-neutral-400">{profile.major} - {levelLabel}</p>
                            </div>
                            <Button
                                variant={isEditing ? 'default' : 'outline'}
                                onClick={() => isEditing ? handleSave() : setIsEditing(true)}
                            >
                                {isEditing ? (
                                    <>
                                        <Save className="w-4 h-4 mr-2" />
                                        Lưu
                                    </>
                                ) : (
                                    <>
                                        <Settings className="w-4 h-4 mr-2" />
                                        Chỉnh sửa
                                    </>
                                )}
                            </Button>
                        </div>
                    </CardContent>
                </Card>

                {/* Profile Info */}
                <Card>
                    <CardHeader>
                        <CardTitle className="text-base flex items-center gap-2">
                            <User className="w-5 h-5" />
                            Thông tin cá nhân
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div>
                            <label className="text-sm font-medium text-neutral-700">Họ và tên</label>
                            <Input
                                value={profile.name}
                                onChange={(e) => setProfile({ ...profile, name: e.target.value })}
                                disabled={!isEditing}
                                className="mt-1"
                            />
                        </div>
                        <div>
                            <label className="text-sm font-medium text-neutral-700">Mã sinh viên</label>
                            <Input
                                value={profile.studentId}
                                onChange={(e) => setProfile({ ...profile, studentId: e.target.value })}
                                disabled={!isEditing}
                                className="mt-1"
                            />
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="text-sm font-medium text-neutral-700">Ngành học</label>
                                <Input
                                    value={profile.major}
                                    onChange={(e) => setProfile({ ...profile, major: e.target.value })}
                                    disabled={!isEditing}
                                    className="mt-1"
                                />
                            </div>
                            <div>
                                <label className="text-sm font-medium text-neutral-700">Năm học</label>
                                <Input
                                    value={levelLabel}
                                    disabled
                                    className="mt-1 bg-neutral-50"
                                />
                            </div>
                        </div>
                        <div>
                            <label className="text-sm font-medium text-neutral-700">Email</label>
                            <Input
                                value={profile.email}
                                onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                                disabled={!isEditing}
                                className="mt-1"
                            />
                        </div>
                    </CardContent>
                </Card>

                {/* Preferences */}
                <Card>
                    <CardHeader>
                        <CardTitle className="text-base flex items-center gap-2">
                            <Settings className="w-5 h-5" />
                            Tùy chọn
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        {(user?.role === 'admin' || user?.role === 'manager') && (
                            <div className="flex items-center justify-between p-4 bg-primary/5 rounded-lg border border-primary/20">
                                <div>
                                    <p className="font-medium text-primary">Admin Console</p>
                                    <p className="text-sm text-neutral-500">Truy cập trang quản trị hệ thống</p>
                                </div>
                                <Button asChild variant="default" size="sm">
                                    <Link to="/admin">Đi tới Admin</Link>
                                </Button>
                            </div>
                        )}
                    </CardContent>
                </Card>

                {/* Logout */}
                <Button variant="outline" className="w-full text-error border-error hover:bg-error/5">
                    <LogOut className="w-4 h-4 mr-2" />
                    Đăng xuất
                </Button>
            </div>
        </div>
    )
}

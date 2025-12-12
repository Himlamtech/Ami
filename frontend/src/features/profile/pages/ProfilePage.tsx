import { useState } from 'react'
import { User, Settings, Bell, Shield, HelpCircle, LogOut, ChevronRight, Save } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Switch } from '@/components/ui/switch'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'

interface UserProfile {
    name: string
    studentId: string
    major: string
    year: string
    email: string
}

export default function ProfilePage() {
    const [profile, setProfile] = useState<UserProfile>({
        name: 'Nguyen Van A',
        studentId: 'B21DCCN001',
        major: 'Công nghệ thông tin',
        year: 'K66',
        email: 'nguyenvana.b21cn001@stu.ptit.edu.vn',
    })

    const [preferences, setPreferences] = useState({
        detailLevel: 'detailed',
        notifications: true,
        language: 'vi',
    })

    const [isEditing, setIsEditing] = useState(false)

    const handleSave = () => {
        // TODO: Save to API
        setIsEditing(false)
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
                                    {profile.name.charAt(0)}
                                </AvatarFallback>
                            </Avatar>
                            <div className="flex-1">
                                <h2 className="text-xl font-bold text-neutral-900">{profile.name}</h2>
                                <p className="text-neutral-500">{profile.studentId}</p>
                                <p className="text-sm text-neutral-400">{profile.major} - {profile.year}</p>
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
                                disabled
                                className="mt-1 bg-neutral-50"
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
                                <label className="text-sm font-medium text-neutral-700">Khóa</label>
                                <Input
                                    value={profile.year}
                                    onChange={(e) => setProfile({ ...profile, year: e.target.value })}
                                    disabled={!isEditing}
                                    className="mt-1"
                                />
                            </div>
                        </div>
                        <div>
                            <label className="text-sm font-medium text-neutral-700">Email</label>
                            <Input
                                value={profile.email}
                                disabled
                                className="mt-1 bg-neutral-50"
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
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="font-medium">Mức độ chi tiết câu trả lời</p>
                                <p className="text-sm text-neutral-500">AMI sẽ trả lời theo mức độ bạn chọn</p>
                            </div>
                            <select
                                value={preferences.detailLevel}
                                onChange={(e) => setPreferences({ ...preferences, detailLevel: e.target.value })}
                                className="border rounded-lg px-3 py-2 text-sm"
                            >
                                <option value="brief">Ngắn gọn</option>
                                <option value="detailed">Chi tiết</option>
                            </select>
                        </div>
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="font-medium">Thông báo</p>
                                <p className="text-sm text-neutral-500">Nhận thông báo về tin tức PTIT</p>
                            </div>
                            <Switch
                                checked={preferences.notifications}
                                onCheckedChange={(checked) => setPreferences({ ...preferences, notifications: checked })}
                            />
                        </div>
                    </CardContent>
                </Card>

                {/* Quick Links */}
                <Card>
                    <CardContent className="p-0">
                        <div className="divide-y">
                            {[
                                { icon: Bell, label: 'Thông báo', path: '/notifications' },
                                { icon: Shield, label: 'Bảo mật & Quyền riêng tư', path: '/privacy' },
                                { icon: HelpCircle, label: 'Trợ giúp & Hỗ trợ', path: '/help' },
                            ].map((item) => (
                                <button
                                    key={item.path}
                                    className="flex items-center justify-between w-full px-4 py-3 hover:bg-neutral-50 transition-colors"
                                >
                                    <div className="flex items-center gap-3">
                                        <item.icon className="w-5 h-5 text-neutral-500" />
                                        <span>{item.label}</span>
                                    </div>
                                    <ChevronRight className="w-5 h-5 text-neutral-400" />
                                </button>
                            ))}
                        </div>
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

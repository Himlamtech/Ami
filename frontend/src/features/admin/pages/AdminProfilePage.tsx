import { useState, useEffect } from 'react'
import { User, Mail, Shield, Calendar, RefreshCw, Save, Eye, EyeOff, Key } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { useToast } from '@/hooks/useToast'
import { useAuthStore } from '@/stores/authStore'
import { formatDate } from '@/lib/utils'

interface AdminProfile {
    id: string
    email: string
    name: string
    role: string
    createdAt: string
    lastLogin: string
}

export default function AdminProfilePage() {
    const { user } = useAuthStore()
    const [profile, setProfile] = useState<AdminProfile | null>(null)
    const [loading, setLoading] = useState(true)
    const [saving, setSaving] = useState(false)
    const [showPasswordForm, setShowPasswordForm] = useState(false)
    const [passwords, setPasswords] = useState({
        current: '',
        new: '',
        confirm: '',
    })
    const [showPasswords, setShowPasswords] = useState({
        current: false,
        new: false,
        confirm: false,
    })
    const { toast } = useToast()

    useEffect(() => {
        loadProfile()
    }, [])

    const loadProfile = async () => {
        setLoading(true)
        try {
            // In real implementation, fetch from API
            setProfile({
                id: user?.id || 'admin-1',
                email: user?.email || 'admin@ami.edu.vn',
                name: user?.name || 'Administrator',
                role: 'admin',
                createdAt: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
                lastLogin: new Date().toISOString(),
            })
        } finally {
            setLoading(false)
        }
    }

    const handleSaveProfile = async () => {
        if (!profile) return
        setSaving(true)
        try {
            // API call to update profile
            await new Promise((resolve) => setTimeout(resolve, 500))
            toast({
                title: 'Profile updated',
                description: 'Your profile has been saved successfully.',
            })
        } catch {
            toast({
                title: 'Error',
                description: 'Failed to update profile.',
                variant: 'destructive',
            })
        } finally {
            setSaving(false)
        }
    }

    const handleChangePassword = async () => {
        if (passwords.new !== passwords.confirm) {
            toast({
                title: 'Error',
                description: 'New passwords do not match.',
                variant: 'destructive',
            })
            return
        }

        if (passwords.new.length < 8) {
            toast({
                title: 'Error',
                description: 'Password must be at least 8 characters.',
                variant: 'destructive',
            })
            return
        }

        setSaving(true)
        try {
            // API call to change password
            await new Promise((resolve) => setTimeout(resolve, 500))
            toast({
                title: 'Password changed',
                description: 'Your password has been updated successfully.',
            })
            setPasswords({ current: '', new: '', confirm: '' })
            setShowPasswordForm(false)
        } catch {
            toast({
                title: 'Error',
                description: 'Failed to change password.',
                variant: 'destructive',
            })
        } finally {
            setSaving(false)
        }
    }

    const getInitials = (name: string) => {
        return name
            .split(' ')
            .map((n) => n[0])
            .join('')
            .toUpperCase()
            .slice(0, 2)
    }

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <RefreshCw className="w-6 h-6 animate-spin text-primary" />
            </div>
        )
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-2xl font-semibold text-neutral-900">Admin Profile</h1>
                <p className="text-sm text-neutral-500 mt-1">Manage your admin account settings</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Profile Card */}
                <Card className="lg:col-span-1">
                    <CardContent className="p-6">
                        <div className="flex flex-col items-center text-center">
                            <Avatar className="w-24 h-24 mb-4">
                                <AvatarFallback className="text-2xl bg-primary/10 text-primary">
                                    {profile ? getInitials(profile.name) : 'AD'}
                                </AvatarFallback>
                            </Avatar>
                            <h2 className="text-xl font-semibold text-neutral-900">
                                {profile?.name}
                            </h2>
                            <p className="text-sm text-neutral-500">{profile?.email}</p>
                            <Badge className="mt-2 capitalize">{profile?.role}</Badge>
                        </div>

                        <Separator className="my-6" />

                        <div className="space-y-4">
                            <div className="flex items-center gap-3 text-sm">
                                <Calendar className="w-4 h-4 text-neutral-400" />
                                <div>
                                    <p className="text-neutral-500">Member since</p>
                                    <p className="font-medium">
                                        {profile?.createdAt ? formatDate(profile.createdAt) : '-'}
                                    </p>
                                </div>
                            </div>
                            <div className="flex items-center gap-3 text-sm">
                                <Shield className="w-4 h-4 text-neutral-400" />
                                <div>
                                    <p className="text-neutral-500">Last login</p>
                                    <p className="font-medium">
                                        {profile?.lastLogin ? formatDate(profile.lastLogin) : '-'}
                                    </p>
                                </div>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {/* Edit Profile */}
                <Card className="lg:col-span-2">
                    <CardHeader>
                        <CardTitle>Profile Information</CardTitle>
                        <CardDescription>Update your account details</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="space-y-2">
                                <Label htmlFor="name">Full Name</Label>
                                <div className="relative">
                                    <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
                                    <Input
                                        id="name"
                                        value={profile?.name || ''}
                                        onChange={(e) =>
                                            setProfile((prev) =>
                                                prev ? { ...prev, name: e.target.value } : null
                                            )
                                        }
                                        className="pl-10"
                                    />
                                </div>
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="email">Email</Label>
                                <div className="relative">
                                    <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
                                    <Input
                                        id="email"
                                        type="email"
                                        value={profile?.email || ''}
                                        onChange={(e) =>
                                            setProfile((prev) =>
                                                prev ? { ...prev, email: e.target.value } : null
                                            )
                                        }
                                        className="pl-10"
                                    />
                                </div>
                            </div>
                        </div>

                        <div className="flex justify-end">
                            <Button onClick={handleSaveProfile} disabled={saving}>
                                {saving ? (
                                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                                ) : (
                                    <Save className="w-4 h-4 mr-2" />
                                )}
                                Save Changes
                            </Button>
                        </div>
                    </CardContent>
                </Card>

                {/* Change Password */}
                <Card className="lg:col-span-3">
                    <CardHeader>
                        <div className="flex items-center justify-between">
                            <div>
                                <CardTitle>Security</CardTitle>
                                <CardDescription>Manage your password</CardDescription>
                            </div>
                            {!showPasswordForm && (
                                <Button variant="outline" onClick={() => setShowPasswordForm(true)}>
                                    <Key className="w-4 h-4 mr-2" />
                                    Change Password
                                </Button>
                            )}
                        </div>
                    </CardHeader>
                    {showPasswordForm && (
                        <CardContent className="space-y-6">
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                <div className="space-y-2">
                                    <Label htmlFor="current-password">Current Password</Label>
                                    <div className="relative">
                                        <Input
                                            id="current-password"
                                            type={showPasswords.current ? 'text' : 'password'}
                                            value={passwords.current}
                                            onChange={(e) =>
                                                setPasswords({ ...passwords, current: e.target.value })
                                            }
                                        />
                                        <Button
                                            type="button"
                                            variant="ghost"
                                            size="icon"
                                            className="absolute right-1 top-1/2 -translate-y-1/2 h-7 w-7"
                                            onClick={() =>
                                                setShowPasswords({
                                                    ...showPasswords,
                                                    current: !showPasswords.current,
                                                })
                                            }
                                        >
                                            {showPasswords.current ? (
                                                <EyeOff className="w-4 h-4" />
                                            ) : (
                                                <Eye className="w-4 h-4" />
                                            )}
                                        </Button>
                                    </div>
                                </div>

                                <div className="space-y-2">
                                    <Label htmlFor="new-password">New Password</Label>
                                    <div className="relative">
                                        <Input
                                            id="new-password"
                                            type={showPasswords.new ? 'text' : 'password'}
                                            value={passwords.new}
                                            onChange={(e) =>
                                                setPasswords({ ...passwords, new: e.target.value })
                                            }
                                        />
                                        <Button
                                            type="button"
                                            variant="ghost"
                                            size="icon"
                                            className="absolute right-1 top-1/2 -translate-y-1/2 h-7 w-7"
                                            onClick={() =>
                                                setShowPasswords({
                                                    ...showPasswords,
                                                    new: !showPasswords.new,
                                                })
                                            }
                                        >
                                            {showPasswords.new ? (
                                                <EyeOff className="w-4 h-4" />
                                            ) : (
                                                <Eye className="w-4 h-4" />
                                            )}
                                        </Button>
                                    </div>
                                </div>

                                <div className="space-y-2">
                                    <Label htmlFor="confirm-password">Confirm Password</Label>
                                    <div className="relative">
                                        <Input
                                            id="confirm-password"
                                            type={showPasswords.confirm ? 'text' : 'password'}
                                            value={passwords.confirm}
                                            onChange={(e) =>
                                                setPasswords({ ...passwords, confirm: e.target.value })
                                            }
                                        />
                                        <Button
                                            type="button"
                                            variant="ghost"
                                            size="icon"
                                            className="absolute right-1 top-1/2 -translate-y-1/2 h-7 w-7"
                                            onClick={() =>
                                                setShowPasswords({
                                                    ...showPasswords,
                                                    confirm: !showPasswords.confirm,
                                                })
                                            }
                                        >
                                            {showPasswords.confirm ? (
                                                <EyeOff className="w-4 h-4" />
                                            ) : (
                                                <Eye className="w-4 h-4" />
                                            )}
                                        </Button>
                                    </div>
                                </div>
                            </div>

                            <div className="flex justify-end gap-2">
                                <Button
                                    variant="outline"
                                    onClick={() => {
                                        setShowPasswordForm(false)
                                        setPasswords({ current: '', new: '', confirm: '' })
                                    }}
                                >
                                    Cancel
                                </Button>
                                <Button onClick={handleChangePassword} disabled={saving}>
                                    {saving ? (
                                        <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                                    ) : (
                                        <Key className="w-4 h-4 mr-2" />
                                    )}
                                    Update Password
                                </Button>
                            </div>
                        </CardContent>
                    )}
                </Card>
            </div>
        </div>
    )
}

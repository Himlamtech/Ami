import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { adminApi } from '../api/adminApi'
import {
    Search,
    Filter,
    Download,
    MoreHorizontal,
    Eye,
    ChevronLeft,
    ChevronRight,
    Star,
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { formatDate } from '@/lib/utils'
import type { AdminUser } from '@/types/admin'


export default function UsersPage() {
    const [searchQuery, setSearchQuery] = useState('')

    const { data } = useQuery({
        queryKey: ['admin', 'users', searchQuery],
        queryFn: () => adminApi.getUsers({
            search: searchQuery
        }),
    })

    const filteredUsers: AdminUser[] = data?.data || []

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-neutral-900">User Profiles</h2>
                <Button variant="outline" size="sm">
                    <Download className="w-4 h-4 mr-2" />
                    Export
                </Button>
            </div>

            {/* Filters */}
            <Card>
                <CardContent className="p-4">
                    <div className="flex flex-wrap items-center gap-4">
                        <div className="relative flex-1 min-w-[200px]">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
                            <Input
                                placeholder="Search users..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="pl-9"
                            />
                        </div>
                        <Button variant="outline" size="sm">
                            <Filter className="w-4 h-4 mr-2" />
                            Major
                        </Button>
                        <Button variant="outline" size="sm">
                            <Filter className="w-4 h-4 mr-2" />
                            Level
                        </Button>
                        <Button variant="outline" size="sm">
                            Sort: Last Active ▼
                        </Button>
                    </div>
                </CardContent>
            </Card>

            {/* Table */}
            <Card>
                <CardContent className="p-0">
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead>
                                <tr className="border-b bg-neutral-50">
                                    <th className="text-left py-3 px-4 text-sm font-medium text-neutral-500">
                                        User
                                    </th>
                                    <th className="text-left py-3 px-4 text-sm font-medium text-neutral-500">
                                        Major
                                    </th>
                                    <th className="text-left py-3 px-4 text-sm font-medium text-neutral-500">
                                        Sessions
                                    </th>
                                    <th className="text-left py-3 px-4 text-sm font-medium text-neutral-500">
                                        Avg Rating
                                    </th>
                                    <th className="text-left py-3 px-4 text-sm font-medium text-neutral-500">
                                        Last Active
                                    </th>
                                    <th className="text-left py-3 px-4 text-sm font-medium text-neutral-500"></th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredUsers.map((user) => (
                                    <tr key={user.id} className="border-b last:border-0 hover:bg-neutral-50">
                                        <td className="py-3 px-4">
                                            <div>
                                                <p className="text-sm font-medium">👤 {user.name}</p>
                                                <p className="text-xs text-neutral-500">{user.studentId}</p>
                                                <div className="flex gap-1 mt-1">
                                                    {user.topInterests.map((interest) => (
                                                        <span
                                                            key={interest}
                                                            className="text-xs px-1.5 py-0.5 bg-neutral-100 rounded"
                                                        >
                                                            🏷️ {interest}
                                                        </span>
                                                    ))}
                                                </div>
                                            </div>
                                        </td>
                                        <td className="py-3 px-4">
                                            <p className="text-sm">{user.major}</p>
                                            <p className="text-xs text-neutral-500">{user.year}</p>
                                        </td>
                                        <td className="py-3 px-4 text-sm">{user.sessionCount}</td>
                                        <td className="py-3 px-4">
                                            <div className="flex items-center gap-1">
                                                <Star className="w-4 h-4 text-warning fill-warning" />
                                                <span className="text-sm">{user.avgRating.toFixed(1)}</span>
                                            </div>
                                        </td>
                                        <td className="py-3 px-4 text-sm text-neutral-500">
                                            {formatDate(user.lastActive)}
                                        </td>
                                        <td className="py-3 px-4">
                                            <DropdownMenu>
                                                <DropdownMenuTrigger asChild>
                                                    <Button variant="ghost" size="icon">
                                                        <MoreHorizontal className="w-4 h-4" />
                                                    </Button>
                                                </DropdownMenuTrigger>
                                                <DropdownMenuContent align="end">
                                                    <DropdownMenuItem>
                                                        <Eye className="w-4 h-4 mr-2" />
                                                        View Profile
                                                    </DropdownMenuItem>
                                                    <DropdownMenuItem>View Sessions</DropdownMenuItem>
                                                </DropdownMenuContent>
                                            </DropdownMenu>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>

                    {/* Pagination */}
                    <div className="flex items-center justify-between p-4 border-t">
                        <p className="text-sm text-neutral-500">
                            Showing 1-{filteredUsers.length} of {data?.total || 0} users
                        </p>
                        <div className="flex items-center gap-2">
                            <Button variant="outline" size="sm" disabled>
                                <ChevronLeft className="w-4 h-4" />
                                Prev
                            </Button>
                            <Button variant="outline" size="sm" className="bg-primary text-white">
                                1
                            </Button>
                            <Button variant="outline" size="sm">
                                2
                            </Button>
                            <Button variant="outline" size="sm">
                                3
                            </Button>
                            <Button variant="outline" size="sm">
                                Next
                                <ChevronRight className="w-4 h-4" />
                            </Button>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* User Insights */}
            <Card>
                <CardHeader>
                    <CardTitle className="text-base">📊 User Insights</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-4 gap-4">
                        <div className="text-center p-4 bg-neutral-50 rounded-lg">
                            <p className="text-2xl font-bold">567</p>
                            <p className="text-sm text-neutral-500">Total Users</p>
                        </div>
                        <div className="text-center p-4 bg-neutral-50 rounded-lg">
                            <p className="text-2xl font-bold">234</p>
                            <p className="text-sm text-neutral-500">Active (7d)</p>
                        </div>
                        <div className="text-center p-4 bg-neutral-50 rounded-lg">
                            <p className="text-2xl font-bold">45</p>
                            <p className="text-sm text-neutral-500">New (30d)</p>
                        </div>
                        <div className="text-center p-4 bg-neutral-50 rounded-lg">
                            <p className="text-2xl font-bold">12</p>
                            <p className="text-sm text-neutral-500">Avg Sessions</p>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    )
}

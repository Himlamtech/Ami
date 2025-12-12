import { useState } from 'react'
import {
    ThumbsUp,
    ThumbsDown,
    Download,
    Filter,
    ChevronDown,
    AlertTriangle,
    CheckCircle,
} from 'lucide-react'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { cn } from '@/lib/utils'
import type { FeedbackItem } from '@/types/admin'

// Mock data
const mockFeedback: FeedbackItem[] = [
    {
        id: '1',
        type: 'not_helpful',
        userId: 'u1',
        userName: 'Nguyen Van A',
        studentId: 'B21DCCN001',
        question: 'Điều kiện để được học bổng khuyến khích học tập là gì?',
        response: 'Học bổng KKHT dành cho sinh viên có điểm trung bình từ 3.2 trở lên...',
        comment: 'Thông tin này cũ rồi, năm nay đổi điều kiện mới',
        categories: ['Incorrect', 'Outdated'],
        sources: [{ title: 'Quy định học bổng 2023', score: 0.78, outdated: true }],
        createdAt: new Date(Date.now() - 7200000).toISOString(),
        reviewed: false,
    },
    {
        id: '2',
        type: 'incomplete',
        userId: 'u2',
        userName: 'Tran Thi B',
        studentId: 'B21DCCN045',
        question: 'Làm sao để đăng ký thực tập?',
        response: 'Bạn cần liên hệ với khoa để được hướng dẫn...',
        comment: 'Thiếu thông tin về thời gian và quy trình cụ thể',
        categories: ['Incomplete'],
        sources: [{ title: 'Hướng dẫn thực tập', score: 0.65 }],
        createdAt: new Date(Date.now() - 18000000).toISOString(),
        reviewed: false,
    },
]

export default function FeedbackPage() {
    const [activeTab, setActiveTab] = useState('negative')

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-neutral-900">Feedback Analysis</h2>
                <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm">
                        Period: Last 30 days
                        <ChevronDown className="w-4 h-4 ml-2" />
                    </Button>
                    <Button variant="outline" size="sm">
                        <Download className="w-4 h-4 mr-2" />
                        Export
                    </Button>
                </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card>
                    <CardContent className="p-6">
                        <div className="flex items-center gap-4">
                            <div className="p-3 rounded-lg bg-secondary/10">
                                <BarChart className="w-6 h-6 text-secondary" />
                            </div>
                            <div>
                                <p className="text-2xl font-bold">1,234</p>
                                <p className="text-sm text-neutral-500">Total Feedback</p>
                                <p className="text-xs text-success">↑ 15%</p>
                            </div>
                        </div>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="p-6">
                        <div className="flex items-center gap-4">
                            <div className="p-3 rounded-lg bg-success/10">
                                <ThumbsUp className="w-6 h-6 text-success" />
                            </div>
                            <div>
                                <p className="text-2xl font-bold">72%</p>
                                <p className="text-sm text-neutral-500">Helpful Rate</p>
                                <p className="text-xs text-success">↑ 5%</p>
                            </div>
                        </div>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="p-6">
                        <div className="flex items-center gap-4">
                            <div className="p-3 rounded-lg bg-warning/10">
                                <Star className="w-6 h-6 text-warning" />
                            </div>
                            <div>
                                <p className="text-2xl font-bold">4.2/5</p>
                                <p className="text-sm text-neutral-500">Avg Rating</p>
                                <p className="text-xs text-success">↑ 0.3</p>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Tabs */}
            <Tabs value={activeTab} onValueChange={setActiveTab}>
                <TabsList>
                    <TabsTrigger value="overview">Overview</TabsTrigger>
                    <TabsTrigger value="negative">Negative Feedback</TabsTrigger>
                    <TabsTrigger value="by-topic">By Topic</TabsTrigger>
                    <TabsTrigger value="trends">Trends</TabsTrigger>
                </TabsList>

                <TabsContent value="negative" className="mt-6">
                    {/* Filters */}
                    <Card className="mb-6">
                        <CardContent className="p-4">
                            <div className="flex flex-wrap items-center gap-4">
                                <Button variant="outline" size="sm">
                                    <Filter className="w-4 h-4 mr-2" />
                                    Type
                                </Button>
                                <Button variant="outline" size="sm">
                                    <Filter className="w-4 h-4 mr-2" />
                                    Category
                                </Button>
                                <Button variant="outline" size="sm">
                                    📅 Date
                                </Button>
                                <span className="text-sm text-neutral-500">Showing 342 items</span>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Feedback List */}
                    <div className="space-y-4">
                        {mockFeedback.map((feedback) => (
                            <FeedbackCard key={feedback.id} feedback={feedback} />
                        ))}
                    </div>
                </TabsContent>

                <TabsContent value="overview">
                    <Card>
                        <CardContent className="p-6">
                            <p className="text-neutral-500">Overview content coming soon...</p>
                        </CardContent>
                    </Card>
                </TabsContent>

                <TabsContent value="by-topic">
                    <Card>
                        <CardContent className="p-6">
                            <p className="text-neutral-500">By Topic content coming soon...</p>
                        </CardContent>
                    </Card>
                </TabsContent>

                <TabsContent value="trends">
                    <Card>
                        <CardContent className="p-6">
                            <p className="text-neutral-500">Trends content coming soon...</p>
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>
        </div>
    )
}

function FeedbackCard({ feedback }: { feedback: FeedbackItem }) {
    const typeStyles = {
        not_helpful: { icon: ThumbsDown, color: 'text-error', bg: 'bg-error/10' },
        incomplete: { icon: AlertTriangle, color: 'text-warning', bg: 'bg-warning/10' },
        incorrect: { icon: AlertTriangle, color: 'text-error', bg: 'bg-error/10' },
        helpful: { icon: ThumbsUp, color: 'text-success', bg: 'bg-success/10' },
    }

    const style = typeStyles[feedback.type] || typeStyles.not_helpful
    const Icon = style.icon

    return (
        <Card>
            <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className={cn('p-2 rounded-lg', style.bg)}>
                            <Icon className={cn('w-4 h-4', style.color)} />
                        </div>
                        <div>
                            <p className="font-medium uppercase text-sm">{feedback.type.replace('_', ' ')}</p>
                            <p className="text-xs text-neutral-500">
                                {new Date(feedback.createdAt).toLocaleString('vi-VN')}
                            </p>
                        </div>
                    </div>
                    <Button variant="ghost" size="sm">
                        ⋮
                    </Button>
                </div>
            </CardHeader>
            <CardContent className="space-y-4">
                {/* User */}
                <div className="flex items-center gap-2 text-sm">
                    <span>👤</span>
                    <span className="font-medium">{feedback.userName}</span>
                    <span className="text-neutral-500">({feedback.studentId})</span>
                </div>

                {/* Question */}
                <div>
                    <p className="text-xs font-medium text-neutral-500 mb-1">❓ Question:</p>
                    <p className="text-sm bg-neutral-50 p-3 rounded-lg">"{feedback.question}"</p>
                </div>

                {/* Response */}
                <div>
                    <p className="text-xs font-medium text-neutral-500 mb-1">🤖 Response:</p>
                    <p className="text-sm bg-neutral-50 p-3 rounded-lg">"{feedback.response}"</p>
                </div>

                {/* User Comment */}
                {feedback.comment && (
                    <div>
                        <p className="text-xs font-medium text-neutral-500 mb-1">📝 User Comment:</p>
                        <p className="text-sm bg-warning/10 p-3 rounded-lg text-warning-700">
                            "{feedback.comment}"
                        </p>
                    </div>
                )}

                {/* Categories */}
                <div className="flex items-center gap-2">
                    <span className="text-xs text-neutral-500">🏷️ Categories:</span>
                    {feedback.categories.map((cat) => (
                        <span
                            key={cat}
                            className="px-2 py-1 bg-neutral-100 rounded-full text-xs font-medium"
                        >
                            {cat}
                        </span>
                    ))}
                </div>

                {/* Sources */}
                <div>
                    <p className="text-xs font-medium text-neutral-500 mb-1">📄 Sources Used:</p>
                    <ul className="space-y-1">
                        {feedback.sources.map((source, i) => (
                            <li key={i} className="text-sm flex items-center gap-2">
                                <span>•</span>
                                <span>{source.title}</span>
                                <span className="text-neutral-400">(score: {source.score.toFixed(2)})</span>
                                {source.outdated && (
                                    <span className="text-warning text-xs">⚠️ Outdated</span>
                                )}
                            </li>
                        ))}
                    </ul>
                </div>

                {/* Actions */}
                <div className="flex gap-2 pt-2 border-t">
                    <Button variant="outline" size="sm">
                        <CheckCircle className="w-4 h-4 mr-1" />
                        Mark Reviewed
                    </Button>
                    <Button variant="outline" size="sm">
                        Create Improvement Task
                    </Button>
                    <Button variant="outline" size="sm">
                        Link to Gap
                    </Button>
                </div>
            </CardContent>
        </Card>
    )
}

// Missing imports
import { BarChart2 as BarChart, Star } from 'lucide-react'

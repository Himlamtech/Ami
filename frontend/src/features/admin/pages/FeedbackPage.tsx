import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { adminApi } from '../api/adminApi'
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

interface FeedbackDashboardMetrics {
    total_feedback?: number
    helpful_rate?: number
    negative_count?: number
}


export default function FeedbackPage() {
    const [activeTab, setActiveTab] = useState('negative')

    const { data, isLoading } = useQuery({
        queryKey: ['admin', 'feedback', activeTab],
        queryFn: () => adminApi.getFeedbackList({
            limit: 20
        }),
    })

    const { data: dashboard } = useQuery<FeedbackDashboardMetrics>({
        queryKey: ['admin', 'feedback-dashboard'],
        queryFn: async () => {
            const response = await adminApi.getFeedbackDashboard()
            return response as FeedbackDashboardMetrics
        },
    })

    const feedbackList = data?.data || []

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
                            <div className="p-3 rounded-lg bg-primary/10">
                                <ThumbsDown className="w-6 h-6 text-primary" />
                            </div>
                            <div>
                                <p className="text-2xl font-bold">{dashboard?.total_feedback || 0}</p>
                                <p className="text-sm text-neutral-500">Total Feedback</p>
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
                                <p className="text-2xl font-bold">{dashboard?.helpful_rate ? `${(dashboard.helpful_rate * 100).toFixed(0)}%` : '0%'}</p>
                                <p className="text-sm text-neutral-500">Helpful Rate</p>
                            </div>
                        </div>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="p-6">
                        <div className="flex items-center gap-4">
                            <div className="p-3 rounded-lg bg-neutral-100">
                                <AlertTriangle className="w-6 h-6 text-neutral-600" />
                            </div>
                            <div>
                                <p className="text-2xl font-bold">{dashboard?.negative_count || 0}</p>
                                <p className="text-sm text-neutral-500">Negative</p>
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
                                <span className="text-sm text-neutral-500">Showing {feedbackList.length} items</span>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Feedback List */}
                    <div className="space-y-4">
                        {isLoading ? (
                            <div className="text-center py-8 text-neutral-500">Loading...</div>
                        ) : (
                            feedbackList.map((feedback) => (
                                <FeedbackCard key={feedback.id} feedback={feedback} />
                            ))
                        )}
                        {!isLoading && feedbackList.length === 0 && (
                            <div className="text-center py-8 text-neutral-500">No feedback found</div>
                        )}
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

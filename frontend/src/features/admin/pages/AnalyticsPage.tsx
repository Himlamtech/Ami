import { useState } from 'react'
import { ChevronDown, AlertCircle } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Input } from '@/components/ui/input'

import { useQuery } from '@tanstack/react-query'
import { adminApi } from '../api/adminApi'

export default function AnalyticsPage() {
    const [activeTab, setActiveTab] = useState('costs')

    const costQuery = useQuery({
        queryKey: ['admin', 'analytics-costs'],
        queryFn: () => adminApi.getCostBreakdown({ period: 'month' }),
    })

    const usageQuery = useQuery({
        queryKey: ['admin', 'analytics-usage'],
        queryFn: () => adminApi.getAnalytics({ period: 'month' }),
    })

    const costData = (costQuery.data as Record<string, number>) || {}
    const usageData = (usageQuery.data as Record<string, number>) || {}
    const loadingCosts = costQuery.isLoading
    const loadingUsage = usageQuery.isLoading

    const totalSpent = costData.total_spent ?? costData.total ?? 0
    const budget = costData.budget ?? 200
    const remaining = budget - totalSpent
    const projected = costData.projected ?? totalSpent
    const budgetUsedPercent = budget > 0 ? Math.min(100, Math.max(0, (totalSpent / budget) * 100)) : 0
    const remainingPercent = 100 - budgetUsedPercent

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-neutral-900">Analytics & Costs</h2>
                <Button variant="outline" size="sm">
                    Period: This Month
                    <ChevronDown className="w-4 h-4 ml-2" />
                </Button>
            </div>

            {/* Tabs */}
            <Tabs value={activeTab} onValueChange={setActiveTab}>
                <TabsList>
                    <TabsTrigger value="usage">Usage</TabsTrigger>
                    <TabsTrigger value="costs">Costs</TabsTrigger>
                    <TabsTrigger value="performance">Performance</TabsTrigger>
                </TabsList>

                <TabsContent value="costs" className="mt-6 space-y-6">
                    {/* Cost Overview */}
                    <Card>
                        <CardHeader>
                            <CardTitle>💰 Cost Overview - December 2024</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="grid grid-cols-4 gap-6 mb-6">
                                <div className="text-center p-4 bg-neutral-50 rounded-lg">
                                    <p className="text-3xl font-bold text-primary">
                                        {loadingCosts ? '...' : `$${totalSpent.toFixed(2)}`}
                                    </p>
                                    <p className="text-sm text-neutral-500">Total Spent</p>
                                    <p className="text-xs text-neutral-400">
                                        {loadingCosts ? '--' : `${budgetUsedPercent.toFixed(0)}%`}
                                    </p>
                                </div>
                                <div className="text-center p-4 bg-neutral-50 rounded-lg">
                                    <p className="text-3xl font-bold">
                                        {loadingCosts ? '...' : `$${budget.toFixed(2)}`}
                                    </p>
                                    <p className="text-sm text-neutral-500">Budget</p>
                                    <p className="text-xs text-neutral-400">100%</p>
                                </div>
                                <div className="text-center p-4 bg-neutral-50 rounded-lg">
                                    <p className="text-3xl font-bold text-success">
                                        {loadingCosts ? '...' : `$${Math.max(0, remaining).toFixed(2)}`}
                                    </p>
                                    <p className="text-sm text-neutral-500">Remaining</p>
                                    <p className="text-xs text-neutral-400">
                                        {loadingCosts ? '--' : `${remainingPercent.toFixed(0)}%`}
                                    </p>
                                </div>
                                <div className="text-center p-4 bg-neutral-50 rounded-lg">
                                    <p className="text-3xl font-bold text-warning">
                                        {loadingCosts ? '...' : `$${projected.toFixed(2)}`}
                                    </p>
                                    <p className="text-sm text-neutral-500">Projected</p>
                                    <p className="text-xs text-neutral-400">
                                        {loadingCosts ? '--' : `${Math.min(100, ((projected / budget) * 100 || 0)).toFixed(0)}%`}
                                    </p>
                                </div>
                            </div>

                            {/* Progress bar */}
                            <div className="h-4 bg-neutral-100 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-gradient-to-r from-primary to-primary-600 rounded-full"
                                    style={{ width: `${budgetUsedPercent}%` }}
                                />
                            </div>
                            <p className="text-sm text-neutral-500 mt-2 text-center">
                                {loadingCosts ? 'Loading cost data...' : `${budgetUsedPercent.toFixed(0)}% of budget used`}
                            </p>
                        </CardContent>
                    </Card>

                    {/* Breakdown */}
                    <div className="grid grid-cols-2 gap-6">
                        {/* By Provider */}
                        <Card>
                            <CardHeader>
                                <CardTitle className="text-base">By Provider</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                {[
                                    { name: 'OpenAI', amount: 89.2, percentage: 70 },
                                    { name: 'Anthropic', amount: 28.5, percentage: 22 },
                                    { name: 'Gemini', amount: 9.75, percentage: 8 },
                                ].map((item) => (
                                    <div key={item.name} className="space-y-2">
                                        <div className="flex justify-between text-sm">
                                            <span>{item.name}</span>
                                            <span className="font-medium">${item.amount.toFixed(2)} ({item.percentage}%)</span>
                                        </div>
                                        <div className="h-2 bg-neutral-100 rounded-full overflow-hidden">
                                            <div
                                                className="h-full bg-primary rounded-full"
                                                style={{ width: `${item.percentage}%` }}
                                            />
                                        </div>
                                    </div>
                                ))}
                            </CardContent>
                        </Card>

                        {/* By Use Case */}
                        <Card>
                            <CardHeader>
                                <CardTitle className="text-base">By Use Case</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                {[
                                    { name: 'Chat', amount: 85.3, percentage: 67 },
                                    { name: 'RAG', amount: 25.15, percentage: 20 },
                                    { name: 'Summary', amount: 12.0, percentage: 9 },
                                    { name: 'Embedding', amount: 5.0, percentage: 4 },
                                ].map((item) => (
                                    <div key={item.name} className="space-y-2">
                                        <div className="flex justify-between text-sm">
                                            <span>{item.name}</span>
                                            <span className="font-medium">${item.amount.toFixed(2)}</span>
                                        </div>
                                        <div className="h-2 bg-neutral-100 rounded-full overflow-hidden">
                                            <div
                                                className="h-full bg-secondary rounded-full"
                                                style={{ width: `${item.percentage}%` }}
                                            />
                                        </div>
                                    </div>
                                ))}
                            </CardContent>
                        </Card>
                    </div>

                    {/* Daily Trend */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="text-base">📊 Daily Cost Trend</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="h-48 flex items-end justify-between gap-1">
                                {Array.from({ length: 30 }, (_, i) => {
                                    const height = Math.random() * 80 + 20
                                    return (
                                        <div
                                            key={i}
                                            className="flex-1 bg-primary/20 hover:bg-primary/40 rounded-t cursor-pointer transition-colors"
                                            style={{ height: `${height}%` }}
                                            title={`Day ${i + 1}: $${(height / 10).toFixed(2)}`}
                                        />
                                    )
                                })}
                            </div>
                            <div className="flex justify-between mt-2 text-xs text-neutral-500">
                                <span>1</span>
                                <span>5</span>
                                <span>10</span>
                                <span>15</span>
                                <span>20</span>
                                <span>25</span>
                                <span>30</span>
                            </div>
                            <div className="flex items-center gap-4 mt-4 text-sm">
                                <span className="flex items-center gap-2">
                                    <span className="w-3 h-3 bg-primary rounded" /> OpenAI
                                </span>
                                <span className="flex items-center gap-2">
                                    <span className="w-3 h-3 bg-secondary rounded" /> Anthropic
                                </span>
                                <span className="flex items-center gap-2">
                                    <span className="w-3 h-3 bg-success rounded" /> Gemini
                                </span>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Budget Alert Settings */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="text-base flex items-center gap-2">
                                <AlertCircle className="w-5 h-5 text-warning" />
                                Budget Alert Settings
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="flex items-end gap-4">
                                <div className="flex-1">
                                    <label className="text-sm font-medium">Threshold</label>
                                    <Input type="number" defaultValue={200} className="mt-1" />
                                </div>
                                <div className="flex-1">
                                    <label className="text-sm font-medium">Alert at</label>
                                    <Input type="number" defaultValue={80} className="mt-1" />
                                    <span className="text-xs text-neutral-500">%</span>
                                </div>
                                <div className="flex-1">
                                    <label className="text-sm font-medium">Notify via</label>
                                    <div className="flex items-center gap-2 mt-1">
                                        <input type="checkbox" defaultChecked className="rounded" />
                                        <span className="text-sm">Email</span>
                                    </div>
                                </div>
                                <Button>Save</Button>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                <TabsContent value="usage">
                    <Card>
                        <CardHeader>
                            <CardTitle className="text-base">Usage Summary</CardTitle>
                        </CardHeader>
                        <CardContent className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                            {[
                                { label: 'Requests', value: usageData.requests ?? usageData.total_requests ?? 0 },
                                { label: 'Tokens', value: usageData.tokens ?? usageData.total_tokens ?? 0 },
                                { label: 'Avg Latency (ms)', value: usageData.avg_latency ?? usageData.avg_latency_ms ?? 0 },
                            ].map((item) => (
                                <div key={item.label} className="p-4 rounded-lg bg-neutral-50 text-center">
                                    <p className="text-2xl font-semibold">
                                        {loadingUsage ? '...' : item.value}
                                    </p>
                                    <p className="text-sm text-neutral-500">{item.label}</p>
                                </div>
                            ))}
                        </CardContent>
                    </Card>
                </TabsContent>

                <TabsContent value="performance">
                    <Card>
                        <CardContent className="p-6">
                            <p className="text-neutral-500">Performance metrics coming soon...</p>
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>
        </div>
    )
}

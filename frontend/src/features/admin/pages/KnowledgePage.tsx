import { useState } from 'react'
import {
    AlertTriangle,
    ChevronDown,
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { cn } from '@/lib/utils'
import type { KnowledgeGap } from '@/types/admin'

import { useQuery } from '@tanstack/react-query'
import { adminApi } from '../api/adminApi'

export default function KnowledgePage() {
    const [activeTab, setActiveTab] = useState('gaps')

    const { data: gaps = [], isLoading: gapsLoading } = useQuery({
        queryKey: ['admin', 'knowledge-gaps'],
        queryFn: adminApi.getKnowledgeGaps,
    })

    const gapsByPriority = {
        high: gaps.filter((g: KnowledgeGap) => g.priority === 'high'),
        medium: gaps.filter((g: KnowledgeGap) => g.priority === 'medium'),
        low: gaps.filter((g: KnowledgeGap) => g.priority === 'low'),
    }

    const stats = {
        todo: gaps.filter((g: KnowledgeGap) => g.status === 'todo').length,
        inProgress: gaps.filter((g: KnowledgeGap) => g.status === 'in_progress').length,
        resolved: gaps.filter((g: KnowledgeGap) => g.status === 'resolved').length,
        ignored: gaps.filter((g: KnowledgeGap) => g.status === 'ignored').length,
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-semibold tracking-tight text-neutral-900">Knowledge Base Quality</h2>
                    <p className="text-sm text-[var(--muted)] mt-1">Identify gaps and improve answer coverage.</p>
                </div>
            </div>

            {gapsLoading && (
                <Card>
                    <CardContent className="p-4 text-sm text-neutral-500">
                        Loading knowledge gaps...
                    </CardContent>
                </Card>
            )}

            {/* Tabs */}
            <Tabs value={activeTab} onValueChange={setActiveTab}>
                <TabsList>
                    <TabsTrigger value="overview">Overview</TabsTrigger>
                    <TabsTrigger value="documents">Documents</TabsTrigger>
                    <TabsTrigger value="gaps">Gaps</TabsTrigger>
                    <TabsTrigger value="quality">Quality Metrics</TabsTrigger>
                </TabsList>

                <TabsContent value="gaps" className="mt-6 space-y-6">
                    {/* Header */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <AlertTriangle className="w-5 h-5 text-warning" />
                                Knowledge Gaps Detected
                            </CardTitle>
                            <p className="text-sm text-neutral-500">
                                Queries with low confidence (score &lt; 0.5) in the last 30 days
                            </p>
                        </CardHeader>
                    </Card>

                    {/* Gap Lists by Priority */}
                    <div className="space-y-4">
                        {/* High Priority */}
                        {gapsByPriority.high.length > 0 && (
                            <GapSection
                                title="HIGH PRIORITY"
                                count={gapsByPriority.high.reduce((acc, g) => acc + g.queryCount, 0)}
                                color="error"
                                gaps={gapsByPriority.high}
                            />
                        )}

                        {/* Medium Priority */}
                        {gapsByPriority.medium.length > 0 && (
                            <GapSection
                                title="MEDIUM PRIORITY"
                                count={gapsByPriority.medium.reduce((acc, g) => acc + g.queryCount, 0)}
                                color="warning"
                                gaps={gapsByPriority.medium}
                            />
                        )}

                        {/* Low Priority */}
                        {gapsByPriority.low.length > 0 && (
                            <GapSection
                                title="LOW PRIORITY"
                                count={gapsByPriority.low.reduce((acc, g) => acc + g.queryCount, 0)}
                                color="success"
                                gaps={gapsByPriority.low}
                            />
                        )}
                    </div>

                    {/* Resolution Progress */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="text-base">📊 Gap Resolution Progress</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="flex items-center gap-4 mb-4 text-sm">
                                <span>To Do: {stats.todo}</span>
                                <span>|</span>
                                <span>In Progress: {stats.inProgress}</span>
                                <span>|</span>
                                <span>Resolved (30d): {stats.resolved}</span>
                                <span>|</span>
                                <span>Ignored: {stats.ignored}</span>
                            </div>
                            <div className="h-3 bg-neutral-100 rounded-full overflow-hidden flex">
                                <div className="bg-success h-full" style={{ width: '55%' }} />
                                <div className="bg-warning h-full" style={{ width: '15%' }} />
                                <div className="bg-neutral-300 h-full" style={{ width: '30%' }} />
                            </div>
                            <p className="text-sm text-neutral-500 mt-2">55% resolved</p>
                        </CardContent>
                    </Card>
                </TabsContent>

                <TabsContent value="overview">
                    <Card>
                        <CardContent className="p-6">
                            <p className="text-neutral-500">Overview content coming soon...</p>
                        </CardContent>
                    </Card>
                </TabsContent>

                <TabsContent value="documents">
                    <Card>
                        <CardContent className="p-6">
                            <p className="text-neutral-500">Documents management coming soon...</p>
                        </CardContent>
                    </Card>
                </TabsContent>

                <TabsContent value="quality">
                    <Card>
                        <CardContent className="p-6">
                            <p className="text-neutral-500">Quality metrics coming soon...</p>
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>
        </div>
    )
}

function GapSection({
    title,
    count,
    color,
    gaps,
}: {
    title: string
    count: number
    color: 'error' | 'warning' | 'success'
    gaps: KnowledgeGap[]
}) {
    const dotColors = {
        error: 'bg-error',
        warning: 'bg-warning',
        success: 'bg-success',
    }

    return (
        <Card>
            <CardHeader className="flex flex-row items-center justify-between p-4 bg-[var(--surface2)]">
                <div className="flex items-center gap-2">
                    <span className={cn('w-2.5 h-2.5 rounded-full', dotColors[color])} />
                    <CardTitle className="text-sm font-semibold tracking-wide">
                        {title}
                    </CardTitle>
                </div>
                <Badge variant={color === 'error' ? 'softError' : color === 'warning' ? 'softWarning' : 'softSuccess'}>
                    {count} queries
                </Badge>
            </CardHeader>
            <CardContent className="p-0">
                {gaps.map((gap) => (
                    <GapItem key={gap.id} gap={gap} />
                ))}
            </CardContent>
        </Card>
    )
}

function GapItem({ gap }: { gap: KnowledgeGap }) {
    const [expanded, setExpanded] = useState(true)

    return (
        <div className="p-4 border-b border-[color:var(--border)] last:border-0">
            <div className="flex items-start justify-between mb-3">
                <h4 className="font-medium">"{gap.topic}"</h4>
                <Button variant="ghost" size="sm" onClick={() => setExpanded(!expanded)}>
                    <ChevronDown className={cn('w-4 h-4 transition-transform', expanded && 'rotate-180')} />
                </Button>
            </div>

            <div className="flex items-center gap-4 text-sm text-neutral-500 mb-3">
                <span>Queries: {gap.queryCount}</span>
                <span>|</span>
                <span>Avg Score: {gap.avgScore.toFixed(2)}</span>
                <span>|</span>
                <span>Feedback: 👎 {100 - gap.feedbackRate}%</span>
            </div>

            {expanded && (
                <div className="space-y-3 mt-4">
                    {/* Sample queries */}
                    <div>
                        <p className="text-xs font-medium text-neutral-500 mb-1">📝 Sample queries:</p>
                        <ul className="text-sm space-y-1">
                            {gap.sampleQueries.map((q, i) => (
                                <li key={i} className="flex items-center gap-2">
                                    <span className="text-neutral-400">•</span>
                                    "{q}"
                                </li>
                            ))}
                        </ul>
                    </div>

                    {/* Best match */}
                    {gap.bestMatch && (
                        <div>
                            <p className="text-xs font-medium text-neutral-500 mb-1">🔍 Best current match:</p>
                            <p className="text-sm">
                                "{gap.bestMatch.title}" (score: {gap.bestMatch.score.toFixed(2)})
                                {gap.bestMatch.outdated && (
                                    <span className="text-warning ml-2">⚠️ Outdated</span>
                                )}
                            </p>
                        </div>
                    )}

                    {/* Suggested action */}
                    <div>
                        <p className="text-xs font-medium text-neutral-500 mb-1">💡 Suggested action:</p>
                        <p className="text-sm text-primary">{gap.suggestedAction}</p>
                    </div>

                    {/* Status */}
                    <div className="flex items-center gap-2">
                        <span className="text-sm">Status:</span>
                        <select
                            defaultValue={gap.status}
                            className="text-sm bg-[var(--surface2)] border border-[color:var(--border)] rounded-lg px-2 py-1 focus:outline-none focus:ring-2 focus:ring-[var(--ring)]"
                        >
                            <option value="todo">To Do</option>
                            <option value="in_progress">In Progress</option>
                            <option value="resolved">Resolved</option>
                            <option value="ignored">Ignored</option>
                        </select>
                    </div>

                    {/* Actions */}
                    <div className="flex gap-2 pt-2">
                        <Button variant="outline" size="sm">
                            Mark as To Do
                        </Button>
                        <Button variant="outline" size="sm">
                            In Progress
                        </Button>
                        <Button variant="outline" size="sm">
                            Resolved
                        </Button>
                        <Button variant="ghost" size="sm" className="text-neutral-500">
                            Ignore
                        </Button>
                    </div>
                </div>
            )}
        </div>
    )
}

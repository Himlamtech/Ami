import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { formatDistanceToNow } from 'date-fns'
import { adminApi } from '../api/adminApi'
import { PendingUpdate, PendingUpdateDetail } from '@/types/admin'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
} from '@/components/ui/dialog'
import { ScrollArea } from '@/components/ui/scroll-area'
import {
    Select,
    SelectTrigger,
    SelectValue,
    SelectContent,
    SelectItem,
} from '@/components/ui/select'
import { useToast } from '@/hooks/useToast'
import { Loader2, Eye, CheckCircle, XCircle } from 'lucide-react'

const statusOptions = [
    { value: 'pending', label: 'Pending' },
    { value: 'approved', label: 'Approved' },
    { value: 'rejected', label: 'Rejected' },
    { value: 'auto_approved', label: 'Auto Approved' },
    { value: 'all', label: 'All' },
]

const detectionOptions = [
    { value: 'all', label: 'All types' },
    { value: 'new', label: 'New content' },
    { value: 'update', label: 'Update' },
    { value: 'duplicate', label: 'Duplicate' },
    { value: 'unrelated', label: 'Low value' },
]

export default function PendingApprovalsPage() {
    const [statusFilter, setStatusFilter] = useState('pending')
    const [detectionFilter, setDetectionFilter] = useState('all')
    const [detailOpen, setDetailOpen] = useState(false)
    const [detail, setDetail] = useState<PendingUpdateDetail | null>(null)
    const [detailLoading, setDetailLoading] = useState(false)
    const { toast } = useToast()
    const queryClient = useQueryClient()

    const { data, isLoading } = useQuery({
        queryKey: ['pendingUpdates', statusFilter, detectionFilter],
        queryFn: () =>
            adminApi.getPendingUpdates({
                skip: 0,
                limit: 50,
                status: statusFilter === 'all' ? undefined : statusFilter,
                detection_type: detectionFilter === 'all' ? undefined : detectionFilter,
            }),
    })
    const pendingItems = data?.items ?? []

    const approveMutation = useMutation({
        mutationFn: (id: string) => adminApi.approvePendingUpdate(id),
        onSuccess: () => {
            toast({ title: 'Update approved', variant: 'success' })
            queryClient.invalidateQueries({ queryKey: ['pendingUpdates'] })
        },
        onError: (error: any) => {
            toast({
                title: 'Approve failed',
                description: error.message,
                variant: 'destructive',
            })
        },
    })

    const rejectMutation = useMutation({
        mutationFn: (id: string) => adminApi.rejectPendingUpdate(id),
        onSuccess: () => {
            toast({ title: 'Update rejected', variant: 'success' })
            queryClient.invalidateQueries({ queryKey: ['pendingUpdates'] })
        },
        onError: (error: any) => {
            toast({
                title: 'Reject failed',
                description: error.message,
                variant: 'destructive',
            })
        },
    })

    const loadDetail = async (pendingId: string) => {
        setDetailOpen(true)
        setDetail(null)
        setDetailLoading(true)
        try {
            const response = await adminApi.getPendingUpdateDetail(pendingId)
            setDetail(response)
        } catch (error: any) {
            toast({
                title: 'Failed to load detail',
                description: error.message,
                variant: 'destructive',
            })
            setDetailOpen(false)
        } finally {
            setDetailLoading(false)
        }
    }

    const detectionBadge = (type: PendingUpdate['detection_type']) => {
        switch (type) {
            case 'new':
                return { label: 'New', variant: 'softSuccess' as const }
            case 'update':
                return { label: 'Update', variant: 'softWarning' as const }
            case 'duplicate':
                return { label: 'Duplicate', variant: 'softNeutral' as const }
            default:
                return { label: 'Low value', variant: 'softNeutral' as const }
        }
    }

    return (
        <div className="space-y-6">
            <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                <div>
                    <h2 className="text-2xl font-semibold tracking-tight">Pending Approvals</h2>
                    <p className="text-sm text-[var(--muted)] mt-1">
                        Review crawled content before it becomes part of the knowledge base.
                    </p>
                </div>
                <div className="flex flex-col md:flex-row gap-3 w-full md:w-auto">
                    <Select value={statusFilter} onValueChange={setStatusFilter}>
                        <SelectTrigger className="md:w-40">
                            <SelectValue placeholder="Status" />
                        </SelectTrigger>
                        <SelectContent>
                            {statusOptions.map((option) => (
                                <SelectItem key={option.value} value={option.value}>
                                    {option.label}
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                    <Select value={detectionFilter} onValueChange={setDetectionFilter}>
                        <SelectTrigger className="md:w-48">
                            <SelectValue placeholder="Type" />
                        </SelectTrigger>
                        <SelectContent>
                            {detectionOptions.map((option) => (
                                <SelectItem key={option.value} value={option.value}>
                                    {option.label}
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </div>
            </div>

            <Card>
                <CardHeader className="flex flex-row items-center justify-between">
                    <div>
                        <CardTitle>Approval queue</CardTitle>
                        <p className="text-sm text-[var(--muted)]">
                            {pendingItems.length} items · filtering by {statusFilter} / {detectionFilter}
                        </p>
                    </div>
                </CardHeader>
                <CardContent>
                    {isLoading ? (
                        <div className="py-12 flex items-center justify-center text-sm text-[var(--muted)]">
                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                            Loading pending updates...
                        </div>
                    ) : pendingItems.length === 0 ? (
                        <div className="py-12 text-center text-sm text-[var(--muted)]">
                            No items match the selected filters.
                        </div>
                    ) : (
                        <div className="space-y-3">
                            {pendingItems.map((item: PendingUpdate) => {
                                const detection = detectionBadge(item.detection_type)
                                return (
                                    <div
                                        key={item.id}
                                        className="p-4 rounded-xl border border-[var(--surface2)] bg-[var(--surface)] space-y-3"
                                    >
                                        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
                                            <div className="space-y-1">
                                                <div className="flex items-center gap-2">
                                                    <h3 className="font-medium">{item.title}</h3>
                                                    <Badge variant={detection.variant}>{detection.label}</Badge>
                                                    <Badge variant="softNeutral">Sim {item.similarity_score.toFixed(2)}</Badge>
                                                </div>
                                                <p className="text-sm text-[var(--muted)]">
                                                    Source: {item.source_url}
                                                </p>
                                            </div>
                                            <div className="flex items-center gap-2">
                                                <Button
                                                    variant="outline"
                                                    size="sm"
                                                    onClick={() => loadDetail(item.id)}
                                                >
                                                    <Eye className="w-4 h-4 mr-2" />
                                                    View
                                                </Button>
                                                <Button
                                                    variant="outline"
                                                    size="sm"
                                                    onClick={() => approveMutation.mutate(item.id)}
                                                    disabled={approveMutation.isPending}
                                                >
                                                    <CheckCircle className="w-4 h-4 mr-2 text-success" />
                                                    Approve
                                                </Button>
                                                <Button
                                                    variant="ghost"
                                                    size="sm"
                                                    onClick={() => rejectMutation.mutate(item.id)}
                                                    disabled={rejectMutation.isPending}
                                                >
                                                    <XCircle className="w-4 h-4 mr-2 text-error" />
                                                    Reject
                                                </Button>
                                            </div>
                                        </div>
                                        <p className="text-sm text-[var(--muted)] line-clamp-3">
                                            {item.content_preview}
                                        </p>
                                        <div className="flex flex-wrap gap-4 text-xs text-[var(--muted)]">
                                            <span>Category: {item.category}</span>
                                            <span>Created: {formatDistanceToNow(new Date(item.created_at), { addSuffix: true })}</span>
                                            <span>Status: {item.status}</span>
                                            {item.llm_analysis && <span>LLM reason: {item.llm_analysis}</span>}
                                        </div>
                                    </div>
                                )
                            })}
                        </div>
                    )}
                </CardContent>
            </Card>

            <Dialog open={detailOpen} onOpenChange={setDetailOpen}>
                <DialogContent className="max-w-3xl">
                    <DialogHeader>
                        <DialogTitle>{detail?.title || 'Pending update'}</DialogTitle>
                        <DialogDescription>
                            {detail ? `Source: ${detail.source_url}` : 'Loading details...'}
                        </DialogDescription>
                    </DialogHeader>
                    {detailLoading ? (
                        <div className="flex items-center justify-center py-12 text-sm text-[var(--muted)]">
                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                            Fetching details...
                        </div>
                    ) : detail ? (
                        <ScrollArea className="max-h-[60vh] pr-3">
                            <div className="space-y-4 text-sm">
                                <div>
                                    <p className="text-xs uppercase text-[var(--muted)] mb-1">Summary</p>
                                    <p>{detail.llm_summary || 'No summary provided'}</p>
                                </div>
                                {detail.llm_analysis && (
                                    <div>
                                        <p className="text-xs uppercase text-[var(--muted)] mb-1">LLM reasoning</p>
                                        <p className="whitespace-pre-wrap">{detail.llm_analysis}</p>
                                    </div>
                                )}
                                <div>
                                    <p className="text-xs uppercase text-[var(--muted)] mb-1">Full content</p>
                                    <div className="p-3 rounded-lg bg-[var(--surface2)] whitespace-pre-wrap text-sm">
                                        {detail.content}
                                    </div>
                                </div>
                                {detail.matched_doc_ids?.length > 0 && (
                                    <div>
                                        <p className="text-xs uppercase text-[var(--muted)] mb-1">Similar document IDs</p>
                                        <p>{detail.matched_doc_ids.join(', ')}</p>
                                    </div>
                                )}
                                {detail.metadata?.summary && (
                                    <div>
                                        <p className="text-xs uppercase text-[var(--muted)] mb-1">Metadata summary</p>
                                        <p>{detail.metadata.summary}</p>
                                    </div>
                                )}
                            </div>
                        </ScrollArea>
                    ) : (
                        <div className="text-sm text-[var(--muted)]">Select an update to view details.</div>
                    )}
                </DialogContent>
            </Dialog>
        </div>
    )
}

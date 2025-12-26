import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { formatDistanceToNow } from 'date-fns'
import { adminApi } from '../api/adminApi'
import { MonitorTarget } from '@/types/admin'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogDescription,
} from '@/components/ui/dialog'
import {
    Select,
    SelectTrigger,
    SelectValue,
    SelectContent,
    SelectItem,
} from '@/components/ui/select'
import { useToast } from '@/hooks/useToast'
import {
    Globe,
    PauseCircle,
    PlayCircle,
    Plus,
    Trash2,
    Loader2,
} from 'lucide-react'

type MonitorFormState = {
    name: string
    url: string
    collection: string
    category: string
    interval_hours: number
    selector: string
}

const defaultForm: MonitorFormState = {
    name: '',
    url: '',
    collection: 'default',
    category: 'general',
    interval_hours: 6,
    selector: '',
}

const categoryOptions = [
    { value: 'general', label: 'General' },
    { value: 'announcement', label: 'Announcement' },
    { value: 'academic', label: 'Academic' },
    { value: 'news', label: 'News' },
]

export default function MonitorTargetsPage() {
    const [dialogOpen, setDialogOpen] = useState(false)
    const [form, setForm] = useState<MonitorFormState>(defaultForm)
    const { toast } = useToast()
    const queryClient = useQueryClient()

    const { data, isLoading, isFetching } = useQuery({
        queryKey: ['monitorTargets'],
        queryFn: () => adminApi.getMonitorTargets({ skip: 0, limit: 100 }),
    })
    const targets = data?.items ?? []

    const createMutation = useMutation({
        mutationFn: (payload: MonitorFormState) =>
            adminApi.createMonitorTarget({
                ...payload,
                selector: payload.selector || undefined,
            }),
        onSuccess: () => {
            toast({ title: 'Monitor target created', variant: 'success' })
            setDialogOpen(false)
            setForm(defaultForm)
            queryClient.invalidateQueries({ queryKey: ['monitorTargets'] })
        },
        onError: (error: any) => {
            toast({
                title: 'Failed to create target',
                description: error.message,
                variant: 'destructive',
            })
        },
    })

    const toggleMutation = useMutation({
        mutationFn: (payload: { id: string; is_active: boolean }) =>
            adminApi.updateMonitorTarget(payload.id, { is_active: payload.is_active }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['monitorTargets'] })
        },
        onError: (error: any) => {
            toast({
                title: 'Failed to update target',
                description: error.message,
                variant: 'destructive',
            })
        },
    })

    const deleteMutation = useMutation({
        mutationFn: (id: string) => adminApi.deleteMonitorTarget(id),
        onSuccess: () => {
            toast({ title: 'Target removed', variant: 'success' })
            queryClient.invalidateQueries({ queryKey: ['monitorTargets'] })
        },
        onError: (error: any) => {
            toast({
                title: 'Failed to remove target',
                description: error.message,
                variant: 'destructive',
            })
        },
    })

    const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault()
        createMutation.mutate(form)
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-semibold tracking-tight">Monitor Targets</h2>
                    <p className="text-sm text-[var(--muted)] mt-1">
                        Configure portals or feeds to watch for new announcements automatically.
                    </p>
                </div>
                <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
                    <Button onClick={() => setDialogOpen(true)}>
                        <Plus className="w-4 h-4 mr-2" />
                        Add Target
                    </Button>
                    <DialogContent>
                        <DialogHeader>
                            <DialogTitle>Add Monitor Target</DialogTitle>
                            <DialogDescription>
                                Provide the public URL you want Ami to check every few hours.
                            </DialogDescription>
                        </DialogHeader>
                        <form className="space-y-4" onSubmit={handleSubmit}>
                            <div className="grid gap-3">
                                <div className="space-y-2">
                                    <Label htmlFor="name">Display name</Label>
                                    <Input
                                        id="name"
                                        value={form.name}
                                        onChange={(e) => setForm((prev) => ({ ...prev, name: e.target.value }))}
                                        placeholder="PTIT Portal"
                                        required
                                    />
                                </div>
                                <div className="space-y-2">
                                    <Label htmlFor="url">URL</Label>
                                    <Input
                                        id="url"
                                        type="url"
                                        value={form.url}
                                        onChange={(e) => setForm((prev) => ({ ...prev, url: e.target.value }))}
                                        placeholder="https://portal.ptit.edu.vn/latest"
                                        required
                                    />
                                </div>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                    <div className="space-y-2">
                                        <Label>Category</Label>
                                        <Select
                                            value={form.category}
                                            onValueChange={(value) => setForm((prev) => ({ ...prev, category: value }))}
                                        >
                                            <SelectTrigger>
                                                <SelectValue placeholder="Select category" />
                                            </SelectTrigger>
                                            <SelectContent>
                                                {categoryOptions.map((option) => (
                                                    <SelectItem key={option.value} value={option.value}>
                                                        {option.label}
                                                    </SelectItem>
                                                ))}
                                            </SelectContent>
                                        </Select>
                                    </div>
                                    <div className="space-y-2">
                                        <Label htmlFor="collection">Collection</Label>
                                        <Input
                                            id="collection"
                                            value={form.collection}
                                            onChange={(e) =>
                                                setForm((prev) => ({ ...prev, collection: e.target.value }))
                                            }
                                        />
                                    </div>
                                </div>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                    <div className="space-y-2">
                                        <Label htmlFor="interval">Interval (hours)</Label>
                                        <Input
                                            id="interval"
                                            type="number"
                                            min={1}
                                            max={168}
                                            value={form.interval_hours}
                                            onChange={(e) =>
                                                setForm((prev) => ({
                                                    ...prev,
                                                    interval_hours: Number(e.target.value),
                                                }))
                                            }
                                        />
                                    </div>
                                    <div className="space-y-2">
                                        <Label htmlFor="selector">Content selector (optional)</Label>
                                        <Input
                                            id="selector"
                                            value={form.selector}
                                            onChange={(e) =>
                                                setForm((prev) => ({ ...prev, selector: e.target.value }))
                                            }
                                            placeholder=".article-content"
                                        />
                                    </div>
                                </div>
                            </div>
                            <Button type="submit" className="w-full" disabled={createMutation.isPending}>
                                {createMutation.isPending ? (
                                    <>
                                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                        Creating...
                                    </>
                                ) : (
                                    'Create target'
                                )}
                            </Button>
                        </form>
                    </DialogContent>
                </Dialog>
            </div>

            <Card>
                <CardHeader className="flex flex-row items-center justify-between">
                    <div>
                        <CardTitle>Active monitors</CardTitle>
                        <p className="text-sm text-[var(--muted)]">
                            {isFetching ? 'Refreshing...' : `${targets.length} configured targets`}
                        </p>
                    </div>
                </CardHeader>
                <CardContent>
                    {isLoading ? (
                        <div className="py-10 text-center text-sm text-[var(--muted)]">Loading monitor targets...</div>
                    ) : targets.length === 0 ? (
                        <div className="py-10 text-center text-sm text-[var(--muted)]">
                            No monitor targets yet. Add one to start watching a portal.
                        </div>
                    ) : (
                        <div className="space-y-3">
                            {targets.map((target: MonitorTarget) => (
                                <div
                                    key={target.id}
                                    className="flex flex-col md:flex-row md:items-center gap-4 p-4 rounded-xl border border-[var(--surface2)] bg-[var(--surface)]"
                                >
                                    <div className="flex-1 space-y-2">
                                        <div className="flex items-center gap-3">
                                            <div className="p-2 rounded-lg bg-[var(--surface2)]">
                                                <Globe className="w-5 h-5 text-neutral-500" />
                                            </div>
                                            <div>
                                                <div className="flex items-center gap-2">
                                                    <p className="font-medium">{target.name}</p>
                                                    <Badge variant={target.is_active ? 'softSuccess' : 'softNeutral'}>
                                                        {target.is_active ? 'Active' : 'Paused'}
                                                    </Badge>
                                                </div>
                                                <p className="text-sm text-[var(--muted)] break-all">{target.url}</p>
                                            </div>
                                        </div>
                                        <div className="flex flex-wrap gap-4 text-xs text-[var(--muted)] pl-14 md:pl-11">
                                            <span>Collection: {target.collection}</span>
                                            <span>Category: {target.category}</span>
                                            <span>
                                                Interval: {target.interval_hours}h &middot; Last check:{' '}
                                                {target.last_checked_at
                                                    ? formatDistanceToNow(new Date(target.last_checked_at), {
                                                        addSuffix: true,
                                                    })
                                                    : 'never'}
                                            </span>
                                            {target.last_error && (
                                                <span className="text-error">Last error: {target.last_error}</span>
                                            )}
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <Button
                                            variant="outline"
                                            size="sm"
                                            onClick={() =>
                                                toggleMutation.mutate({
                                                    id: target.id,
                                                    is_active: !target.is_active,
                                                })
                                            }
                                            disabled={toggleMutation.isPending}
                                        >
                                            {target.is_active ? (
                                                <>
                                                    <PauseCircle className="w-4 h-4 mr-2" />
                                                    Pause
                                                </>
                                            ) : (
                                                <>
                                                    <PlayCircle className="w-4 h-4 mr-2" />
                                                    Resume
                                                </>
                                            )}
                                        </Button>
                                        <Button
                                            variant="ghost"
                                            size="icon"
                                            onClick={() => deleteMutation.mutate(target.id)}
                                            disabled={deleteMutation.isPending}
                                        >
                                            <Trash2 className="w-4 h-4 text-error" />
                                        </Button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    )
}

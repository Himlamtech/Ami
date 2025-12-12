import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Layers, RefreshCw, Trash2 } from "lucide-react"

export default function VectorStorePage() {
    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-semibold tracking-tight">Vector Store</h2>
                    <p className="text-sm text-[var(--muted)] mt-1">Monitor and manage vector embeddings.</p>
                </div>
                <div className="flex gap-2">
                    <Button variant="outline">
                        <RefreshCw className="w-4 h-4 mr-2" />
                        Reindex
                    </Button>
                    <Button variant="destructive">
                        <Trash2 className="w-4 h-4 mr-2" />
                        Clear All
                    </Button>
                </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Total Vectors</CardTitle>
                        <Layers className="h-4 w-4 text-neutral-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-semibold">12,345</div>
                        <p className="text-xs text-[var(--muted)]">Across 5 collections</p>
                    </CardContent>
                </Card>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>Collections</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="text-sm text-neutral-500 text-center py-8">
                        Vector collections details will appear here.
                    </div>
                </CardContent>
            </Card>
        </div>
    )
}

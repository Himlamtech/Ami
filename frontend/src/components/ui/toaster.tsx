import { useToast } from '@/hooks/useToast'
import { X } from 'lucide-react'
import { cn } from '@/lib/utils'

export function Toaster() {
    const { toasts, dismiss } = useToast()

    return (
        <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2">
            {toasts.map((toast) => (
                <div
                    key={toast.id}
                    className={cn(
                        'flex items-center gap-3 rounded-lg border bg-white px-4 py-3 shadow-lg animate-in slide-in-from-right-full',
                        toast.variant === 'destructive' && 'border-error bg-error/10 text-error',
                        toast.variant === 'success' && 'border-success bg-success/10 text-success'
                    )}
                >
                    <div className="flex-1">
                        {toast.title && <p className="font-medium">{toast.title}</p>}
                        {toast.description && <p className="text-sm opacity-90">{toast.description}</p>}
                    </div>
                    <button
                        onClick={() => dismiss(toast.id)}
                        className="rounded-md p-1 hover:bg-neutral-100"
                    >
                        <X className="h-4 w-4" />
                    </button>
                </div>
            ))}
        </div>
    )
}

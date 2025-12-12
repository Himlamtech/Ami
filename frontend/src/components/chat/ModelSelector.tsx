import { ChevronDown, Zap, Brain, Sparkles } from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { cn } from '@/lib/utils'

export type ThinkingMode = 'fast' | 'balance' | 'thinking'

interface ModelOption {
    value: ThinkingMode
    label: string
    description: string
    icon: typeof Zap
}

const models: ModelOption[] = [
    {
        value: 'fast',
        label: 'Nhanh',
        description: 'Phản hồi nhanh nhất',
        icon: Zap,
    },
    {
        value: 'balance',
        label: 'Cân bằng',
        description: 'Cân bằng tốc độ & chất lượng',
        icon: Sparkles,
    },
    {
        value: 'thinking',
        label: 'Suy luận',
        description: 'Câu hỏi phức tạp, chính xác nhất',
        icon: Brain,
    },
]

interface ModelSelectorProps {
    value: ThinkingMode
    onChange: (value: ThinkingMode) => void
    className?: string
}

export default function ModelSelector({ value, onChange, className }: ModelSelectorProps) {
    const selected = models.find((m) => m.value === value) || models[1]
    const Icon = selected.icon

    return (
        <DropdownMenu>
            <DropdownMenuTrigger asChild>
                <Button
                    variant="ghost"
                    size="sm"
                    className={cn(
                        'gap-1.5 text-xs font-normal text-neutral-600 hover:text-neutral-900',
                        className
                    )}
                >
                    <Icon className="w-3.5 h-3.5" />
                    <span className="hidden sm:inline">{selected.label}</span>
                    <ChevronDown className="w-3 h-3 opacity-50" />
                </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="start" className="w-56">
                {models.map((model) => {
                    const ModelIcon = model.icon
                    return (
                        <DropdownMenuItem
                            key={model.value}
                            onClick={() => onChange(model.value)}
                            className={cn(
                                'flex items-start gap-3 p-3 cursor-pointer',
                                value === model.value && 'bg-primary/5'
                            )}
                        >
                            <ModelIcon className={cn(
                                'w-4 h-4 mt-0.5',
                                value === model.value ? 'text-primary' : 'text-neutral-500'
                            )} />
                            <div className="flex-1">
                                <div className={cn(
                                    'font-medium text-sm',
                                    value === model.value && 'text-primary'
                                )}>
                                    {model.label}
                                </div>
                                <div className="text-xs text-neutral-500">
                                    {model.description}
                                </div>
                            </div>
                            {value === model.value && (
                                <div className="w-2 h-2 rounded-full bg-primary" />
                            )}
                        </DropdownMenuItem>
                    )
                })}
            </DropdownMenuContent>
        </DropdownMenu>
    )
}

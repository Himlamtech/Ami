import { Button } from '@/components/ui/button'
import { Sparkles } from 'lucide-react'
import type { SuggestedQuestion } from '@/types/chat'

interface SuggestionChipsProps {
    suggestions: SuggestedQuestion[]
    onSelect: (question: string) => void
}

export default function SuggestionChips({ suggestions, onSelect }: SuggestionChipsProps) {
    if (suggestions.length === 0) return null

    return (
        <div className="flex flex-wrap gap-2 mt-3">
            <span className="text-xs text-neutral-500 flex items-center mr-1 gap-1">
                <Sparkles className="w-3.5 h-3.5 text-neutral-400" />
                Gợi ý
            </span>
            {suggestions.map((suggestion) => {
                const meta = [suggestion.category, suggestion.source].filter(Boolean).join(' · ')
                return (
                    <div key={suggestion.id} className="flex flex-col items-start gap-1">
                        <Button
                            variant="ghost"
                            size="sm"
                            className="text-xs h-8 px-3 rounded-full bg-[var(--surface2)] text-neutral-700 hover:text-neutral-900 hover:bg-[var(--surface2)] shadow-sm hover:shadow-md transition-all"
                            onClick={() => onSelect(suggestion.text)}
                        >
                            {suggestion.text}
                        </Button>
                        {meta && (
                            <span className="text-[10px] text-neutral-400">
                                {meta}
                            </span>
                        )}
                    </div>
                )
            })}
        </div>
    )
}

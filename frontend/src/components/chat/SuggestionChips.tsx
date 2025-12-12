import { Button } from '@/components/ui/button'
import type { SuggestedQuestion } from '@/types/chat'

interface SuggestionChipsProps {
    suggestions: SuggestedQuestion[]
    onSelect: (question: string) => void
}

export default function SuggestionChips({ suggestions, onSelect }: SuggestionChipsProps) {
    if (suggestions.length === 0) return null

    return (
        <div className="flex flex-wrap gap-2 mt-3">
            <span className="text-xs text-neutral-500 flex items-center mr-1">💡 Gợi ý:</span>
            {suggestions.map((suggestion) => (
                <Button
                    key={suggestion.id}
                    variant="outline"
                    size="sm"
                    className="text-xs h-7 px-3 rounded-full border-neutral-200 hover:border-primary hover:text-primary"
                    onClick={() => onSelect(suggestion.text)}
                >
                    {suggestion.text}
                </Button>
            ))}
        </div>
    )
}

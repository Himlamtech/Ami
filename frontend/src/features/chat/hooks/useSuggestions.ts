import { useQuery } from '@tanstack/react-query'
import { chatApi } from '../api/chatApi'
import type { SuggestedQuestion } from '@/types/chat'

export function useSuggestions() {
    const { data: suggestions = [], isLoading } = useQuery<SuggestedQuestion[]>({
        queryKey: ['suggestions'],
        queryFn: () => chatApi.getSuggestions(),
        staleTime: 1000 * 60 * 5, // 5 minutes
    })

    return { suggestions, isLoading }
}

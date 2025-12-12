import { useQuery, useMutation, useQueryClient, QueryKey } from '@tanstack/react-query'
import { api } from '@/lib/api'

interface UseApiOptions<T> {
    queryKey: QueryKey
    endpoint: string
    params?: Record<string, string | number | boolean | undefined>
    enabled?: boolean
    staleTime?: number
    onSuccess?: (data: T) => void
    onError?: (error: Error) => void
}

export function useApiQuery<T>({
    queryKey,
    endpoint,
    params,
    enabled = true,
    staleTime,
}: UseApiOptions<T>) {
    return useQuery({
        queryKey,
        queryFn: () => api.get<T>(endpoint, params),
        enabled,
        staleTime,
    })
}

interface UseMutationOptions<TData> {
    endpoint: string
    method?: 'POST' | 'PUT' | 'DELETE'
    invalidateKeys?: QueryKey[]
    onSuccess?: (data: TData) => void
    onError?: (error: Error) => void
}

export function useApiMutation<TData, TVariables = unknown>({
    endpoint,
    method = 'POST',
    invalidateKeys,
    onSuccess,
    onError,
}: UseMutationOptions<TData>) {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: async (variables: TVariables) => {
            switch (method) {
                case 'POST':
                    return api.post<TData>(endpoint, variables)
                case 'PUT':
                    return api.put<TData>(endpoint, variables)
                case 'DELETE':
                    return api.delete<TData>(endpoint)
                default:
                    throw new Error(`Unsupported method: ${method}`)
            }
        },
        onSuccess: (data) => {
            if (invalidateKeys) {
                invalidateKeys.forEach((key: QueryKey) => {
                    queryClient.invalidateQueries({ queryKey: key })
                })
            }
            onSuccess?.(data)
        },
        onError,
    })
}

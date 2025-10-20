import { create } from 'zustand'

interface DataStats {
    total_documents: number
    total_chunks: number
    collections: string[]
    vector_store: string
}

interface UploadProgress {
    filename: string
    progress: number
    status: 'uploading' | 'processing' | 'complete' | 'error'
    error?: string
}

interface DataState {
    stats: DataStats | null
    collections: string[]
    selectedCollection: string
    uploadProgress: UploadProgress[]
    loading: boolean
    error: string | null

    setStats: (stats: DataStats) => void
    setCollections: (collections: string[]) => void
    setSelectedCollection: (collection: string) => void
    addUploadProgress: (progress: UploadProgress) => void
    updateUploadProgress: (filename: string, updates: Partial<UploadProgress>) => void
    removeUploadProgress: (filename: string) => void
    setLoading: (loading: boolean) => void
    setError: (error: string | null) => void
    clearState: () => void
}

export const useDataStore = create<DataState>((set) => ({
    stats: null,
    collections: [],
    selectedCollection: 'default',
    uploadProgress: [],
    loading: false,
    error: null,

    setStats: (stats) => set({ stats }),
    setCollections: (collections) => set({ collections }),
    setSelectedCollection: (collection) => set({ selectedCollection: collection }),
    addUploadProgress: (progress) =>
        set((state) => ({
            uploadProgress: [...state.uploadProgress, progress],
        })),
    updateUploadProgress: (filename, updates) =>
        set((state) => ({
            uploadProgress: state.uploadProgress.map((p) =>
                p.filename === filename ? { ...p, ...updates } : p
            ),
        })),
    removeUploadProgress: (filename) =>
        set((state) => ({
            uploadProgress: state.uploadProgress.filter((p) => p.filename !== filename),
        })),
    setLoading: (loading) => set({ loading }),
    setError: (error) => set({ error }),
    clearState: () =>
        set({
            stats: null,
            collections: [],
            selectedCollection: 'default',
            uploadProgress: [],
            loading: false,
            error: null,
        }),
}))


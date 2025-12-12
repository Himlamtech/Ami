
import { api } from '@/lib/api'

export interface UserProfile {
    id: string
    user_id: string
    student_id: string
    name: string
    email: string
    level: string
    major: string
    class_name?: string
    preferred_detail_level?: string
    top_interests: string[]
    total_questions: number
}

export interface UpdateProfileRequest {
    name?: string
    student_id?: string
    major?: string
    level?: string
    class_name?: string
}

export const profileApi = {
    get: (userId: string) => api.get<UserProfile>(`/profile/${userId}`),
    
    update: (userId: string, data: UpdateProfileRequest) => 
        api.put<UserProfile>(`/profile/${userId}`, data),
        
    setPreferences: (userId: string, data: { detail_level?: string, language?: string }) =>
        api.put<UserProfile>(`/profile/${userId}/preferences`, data)
}

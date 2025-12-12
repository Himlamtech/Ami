// API endpoints
export const API_BASE = '/api/v1'

// App info
export const APP_NAME = 'AMI'
export const APP_DESCRIPTION = 'Trợ lý thông minh Học viện PTIT'

// Pagination
export const DEFAULT_PAGE_SIZE = 20

// Chat
export const MAX_MESSAGE_LENGTH = 4000
export const MAX_ATTACHMENTS = 5
export const ALLOWED_FILE_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf']
export const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB

// Feedback categories
export const FEEDBACK_CATEGORIES = [
    { value: 'incorrect', label: 'Thông tin không chính xác' },
    { value: 'outdated', label: 'Thông tin đã cũ' },
    { value: 'incomplete', label: 'Thiếu thông tin' },
    { value: 'unclear', label: 'Không rõ ràng' },
    { value: 'other', label: 'Khác' },
]

// Knowledge gap priorities
export const GAP_PRIORITIES = {
    high: { label: 'Cao', color: 'error' },
    medium: { label: 'Trung bình', color: 'warning' },
    low: { label: 'Thấp', color: 'success' },
}

// Status colors
export const STATUS_COLORS = {
    active: 'success',
    issues: 'warning',
    multiple_issues: 'error',
    archived: 'neutral',
}

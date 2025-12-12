import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs))
}

export function formatDate(date: Date | string): string {
    const d = new Date(date)
    const now = new Date()
    const diff = now.getTime() - d.getTime()

    const minutes = Math.floor(diff / 60000)
    const hours = Math.floor(diff / 3600000)
    const days = Math.floor(diff / 86400000)

    if (minutes < 1) return 'Vừa xong'
    if (minutes < 60) return `${minutes} phút trước`
    if (hours < 24) return `${hours} giờ trước`
    if (days < 7) return `${days} ngày trước`

    return d.toLocaleDateString('vi-VN')
}

export function formatTime(date?: Date | string): string {
    if (!date) return ''
    const value = new Date(date)
    if (Number.isNaN(value.getTime())) {
        return ''
    }
    return value.toLocaleTimeString('vi-VN', {
        hour: '2-digit',
        minute: '2-digit',
    })
}

export function formatCurrency(amount: number): string {
    return new Intl.NumberFormat('vi-VN', {
        style: 'currency',
        currency: 'VND',
    }).format(amount)
}

export function formatNumber(num: number): string {
    return new Intl.NumberFormat('vi-VN').format(num)
}

export function truncate(str: string, length: number): string {
    if (str.length <= length) return str
    return str.slice(0, length) + '...'
}

export function generateId(): string {
    return Math.random().toString(36).substring(2, 15)
}

import { useState } from 'react'
import { Search, Bookmark, Trash2, ExternalLink, Clock, Tag } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { formatDate } from '@/lib/utils'

interface BookmarkedItem {
    id: string
    question: string
    answer: string
    tags: string[]
    savedAt: string
    sessionId: string
}

// Mock data
const mockBookmarks: BookmarkedItem[] = [
    {
        id: '1',
        question: 'Học phí kỳ 1 năm 2024 là bao nhiêu?',
        answer: 'Học phí kỳ 1 năm học 2024-2025 cho sinh viên ngành CNTT là 15,500,000 VNĐ (hệ đại trà) và 25,000,000 VNĐ (hệ chất lượng cao).',
        tags: ['học phí', 'tài chính'],
        savedAt: new Date(Date.now() - 86400000).toISOString(),
        sessionId: 'sess_1',
    },
    {
        id: '2',
        question: 'Cách đăng ký môn học online?',
        answer: 'Để đăng ký môn học online, bạn truy cập portal.ptit.edu.vn, đăng nhập bằng tài khoản sinh viên, chọn "Đăng ký học" và làm theo hướng dẫn.',
        tags: ['đăng ký môn', 'portal'],
        savedAt: new Date(Date.now() - 172800000).toISOString(),
        sessionId: 'sess_2',
    },
    {
        id: '3',
        question: 'Điều kiện được học bổng KKHT?',
        answer: 'Học bổng khuyến khích học tập dành cho sinh viên có điểm trung bình tích lũy từ 3.2 trở lên và không có môn dưới 5.0.',
        tags: ['học bổng', 'tài chính'],
        savedAt: new Date(Date.now() - 604800000).toISOString(),
        sessionId: 'sess_3',
    },
]

export default function SavedPage() {
    const [bookmarks, setBookmarks] = useState(mockBookmarks)
    const [searchQuery, setSearchQuery] = useState('')
    const [selectedTag, setSelectedTag] = useState<string | null>(null)

    // Get all unique tags
    const allTags = Array.from(new Set(bookmarks.flatMap((b) => b.tags)))

    // Filter bookmarks
    const filteredBookmarks = bookmarks.filter((bookmark) => {
        const matchesSearch = searchQuery
            ? bookmark.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
            bookmark.answer.toLowerCase().includes(searchQuery.toLowerCase())
            : true
        const matchesTag = selectedTag ? bookmark.tags.includes(selectedTag) : true
        return matchesSearch && matchesTag
    })

    const handleDelete = (id: string) => {
        setBookmarks(bookmarks.filter((b) => b.id !== id))
    }

    return (
        <div className="flex-1 overflow-y-auto p-4 lg:p-6">
            <div className="max-w-3xl mx-auto space-y-6">
                {/* Header */}
                <div>
                    <h1 className="text-2xl font-bold text-neutral-900">Đã lưu</h1>
                    <p className="text-neutral-500">Các câu hỏi và câu trả lời bạn đã đánh dấu</p>
                </div>

                {/* Search and Filter */}
                <div className="flex flex-col sm:flex-row gap-4">
                    <div className="relative flex-1">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
                        <Input
                            placeholder="Tìm kiếm trong đã lưu..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="pl-9"
                        />
                    </div>
                </div>

                {/* Tags */}
                <div className="flex flex-wrap gap-2">
                    <Badge
                        variant={selectedTag === null ? 'default' : 'outline'}
                        className="cursor-pointer"
                        onClick={() => setSelectedTag(null)}
                    >
                        Tất cả ({bookmarks.length})
                    </Badge>
                    {allTags.map((tag) => (
                        <Badge
                            key={tag}
                            variant={selectedTag === tag ? 'default' : 'outline'}
                            className="cursor-pointer"
                            onClick={() => setSelectedTag(tag === selectedTag ? null : tag)}
                        >
                            <Tag className="w-3 h-3 mr-1" />
                            {tag}
                        </Badge>
                    ))}
                </div>

                {/* Bookmarks List */}
                <div className="space-y-4">
                    {filteredBookmarks.length === 0 ? (
                        <Card>
                            <CardContent className="p-12 text-center">
                                <Bookmark className="w-12 h-12 mx-auto text-neutral-300 mb-4" />
                                <p className="text-neutral-500">
                                    {searchQuery || selectedTag
                                        ? 'Không tìm thấy kết quả'
                                        : 'Chưa có nội dung đã lưu'}
                                </p>
                            </CardContent>
                        </Card>
                    ) : (
                        filteredBookmarks.map((bookmark) => (
                            <Card key={bookmark.id} className="hover:shadow-md transition-shadow">
                                <CardContent className="p-4">
                                    <div className="flex items-start gap-4">
                                        <div className="flex-1 space-y-2">
                                            <h3 className="font-medium text-neutral-900">
                                                {bookmark.question}
                                            </h3>
                                            <p className="text-sm text-neutral-600 line-clamp-2">
                                                {bookmark.answer}
                                            </p>
                                            <div className="flex items-center gap-2 flex-wrap">
                                                {bookmark.tags.map((tag) => (
                                                    <Badge key={tag} variant="secondary" className="text-xs">
                                                        {tag}
                                                    </Badge>
                                                ))}
                                                <span className="text-xs text-neutral-400 flex items-center gap-1">
                                                    <Clock className="w-3 h-3" />
                                                    {formatDate(bookmark.savedAt)}
                                                </span>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-1">
                                            <Button variant="ghost" size="sm" asChild>
                                                <a href={`/chat/${bookmark.sessionId}`}>
                                                    <ExternalLink className="w-4 h-4" />
                                                </a>
                                            </Button>
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                onClick={() => handleDelete(bookmark.id)}
                                                className="text-error hover:text-error hover:bg-error/10"
                                            >
                                                <Trash2 className="w-4 h-4" />
                                            </Button>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        ))
                    )}
                </div>
            </div>
        </div>
    )
}

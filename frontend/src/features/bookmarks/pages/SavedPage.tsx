import { useState, useEffect } from 'react'
import { Search, Bookmark as BookmarkIcon, Trash2, ExternalLink, Clock, Tag } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { formatDate } from '@/lib/utils'


import { bookmarksApi, Bookmark } from '../api/bookmarksApi'

export default function SavedPage() {
    const [bookmarks, setBookmarks] = useState<Bookmark[]>([])

    // Fetch bookmarks on mount
    useEffect(() => {
        bookmarksApi.getAll().then(res => setBookmarks(res.bookmarks || []))
    }, [])
    const [searchQuery, setSearchQuery] = useState('')
    const [selectedTag, setSelectedTag] = useState<string | null>(null)

    // Get all unique tags
    const allTags = Array.from(new Set(bookmarks.flatMap((b) => b.tags)))

    // Filter bookmarks
    const filteredBookmarks = bookmarks.filter((bookmark) => {
        const matchesSearch = searchQuery
            ? bookmark.query.toLowerCase().includes(searchQuery.toLowerCase()) ||
            bookmark.response.toLowerCase().includes(searchQuery.toLowerCase())
            : true
        const matchesTag = selectedTag ? bookmark.tags.includes(selectedTag) : true
        return matchesSearch && matchesTag
    })

    const handleDelete = async (id: string) => {
        await bookmarksApi.delete(id)
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
                                <BookmarkIcon className="w-12 h-12 mx-auto text-neutral-300 mb-4" />
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
                                                {bookmark.query}
                                            </h3>
                                            <p className="text-sm text-neutral-600 line-clamp-2">
                                                {bookmark.response}
                                            </p>
                                            <div className="flex items-center gap-2 flex-wrap">
                                                {bookmark.tags.map((tag) => (
                                                    <Badge key={tag} variant="secondary" className="text-xs">
                                                        {tag}
                                                    </Badge>
                                                ))}
                                                <span className="text-xs text-neutral-400 flex items-center gap-1">
                                                    <Clock className="w-3 h-3" />
                                                    {formatDate(bookmark.created_at)}
                                                </span>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-1">
                                            <Button variant="ghost" size="sm" asChild>
                                                <a href={`/chat/${bookmark.session_id}`}>
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

import { useState } from 'react'
import { Search, FileText, Download, ExternalLink, FolderOpen, Calendar, HelpCircle } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { formatDate } from '@/lib/utils'

interface Document {
    id: string
    title: string
    category: string
    description: string
    url?: string
    updatedAt: string
    type: 'pdf' | 'doc' | 'link' | 'form'
}

// Mock data - Popular documents
const mockDocuments: Document[] = [
    {
        id: '1',
        title: 'Thông báo học phí năm học 2024-2025',
        category: 'Tài chính',
        description: 'Chi tiết học phí các ngành, hệ đào tạo và hướng dẫn đóng học phí online.',
        url: '/docs/hoc-phi-2024.pdf',
        updatedAt: new Date(Date.now() - 604800000).toISOString(),
        type: 'pdf',
    },
    {
        id: '2',
        title: 'Hướng dẫn đăng ký môn học trên Portal',
        category: 'Đào tạo',
        description: 'Các bước đăng ký môn học, hủy môn, đổi lớp trên hệ thống Portal sinh viên.',
        url: '/docs/dang-ky-mon-hoc.pdf',
        updatedAt: new Date(Date.now() - 1209600000).toISOString(),
        type: 'pdf',
    },
    {
        id: '3',
        title: 'Quy định về học bổng và hỗ trợ tài chính',
        category: 'Học bổng',
        description: 'Điều kiện, mức học bổng KKHT, học bổng tài trợ và các chương trình hỗ trợ.',
        url: '/docs/hoc-bong.pdf',
        updatedAt: new Date(Date.now() - 2592000000).toISOString(),
        type: 'pdf',
    },
    {
        id: '4',
        title: 'Mẫu đơn xin nghỉ học có thời hạn',
        category: 'Biểu mẫu',
        description: 'Mẫu đơn và hướng dẫn thủ tục xin nghỉ học tạm thời, bảo lưu kết quả.',
        url: '/docs/mau-don-nghi-hoc.doc',
        updatedAt: new Date(Date.now() - 5184000000).toISOString(),
        type: 'form',
    },
    {
        id: '5',
        title: 'Lịch học kỳ 1 năm 2024-2025',
        category: 'Lịch học',
        description: 'Lịch học, lịch thi, các ngày nghỉ lễ trong học kỳ 1 năm học 2024-2025.',
        url: '/docs/lich-hoc-ky-1.pdf',
        updatedAt: new Date(Date.now() - 1209600000).toISOString(),
        type: 'pdf',
    },
]

const categories = ['Tất cả', 'Tài chính', 'Đào tạo', 'Học bổng', 'Biểu mẫu', 'Lịch học']

const faqs = [
    { question: 'Làm sao để xin miễn giảm học phí?', answer: 'Liên hệ phòng Công tác sinh viên...' },
    { question: 'Thời gian đăng ký môn học kỳ 2?', answer: 'Thường bắt đầu từ tuần cuối của kỳ 1...' },
    { question: 'Cách kiểm tra lịch thi?', answer: 'Truy cập Portal → Lịch thi...' },
]

export default function DocsPage() {
    const [searchQuery, setSearchQuery] = useState('')
    const [selectedCategory, setSelectedCategory] = useState('Tất cả')

    const filteredDocs = mockDocuments.filter((doc) => {
        const matchesSearch = searchQuery
            ? doc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
            doc.description.toLowerCase().includes(searchQuery.toLowerCase())
            : true
        const matchesCategory = selectedCategory === 'Tất cả' || doc.category === selectedCategory
        return matchesSearch && matchesCategory
    })

    const getTypeIcon = (type: Document['type']) => {
        switch (type) {
            case 'pdf':
                return '📄'
            case 'doc':
                return '📝'
            case 'form':
                return '📋'
            case 'link':
                return '🔗'
            default:
                return '📁'
        }
    }

    return (
        <div className="flex-1 overflow-y-auto p-4 lg:p-6">
            <div className="max-w-3xl mx-auto space-y-6">
                {/* Header */}
                <div>
                    <h1 className="text-2xl font-bold text-neutral-900">Tài liệu</h1>
                    <p className="text-neutral-500">Tài liệu và biểu mẫu sinh viên PTIT</p>
                </div>

                {/* Search */}
                <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
                    <Input
                        placeholder="Tìm kiếm tài liệu..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="pl-9"
                    />
                </div>

                {/* Categories */}
                <div className="flex flex-wrap gap-2">
                    {categories.map((category) => (
                        <Badge
                            key={category}
                            variant={selectedCategory === category ? 'default' : 'outline'}
                            className="cursor-pointer"
                            onClick={() => setSelectedCategory(category)}
                        >
                            {category}
                        </Badge>
                    ))}
                </div>

                {/* Documents List */}
                <div className="space-y-4">
                    <h2 className="text-lg font-semibold flex items-center gap-2">
                        <FolderOpen className="w-5 h-5" />
                        Tài liệu phổ biến
                    </h2>

                    {filteredDocs.length === 0 ? (
                        <Card>
                            <CardContent className="p-12 text-center">
                                <FileText className="w-12 h-12 mx-auto text-neutral-300 mb-4" />
                                <p className="text-neutral-500">Không tìm thấy tài liệu</p>
                            </CardContent>
                        </Card>
                    ) : (
                        filteredDocs.map((doc) => (
                            <Card key={doc.id} className="hover:shadow-md transition-shadow">
                                <CardContent className="p-4">
                                    <div className="flex items-start gap-4">
                                        <div className="text-2xl">{getTypeIcon(doc.type)}</div>
                                        <div className="flex-1 min-w-0">
                                            <h3 className="font-medium text-neutral-900 truncate">
                                                {doc.title}
                                            </h3>
                                            <p className="text-sm text-neutral-600 line-clamp-2 mt-1">
                                                {doc.description}
                                            </p>
                                            <div className="flex items-center gap-3 mt-2">
                                                <Badge variant="secondary" className="text-xs">
                                                    {doc.category}
                                                </Badge>
                                                <span className="text-xs text-neutral-400 flex items-center gap-1">
                                                    <Calendar className="w-3 h-3" />
                                                    {formatDate(doc.updatedAt)}
                                                </span>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-1">
                                            <Button variant="ghost" size="sm">
                                                <ExternalLink className="w-4 h-4" />
                                            </Button>
                                            <Button variant="ghost" size="sm">
                                                <Download className="w-4 h-4" />
                                            </Button>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        ))
                    )}
                </div>

                {/* FAQ Section */}
                <div className="space-y-4 pt-4">
                    <h2 className="text-lg font-semibold flex items-center gap-2">
                        <HelpCircle className="w-5 h-5" />
                        Câu hỏi thường gặp
                    </h2>
                    <div className="space-y-2">
                        {faqs.map((faq, index) => (
                            <Card key={index}>
                                <CardContent className="p-4">
                                    <button className="w-full text-left">
                                        <h4 className="font-medium text-neutral-900">{faq.question}</h4>
                                    </button>
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    )
}

import { Bot, GraduationCap, FileText, Calendar, CreditCard, Sparkles } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface WelcomeScreenProps {
    onQuestionSelect: (question: string) => void
}

const quickQuestions = [
    {
        icon: CreditCard,
        title: 'Học phí',
        question: 'Học phí kỳ này là bao nhiêu?',
        color: 'text-blue-500',
        bg: 'bg-blue-50 hover:bg-blue-100',
    },
    {
        icon: Calendar,
        title: 'Đăng ký môn',
        question: 'Làm sao để đăng ký môn học?',
        color: 'text-green-500',
        bg: 'bg-green-50 hover:bg-green-100',
    },
    {
        icon: FileText,
        title: 'Mẫu đơn',
        question: 'Cho tôi mẫu đơn xin nghỉ học',
        color: 'text-orange-500',
        bg: 'bg-orange-50 hover:bg-orange-100',
    },
    {
        icon: GraduationCap,
        title: 'Học bổng',
        question: 'Điều kiện để được học bổng KKHT?',
        color: 'text-purple-500',
        bg: 'bg-purple-50 hover:bg-purple-100',
    },
]

export default function WelcomeScreen({ onQuestionSelect }: WelcomeScreenProps) {
    return (
        <div className="flex flex-col items-center justify-center h-full px-4 py-8">
            {/* Logo and greeting */}
            <div className="flex flex-col items-center mb-10">
                <div className="relative mb-6">
                    <div className="w-24 h-24 rounded-3xl bg-gradient-to-br from-primary via-primary to-primary-600 flex items-center justify-center shadow-2xl shadow-primary/30">
                        <Bot className="w-12 h-12 text-white" />
                    </div>
                    <div className="absolute -top-1 -right-1 w-8 h-8 rounded-full bg-white shadow-lg flex items-center justify-center">
                        <Sparkles className="w-4 h-4 text-yellow-500" />
                    </div>
                </div>
                <h1 className="text-3xl font-bold text-neutral-900 mb-3">Xin chào! 👋</h1>
                <p className="text-neutral-500 text-center max-w-md leading-relaxed">
                    Tôi là <span className="font-semibold text-primary">AMI</span> - Trợ lý AI của
                    Học viện Công nghệ Bưu chính Viễn thông. Tôi có thể giúp bạn giải đáp mọi thắc mắc.
                </p>
            </div>

            {/* Quick questions */}
            <div className="w-full max-w-2xl">
                <p className="text-sm font-medium text-neutral-400 mb-4 text-center uppercase tracking-wide">
                    Bạn có thể hỏi tôi về
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {quickQuestions.map((item) => (
                        <Button
                            key={item.title}
                            variant="ghost"
                            className={`h-auto p-4 flex items-center gap-4 rounded-xl border border-transparent transition-all duration-200 ${item.bg}`}
                            onClick={() => onQuestionSelect(item.question)}
                        >
                            <div className={`w-10 h-10 rounded-lg flex items-center justify-center bg-white shadow-sm`}>
                                <item.icon className={`w-5 h-5 ${item.color}`} />
                            </div>
                            <div className="text-left flex-1">
                                <span className="font-semibold text-neutral-900 block">{item.title}</span>
                                <span className="text-xs text-neutral-500">{item.question}</span>
                            </div>
                        </Button>
                    ))}
                </div>
            </div>

            {/* Hint */}
            <p className="text-xs text-neutral-400 mt-10">
                Nhập câu hỏi hoặc nhấn{' '}
                <kbd className="px-2 py-1 bg-white rounded-md text-neutral-600 shadow-sm border border-neutral-200 font-mono text-[10px]">
                    Enter
                </kbd>{' '}
                để gửi
            </p>
        </div>
    )
}

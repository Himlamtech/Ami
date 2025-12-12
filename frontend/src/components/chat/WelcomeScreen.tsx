interface WelcomeScreenProps {
    onQuestionSelect: (question: string) => void
}

const quickQuestions = [
    'Học phí kỳ này là bao nhiêu?',
    'Làm sao để đăng ký môn học?',
    'Cho tôi mẫu đơn xin nghỉ học',
    'Điều kiện để được học bổng KKHT?',
]

export default function WelcomeScreen({ onQuestionSelect }: WelcomeScreenProps) {
    return (
        <div className="flex flex-col items-center justify-center h-full px-6 py-12">
            <div className="text-center max-w-2xl space-y-2">
                <h2 className="text-3xl font-semibold text-neutral-900">AMI / AI Assistant</h2>
                <p className="text-base text-neutral-500">
                    Hỏi AMI bất cứ điều gì về PTIT.
                </p>
            </div>

            <div className="mt-6 flex flex-wrap justify-center gap-2 max-w-2xl">
                {quickQuestions.map((q) => (
                    <button
                        key={q}
                        onClick={() => onQuestionSelect(q)}
                        className="px-4 py-2 rounded-full bg-[var(--surface2)] text-sm text-neutral-700 shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all"
                    >
                        {q}
                    </button>
                ))}
            </div>
        </div>
    )
}

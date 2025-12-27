const faqs = [
    {
        question: "Ami lấy thông tin từ đâu?",
        answer: "Hệ thống truy xuất từ tài liệu chính thống của PTIT thông qua hybrid search và RAG.",
    },
    {
        question: "Voice Query hoạt động thế nào?",
        answer: "Audio được nhận dạng bằng STT, kiểm tra độ tin cậy trước khi đưa vào pipeline RAG.",
    },
    {
        question: "Có hỗ trợ ảnh thông báo không?",
        answer: "Ami đọc ảnh bằng OCR + Vision AI và trả lời kèm ngữ cảnh từ tài liệu liên quan.",
    },
    {
        question: "Dữ liệu phản hồi được sử dụng để làm gì?",
        answer: "Feedback được tổng hợp và đánh giá chất lượng để cải thiện phản hồi từ hệ thống.",
    },
]

export default function Faq() {
    return (
        <section id="faq" className="py-20">
            <div className="container px-4 mx-auto">
                <div className="text-center">
                    <span className="text-sm font-semibold uppercase tracking-[0.2em] text-gray-500">Hỏi đáp</span>
                    <h3 className="mt-3 text-4xl md:text-5xl font-semibold tracking-tight text-gray-900">
                        Những câu hỏi thường gặp
                    </h3>
                    <p className="mt-4 text-lg text-gray-600 max-w-2xl mx-auto">
                        Tổng hợp nhanh các điểm nổi bật trong tài liệu usecase của Ami.
                    </p>
                </div>
                <div className="mt-12 grid gap-6 md:grid-cols-2">
                    {faqs.map((faq) => (
                        <div key={faq.question} className="rounded-3xl border border-gray-200 bg-white p-6 shadow-sm">
                            <h4 className="text-lg font-semibold text-gray-900">{faq.question}</h4>
                            <p className="mt-3 text-sm text-gray-600 leading-relaxed">{faq.answer}</p>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    )
}

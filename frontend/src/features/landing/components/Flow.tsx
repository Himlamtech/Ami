const flowSteps = [
    {
        title: "Input",
        description: "Text, voice hoặc image từ sinh viên.",
    },
    {
        title: "Validation",
        description: "Kiểm tra định dạng, độ dài và ngữ cảnh.",
    },
    {
        title: "Session",
        description: "Tải lịch sử và xây dựng context.",
    },
    {
        title: "Semantic",
        description: "Embedding, STT hoặc OCR theo loại dữ liệu.",
    },
    {
        title: "Hybrid Search",
        description: "Kết hợp semantic + BM25 để truy xuất.",
    },
    {
        title: "LLM",
        description: "Tổng hợp câu trả lời có trích dẫn.",
    },
    {
        title: "Delivery",
        description: "Streaming phản hồi nhanh, mượt.",
    },
    {
        title: "Feedback",
        description: "Ghi nhận đánh giá, tối ưu chất lượng.",
    },
]

export default function Flow() {
    return (
        <section className="py-16">
            <div className="container px-4 mx-auto">
                <div className="rounded-[32px] border border-gray-200 bg-white p-10 shadow-sm">
                    <div className="flex flex-col gap-3">
                        <span className="text-sm font-semibold uppercase tracking-[0.2em] text-gray-500">Luồng xử lý</span>
                        <h3 className="text-3xl md:text-4xl font-semibold tracking-tight text-gray-900">
                            Data Flow từ input đến phản hồi
                        </h3>
                        <p className="text-gray-600 max-w-2xl">
                            Theo tài liệu Chat Flow, hệ thống chia thành 8 lớp xử lý, đảm bảo câu trả lời đầy đủ và rõ ràng.
                        </p>
                    </div>
                    <div className="mt-8 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                        {flowSteps.map((step, index) => (
                            <div key={step.title} className="rounded-2xl border border-gray-200 bg-gray-50/60 p-5">
                                <div className="text-xs font-semibold text-gray-500">0{index + 1}</div>
                                <div className="mt-2 text-lg font-semibold text-gray-900">{step.title}</div>
                                <p className="mt-2 text-sm text-gray-600">{step.description}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </section>
    )
}

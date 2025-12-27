const featureList = [
    {
        title: "RAG tra cứu thông minh",
        description: "Kết hợp hybrid search (semantic + BM25) để truy xuất tài liệu PTIT chuẩn xác, trả lời kèm ngữ cảnh.",
        accent: "from-primary/15 to-orange-100",
    },
    {
        title: "Voice Query chuẩn hóa",
        description: "Hỗ trợ STT với cơ chế kiểm chứng độ tin cậy, tối ưu cho tra cứu nhanh khi đang di chuyển.",
        accent: "from-blue-100 to-sky-50",
    },
    {
        title: "Image Query + OCR",
        description: "Nhận ảnh thông báo, lịch học, biểu mẫu và trích xuất nội dung để hỏi đáp ngay lập tức.",
        accent: "from-amber-100 to-orange-50",
    },
    {
        title: "Session & Context",
        description: "Quản lý phiên, tải lịch sử và xây dựng ngữ cảnh để câu trả lời luôn đúng mạch cuộc trò chuyện.",
        accent: "from-emerald-100 to-green-50",
    },
    {
        title: "Feedback & Analytics",
        description: "Ghi nhận đánh giá, thống kê chất lượng phản hồi và cải thiện liên tục từ phản hồi thực tế.",
        accent: "from-purple-100 to-fuchsia-50",
    },
    {
        title: "Cá nhân hóa",
        description: "Tùy biến câu trả lời theo ngành học, năm học và sở thích, tạo trải nghiệm riêng cho từng sinh viên.",
        accent: "from-rose-100 to-red-50",
    },
]

export default function Features() {
    return (
        <section id="features" className="relative py-20">
            <div className="container px-4 mx-auto">
                <div className="flex flex-col gap-4 text-center">
                    <span className="text-sm font-semibold uppercase tracking-[0.2em] text-gray-500">Tính năng</span>
                    <h2 className="text-4xl md:text-5xl font-semibold tracking-tight text-gray-900">
                        Bộ công cụ đầy đủ cho trợ lý học vụ
                    </h2>
                    <p className="max-w-2xl mx-auto text-lg text-gray-600">
                        Dựa trên luồng usecase trong tài liệu, Ami kết hợp RAG, voice, image và hệ thống phiên để phục vụ sinh viên PTIT toàn diện.
                    </p>
                </div>

                <div className="mt-12 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                    {featureList.map((feature) => (
                        <div
                            key={feature.title}
                            className="group relative overflow-hidden rounded-3xl border border-gray-200 bg-white p-6 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-md"
                        >
                            <div className="relative">
                                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-primary/10">
                                    <span className="h-2 w-2 rounded-full bg-primary" />
                                </div>
                                <h3 className="text-xl font-semibold text-gray-900 mb-2">{feature.title}</h3>
                                <p className="text-sm text-gray-600 leading-relaxed">{feature.description}</p>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    )
}

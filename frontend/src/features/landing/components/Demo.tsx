export default function Demo() {
    return (
        <section id="demo" className="relative py-20">
            <div className="absolute inset-0 bg-gradient-to-b from-white via-[#fafafa] to-white -z-10" />
            <div className="container px-4 mx-auto">
                <div className="grid gap-12 lg:grid-cols-[1fr_1.1fr] items-center">
                    <div className="space-y-6">
                        <span className="text-sm font-semibold uppercase tracking-[0.2em] text-gray-500">Demo</span>
                        <h3 className="text-4xl md:text-5xl font-semibold tracking-tight text-gray-900">
                            Trải nghiệm phản hồi nhanh và có trích dẫn
                        </h3>
                        <p className="text-lg text-gray-600">
                            Ami xử lý yêu cầu theo từng bước: validate, truy xuất tài liệu, tổng hợp và stream phản hồi.
                            Bạn luôn biết câu trả lời đến từ đâu.
                        </p>
                        <div className="grid gap-4 md:grid-cols-2">
                            <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
                                <div className="text-sm font-semibold text-gray-900">Thời gian phản hồi</div>
                                <div className="mt-2 text-3xl font-bold text-gray-900">2.3s</div>
                                <p className="mt-2 text-sm text-gray-500">Streaming phản hồi theo từng đoạn.</p>
                            </div>
                            <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
                                <div className="text-sm font-semibold text-gray-900">Nguồn trích dẫn</div>
                                <div className="mt-2 text-3xl font-bold text-gray-900">12</div>
                                <p className="mt-2 text-sm text-gray-500">Từ tài liệu chính thức PTIT.</p>
                            </div>
                        </div>
                    </div>

                    <div className="relative">
                        <div className="absolute -top-6 -right-6 h-24 w-24 rounded-full bg-primary/10 blur-2xl" />
                        <div className="rounded-[28px] border border-gray-200 bg-white shadow-sm">
                            <div className="border-b border-gray-100 px-6 py-4 text-sm text-gray-500">
                                Session: ses_2025_001 • Context: CNTT K19
                            </div>
                            <div className="space-y-4 px-6 py-6">
                                <div className="rounded-2xl bg-gray-50 px-4 py-3 text-sm text-gray-600">
                                    "Quy chế điểm danh học phần tiếng Anh là gì?"
                                </div>
                                <div className="rounded-2xl bg-gray-50 px-4 py-3 text-sm text-gray-700">
                                    Theo quy định hiện hành, sinh viên cần đạt tối thiểu 80% số buổi học.
                                    <span className="mt-2 block text-xs text-gray-500">Nguồn: Quy chế đào tạo 2024 (trang 6)</span>
                                </div>
                                <div className="flex flex-wrap gap-2">
                                    <span className="rounded-full bg-gray-100 px-3 py-1 text-xs text-gray-500">Voice Query</span>
                                    <span className="rounded-full bg-gray-100 px-3 py-1 text-xs text-gray-500">Image OCR</span>
                                    <span className="rounded-full bg-gray-100 px-3 py-1 text-xs text-gray-500">Session History</span>
                                </div>
                            </div>
                        </div>
                        <div className="mt-6 grid gap-4 sm:grid-cols-2">
                            <div className="rounded-2xl border border-gray-200 bg-white p-4">
                                <div className="text-xs font-semibold uppercase tracking-[0.2em] text-gray-400">Voice</div>
                                <p className="mt-2 text-sm text-gray-600">Wav2Vec2 / Gemini STT với kiểm chứng độ tin cậy.</p>
                            </div>
                            <div className="rounded-2xl border border-gray-200 bg-white p-4">
                                <div className="text-xs font-semibold uppercase tracking-[0.2em] text-gray-400">Image</div>
                                <p className="mt-2 text-sm text-gray-600">OCR + Vision AI cho thông báo và lịch học.</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    )
}

import { Button } from "@/components/ui/button"
import { useNavigate } from "react-router-dom"

export default function Hero() {
    const navigate = useNavigate()

    return (
        <section className="relative pt-24 pb-20 overflow-hidden">
            <div className="absolute inset-0 bg-radial-red -z-10" />
            <div className="absolute inset-0 bg-grid-soft opacity-15 -z-10" />
            <div className="container relative z-10 px-4 mx-auto">
                <div className="mx-auto max-w-3xl text-center">
                    <div className="inline-flex items-center gap-2 px-4 py-2 mb-6 rounded-full border border-gray-200 text-gray-600 text-sm font-medium">
                        Trợ lý ảo AI dành riêng cho sinh viên PTIT
                    </div>
                    <h1 className="text-4xl font-semibold tracking-tight text-gray-900 mb-6 md:text-6xl">
                        Hỏi đáp thông minh
                        <span className="block text-primary">Đồng hành cùng bạn</span>
                    </h1>
                    <p className="mx-auto mb-10 text-lg text-gray-600 md:text-xl">
                        Tra cứu lịch học, quy chế, điểm số và mọi thông tin về PTIT chỉ trong vài giây.
                        Được hỗ trợ bởi công nghệ AI tiên tiến nhất, với luồng xử lý RAG chuẩn hóa.
                    </p>
                    <div className="flex flex-col items-center justify-center gap-4 sm:flex-row">
                        <Button
                            size="lg"
                            className="w-full sm:w-auto text-lg h-12 px-8 bg-primary hover:bg-primary/90"
                            onClick={() => navigate('/chat')}
                        >
                            Bắt đầu chat ngay
                        </Button>
                        <Button
                            variant="outline"
                            size="lg"
                            className="w-full sm:w-auto text-lg h-12 px-8 border-gray-300 text-gray-700 hover:bg-gray-50"
                            onClick={() => document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' })}
                        >
                            Tìm hiểu thêm
                        </Button>
                    </div>
                </div>
            </div>
        </section>
    )
}

import { Button } from "@/components/ui/button"
import { useNavigate } from "react-router-dom"

export default function Hero() {
    const navigate = useNavigate()

    return (
        <section className="relative pt-32 pb-20 overflow-hidden">
            <div className="container relative z-10 px-4 mx-auto text-center">
                <div className="inline-block px-4 py-2 mb-6 rounded-full bg-primary/10 text-primary font-medium animate-fade-in-up">
                    Trợ lý ảo AI dành riêng cho sinh viên PTIT
                </div>
                <h1 className="text-5xl font-bold tracking-tight text-gray-900 mb-6 md:text-7xl">
                    Hỏi đáp thông minh <br />
                    <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-orange-600">
                        Đồng hành cùng bạn
                    </span>
                </h1>
                <p className="max-w-2xl mx-auto mb-10 text-lg text-gray-600 md:text-xl">
                    Tra cứu lịch học, quy chế, điểm số và mọi thông tin về PTIT chỉ trong vài giây.
                    Được hỗ trợ bởi công nghệ AI tiên tiến nhất.
                </p>
                <div className="flex flex-col items-center justify-center gap-4 md:flex-row">
                    <Button
                        size="lg"
                        className="w-full md:w-auto text-lg h-12 px-8 bg-primary hover:bg-primary/90"
                        onClick={() => navigate('/chat')}
                    >
                        Bắt đầu chat ngay
                    </Button>
                    <Button
                        variant="outline"
                        size="lg"
                        className="w-full md:w-auto text-lg h-12 px-8"
                        onClick={() => document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' })}
                    >
                        Tìm hiểu thêm
                    </Button>
                </div>
            </div>

            {/* Background Elements */}
            <div className="absolute top-0 left-0 w-full h-full overflow-hidden -z-10">
                <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-primary/10 blur-[120px]" />
                <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-blue-500/10 blur-[120px]" />
            </div>
        </section>
    )
}

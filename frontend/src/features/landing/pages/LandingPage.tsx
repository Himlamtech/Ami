import Hero from "../components/Hero"
import Features from "../components/Features"
import Flow from "../components/Flow"
import Demo from "../components/Demo"
import Faq from "../components/Faq"
import Footer from "../components/Footer"

export default function LandingPage() {
    return (
        <div className="min-h-screen flex flex-col bg-white">
            {/* Simple Navbar for Landing */}
            <header className="sticky top-0 z-50 w-full border-b bg-white/80 backdrop-blur supports-[backdrop-filter]:bg-white/60">
                <div className="container flex h-16 items-center justify-between px-4 mx-auto">
                    <div className="flex items-center gap-2 font-bold text-xl text-primary">
                        <span>Ami</span>
                    </div>
                    <nav className="hidden md:flex gap-6 text-sm font-medium">
                        <a href="#features" className="text-gray-600 hover:text-primary">Tính năng</a>
                        <a href="#demo" className="text-gray-600 hover:text-primary">Demo</a>
                        <a href="#faq" className="text-gray-600 hover:text-primary">Hỏi đáp</a>
                    </nav>
                    <div className="flex items-center gap-4">
                        <a href="/login" className="text-sm font-medium hover:text-primary">Đăng nhập</a>
                        <a href="/chat" className="px-4 py-2 text-sm font-medium text-white bg-primary rounded-full hover:bg-primary/90 transition-colors">
                            Vào Ami
                        </a>
                    </div>
                </div>
            </header>

            <main className="flex-1">
                <Hero />
                <Features />
                <Flow />
                <Demo />
                <Faq />
            </main>

            <Footer />
        </div>
    )
}

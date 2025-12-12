import { Outlet } from 'react-router-dom'
import { useState } from 'react'
import ChatSidebar from '@/components/chat/ChatSidebar'
import MobileNav from '@/components/shared/MobileNav'
import { Menu, Bot } from 'lucide-react'
import { Button } from '@/components/ui/button'

export default function ChatLayout() {
    const [sidebarOpen, setSidebarOpen] = useState(false)

    return (
        <div className="flex h-screen bg-gradient-to-br from-neutral-50 to-neutral-100/50">
            {/* Mobile header */}
            <header className="fixed top-0 left-0 right-0 h-14 bg-white/80 backdrop-blur-lg border-b border-neutral-200/50 flex items-center px-4 gap-3 lg:hidden z-30">
                <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => setSidebarOpen(true)}
                    className="hover:bg-neutral-100"
                >
                    <Menu className="h-5 w-5" />
                </Button>
                <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
                        <Bot className="h-4 w-4 text-white" />
                    </div>
                    <span className="font-bold text-neutral-900">AMI</span>
                </div>
            </header>

            {/* Sidebar */}
            <aside
                className={`
                    fixed inset-y-0 left-0 z-40 w-[280px] transform bg-white border-r border-neutral-200/50 transition-transform duration-300 ease-out shadow-xl lg:shadow-none
                    lg:relative lg:translate-x-0
                    ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
                `}
            >
                <ChatSidebar onClose={() => setSidebarOpen(false)} />
            </aside>

            {/* Overlay for mobile */}
            {sidebarOpen && (
                <div
                    className="fixed inset-0 z-30 bg-black/30 backdrop-blur-sm lg:hidden transition-opacity"
                    onClick={() => setSidebarOpen(false)}
                />
            )}

            {/* Main content */}
            <main className="flex-1 flex flex-col min-w-0 pt-14 pb-14 lg:pt-0 lg:pb-0">
                <Outlet />
            </main>

            {/* Mobile bottom navigation */}
            <MobileNav />
        </div>
    )
}

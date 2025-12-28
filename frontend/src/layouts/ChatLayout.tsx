import { Outlet } from 'react-router-dom'
import { useState } from 'react'
import ChatSidebar from '@/components/chat/ChatSidebar'
import MobileNav from '@/components/shared/MobileNav'
import { Menu, Bot } from 'lucide-react'
import { Button } from '@/components/ui/button'

export default function ChatLayout() {
    const [sidebarOpen, setSidebarOpen] = useState(false)

    return (
        <div className="flex h-screen bg-[var(--bg)] text-[var(--text)]">
            {/* Mobile header */}
            <header className="fixed top-0 left-0 right-0 h-14 bg-[var(--surface)]/95 backdrop-blur-lg flex items-center px-4 gap-3 lg:hidden z-30 shadow-sm">
                <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => setSidebarOpen(true)}
                    className="hover:bg-[var(--surface2)]"
                >
                    <Menu className="h-5 w-5" />
                </Button>
                <div className="flex items-center gap-2">
                    <span className="font-bold text-2xl text-red-600">AMI</span>
                </div>
            </header>

            {/* Sidebar */}
            <aside
                className={`
                    fixed inset-y-0 left-0 z-40 w-[280px] transform bg-[var(--panel)] border-r border-[color:var(--border)] transition-transform duration-300 ease-out shadow-md lg:shadow-sm
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
            <main className="flex-1 flex flex-col min-w-0 pt-14 pb-14 lg:pt-0 lg:pb-0 bg-[var(--bg)]">
                <Outlet />
            </main>

            {/* Mobile bottom navigation */}
            <MobileNav />
        </div>
    )
}

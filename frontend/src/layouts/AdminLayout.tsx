import { Outlet, NavLink, useLocation } from 'react-router-dom'
import { useState } from 'react'
import {
    LayoutDashboard,
    MessageSquare,
    Star,
    BarChart3,
    BookOpen,
    Users,
    Settings,
    Menu,
    Bell,
    ChevronDown,
    Bot,
    X,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { cn } from '@/lib/utils'
import { Separator } from '@/components/ui/separator'

const navItems = [
    { icon: LayoutDashboard, label: 'Dashboard', path: '/admin' },
    { icon: MessageSquare, label: 'Conversations', path: '/admin/conversations' },
    { icon: Star, label: 'Feedback', path: '/admin/feedback' },
    { icon: BarChart3, label: 'Analytics', path: '/admin/analytics' },
    { icon: BookOpen, label: 'Knowledge', path: '/admin/knowledge' },
    { icon: Users, label: 'Users', path: '/admin/users' },
]

export default function AdminLayout() {
    const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
    const location = useLocation()

    const getPageTitle = () => {
        const item = navItems.find((item) => item.path === location.pathname)
        return item?.label || 'Settings'
    }

    return (
        <div className="flex h-screen bg-neutral-50">
            {/* Mobile overlay */}
            {mobileMenuOpen && (
                <div
                    className="fixed inset-0 z-40 bg-black/50 lg:hidden"
                    onClick={() => setMobileMenuOpen(false)}
                />
            )}

            {/* Sidebar */}
            <aside
                className={cn(
                    'flex flex-col bg-white border-r border-neutral-200 transition-all duration-200',
                    // Desktop
                    'hidden lg:flex',
                    sidebarCollapsed ? 'lg:w-16' : 'lg:w-64',
                )}
            >
                {/* Logo */}
                <div className="flex items-center gap-3 px-4 h-16 border-b border-neutral-200">
                    <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-primary text-white">
                        <Bot className="w-6 h-6" />
                    </div>
                    {!sidebarCollapsed && (
                        <span className="font-bold text-lg text-neutral-900">AMI Admin</span>
                    )}
                </div>

                {/* Navigation */}
                <nav className="flex-1 p-3 space-y-1">
                    {navItems.map((item) => (
                        <NavLink
                            key={item.path}
                            to={item.path}
                            end={item.path === '/admin'}
                            className={({ isActive }) =>
                                cn(
                                    'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                                    isActive
                                        ? 'bg-primary text-white'
                                        : 'text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900'
                                )
                            }
                        >
                            <item.icon className="w-5 h-5 flex-shrink-0" />
                            {!sidebarCollapsed && <span>{item.label}</span>}
                        </NavLink>
                    ))}
                </nav>

                <Separator />

                {/* Settings */}
                <div className="p-3">
                    <NavLink
                        to="/admin/settings"
                        className={({ isActive }) =>
                            cn(
                                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                                isActive
                                    ? 'bg-primary text-white'
                                    : 'text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900'
                            )
                        }
                    >
                        <Settings className="w-5 h-5 flex-shrink-0" />
                        {!sidebarCollapsed && <span>Settings</span>}
                    </NavLink>
                </div>
            </aside>

            {/* Mobile Sidebar */}
            <aside
                className={cn(
                    'fixed inset-y-0 left-0 z-50 w-64 flex flex-col bg-white border-r border-neutral-200 transition-transform duration-200 lg:hidden',
                    mobileMenuOpen ? 'translate-x-0' : '-translate-x-full'
                )}
            >
                {/* Logo */}
                <div className="flex items-center justify-between px-4 h-16 border-b border-neutral-200">
                    <div className="flex items-center gap-3">
                        <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-primary text-white">
                            <Bot className="w-6 h-6" />
                        </div>
                        <span className="font-bold text-lg text-neutral-900">AMI Admin</span>
                    </div>
                    <Button variant="ghost" size="icon" onClick={() => setMobileMenuOpen(false)}>
                        <X className="w-5 h-5" />
                    </Button>
                </div>

                {/* Navigation */}
                <nav className="flex-1 p-3 space-y-1">
                    {navItems.map((item) => (
                        <NavLink
                            key={item.path}
                            to={item.path}
                            end={item.path === '/admin'}
                            onClick={() => setMobileMenuOpen(false)}
                            className={({ isActive }) =>
                                cn(
                                    'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                                    isActive
                                        ? 'bg-primary text-white'
                                        : 'text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900'
                                )
                            }
                        >
                            <item.icon className="w-5 h-5 flex-shrink-0" />
                            <span>{item.label}</span>
                        </NavLink>
                    ))}
                </nav>

                <Separator />

                {/* Settings */}
                <div className="p-3">
                    <NavLink
                        to="/admin/settings"
                        onClick={() => setMobileMenuOpen(false)}
                        className={({ isActive }) =>
                            cn(
                                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                                isActive
                                    ? 'bg-primary text-white'
                                    : 'text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900'
                            )
                        }
                    >
                        <Settings className="w-5 h-5 flex-shrink-0" />
                        <span>Settings</span>
                    </NavLink>
                </div>
            </aside>

            {/* Main area */}
            <div className="flex-1 flex flex-col min-w-0">
                {/* Top bar */}
                <header className="flex items-center justify-between h-16 px-4 lg:px-6 bg-white border-b border-neutral-200">
                    <div className="flex items-center gap-3 lg:gap-4">
                        {/* Mobile menu button */}
                        <Button
                            variant="ghost"
                            size="icon"
                            className="lg:hidden"
                            onClick={() => setMobileMenuOpen(true)}
                        >
                            <Menu className="w-5 h-5" />
                        </Button>
                        {/* Desktop collapse button */}
                        <Button
                            variant="ghost"
                            size="icon"
                            className="hidden lg:flex"
                            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
                        >
                            <Menu className="w-5 h-5" />
                        </Button>
                        <h1 className="text-lg font-semibold text-neutral-900">{getPageTitle()}</h1>
                    </div>

                    <div className="flex items-center gap-2 lg:gap-3">
                        <Button variant="ghost" size="icon" className="relative">
                            <Bell className="w-5 h-5" />
                            <span className="absolute top-1 right-1 w-2 h-2 bg-primary rounded-full" />
                        </Button>

                        <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                                <Button variant="ghost" className="flex items-center gap-2 px-2 lg:px-3">
                                    <Avatar className="w-8 h-8">
                                        <AvatarFallback>AD</AvatarFallback>
                                    </Avatar>
                                    <span className="text-sm font-medium hidden sm:inline">Admin</span>
                                    <ChevronDown className="w-4 h-4 hidden sm:block" />
                                </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end" className="w-48">
                                <DropdownMenuItem>Profile</DropdownMenuItem>
                                <DropdownMenuItem>Settings</DropdownMenuItem>
                                <DropdownMenuSeparator />
                                <DropdownMenuItem className="text-error">Logout</DropdownMenuItem>
                            </DropdownMenuContent>
                        </DropdownMenu>
                    </div>
                </header>

                {/* Page content */}
                <main className="flex-1 overflow-auto p-4 lg:p-6">
                    <Outlet />
                </main>
            </div>
        </div>
    )
}

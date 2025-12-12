import { Outlet, NavLink, useLocation, Link } from 'react-router-dom'
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
    Database,
    Layers,
    Search,
    ArrowLeft,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Input } from '@/components/ui/input'
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { cn } from '@/lib/utils'
import { Separator } from '@/components/ui/separator'

const navGroups = [
    {
        title: 'Overview',
        items: [
            { icon: LayoutDashboard, label: 'Dashboard', path: '/admin' },
            { icon: MessageSquare, label: 'Conversations', path: '/admin/conversations' },
            { icon: Star, label: 'Feedback', path: '/admin/feedback' },
            { icon: BarChart3, label: 'Analytics', path: '/admin/analytics' },
        ],
    },
    {
        title: 'Knowledge',
        items: [
            { icon: BookOpen, label: 'Knowledge', path: '/admin/knowledge' },
            { icon: Database, label: 'Datasources', path: '/admin/datasources' },
            { icon: Layers, label: 'Vector Store', path: '/admin/vector-store' },
            { icon: Users, label: 'Users', path: '/admin/users' },
        ],
    },
]

export default function AdminLayout() {
    const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
    const location = useLocation()

    const getPageTitle = () => {
        for (const group of navGroups) {
            const item = group.items.find((i) => i.path === location.pathname)
            if (item) return item.label
        }
        return 'Settings'
    }

    return (
        <div className="flex h-screen bg-[var(--bg)] text-[var(--text)]">
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
                    'flex flex-col bg-[var(--surface2)] shadow-md transition-all duration-200',
                    // Desktop
                    'hidden lg:flex',
                    sidebarCollapsed ? 'lg:w-16' : 'lg:w-64',
                )}
            >
                {/* Logo */}
                <div className="flex items-center gap-3 px-4 h-14">
                    <div className="flex items-center justify-center w-9 h-9 rounded-lg bg-primary/10 text-primary">
                        <Bot className="w-5 h-5" />
                    </div>
                    {!sidebarCollapsed && (
                        <span className="font-semibold text-base tracking-tight text-neutral-900">AMI Admin</span>
                    )}
                </div>

                {/* Navigation */}
                <nav className="flex-1 px-2 py-3 space-y-3">
                    {navGroups.map((group) => (
                        <div key={group.title} className="space-y-1">
                            {!sidebarCollapsed && (
                                <p className="px-3 py-1 text-[10px] font-semibold tracking-wider uppercase text-[var(--muted)]">
                                    {group.title}
                                </p>
                            )}
                            {group.items.map((item) => (
                                <NavLink
                                    key={item.path}
                                    to={item.path}
                                    end={item.path === '/admin'}
                                    className={({ isActive }) =>
                                        cn(
                                            'group relative flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors',
                                            isActive
                                                ? 'bg-primary/5 text-neutral-900 before:absolute before:left-1 before:top-2 before:bottom-2 before:w-0.5 before:rounded-full before:bg-primary'
                                                : 'text-neutral-700 hover:bg-[var(--surface)] hover:text-neutral-900'
                                        )
                                    }
                                >
                                    <item.icon className="w-5 h-5 flex-shrink-0 text-neutral-400 group-hover:text-neutral-600" />
                                    {!sidebarCollapsed && <span>{item.label}</span>}
                                </NavLink>
                            ))}
                        </div>
                    ))}
                </nav>

                <Separator className="opacity-50" />

                {/* Settings */}
                <div className="px-2 py-3">
                    <Button
                        asChild
                        variant="ghost"
                        size="sm"
                        className={cn(
                            'w-full justify-start h-10 rounded-xl bg-[var(--surface)] shadow-sm mb-2',
                            sidebarCollapsed && 'justify-center px-0'
                        )}
                    >
                        <Link to="/chat" aria-label="Back to chat">
                            <ArrowLeft className="w-5 h-5 flex-shrink-0 text-neutral-400" />
                            {!sidebarCollapsed && <span className="ml-3">Back to Chat</span>}
                        </Link>
                    </Button>
                    <NavLink
                        to="/admin/settings"
                        className={({ isActive }) =>
                            cn(
                                'group relative flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors',
                                isActive
                                    ? 'bg-primary/5 text-neutral-900 before:absolute before:left-1 before:top-2 before:bottom-2 before:w-0.5 before:rounded-full before:bg-primary'
                                    : 'text-neutral-700 hover:bg-[var(--surface)] hover:text-neutral-900'
                            )
                        }
                    >
                        <Settings className="w-5 h-5 flex-shrink-0 text-neutral-400 group-hover:text-neutral-600" />
                        {!sidebarCollapsed && <span>Settings</span>}
                    </NavLink>
                </div>
            </aside>

            {/* Mobile Sidebar */}
            <aside
                className={cn(
                    'fixed inset-y-0 left-0 z-50 w-64 flex flex-col bg-[var(--surface2)] shadow-lg transition-transform duration-200 lg:hidden',
                    mobileMenuOpen ? 'translate-x-0' : '-translate-x-full'
                )}
            >
                {/* Logo */}
                <div className="flex items-center justify-between px-4 h-14">
                    <div className="flex items-center gap-3">
                        <div className="flex items-center justify-center w-9 h-9 rounded-lg bg-primary/10 text-primary">
                            <Bot className="w-5 h-5" />
                        </div>
                        <span className="font-semibold text-base tracking-tight text-neutral-900">AMI Admin</span>
                    </div>
                    <Button variant="ghost" size="icon" onClick={() => setMobileMenuOpen(false)}>
                        <X className="w-5 h-5" />
                    </Button>
                </div>

                {/* Navigation */}
                <nav className="flex-1 px-2 py-3 space-y-3">
                    {navGroups.map((group) => (
                        <div key={group.title} className="space-y-1">
                            <p className="px-3 py-1 text-[10px] font-semibold tracking-wider uppercase text-[var(--muted)]">
                                {group.title}
                            </p>
                            {group.items.map((item) => (
                                <NavLink
                                    key={item.path}
                                    to={item.path}
                                    end={item.path === '/admin'}
                                    onClick={() => setMobileMenuOpen(false)}
                                    className={({ isActive }) =>
                                        cn(
                                            'group relative flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors',
                                            isActive
                                                ? 'bg-primary/5 text-neutral-900 before:absolute before:left-1 before:top-2 before:bottom-2 before:w-0.5 before:rounded-full before:bg-primary'
                                                : 'text-neutral-700 hover:bg-[var(--surface)] hover:text-neutral-900'
                                        )
                                    }
                                >
                                    <item.icon className="w-5 h-5 flex-shrink-0 text-neutral-400 group-hover:text-neutral-600" />
                                    <span>{item.label}</span>
                                </NavLink>
                            ))}
                        </div>
                    ))}
                </nav>

                <Separator className="opacity-50" />

                {/* Settings */}
                <div className="px-2 py-3">
                    <NavLink
                        to="/admin/settings"
                        onClick={() => setMobileMenuOpen(false)}
                        className={({ isActive }) =>
                            cn(
                                'group relative flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors',
                                isActive
                                    ? 'bg-primary/5 text-neutral-900 before:absolute before:left-1 before:top-2 before:bottom-2 before:w-0.5 before:rounded-full before:bg-primary'
                                    : 'text-neutral-700 hover:bg-[var(--surface)] hover:text-neutral-900'
                            )
                        }
                    >
                        <Settings className="w-5 h-5 flex-shrink-0 text-neutral-400 group-hover:text-neutral-600" />
                        <span>Settings</span>
                    </NavLink>
                </div>
            </aside>

            {/* Main area */}
            <div className="flex-1 flex flex-col min-w-0">
                {/* Top bar */}
                <header className="flex items-center justify-between h-14 px-4 lg:px-6 bg-[var(--surface)] shadow-sm">
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
                        <Button
                            asChild
                            variant="ghost"
                            size="sm"
                            className="hidden md:inline-flex h-9 rounded-full bg-[var(--surface2)] shadow-sm"
                        >
                            <Link to="/chat">
                                <ArrowLeft className="w-4 h-4 mr-2" />
                                Back to Chat
                            </Link>
                        </Button>
                        <h1 className="text-lg font-semibold text-neutral-900">{getPageTitle()}</h1>
                    </div>

                    <div className="flex items-center gap-2 lg:gap-3">
                        <div className="hidden lg:block relative w-64">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
                            <Input
                                placeholder="Search..."
                                className="pl-9 h-9 bg-[var(--surface2)]"
                                aria-label="Global search"
                            />
                        </div>
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
                <main className="flex-1 overflow-auto px-4 lg:px-8 py-6 lg:py-8">
                    <div className="max-w-[1200px] mx-auto w-full">
                        <Outlet />
                    </div>
                </main>
            </div>
        </div>
    )
}

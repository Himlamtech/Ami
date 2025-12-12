import { NavLink } from 'react-router-dom'
import { MessageSquare, BookOpen, Bookmark, User } from 'lucide-react'
import { cn } from '@/lib/utils'

const navItems = [
    { icon: MessageSquare, label: 'Chat', path: '/' },
    { icon: BookOpen, label: 'Docs', path: '/docs' },
    { icon: Bookmark, label: 'Saved', path: '/saved' },
    { icon: User, label: 'Profile', path: '/profile' },
]

export default function MobileNav() {
    return (
        <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-neutral-200 lg:hidden z-50">
            <div className="flex items-center justify-around h-14">
                {navItems.map((item) => (
                    <NavLink
                        key={item.path}
                        to={item.path}
                        className={({ isActive }) =>
                            cn(
                                'flex flex-col items-center justify-center flex-1 h-full gap-0.5',
                                'text-xs transition-colors',
                                isActive
                                    ? 'text-primary'
                                    : 'text-neutral-500 hover:text-neutral-700'
                            )
                        }
                    >
                        {({ isActive }) => (
                            <>
                                <item.icon
                                    className={cn(
                                        'w-5 h-5',
                                        isActive && 'fill-current'
                                    )}
                                />
                                <span>{item.label}</span>
                            </>
                        )}
                    </NavLink>
                ))}
            </div>
        </nav>
    )
}

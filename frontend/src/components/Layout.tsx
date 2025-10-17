import { ReactNode } from 'react'
import { useNavigate } from 'react-router-dom'
import {
    AppBar,
    Box,
    Toolbar,
    Typography,
    Button,
    Drawer,
    List,
    ListItem,
    ListItemButton,
    ListItemIcon,
    ListItemText,
} from '@mui/material'
import {
    Dashboard as DashboardIcon,
    Description as DocumentsIcon,
    Logout as LogoutIcon,
} from '@mui/icons-material'
import { useAuthStore } from '../store/authStore'

const DRAWER_WIDTH = 240

interface LayoutProps {
    children: ReactNode
}

export default function Layout({ children }: LayoutProps) {
    const navigate = useNavigate()
    const { user, logout } = useAuthStore()

    const handleLogout = () => {
        logout()
        navigate('/login')
    }

    const menuItems = [
        { text: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard' },
        { text: 'Documents', icon: <DocumentsIcon />, path: '/documents' },
    ]

    return (
        <Box sx={{ display: 'flex' }}>
            <AppBar
                position="fixed"
                sx={{
                    zIndex: (theme) => theme.zIndex.drawer + 1,
                    background: 'linear-gradient(135deg, #ff8a9a 0%, #ff5c7c 100%)',
                    boxShadow: '0 4px 20px rgba(255, 138, 154, 0.2)',
                }}
            >
                <Toolbar>
                    <Typography
                        variant="h6"
                        component="div"
                        sx={{
                            flexGrow: 1,
                            fontWeight: 700,
                            letterSpacing: '0.5px',
                        }}
                    >
                        AMI Admin - PTIT
                    </Typography>
                    <Typography variant="body2" sx={{ mr: 2, opacity: 0.9 }}>
                        {user?.full_name || user?.username}
                    </Typography>
                    <Button
                        color="inherit"
                        startIcon={<LogoutIcon />}
                        onClick={handleLogout}
                        sx={{
                            '&:hover': {
                                bgcolor: 'rgba(255, 255, 255, 0.15)',
                            },
                        }}
                    >
                        Logout
                    </Button>
                </Toolbar>
            </AppBar>

            <Drawer
                variant="permanent"
                sx={{
                    width: DRAWER_WIDTH,
                    flexShrink: 0,
                    '& .MuiDrawer-paper': {
                        width: DRAWER_WIDTH,
                        boxSizing: 'border-box',
                        borderRight: '1px solid rgba(255, 138, 154, 0.1)',
                        background: 'linear-gradient(180deg, #ffffff 0%, #fff8f9 100%)',
                    },
                }}
            >
                <Toolbar />
                <Box sx={{ overflow: 'auto', p: 1 }}>
                    <List>
                        {menuItems.map((item) => (
                            <ListItem key={item.text} disablePadding sx={{ mb: 0.5 }}>
                                <ListItemButton
                                    onClick={() => navigate(item.path)}
                                    sx={{
                                        borderRadius: 2,
                                        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                                        '&:hover': {
                                            bgcolor: 'rgba(255, 138, 154, 0.08)',
                                            transform: 'translateX(4px)',
                                            '& .MuiListItemIcon-root': {
                                                color: 'primary.main',
                                            },
                                        },
                                    }}
                                >
                                    <ListItemIcon
                                        sx={{
                                            transition: 'color 0.3s ease',
                                            color: 'text.secondary',
                                        }}
                                    >
                                        {item.icon}
                                    </ListItemIcon>
                                    <ListItemText
                                        primary={item.text}
                                        primaryTypographyProps={{
                                            fontWeight: 500,
                                        }}
                                    />
                                </ListItemButton>
                            </ListItem>
                        ))}
                    </List>
                </Box>
            </Drawer>

            <Box
                component="main"
                sx={{
                    flexGrow: 1,
                    p: 3,
                    bgcolor: 'background.default',
                    minHeight: '100vh',
                }}
            >
                <Toolbar />
                {children}
            </Box>
        </Box>
    )
}


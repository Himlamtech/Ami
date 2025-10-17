import { useState } from 'react'
import { Box, Button, Card, CardContent, TextField, Typography, Alert } from '@mui/material'
import { useAuthStore } from '../store/authStore'
import { authAPI } from '../api/client'

export default function Login() {
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState('')
    const [loading, setLoading] = useState(false)
    const setAuth = useAuthStore((state) => state.setAuth)

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setError('')
        setLoading(true)

        try {
            const response = await authAPI.login(username, password)
            setAuth(response.access_token, response.user)
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Login failed. Please check your credentials.')
        } finally {
            setLoading(false)
        }
    }

    return (
        <Box
            sx={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                minHeight: '100vh',
                bgcolor: 'background.default',
                background: 'linear-gradient(135deg, #fff5f7 0%, #ffe8ec 100%)',
                position: 'relative',
                overflow: 'hidden',
                '&::before': {
                    content: '""',
                    position: 'absolute',
                    width: '400px',
                    height: '400px',
                    background: 'radial-gradient(circle, rgba(255, 138, 154, 0.1) 0%, transparent 70%)',
                    top: '-100px',
                    right: '-100px',
                    animation: 'float 6s ease-in-out infinite',
                },
                '&::after': {
                    content: '""',
                    position: 'absolute',
                    width: '300px',
                    height: '300px',
                    background: 'radial-gradient(circle, rgba(255, 168, 180, 0.08) 0%, transparent 70%)',
                    bottom: '-80px',
                    left: '-80px',
                    animation: 'float 8s ease-in-out infinite reverse',
                },
                '@keyframes float': {
                    '0%, 100%': { transform: 'translate(0, 0)' },
                    '50%': { transform: 'translate(20px, 20px)' },
                },
            }}
        >
            <Card
                sx={{
                    maxWidth: 400,
                    width: '100%',
                    mx: 2,
                    boxShadow: '0 8px 32px rgba(255, 138, 154, 0.15)',
                    backdropFilter: 'blur(10px)',
                    position: 'relative',
                    zIndex: 1,
                    animation: 'slideIn 0.5s cubic-bezier(0.4, 0, 0.2, 1)',
                    '@keyframes slideIn': {
                        from: { opacity: 0, transform: 'translateY(20px)' },
                        to: { opacity: 1, transform: 'translateY(0)' },
                    },
                }}
            >
                <CardContent sx={{ p: 4 }}>
                    <Typography
                        variant="h4"
                        component="h1"
                        gutterBottom
                        align="center"
                        sx={{
                            background: 'linear-gradient(135deg, #ff8a9a 0%, #ff5c7c 100%)',
                            WebkitBackgroundClip: 'text',
                            WebkitTextFillColor: 'transparent',
                            fontWeight: 700,
                        }}
                    >
                        AMI Admin
                    </Typography>
                    <Typography variant="body2" color="text.secondary" gutterBottom align="center" sx={{ mb: 3 }}>
                        PTIT Document Management System
                    </Typography>

                    {error && (
                        <Alert severity="error" sx={{ mb: 2 }}>
                            {error}
                        </Alert>
                    )}

                    <form onSubmit={handleSubmit}>
                        <TextField
                            label="Username"
                            fullWidth
                            margin="normal"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                            autoFocus
                        />
                        <TextField
                            label="Password"
                            type="password"
                            fullWidth
                            margin="normal"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                        <Button
                            type="submit"
                            variant="contained"
                            fullWidth
                            size="large"
                            sx={{ mt: 3 }}
                            disabled={loading}
                        >
                            {loading ? 'Logging in...' : 'Login'}
                        </Button>
                    </form>
                </CardContent>
            </Card>
        </Box>
    )
}


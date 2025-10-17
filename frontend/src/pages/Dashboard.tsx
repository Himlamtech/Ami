import { Box, Card, CardContent, Grid, Typography } from '@mui/material'
import { Description, CloudUpload, CheckCircle } from '@mui/icons-material'

export default function Dashboard() {
    return (
        <Box
            sx={{
                animation: 'fadeIn 0.6s ease-in-out',
                '@keyframes fadeIn': {
                    from: { opacity: 0, transform: 'translateY(20px)' },
                    to: { opacity: 1, transform: 'translateY(0)' },
                },
            }}
        >
            <Typography
                variant="h4"
                gutterBottom
                sx={{
                    background: 'linear-gradient(135deg, #ff8a9a 0%, #ff5c7c 100%)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    fontWeight: 700,
                }}
            >
                Dashboard
            </Typography>
            <Typography variant="body1" color="text.secondary" paragraph>
                Welcome to AMI Admin Panel - PTIT Document Management
            </Typography>

            <Grid container spacing={3} sx={{ mt: 2 }}>
                <Grid item xs={12} md={4}>
                    <Card
                        sx={{
                            background: 'linear-gradient(135deg, #ffffff 0%, #fff8f9 100%)',
                            border: '1px solid rgba(255, 138, 154, 0.1)',
                            animation: 'slideInLeft 0.5s ease-out',
                            '@keyframes slideInLeft': {
                                from: { opacity: 0, transform: 'translateX(-20px)' },
                                to: { opacity: 1, transform: 'translateX(0)' },
                            },
                        }}
                    >
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                                <Description
                                    sx={{
                                        fontSize: 40,
                                        color: 'primary.main',
                                        mr: 2,
                                        transition: 'transform 0.3s ease',
                                        '&:hover': { transform: 'scale(1.1) rotate(5deg)' },
                                    }}
                                />
                                <div>
                                    <Typography variant="h6" sx={{ fontWeight: 600 }}>Total Documents</Typography>
                                    <Typography variant="h4" sx={{ color: 'primary.main', fontWeight: 700 }}>-</Typography>
                                </div>
                            </Box>
                            <Typography variant="body2" color="text.secondary">
                                All documents in the system
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} md={4}>
                    <Card
                        sx={{
                            background: 'linear-gradient(135deg, #ffffff 0%, #f0fff4 100%)',
                            border: '1px solid rgba(76, 175, 80, 0.1)',
                            animation: 'slideInLeft 0.5s ease-out 0.1s backwards',
                            '@keyframes slideInLeft': {
                                from: { opacity: 0, transform: 'translateX(-20px)' },
                                to: { opacity: 1, transform: 'translateX(0)' },
                            },
                        }}
                    >
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                                <CheckCircle
                                    sx={{
                                        fontSize: 40,
                                        color: 'success.main',
                                        mr: 2,
                                        transition: 'transform 0.3s ease',
                                        '&:hover': { transform: 'scale(1.1) rotate(5deg)' },
                                    }}
                                />
                                <div>
                                    <Typography variant="h6" sx={{ fontWeight: 600 }}>Active Documents</Typography>
                                    <Typography variant="h4" sx={{ color: 'success.main', fontWeight: 700 }}>-</Typography>
                                </div>
                            </Box>
                            <Typography variant="body2" color="text.secondary">
                                Documents available for search
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} md={4}>
                    <Card
                        sx={{
                            background: 'linear-gradient(135deg, #ffffff 0%, #f0f9ff 100%)',
                            border: '1px solid rgba(33, 150, 243, 0.1)',
                            animation: 'slideInLeft 0.5s ease-out 0.2s backwards',
                            '@keyframes slideInLeft': {
                                from: { opacity: 0, transform: 'translateX(-20px)' },
                                to: { opacity: 1, transform: 'translateX(0)' },
                            },
                        }}
                    >
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                                <CloudUpload
                                    sx={{
                                        fontSize: 40,
                                        color: 'info.main',
                                        mr: 2,
                                        transition: 'transform 0.3s ease',
                                        '&:hover': { transform: 'scale(1.1) rotate(5deg)' },
                                    }}
                                />
                                <div>
                                    <Typography variant="h6" sx={{ fontWeight: 600 }}>Collections</Typography>
                                    <Typography variant="h4" sx={{ color: 'info.main', fontWeight: 700 }}>-</Typography>
                                </div>
                            </Box>
                            <Typography variant="body2" color="text.secondary">
                                Document collections
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>

            <Card sx={{ mt: 4 }}>
                <CardContent>
                    <Typography variant="h6" gutterBottom>
                        Quick Start
                    </Typography>
                    <Typography variant="body2" paragraph>
                        1. Go to <strong>Documents</strong> to manage your document library
                    </Typography>
                    <Typography variant="body2" paragraph>
                        2. Upload new documents to make them searchable
                    </Typography>
                    <Typography variant="body2" paragraph>
                        3. Organize documents into collections
                    </Typography>
                    <Typography variant="body2">
                        4. Soft-delete documents to temporarily remove them from search
                    </Typography>
                </CardContent>
            </Card>
        </Box>
    )
}


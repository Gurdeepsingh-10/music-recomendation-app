import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import useMusicStore from '../store/musicStore';
import TrackCard from '../components/TrackCard';
import { Box, Grid, Typography, Paper, Button } from '@mui/material';
import SparklesIcon from '@mui/icons-material/AutoAwesome';
import MusicNoteIcon from '@mui/icons-material/MusicNote';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';

const Home = () => {
    const { isAuthenticated, user, fetchUser } = useAuthStore();
    const { recommendations, loading, fetchRecommendations } = useMusicStore();
    const navigate = useNavigate();
    const [greeting, setGreeting] = useState('');

    useEffect(() => {
        if (!isAuthenticated) {
            navigate('/login');
            return;
        }

        fetchUser();
        fetchRecommendations('hybrid', { limit: 12 });

        const hour = new Date().getHours();
        if (hour < 12) setGreeting('Good morning');
        else if (hour < 18) setGreeting('Good afternoon');
        else setGreeting('Good evening');
    }, [isAuthenticated, navigate]);

    return (
        <Box>
            <Box sx={{ mb: 4 }}>
                <Typography variant="h3" fontWeight={800} gutterBottom>
                    {greeting}{user?.username && `, ${user.username}`}! 👋
                </Typography>
                <Typography variant="h6" color="text.secondary">
                    Discover your next favorite track
                </Typography>
            </Box>

            <Grid container spacing={2} sx={{ mb: 4 }}>
                <Grid item xs={12} md={4}>
                    <Paper sx={{ p: 3, display: 'flex', flexDirection: 'column', gap: 1 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                            <Typography variant="subtitle1" fontWeight={700}>Hybrid Engine</Typography>
                            <SparklesIcon color="primary" />
                        </Box>
                        <Typography variant="body2" color="text.secondary">
                            AI-powered recommendations combining content, user preferences, and popularity
                        </Typography>
                    </Paper>
                </Grid>
                <Grid item xs={12} md={4}>
                    <Paper sx={{ p: 3, display: 'flex', flexDirection: 'column', gap: 1 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                            <Typography variant="subtitle1" fontWeight={700}>106K+ Tracks</Typography>
                            <MusicNoteIcon color="primary" />
                        </Box>
                        <Typography variant="body2" color="text.secondary">
                            Real music from the Free Music Archive with full metadata
                        </Typography>
                    </Paper>
                </Grid>
                <Grid item xs={12} md={4}>
                    <Paper sx={{ p: 3, display: 'flex', flexDirection: 'column', gap: 1 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                            <Typography variant="subtitle1" fontWeight={700}>Personalized</Typography>
                            <TrendingUpIcon color="primary" />
                        </Box>
                        <Typography variant="body2" color="text.secondary">
                            Learns from your listening habits to improve over time
                        </Typography>
                    </Paper>
                </Grid>
            </Grid>

            <Box sx={{ mb: 2, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Typography variant="h4" fontWeight={800} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <SparklesIcon color="primary" /> Recommended For You
                </Typography>
                <Button onClick={() => navigate('/for-you')} variant="text">See All →</Button>
            </Box>

            {loading ? (
                <Grid container spacing={2}>
                    {Array.from({ length: 12 }).map((_, i) => (
                        <Grid item xs={6} md={4} lg={3} xl={2} key={i}>
                            <Paper sx={{ p: 2, height: '100%' }} />
                        </Grid>
                    ))}
                </Grid>
            ) : (
                <Grid container spacing={2}>
                    {recommendations.slice(0, 12).map((track) => (
                        <Grid item xs={6} md={4} lg={3} xl={2} key={track.track_id}>
                            <TrackCard track={track} showScore={true} />
                        </Grid>
                    ))}
                </Grid>
            )}

            <Grid container spacing={2} sx={{ mt: 2 }}>
                <Grid item xs={12} md={6}>
                    <Paper sx={{ p: 4, cursor: 'pointer' }} onClick={() => navigate('/discover')}>
                        <Typography variant="h5" fontWeight={800} gutterBottom>Discover New Music</Typography>
                        <Typography variant="body2" color="text.secondary">Browse 106K+ tracks across all genres</Typography>
                    </Paper>
                </Grid>
                <Grid item xs={12} md={6}>
                    <Paper sx={{ p: 4, cursor: 'pointer' }} onClick={() => navigate('/analytics')}>
                        <Typography variant="h5" fontWeight={800} gutterBottom>View Your Stats</Typography>
                        <Typography variant="body2" color="text.secondary">See your listening habits and preferences</Typography>
                    </Paper>
                </Grid>
            </Grid>
        </Box>
    );
};

export default Home;
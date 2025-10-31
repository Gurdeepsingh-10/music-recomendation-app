import { useEffect, useState } from 'react';
import useMusicStore from '../store/musicStore';
import TrackCard from '../components/TrackCard';
import { Box, Grid, ToggleButton, ToggleButtonGroup, Typography } from '@mui/material';
import SparklesIcon from '@mui/icons-material/AutoAwesome';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import RadioIcon from '@mui/icons-material/Radio';

const ForYou = () => {
    const { recommendations, loading, fetchRecommendations } = useMusicStore();
    const [activeTab, setActiveTab] = useState('hybrid');

    useEffect(() => {
        loadRecommendations(activeTab);
    }, [activeTab]);

    const loadRecommendations = (type) => {
        fetchRecommendations(type, { limit: 24 });
    };

    const tabs = [
        { id: 'hybrid', label: 'Hybrid', icon: <SparklesIcon fontSize="small" /> },
        { id: 'for-you', label: 'For You', icon: <TrendingUpIcon fontSize="small" /> },
        { id: 'popular', label: 'Popular', icon: <RadioIcon fontSize="small" /> },
    ];

    return (
        <Box>
            <Box sx={{ mb: 3 }}>
                <Typography variant="h4" fontWeight={800} gutterBottom>For You</Typography>
                <Typography color="text.secondary">Personalized recommendations powered by AI</Typography>
            </Box>

            <ToggleButtonGroup
                color="primary"
                value={activeTab}
                exclusive
                onChange={(_, v) => v && setActiveTab(v)}
                sx={{ mb: 3, flexWrap: 'wrap', gap: 1 }}
            >
                {tabs.map((t) => (
                    <ToggleButton key={t.id} value={t.id} sx={{ borderRadius: 2 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            {t.icon}
                            {t.label}
                        </Box>
                    </ToggleButton>
                ))}
            </ToggleButtonGroup>

            {loading ? (
                <Grid container spacing={2}>
                    {Array.from({ length: 24 }).map((_, i) => (
                        <Grid item xs={6} md={4} lg={3} xl={2} key={i}>
                            <Box sx={{ p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 2, height: '100%' }} />
                        </Grid>
                    ))}
                </Grid>
            ) : (
                <>
                    <Typography color="text.secondary" sx={{ mb: 1 }}>{recommendations.length} personalized recommendations</Typography>
                    <Grid container spacing={2}>
                        {recommendations.map((track) => (
                            <Grid item xs={6} md={4} lg={3} xl={2} key={track.track_id}>
                                <TrackCard track={track} showScore={true} />
                            </Grid>
                        ))}
                    </Grid>
                </>
            )}
        </Box>
    );
};

export default ForYou;
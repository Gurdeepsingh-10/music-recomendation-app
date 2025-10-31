import useMusicStore from '../store/musicStore';
import { useState } from 'react';
import { Card, CardContent, CardActions, Typography, IconButton, Box, Chip } from '@mui/material';
import PlayArrowRoundedIcon from '@mui/icons-material/PlayArrowRounded';
import FavoriteRoundedIcon from '@mui/icons-material/FavoriteRounded';
import SkipNextRoundedIcon from '@mui/icons-material/SkipNextRounded';
import AlbumRoundedIcon from '@mui/icons-material/AlbumRounded';
import { motion } from 'framer-motion';

const TrackCard = ({ track, showScore = false }) => {
    const { playTrack, likeTrack, skipTrack } = useMusicStore();
    const [isLiked, setIsLiked] = useState(false);
    const [isPlaying, setIsPlaying] = useState(false);

    const handlePlay = async () => {
        setIsPlaying(true);
        await playTrack(track);
        setTimeout(() => setIsPlaying(false), 2000);
    };

    const handleLike = async () => {
        setIsLiked(true);
        await likeTrack(track.track_id);
    };

    const handleSkip = async () => {
        await skipTrack(track.track_id, 0);
    };

    const getScoreColor = (score) => {
        if (score >= 0.8) return 'mui-color-success';
        if (score >= 0.6) return 'mui-color-warning';
        return 'mui-color-muted';
    };

    return (
        <motion.div whileHover={{ y: -4 }} transition={{ type: 'spring', stiffness: 300, damping: 18 }}>
            <Card sx={{ overflow: 'hidden' }}>
                <Box sx={{ position: 'relative', mb: 1 }}>
                    <Box sx={{
                        pt: '100%',
                        bgcolor: 'rgba(29,185,84,0.15)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        borderBottom: '1px solid',
                        borderColor: 'divider'
                    }}>
                        <Box sx={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                            <AlbumRoundedIcon sx={{ fontSize: 48, color: 'primary.main', opacity: 0.6 }} />
                        </Box>
                    </Box>
                    <motion.div initial={{ scale: 0, opacity: 0 }} whileHover={{ scale: 1, opacity: 1 }} animate={isPlaying ? { scale: 1, opacity: 1 } : {}} style={{ position: 'absolute', right: 12, bottom: 12 }}>
                        <IconButton color="primary" onClick={handlePlay} sx={{ bgcolor: 'primary.main', color: 'white', '&:hover': { transform: 'scale(1.08)' } }}>
                            <PlayArrowRoundedIcon />
                        </IconButton>
                    </motion.div>
                </Box>
                <CardContent sx={{ pt: 1 }}>
                    <Typography variant="subtitle1" noWrap fontWeight={700}>{track.title}</Typography>
                    <Typography variant="body2" color="text.secondary" noWrap>{track.artist}</Typography>
                    {track.genre && (
                        <Chip size="small" label={track.genre} sx={{ mt: 1 }} />
                    )}

                    {showScore && (
                        <Box sx={{ mt: 1 }}>
                            {track.hybrid_score !== undefined && (
                                <Box sx={{ display: 'flex', justifyContent: 'space-between', fontSize: 12 }}>
                                    <Typography variant="caption" color="text.secondary">Match Score</Typography>
                                    <Typography variant="caption" fontWeight={700} className={getScoreColor(track.hybrid_score)}>
                                        {(track.hybrid_score * 100).toFixed(0)}%
                                    </Typography>
                                </Box>
                            )}
                            {track.similarity_score !== undefined && (
                                <Box sx={{ display: 'flex', justifyContent: 'space-between', fontSize: 12 }}>
                                    <Typography variant="caption" color="text.secondary">Similarity</Typography>
                                    <Typography variant="caption" fontWeight={700} className={getScoreColor(track.similarity_score)}>
                                        {(track.similarity_score * 100).toFixed(0)}%
                                    </Typography>
                                </Box>
                            )}
                            {track.recommendation_reason && (
                                <Typography variant="caption" color="text.secondary" sx={{ fontStyle: 'italic' }}>{track.recommendation_reason}</Typography>
                            )}
                        </Box>
                    )}
                </CardContent>
                <CardActions sx={{ justifyContent: 'space-between', opacity: 0.0, transition: 'opacity 200ms', '&:hover': { opacity: 1 } }}>
                    <IconButton onClick={handleLike} color={isLiked ? 'error' : 'default'} sx={{ '&:hover': { transform: 'scale(1.08)' } }}>
                        <FavoriteRoundedIcon />
                    </IconButton>
                    <IconButton onClick={handleSkip} sx={{ '&:hover': { transform: 'scale(1.08)' } }}>
                        <SkipNextRoundedIcon />
                    </IconButton>
                </CardActions>
            </Card>
        </motion.div>
    );
};

export default TrackCard;
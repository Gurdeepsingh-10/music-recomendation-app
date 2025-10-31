import { create } from 'zustand';
import { musicAPI, recommendationAPI } from '../services/api';
import toast from 'react-hot-toast';

const useMusicStore = create((set, get) => ({
    tracks: [],
    currentTrack: null,
    recommendations: [],
    loading: false,
    error: null,

    fetchTracks: async (params = {}) => {
        set({ loading: true, error: null });
        try {
            const response = await musicAPI.getTracks(params);
            set({ tracks: response.data.tracks, loading: false });
        } catch (error) {
            set({ error: error.message, loading: false });
            toast.error('Failed to load tracks');
        }
    },

    fetchRecommendations: async (type = 'hybrid', params = {}) => {
        set({ loading: true, error: null });
        try {
            let response;

            switch (type) {
                case 'hybrid':
                    response = await recommendationAPI.getHybrid(params.limit);
                    break;
                case 'for-you':
                    response = await recommendationAPI.getForYou(params.limit);
                    break;
                case 'popular':
                    response = await recommendationAPI.getPopular(params.limit);
                    break;
                case 'similar':
                    response = await recommendationAPI.getSimilar(params.trackId, params.limit);
                    break;
                default:
                    response = await recommendationAPI.getHybrid(params.limit);
            }

            set({
                recommendations: response.data.recommendations,
                loading: false
            });
        } catch (error) {
            set({ error: error.message, loading: false });
            toast.error('Failed to load recommendations');
        }
    },

    playTrack: async (track) => {
        set({ currentTrack: track });

        // Log play event
        try {
            await musicAPI.logPlay({
                user_id: 'frontend',
                track_id: track.track_id,
                duration_played: 0,
                completed: false,
            });
        } catch (error) {
            console.error('Failed to log play:', error);
        }
    },

    likeTrack: async (trackId) => {
        try {
            await musicAPI.logLike({
                user_id: 'frontend',
                track_id: trackId,
            });
            toast.success('Added to liked songs ❤️');
        } catch (error) {
            toast.error('Failed to like track');
        }
    },

    skipTrack: async (trackId, position) => {
        try {
            await musicAPI.logSkip({
                user_id: 'frontend',
                track_id: trackId,
                position: position,
            });
        } catch (error) {
            console.error('Failed to log skip:', error);
        }
    },

    clearError: () => set({ error: null }),
}));

export default useMusicStore;
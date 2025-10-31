import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor - add token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Response interceptor - handle errors
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem('token');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

// Auth API
export const authAPI = {
    signup: (data) => api.post('/auth/signup', data),
    login: (data) => api.post('/auth/login', data),
    getMe: () => api.get('/auth/me'),
};

// Music API
export const musicAPI = {
    getTracks: (params) => api.get('/music/tracks', { params }),
    getTrack: (trackId) => api.get(`/music/tracks/${trackId}`),
    getGenres: () => api.get('/music/genres'),
    search: (query) => api.get('/music/search', { params: { q: query } }),
    logPlay: (data) => api.post('/music/play', data),
    logLike: (data) => api.post('/music/like', data),
    logSkip: (data) => api.post('/music/skip', data),
    getHistory: (limit = 50) => api.get('/music/history', { params: { limit } }),
};

// Recommendation API
export const recommendationAPI = {
    getSimilar: (trackId, limit = 20) =>
        api.get(`/recommendations/similar/${trackId}`, { params: { limit } }),
    getByGenre: (genre, limit = 20) =>
        api.get(`/recommendations/genre/${genre}`, { params: { limit } }),
    getPopular: (limit = 50) =>
        api.get('/recommendations/popular', { params: { limit } }),
    getForYou: (limit = 20) =>
        api.get('/recommendations/for-you', { params: { limit } }),
    getHybrid: (limit = 20) =>
        api.get('/recommendations/hybrid', { params: { limit } }),
};

// Analytics API
export const analyticsAPI = {
    getMyStats: () => api.get('/analytics/me'),
    getSystemStats: () => api.get('/analytics/system'),
    getAlgorithmPerformance: () => api.get('/analytics/algorithms'),
};

export default api;
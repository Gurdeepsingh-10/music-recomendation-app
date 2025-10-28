import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth APIs
export const authAPI = {
  signup: (data) => api.post('/auth/signup', data),
  login: (data) => api.post('/auth/login', data),
  getMe: () => api.get('/auth/me'),
};

// Music APIs
export const musicAPI = {
  logPlay: (data) => api.post('/music/play', data),
  logLike: (data) => api.post('/music/like', data),
  logSkip: (data) => api.post('/music/skip', data),
  getHistory: (limit = 50) => api.get(`/music/history?limit=${limit}`),
};

// Recommendation APIs
export const recommendationAPI = {
  getRecommendations: (limit = 20) => api.get(`/recommendations/?limit=${limit}`),
};

export default api;
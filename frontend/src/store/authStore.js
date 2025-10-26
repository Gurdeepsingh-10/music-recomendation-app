import { create } from 'zustand';
import { authAPI } from '../services/api';

const useAuthStore = create((set) => ({
    user: null,
    token: localStorage.getItem('token'),
    isAuthenticated: !!localStorage.getItem('token'),
    loading: false,
    error: null,

    signup: async (userData) => {
        set({ loading: true, error: null });
        try {
            const response = await authAPI.signup(userData);
            const { access_token } = response.data;
            localStorage.setItem('token', access_token);
            set({ token: access_token, isAuthenticated: true, loading: false });
            return true;
        } catch (error) {
            set({ error: error.response?.data?.detail || 'Signup failed', loading: false });
            return false;
        }
    },

    login: async (credentials) => {
        set({ loading: true, error: null });
        try {
            const response = await authAPI.login(credentials);
            const { access_token } = response.data;
            localStorage.setItem('token', access_token);
            set({ token: access_token, isAuthenticated: true, loading: false });
            return true;
        } catch (error) {
            set({ error: error.response?.data?.detail || 'Login failed', loading: false });
            return false;
        }
    },

    logout: () => {
        localStorage.removeItem('token');
        set({ user: null, token: null, isAuthenticated: false });
    },

    fetchUser: async () => {
        try {
            const response = await authAPI.getMe();
            set({ user: response.data });
        } catch (error) {
            console.error('Failed to fetch user:', error);
        }
    },
}));

export default useAuthStore;
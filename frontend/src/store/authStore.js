import { create } from 'zustand';
import { authAPI } from '../services/api';
import toast from 'react-hot-toast';

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
            set({
                token: access_token,
                isAuthenticated: true,
                loading: false
            });

            toast.success('Welcome to MusicRec! 🎵');
            return true;
        } catch (error) {
            const message = error.response?.data?.detail || 'Signup failed';
            set({ error: message, loading: false });
            toast.error(message);
            return false;
        }
    },

    login: async (credentials) => {
        set({ loading: true, error: null });
        try {
            const response = await authAPI.login(credentials);
            const { access_token } = response.data;

            localStorage.setItem('token', access_token);
            set({
                token: access_token,
                isAuthenticated: true,
                loading: false
            });

            toast.success('Welcome back! 🎶');
            return true;
        } catch (error) {
            const message = error.response?.data?.detail || 'Login failed';
            set({ error: message, loading: false });
            toast.error(message);
            return false;
        }
    },

    logout: () => {
        localStorage.removeItem('token');
        set({ user: null, token: null, isAuthenticated: false });
        toast.success('Logged out successfully');
    },

    fetchUser: async () => {
        try {
            const response = await authAPI.getMe();
            set({ user: response.data });
        } catch (error) {
            console.error('Failed to fetch user:', error);
        }
    },

    clearError: () => set({ error: null }),
}));

export default useAuthStore;
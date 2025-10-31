import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { TrendingUp, Sparkles, Music } from 'lucide-react';
import useAuthStore from '../store/authStore';
import useMusicStore from '../store/musicStore';
import TrackCard from '../components/TrackCard';

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

        // Set greeting based on time
        const hour = new Date().getHours();
        if (hour < 12) setGreeting('Good morning');
        else if (hour < 18) setGreeting('Good afternoon');
        else setGreeting('Good evening');
    }, [isAuthenticated, navigate]);

    return (
        <div className="min-h-screen bg-dark">
            <div className="max-w-7xl mx-auto px-4 py-8">
                {/* Hero Section */}
                <div className="mb-12">
                    <h1 className="text-5xl font-bold text-white mb-2">
                        {greeting}{user?.username && `, ${user.username}`}! 👋
                    </h1>
                    <p className="text-xl text-gray-text">
                        Discover your next favorite track
                    </p>
                </div>

                {/* Quick Stats */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
                    <div className="bg-gradient-to-br from-primary/20 to-primary/5 rounded-2xl p-6 border border-primary/20">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-lg font-semibold text-white">Hybrid Engine</h3>
                            <Sparkles className="text-primary" size={24} />
                        </div>
                        <p className="text-gray-text text-sm">
                            AI-powered recommendations combining content, user preferences, and popularity
                        </p>
                    </div>

                    <div className="bg-dark-card rounded-2xl p-6 border border-dark-card">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-lg font-semibold text-white">106K+ Tracks</h3>
                            <Music className="text-primary" size={24} />
                        </div>
                        <p className="text-gray-text text-sm">
                            Real music from the Free Music Archive with full metadata
                        </p>
                    </div>

                    <div className="bg-dark-card rounded-2xl p-6 border border-dark-card">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-lg font-semibold text-white">Personalized</h3>
                            <TrendingUp className="text-primary" size={24} />
                        </div>
                        <p className="text-gray-text text-sm">
                            Learns from your listening habits to improve over time
                        </p>
                    </div>
                </div>

                {/* Hybrid Recommendations */}
                <section className="mb-12">
                    <div className="flex items-center justify-between mb-6">
                        <h2 className="text-3xl font-bold text-white flex items-center">
                            <Sparkles className="text-primary mr-3" size={32} />
                            Recommended For You
                        </h2>
                        <button
                            onClick={() => navigate('/for-you')}
                            className="text-primary hover:text-primary-light transition-smooth font-semibold"
                        >
                            See All →
                        </button>
                    </div>

                    {loading ? (
                        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-4">
                            {[...Array(12)].map((_, i) => (
                                <div key={i} className="bg-dark-card rounded-lg p-4 animate-pulse">
                                    <div className="aspect-square bg-dark rounded-lg mb-4"></div>
                                    <div className="h-4 bg-dark rounded mb-2"></div>
                                    <div className="h-3 bg-dark rounded w-2/3"></div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-4">
                            {recommendations.slice(0, 12).map((track) => (
                                <TrackCard key={track.track_id} track={track} showScore={true} />
                            ))}
                        </div>
                    )}
                </section>

                {/* Quick Actions */}
                <section className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div
                        onClick={() => navigate('/discover')}
                        className="bg-gradient-to-br from-purple-500/20 to-purple-500/5 rounded-2xl p-8 border border-purple-500/20 cursor-pointer hover:scale-105 transition-smooth"
                    >
                        <h3 className="text-2xl font-bold text-white mb-2">Discover New Music</h3>
                        <p className="text-gray-text">Browse 106K+ tracks across all genres</p>
                    </div>

                    <div
                        onClick={() => navigate('/analytics')}
                        className="bg-gradient-to-br from-blue-500/20 to-blue-500/5 rounded-2xl p-8 border border-blue-500/20 cursor-pointer hover:scale-105 transition-smooth"
                    >
                        <h3 className="text-2xl font-bold text-white mb-2">View Your Stats</h3>
                        <p className="text-gray-text">See your listening habits and preferences</p>
                    </div>
                </section>
            </div>
        </div>
    );
};

export default Home;
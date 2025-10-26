import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import { Music } from 'lucide-react';

const Home = () => {
    const { isAuthenticated, user, fetchUser } = useAuthStore();
    const navigate = useNavigate();

    useEffect(() => {
        if (!isAuthenticated) {
            navigate('/login');
        } else if (isAuthenticated && !user) {
            fetchUser();
        }
    }, [isAuthenticated, user, navigate, fetchUser]);

    return (
        <div className="min-h-screen bg-dark">
            <div className="max-w-7xl mx-auto px-4 py-12">
                <div className="text-center mb-12">
                    <Music className="text-primary mx-auto mb-4" size={64} />
                    <h1 className="text-5xl font-bold text-white mb-4">
                        Welcome to MusicRec
                    </h1>
                    <p className="text-xl text-gray-400">
                        Your personal music recommendation system
                    </p>
                    {user && (
                        <p className="text-lg text-primary mt-4">
                            Hello, {user.username}!
                        </p>
                    )}
                </div>

                <div className="grid md:grid-cols-3 gap-8 mt-12">
                    <div className="bg-secondary p-6 rounded-lg">
                        <h3 className="text-xl font-bold text-white mb-2">🎵 Discover Music</h3>
                        <p className="text-gray-400">
                            Get personalized recommendations based on your taste
                        </p>
                    </div>

                    <div className="bg-secondary p-6 rounded-lg">
                        <h3 className="text-xl font-bold text-white mb-2">📊 Track History</h3>
                        <p className="text-gray-400">
                            Keep track of everything you've listened to
                        </p>
                    </div>

                    <div className="bg-secondary p-6 rounded-lg">
                        <h3 className="text-xl font-bold text-white mb-2">❤️ Like & Skip</h3>
                        <p className="text-gray-400">
                            Help us learn your preferences for better recommendations
                        </p>
                    </div>
                </div>

                <div className="mt-12 text-center">
                    <p className="text-gray-500 text-sm">
                        Step 1 Complete ✅ | Next: Database Setup
                    </p>
                </div>
            </div>
        </div>
    );
};

export default Home;
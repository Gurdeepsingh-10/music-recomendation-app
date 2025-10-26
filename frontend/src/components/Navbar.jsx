import { Link } from 'react-router-dom';
import { Music, LogOut } from 'lucide-react';
import useAuthStore from '../store/authStore';

const Navbar = () => {
    const { isAuthenticated, logout, user } = useAuthStore();

    return (
        <nav className="bg-secondary shadow-lg">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between h-16">
                    <div className="flex items-center">
                        <Music className="text-primary mr-2" size={32} />
                        <Link to="/" className="text-2xl font-bold text-white">
                            MusicRec
                        </Link>
                    </div>

                    <div className="flex items-center space-x-4">
                        {isAuthenticated ? (
                            <>
                                <span className="text-gray-300">{user?.username || 'User'}</span>
                                <button
                                    onClick={logout}
                                    className="flex items-center text-white hover:text-primary transition"
                                >
                                    <LogOut size={20} className="mr-1" />
                                    Logout
                                </button>
                            </>
                        ) : (
                            <>
                                <Link
                                    to="/login"
                                    className="text-white hover:text-primary transition"
                                >
                                    Login
                                </Link>
                                <Link
                                    to="/signup"
                                    className="bg-primary text-white px-4 py-2 rounded-full hover:bg-green-600 transition"
                                >
                                    Sign Up
                                </Link>
                            </>
                        )}
                    </div>
                </div>
            </div>
        </nav>
    );
};

export default Navbar;
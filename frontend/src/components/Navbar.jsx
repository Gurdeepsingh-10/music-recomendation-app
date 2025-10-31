import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Music, Home, Compass, Heart, BarChart, LogOut, User } from 'lucide-react';
import useAuthStore from '../store/authStore';

const Navbar = () => {
    const { isAuthenticated, user, logout } = useAuthStore();
    const navigate = useNavigate();
    const location = useLocation();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    const navItems = [
        { path: '/', icon: Home, label: 'Home' },
        { path: '/discover', icon: Compass, label: 'Discover' },
        { path: '/for-you', icon: Heart, label: 'For You' },
        { path: '/analytics', icon: BarChart, label: 'Stats' },
    ];

    const isActive = (path) => location.pathname === path;

    return (
        <nav className="bg-dark-lighter border-b border-dark-card">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center h-16">
                    {/* Logo */}
                    <Link to="/" className="flex items-center space-x-2 group">
                        <div className="bg-primary p-2 rounded-lg group-hover:scale-110 transition-smooth">
                            <Music className="text-white" size={24} />
                        </div>
                        <span className="text-2xl font-bold text-white">
                            Music<span className="text-primary">Rec</span>
                        </span>
                    </Link>

                    {/* Navigation Links */}
                    {isAuthenticated && (
                        <div className="hidden md:flex items-center space-x-1">
                            {navItems.map((item) => (
                                <Link
                                    key={item.path}
                                    to={item.path}
                                    className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-smooth ${isActive(item.path)
                                        ? 'bg-dark-card text-primary'
                                        : 'text-gray-text hover:text-white hover:bg-dark-card'
                                        }`}
                                >
                                    <item.icon size={20} />
                                    <span className="font-medium">{item.label}</span>
                                </Link>
                            ))}
                        </div>
                    )}

                    {/* User Menu */}
                    <div className="flex items-center space-x-4">
                        {isAuthenticated ? (
                            <>
                                <div className="flex items-center space-x-2 text-gray-text">
                                    <User size={20} />
                                    <span className="hidden sm:inline">{user?.username || 'User'}</span>
                                </div>
                                <button
                                    onClick={handleLogout}
                                    className="flex items-center space-x-2 px-4 py-2 rounded-full bg-dark-card text-white hover:bg-primary hover:text-white transition-smooth"
                                >
                                    <LogOut size={18} />
                                    <span className="hidden sm:inline">Logout</span>
                                </button>
                            </>
                        ) : (
                            <div className="flex items-center space-x-3">
                                <Link
                                    to="/login"
                                    className="px-4 py-2 text-white hover:text-primary transition-smooth"
                                >
                                    Login
                                </Link>
                                <Link
                                    to="/signup"
                                    className="px-6 py-2 bg-primary text-white rounded-full hover:bg-primary-dark transition-smooth font-semibold"
                                >
                                    Sign Up
                                </Link>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Mobile Navigation */}
            {isAuthenticated && (
                <div className="md:hidden border-t border-dark-card">
                    <div className="flex justify-around py-2">
                        {navItems.map((item) => (
                            <Link
                                key={item.path}
                                to={item.path}
                                className={`flex flex-col items-center p-2 ${isActive(item.path) ? 'text-primary' : 'text-gray-text'
                                    }`}
                            >
                                <item.icon size={20} />
                                <span className="text-xs mt-1">{item.label}</span>
                            </Link>
                        ))}
                    </div>
                </div>
            )}
        </nav>
    );
};

export default Navbar;
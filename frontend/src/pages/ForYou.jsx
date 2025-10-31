import { useEffect, useState } from 'react';
import { Sparkles, TrendingUp, Radio } from 'lucide-react';
import useMusicStore from '../store/musicStore';
import TrackCard from '../components/TrackCard';

const ForYou = () => {
    const { recommendations, loading, fetchRecommendations } = useMusicStore();
    const [activeTab, setActiveTab] = useState('hybrid');

    useEffect(() => {
        loadRecommendations(activeTab);
    }, [activeTab]);

    const loadRecommendations = (type) => {
        fetchRecommendations(type, { limit: 24 });
    };

    const tabs = [
        { id: 'hybrid', label: 'Hybrid Mix', icon: Sparkles, description: 'Best of all algorithms' },
        { id: 'for-you', label: 'For You', icon: TrendingUp, description: 'Based on your taste' },
        { id: 'popular', label: 'Popular', icon: Radio, description: 'Trending now' },
    ];

    return (
        <div className="min-h-screen bg-dark">
            <div className="max-w-7xl mx-auto px-4 py-8">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-4xl font-bold text-white mb-2">For You</h1>
                    <p className="text-gray-text">Personalized recommendations powered by AI</p>
                </div>

                {/* Tabs */}
                <div className="flex flex-wrap gap-4 mb-8">
                    {tabs.map((tab) => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id)}
                            className={`flex items-center space-x-3 px-6 py-4 rounded-xl transition-smooth ${activeTab === tab.id
                                    ? 'bg-primary text-white'
                                    : 'bg-dark-card text-gray-text hover:bg-dark-lighter hover:text-white'
                                }`}
                        >
                            <tab.icon size={20} />
                            <div className="text-left">
                                <div className="font-semibold">{tab.label}</div>
                                <div className="text-xs opacity-75">{tab.description}</div>
                            </div>
                        </button>
                    ))}
                </div>

                {/* Recommendations Grid */}
                {loading ? (
                    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-4">
                        {[...Array(24)].map((_, i) => (
                            <div key={i} className="bg-dark-card rounded-lg p-4 animate-pulse">
                                <div className="aspect-square bg-dark rounded-lg mb-4"></div>
                                <div className="h-4 bg-dark rounded mb-2"></div>
                                <div className="h-3 bg-dark rounded w-2/3"></div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <>
                        <div className="mb-6 text-gray-text">
                            {recommendations.length} personalized recommendations
                        </div>
                        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-4">
                            {recommendations.map((track) => (
                                <TrackCard key={track.track_id} track={track} showScore={true} />
                            ))}
                        </div>
                    </>
                )}
            </div>
        </div>
    );
};

export default ForYou;
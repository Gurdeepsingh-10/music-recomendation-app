import { useEffect, useState } from 'react';
import { Search, Filter } from 'lucide-react';
import useMusicStore from '../store/musicStore';
import { musicAPI } from '../services/api';
import TrackCard from '../components/TrackCard';

const Discover = () => {
    const { tracks, loading, fetchTracks } = useMusicStore();
    const [genres, setGenres] = useState([]);
    const [selectedGenre, setSelectedGenre] = useState('');
    const [searchQuery, setSearchQuery] = useState('');

    useEffect(() => {
        fetchTracks({ limit: 24 });
        loadGenres();
    }, []);

    const loadGenres = async () => {
        try {
            const response = await musicAPI.getGenres();
            setGenres(response.data.genres);
        } catch (error) {
            console.error('Failed to load genres:', error);
        }
    };

    const handleGenreChange = (genre) => {
        setSelectedGenre(genre);
        fetchTracks({ genre: genre || undefined, limit: 24 });
    };

    const handleSearch = async () => {
        if (searchQuery.trim()) {
            try {
                const response = await musicAPI.search(searchQuery);
                // Handle search results
            } catch (error) {
                console.error('Search failed:', error);
            }
        }
    };

    return (
        <div className="min-h-screen bg-dark">
            <div className="max-w-7xl mx-auto px-4 py-8">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-4xl font-bold text-white mb-2">Discover Music</h1>
                    <p className="text-gray-text">Browse 106,000+ tracks from the Free Music Archive</p>
                </div>

                {/* Search & Filters */}
                <div className="bg-dark-card rounded-xl p-6 mb-8">
                    <div className="flex flex-col md:flex-row gap-4">
                        {/* Search */}
                        <div className="flex-1 relative">
                            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-text" size={20} />
                            <input
                                type="text"
                                placeholder="Search tracks, artists, albums..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                                className="w-full pl-10 pr-4 py-3 bg-dark rounded-lg text-white placeholder-gray-text border border-dark-lighter focus:border-primary focus:outline-none transition-smooth"
                            />
                        </div>

                        {/* Genre Filter */}
                        <div className="md:w-64">
                            <div className="relative">
                                <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-text" size={20} />
                                <select
                                    value={selectedGenre}
                                    onChange={(e) => handleGenreChange(e.target.value)}
                                    className="w-full pl-10 pr-4 py-3 bg-dark rounded-lg text-white border border-dark-lighter focus:border-primary focus:outline-none appearance-none cursor-pointer transition-smooth"
                                >
                                    <option value="">All Genres</option>
                                    {genres.map((genre) => (
                                        <option key={genre} value={genre}>
                                            {genre}
                                        </option>
                                    ))}
                                </select>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Track Grid */}
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
                        <div className="mb-4 text-gray-text">
                            Showing {tracks.length} tracks
                            {selectedGenre && ` in ${selectedGenre}`}
                        </div>
                        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-4">
                            {tracks.map((track) => (
                                <TrackCard key={track.track_id} track={track} />
                            ))}
                        </div>
                    </>
                )}
            </div>
        </div>
    );
};

export default Discover;
import { Play, Heart, SkipForward, Music2 } from 'lucide-react';
import useMusicStore from '../store/musicStore';
import { useState } from 'react';

const TrackCard = ({ track, showScore = false }) => {
    const { playTrack, likeTrack, skipTrack } = useMusicStore();
    const [isLiked, setIsLiked] = useState(false);
    const [isPlaying, setIsPlaying] = useState(false);

    const handlePlay = async () => {
        setIsPlaying(true);
        await playTrack(track);
        setTimeout(() => setIsPlaying(false), 2000);
    };

    const handleLike = async () => {
        setIsLiked(true);
        await likeTrack(track.track_id);
    };

    const handleSkip = async () => {
        await skipTrack(track.track_id, 0);
    };

    const getScoreColor = (score) => {
        if (score >= 0.8) return 'text-green-400';
        if (score >= 0.6) return 'text-yellow-400';
        return 'text-gray-400';
    };

    return (
        <div className="group bg-dark-card rounded-lg p-4 hover:bg-dark-lighter transition-smooth cursor-pointer">
            {/* Album Art Placeholder */}
            <div className="relative mb-4">
                <div className="aspect-square bg-gradient-to-br from-primary/20 to-primary/5 rounded-lg flex items-center justify-center">
                    <Music2 size={48} className="text-primary/40" />
                </div>

                {/* Play Button Overlay */}
                <button
                    onClick={handlePlay}
                    className={`absolute bottom-2 right-2 bg-primary rounded-full p-3 shadow-lg transform transition-all ${isPlaying
                        ? 'scale-100 opacity-100'
                        : 'scale-0 opacity-0 group-hover:scale-100 group-hover:opacity-100'
                        }`}
                >
                    <Play size={20} className="text-white fill-white" />
                </button>
            </div>

            {/* Track Info */}
            <div className="space-y-2">
                <h3 className="font-semibold text-white truncate">{track.title}</h3>
                <p className="text-sm text-gray-text truncate">{track.artist}</p>

                {track.genre && (
                    <span className="inline-block text-xs px-2 py-1 bg-dark rounded-full text-gray-text">
                        {track.genre}
                    </span>
                )}

                {/* Scores */}
                {showScore && (
                    <div className="space-y-1 text-xs">
                        {track.hybrid_score !== undefined && (
                            <div className="flex justify-between items-center">
                                <span className="text-gray-text">Match Score:</span>
                                <span className={`font-semibold ${getScoreColor(track.hybrid_score)}`}>
                                    {(track.hybrid_score * 100).toFixed(0)}%
                                </span>
                            </div>
                        )}
                        {track.similarity_score !== undefined && (
                            <div className="flex justify-between items-center">
                                <span className="text-gray-text">Similarity:</span>
                                <span className={`font-semibold ${getScoreColor(track.similarity_score)}`}>
                                    {(track.similarity_score * 100).toFixed(0)}%
                                </span>
                            </div>
                        )}
                        {track.recommendation_reason && (
                            <p className="text-gray-text italic mt-2">{track.recommendation_reason}</p>
                        )}
                    </div>
                )}

                {/* Action Buttons */}
                <div className="flex items-center justify-between pt-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                        onClick={handleLike}
                        className={`p-2 rounded-full transition-smooth ${isLiked
                            ? 'bg-red-500 text-white'
                            : 'bg-dark hover:bg-dark-lighter text-gray-text hover:text-white'
                            }`}
                    >
                        <Heart size={18} className={isLiked ? 'fill-white' : ''} />
                    </button>

                    <button
                        onClick={handleSkip}
                        className="p-2 rounded-full bg-dark hover:bg-dark-lighter text-gray-text hover:text-white transition-smooth"
                    >
                        <SkipForward size={18} />
                    </button>
                </div>
            </div>
        </div>
    );
};

export default TrackCard;
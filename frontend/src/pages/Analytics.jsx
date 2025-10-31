import { BarChart3, Activity } from 'lucide-react';

const Analytics = () => {
    return (
        <div className="min-h-screen bg-dark">
            <div className="max-w-7xl mx-auto px-4 py-8">
                <div className="mb-8">
                    <h1 className="text-4xl font-bold text-white mb-2 flex items-center gap-3">
                        <BarChart3 className="text-primary" />
                        Your Stats
                    </h1>
                    <p className="text-gray-text">Overview of your listening activity</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="bg-dark-card rounded-2xl p-6 border border-dark-card">
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-gray-text">Total Plays</span>
                            <Activity className="text-primary" size={20} />
                        </div>
                        <div className="text-3xl font-bold text-white">—</div>
                    </div>

                    <div className="bg-dark-card rounded-2xl p-6 border border-dark-card">
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-gray-text">Liked Tracks</span>
                            <Activity className="text-primary" size={20} />
                        </div>
                        <div className="text-3xl font-bold text-white">—</div>
                    </div>

                    <div className="bg-dark-card rounded-2xl p-6 border border-dark-card">
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-gray-text">Time Listened</span>
                            <Activity className="text-primary" size={20} />
                        </div>
                        <div className="text-3xl font-bold text-white">—</div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Analytics;



import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Leaderboard = () => {
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLeaderboard();
  }, []);

  const fetchLeaderboard = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/leaderboard/');
      setLeaderboard(response.data.leaderboard);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching leaderboard:', error);
      setLoading(false);
    }
  };

  const getRankEmoji = (index) => {
    if (index === 0) return '🥇';
    if (index === 1) return '🥈';
    if (index === 2) return '🥉';
    return `#${index + 1}`;
  };

  const getLevelColor = (level) => {
    if (level >= 10) return 'text-purple-600';
    if (level >= 5) return 'text-blue-600';
    return 'text-green-600';
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-800">🏆 Leaderboard</h2>
        <span className="text-sm text-gray-500">Top Contributors</span>
      </div>

      <div className="space-y-4">
        {leaderboard.map((contributor, index) => (
          <div
            key={contributor.id}
            className={`flex items-center p-4 rounded-lg transition-all hover:shadow-md ${
              index < 3 ? 'bg-gradient-to-r from-yellow-50 to-orange-50' : 'bg-gray-50'
            }`}
          >
            {/* Rank */}
            <div className="text-2xl font-bold mr-4 w-12 text-center">
              {getRankEmoji(index)}
            </div>

            {/* Avatar */}
            <img
              src={contributor.avatar_url}
              alt={contributor.username}
              className="w-12 h-12 rounded-full mr-4 border-2 border-gray-200"
            />

            {/* Info */}
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <h3 className="font-semibold text-gray-800">{contributor.username}</h3>
                <span className={`text-sm font-bold ${getLevelColor(contributor.level)}`}>
                  Lv.{contributor.level}
                </span>
                {contributor.activity_streak > 0 && (
                  <span className="text-xs bg-orange-100 text-orange-600 px-2 py-1 rounded-full">
                    🔥 {contributor.activity_streak} day streak
                  </span>
                )}
              </div>
              <div className="flex gap-4 mt-1 text-sm text-gray-600">
                <span>💻 {contributor.total_commits} commits</span>
                <span>🐛 {contributor.total_issues_closed} issues</span>
                <span>👀 {contributor.total_prs_reviewed} reviews</span>
              </div>
            </div>

            {/* Score */}
            <div className="text-right">
              <div className="text-2xl font-bold text-blue-600">{contributor.total_score.toLocaleString()}</div>
              <div className="text-xs text-gray-500">XP</div>
            </div>
          </div>
        ))}
      </div>

      {leaderboard.length === 0 && (
        <div className="text-center text-gray-500 py-8">
          No contributors yet. Be the first!
        </div>
      )}
    </div>
  );
};

export default Leaderboard;

import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';

const ContributorStats = () => {
  const { contributorId } = useParams();
  const [stats, setStats] = useState(null);
  const [burnout, setBurnout] = useState(null);
  const [loading, setLoading] = useState(true);
  const [awardingBadges, setAwardingBadges] = useState(false);

  useEffect(() => {
    if (contributorId) {
      fetchStats();
    }
  }, [contributorId]);

  const fetchStats = async () => {
    try {
      const [statsRes, burnoutRes] = await Promise.all([
        axios.get(`http://localhost:8000/api/contributors/${contributorId}/stats/`),
        axios.get(`http://localhost:8000/api/contributors/${contributorId}/burnout/`),
      ]);
      
      setStats(statsRes.data);
      setBurnout(burnoutRes.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching contributor stats:', error);
      setLoading(false);
    }
  };

  const handleAwardBadges = async () => {
    setAwardingBadges(true);
    try {
      const response = await axios.post(
        `http://localhost:8000/api/contributors/${contributorId}/badges/`
      );
      alert(`Awarded ${response.data.count} new badges!`);
      fetchStats(); // Refresh data
    } catch (error) {
      console.error('Error awarding badges:', error);
      alert('Failed to award badges');
    } finally {
      setAwardingBadges(false);
    }
  };

  const getBurnoutColor = (riskLevel) => {
    if (riskLevel === 'high') return 'text-red-600 bg-red-50';
    if (riskLevel === 'medium') return 'text-yellow-600 bg-yellow-50';
    return 'text-green-600 bg-green-50';
  };

  const getBurnoutEmoji = (riskLevel) => {
    if (riskLevel === 'high') return '⚠️';
    if (riskLevel === 'medium') return '⚡';
    return '✅';
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-800">Contributor not found</h2>
          <Link to="/contributors" className="text-blue-500 hover:underline mt-4 inline-block">
            Back to Contributors
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-4">
              <img
                src={stats.contributor.avatar_url}
                alt={stats.contributor.username}
                className="w-24 h-24 rounded-full border-4 border-blue-500"
              />
              <div>
                <h1 className="text-3xl font-bold text-gray-800">
                  {stats.contributor.username}
                </h1>
                <div className="flex items-center gap-3 mt-2">
                  <span className="px-3 py-1 bg-blue-100 text-blue-600 rounded-full text-sm font-semibold">
                    Level {stats.contributor.level}
                  </span>
                  {stats.contributor.activity_streak > 0 && (
                    <span className="px-3 py-1 bg-orange-100 text-orange-600 rounded-full text-sm font-semibold">
                      🔥 {stats.contributor.activity_streak} day streak
                    </span>
                  )}
                  {stats.contributor.preferred_work_hours && (
                    <span className="px-3 py-1 bg-purple-100 text-purple-600 rounded-full text-sm">
                      🌙 {stats.contributor.preferred_work_hours} person
                    </span>
                  )}
                </div>
                <div className="mt-3">
                  <div className="text-sm text-gray-600">
                    <strong>XP:</strong> {stats.contributor.experience_points.toLocaleString()} / {((stats.contributor.level + 1) * 1000).toLocaleString()}
                  </div>
                  <div className="w-64 bg-gray-200 rounded-full h-3 mt-1">
                    <div
                      className="bg-gradient-to-r from-blue-500 to-purple-600 h-3 rounded-full"
                      style={{
                        width: `${(stats.contributor.experience_points % 1000) / 10}%`
                      }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
            
            <button
              onClick={handleAwardBadges}
              disabled={awardingBadges}
              className="px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:shadow-lg transition-all disabled:opacity-50"
            >
              {awardingBadges ? 'Awarding...' : '🏆 Check for New Badges'}
            </button>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Total Score</p>
                <p className="text-3xl font-bold text-blue-600">{stats.contributor.total_score.toLocaleString()}</p>
              </div>
              <div className="text-4xl">🏆</div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Commits</p>
                <p className="text-3xl font-bold text-green-600">{stats.metrics.total_commits}</p>
                <p className="text-xs text-gray-500 mt-1">
                  {stats.metrics.recent_commits_30d} in last 30 days
                </p>
              </div>
              <div className="text-4xl">💻</div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Issues Closed</p>
                <p className="text-3xl font-bold text-purple-600">{stats.metrics.total_issues_closed}</p>
              </div>
              <div className="text-4xl">🐛</div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">PR Reviews</p>
                <p className="text-3xl font-bold text-orange-600">{stats.metrics.total_prs_reviewed}</p>
              </div>
              <div className="text-4xl">👀</div>
            </div>
          </div>
        </div>

        {/* Burnout Analysis */}
        {burnout && (
          <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center gap-2">
              <span>🧠</span>
              <span>Burnout Risk Analysis</span>
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div className={`p-4 rounded-lg ${getBurnoutColor(burnout.risk_level)}`}>
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-2xl">{getBurnoutEmoji(burnout.risk_level)}</span>
                  <span className="font-semibold">Risk Level: {burnout.risk_level.toUpperCase()}</span>
                </div>
                <div className="text-3xl font-bold">{(burnout.risk_score * 100).toFixed(0)}%</div>
              </div>

              <div className="col-span-2 bg-gray-50 p-4 rounded-lg">
                <h3 className="font-semibold text-gray-800 mb-2">Recommendations:</h3>
                {burnout.recommendations && burnout.recommendations.length > 0 ? (
                  <ul className="space-y-2">
                    {burnout.recommendations.map((rec, idx) => (
                      <li key={idx} className="text-sm text-gray-700 flex items-start gap-2">
                        <span className="text-blue-500">→</span>
                        <span>{rec}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-gray-600">✅ No concerns detected. Keep up the great work!</p>
                )}
              </div>
            </div>

            {burnout.weekly_activity && burnout.weekly_activity.length > 0 && (
              <div className="mt-4">
                <h3 className="font-semibold text-gray-800 mb-2">Weekly Activity Pattern:</h3>
                <div className="flex items-end gap-2 h-32">
                  {burnout.weekly_activity.map((count, idx) => {
                    const maxCount = Math.max(...burnout.weekly_activity);
                    const height = (count / maxCount) * 100;
                    return (
                      <div key={idx} className="flex-1 flex flex-col items-center">
                        <div
                          className="w-full bg-blue-500 rounded-t transition-all hover:bg-blue-600"
                          style={{ height: `${height}%` }}
                          title={`Week ${idx + 1}: ${count} activities`}
                        ></div>
                        <span className="text-xs text-gray-500 mt-1">W{idx + 1}</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Badges */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">🏅 Badges Earned</h2>
          {stats.badges && stats.badges.length > 0 ? (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {stats.badges.map((badge, idx) => (
                <div
                  key={idx}
                  className="border border-gray-200 rounded-lg p-4 text-center hover:shadow-md transition-shadow"
                >
                  <div className="text-4xl mb-2">
                    {badge.badge_type === 'early_bird' && '🌅'}
                    {badge.badge_type === 'night_owl' && '🦉'}
                    {badge.badge_type === 'bug_hunter' && '🐛'}
                    {badge.badge_type === 'code_reviewer' && '👀'}
                    {badge.badge_type === 'streak_master' && '🔥'}
                    {badge.badge_type === 'team_player' && '🤝'}
                  </div>
                  <h3 className="font-semibold text-gray-800 text-sm mb-1">
                    {badge.badge_type.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                  </h3>
                  <p className="text-xs text-gray-600">{badge.description}</p>
                  <p className="text-xs text-gray-400 mt-2">
                    {new Date(badge.earned_date).toLocaleDateString()}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <div className="text-6xl mb-4">🎯</div>
              <p>No badges earned yet. Keep contributing to earn badges!</p>
            </div>
          )}
        </div>

        {/* Skills */}
        {stats.contributor.skill_tags && stats.contributor.skill_tags.length > 0 && (
          <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">💡 Skills & Expertise</h2>
            <div className="flex flex-wrap gap-2">
              {stats.contributor.skill_tags.map((skill, idx) => (
                <span
                  key={idx}
                  className="px-3 py-1 bg-gradient-to-r from-blue-100 to-purple-100 text-blue-700 rounded-full text-sm font-medium"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Repositories Contributed */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">📁 Repositories ({stats.metrics.repositories_count})</h2>
          <p className="text-gray-600 mb-2">Active collaborations: {stats.metrics.collaborations_count}</p>
        </div>
      </div>
    </div>
  );
};

export default ContributorStats;

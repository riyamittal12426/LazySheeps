import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link, useSearchParams } from 'react-router-dom';
import Leaderboard from '../components/Leaderboard';
import CollaborationNetwork from '../components/CollaborationNetwork';
import CommitsAnalytics from '../components/CommitsAnalytics';
import ContributorCommitSummaries from '../components/ContributorCommitSummaries';

const EnhancedDashboard = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [stats, setStats] = useState(null);
  const [trends, setTrends] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState(searchParams.get('tab') || 'overview');

  // Update URL when tab changes
  useEffect(() => {
    if (activeTab !== 'overview') {
      setSearchParams({ tab: activeTab });
    } else {
      setSearchParams({});
    }
  }, [activeTab, setSearchParams]);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [statsRes, trendsRes] = await Promise.all([
        axios.get('http://localhost:8000/api/dashboard/stats/'),
        axios.get('http://localhost:8000/api/dashboard/trends/?days=30'),
      ]);
      
      setStats(statsRes.data);
      setTrends(trendsRes.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <h1 className="text-4xl font-bold mb-2">🚀 Katalyst Analytics</h1>
          <p className="text-blue-100 text-lg">AI-Powered Developer Insights & Team Analytics</p>
          
          {/* Stats Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-8">
            <div className="bg-white/10 backdrop-blur-md rounded-lg p-4 border border-white/20">
              <div className="text-3xl font-bold">{stats?.totals?.contributors || 0}</div>
              <div className="text-blue-100 text-sm mt-1">Contributors</div>
              <div className="text-xs text-blue-200 mt-1">
                {stats?.totals?.active_contributors || 0} active
              </div>
            </div>
            
            <div className="bg-white/10 backdrop-blur-md rounded-lg p-4 border border-white/20">
              <div className="text-3xl font-bold">{stats?.totals?.repositories || 0}</div>
              <div className="text-blue-100 text-sm mt-1">Repositories</div>
              <div className="text-xs text-blue-200 mt-1">Tracked projects</div>
            </div>
            
            <div className="bg-white/10 backdrop-blur-md rounded-lg p-4 border border-white/20">
              <div className="text-3xl font-bold">{stats?.totals?.commits?.toLocaleString() || 0}</div>
              <div className="text-blue-100 text-sm mt-1">Total Commits</div>
              <div className="text-xs text-blue-200 mt-1">Code contributions</div>
            </div>
            
            <div className="bg-white/10 backdrop-blur-md rounded-lg p-4 border border-white/20">
              <div className="text-3xl font-bold">{stats?.totals?.issues || 0}</div>
              <div className="text-blue-100 text-sm mt-1">Issues Resolved</div>
              <div className="text-xs text-blue-200 mt-1">Problem solutions</div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs Navigation */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="bg-white rounded-lg shadow-sm p-1 flex gap-2 overflow-x-auto">
          {['overview', 'summaries', 'commits', 'leaderboard', 'collaboration', 'insights'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-all whitespace-nowrap ${
                activeTab === tab
                  ? 'bg-blue-500 text-white shadow-md'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              {tab === 'summaries' ? 'Commit Summaries' : tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Content Area */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-12">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Top Repositories */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                <span>⭐</span>
                <span>Top Repositories by Health</span>
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {stats?.top_repositories?.map((repo) => (
                  <Link
                    key={repo.id}
                    to={`/repositories/${repo.id}`}
                    className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-center gap-3 mb-3">
                      <img
                        src={repo.avatar_url}
                        alt={repo.name}
                        className="w-12 h-12 rounded-lg border border-gray-200"
                      />
                      <div className="flex-1">
                        <h4 className="font-semibold text-gray-800 truncate">{repo.name}</h4>
                        <div className="flex items-center gap-2 mt-1">
                          <span className="text-xs text-gray-500">Health:</span>
                          <div className="flex-1 bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-green-500 h-2 rounded-full"
                              style={{ width: `${repo.health_score}%` }}
                            ></div>
                          </div>
                          <span className="text-xs font-semibold text-green-600">
                            {Math.round(repo.health_score)}%
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-4 text-sm text-gray-600">
                      <span>⭐ {repo.stars}</span>
                    </div>
                  </Link>
                ))}
              </div>
            </div>

            {/* Recent Activity */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                <span>📊</span>
                <span>Recent Activity</span>
              </h3>
              <div className="space-y-3">
                {stats?.recent_activities?.map((activity, idx) => (
                  <div key={idx} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                    <img
                      src={activity.contributor__avatar_url}
                      alt={activity.contributor__username}
                      className="w-10 h-10 rounded-full border-2 border-gray-200"
                    />
                    <div className="flex-1">
                      <p className="text-sm text-gray-800">
                        <span className="font-semibold">{activity.contributor__username}</span>
                        {' '}{activity.activity_type === 'commit' ? 'committed to' : 'opened issue in'}
                        {' '}<span className="font-semibold">{activity.repository__name}</span>
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        {new Date(activity.timestamp).toLocaleDateString()} at{' '}
                        {new Date(activity.timestamp).toLocaleTimeString()}
                      </p>
                    </div>
                    <span className={`px-2 py-1 rounded text-xs ${
                      activity.activity_type === 'commit'
                        ? 'bg-blue-100 text-blue-600'
                        : 'bg-green-100 text-green-600'
                    }`}>
                      {activity.activity_type}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'summaries' && (
          <div>
            <ContributorCommitSummaries />
          </div>
        )}

        {activeTab === 'commits' && (
          <div>
            <CommitsAnalytics />
          </div>
        )}

        {activeTab === 'leaderboard' && (
          <div>
            <Leaderboard />
          </div>
        )}

        {activeTab === 'collaboration' && (
          <div>
            <CollaborationNetwork />
          </div>
        )}

        {activeTab === 'insights' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Activity Trends Chart */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-xl font-bold text-gray-800 mb-4">📈 Activity Trends (30 Days)</h3>
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Total Commits:</span>
                  <span className="font-semibold text-blue-600">
                    {trends?.commits?.reduce((sum, item) => sum + item.count, 0) || 0}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Total Issues:</span>
                  <span className="font-semibold text-green-600">
                    {trends?.issues?.reduce((sum, item) => sum + item.count, 0) || 0}
                  </span>
                </div>
                <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                  <p className="text-sm text-gray-700">
                    💡 <strong>Insight:</strong> Your team is maintaining consistent activity with {' '}
                    {stats?.totals?.active_contributors || 0} active contributors in the last 30 days.
                  </p>
                </div>
              </div>
            </div>

            {/* Quick Stats */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-xl font-bold text-gray-800 mb-4">⚡ Quick Stats</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-3 bg-purple-50 rounded-lg">
                  <div>
                    <p className="text-sm text-gray-600">Average Commits/Day</p>
                    <p className="text-2xl font-bold text-purple-600">
                      {trends?.commits ? Math.round(
                        trends.commits.reduce((sum, item) => sum + item.count, 0) / 30
                      ) : 0}
                    </p>
                  </div>
                  <div className="text-4xl">💻</div>
                </div>

                <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                  <div>
                    <p className="text-sm text-gray-600">Active Streak</p>
                    <p className="text-2xl font-bold text-green-600">
                      {Math.max(...(stats?.top_repositories?.map(r => r.health_score) || [0]))}%
                    </p>
                  </div>
                  <div className="text-4xl">🔥</div>
                </div>

                <div className="flex items-center justify-between p-3 bg-orange-50 rounded-lg">
                  <div>
                    <p className="text-sm text-gray-600">Team Size</p>
                    <p className="text-2xl font-bold text-orange-600">
                      {stats?.totals?.contributors || 0}
                    </p>
                  </div>
                  <div className="text-4xl">👥</div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default EnhancedDashboard;

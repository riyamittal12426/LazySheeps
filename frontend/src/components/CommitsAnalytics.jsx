import { useState, useEffect } from 'react';
import axios from 'axios';

const CommitsAnalytics = () => {
  const [commits, setCommits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({
    repo_id: '',
    contributor_id: '',
    limit: 50
  });
  const [repositories, setRepositories] = useState([]);

  useEffect(() => {
    fetchRepositories();
    fetchCommits();
  }, []);

  const fetchRepositories = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/repositories/import-status/');
      setRepositories(response.data.repositories);
    } catch (err) {
      console.error('Error fetching repositories:', err);
    }
  };

  const fetchCommits = async () => {
    setLoading(true);
    setError('');
    
    try {
      const params = new URLSearchParams();
      if (filters.repo_id) params.append('repo_id', filters.repo_id);
      if (filters.contributor_id) params.append('contributor_id', filters.contributor_id);
      params.append('limit', filters.limit);

      const response = await axios.get(`http://localhost:8000/api/commits/analytics/?${params}`);
      setCommits(response.data.commits);
    } catch (err) {
      setError('Failed to load commits');
      console.error('Error fetching commits:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({ ...prev, [field]: value }));
  };

  const applyFilters = () => {
    fetchCommits();
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  };

  const getCommitColor = (additions, deletions) => {
    const total = additions + deletions;
    if (total > 500) return 'border-l-4 border-purple-500';
    if (total > 200) return 'border-l-4 border-blue-500';
    if (total > 50) return 'border-l-4 border-green-500';
    return 'border-l-4 border-gray-400';
  };

  if (loading && commits.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Commit Analytics</h2>
        <p className="text-gray-600">Track all commits across repositories with AI-powered summaries</p>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Repository Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Repository
            </label>
            <select
              value={filters.repo_id}
              onChange={(e) => handleFilterChange('repo_id', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Repositories</option>
              {repositories.map(repo => (
                <option key={repo.id} value={repo.id}>
                  {repo.name}
                </option>
              ))}
            </select>
          </div>

          {/* Limit Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Limit
            </label>
            <select
              value={filters.limit}
              onChange={(e) => handleFilterChange('limit', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="25">25 commits</option>
              <option value="50">50 commits</option>
              <option value="100">100 commits</option>
              <option value="200">200 commits</option>
            </select>
          </div>

          {/* Apply Button */}
          <div className="flex items-end">
            <button
              onClick={applyFilters}
              className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Apply Filters
            </button>
          </div>

          {/* Stats */}
          <div className="flex items-end">
            <div className="w-full px-4 py-2 bg-gradient-to-r from-indigo-50 to-blue-50 rounded-lg">
              <p className="text-sm text-gray-600">Total Commits</p>
              <p className="text-2xl font-bold text-indigo-600">{commits.length}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Commits List */}
      {commits.length === 0 && !loading ? (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
          <svg className="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <h3 className="text-lg font-medium text-gray-900 mb-1">No commits found</h3>
          <p className="text-gray-500">Import a repository to see commits here</p>
        </div>
      ) : (
        <div className="space-y-4">
          {commits.map((commit) => (
            <div
              key={commit.id}
              className={`bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow ${getCommitColor(commit.additions, commit.deletions)}`}
            >
              <div className="p-5">
                {/* Commit Header */}
                <div className="flex items-start gap-4 mb-3">
                  {/* Contributor Avatar */}
                  <img
                    src={commit.contributor.avatar_url || 'https://via.placeholder.com/40'}
                    alt={commit.contributor.username}
                    className="w-10 h-10 rounded-full border-2 border-gray-200"
                  />

                  <div className="flex-1 min-w-0">
                    {/* Contributor & Repository */}
                    <div className="flex items-center gap-2 mb-1">
                      <a
                        href={commit.contributor.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm font-semibold text-gray-900 hover:text-blue-600 transition"
                      >
                        {commit.contributor.username}
                      </a>
                      <span className="text-gray-400">•</span>
                      <a
                        href={commit.repository.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-gray-600 hover:text-blue-600 transition"
                      >
                        {commit.repository.name}
                      </a>
                    </div>

                    {/* Commit Summary */}
                    <p className="text-gray-800 mb-2 leading-relaxed">
                      {commit.summary}
                    </p>

                    {/* Commit Stats */}
                    <div className="flex items-center gap-4 text-sm">
                      <span className="inline-flex items-center gap-1 text-green-600">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                        </svg>
                        +{commit.additions}
                      </span>
                      <span className="inline-flex items-center gap-1 text-red-600">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
                        </svg>
                        -{commit.deletions}
                      </span>
                      <span className="inline-flex items-center gap-1 text-gray-600">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        {commit.files_changed} files
                      </span>
                      {commit.churn > 50 && (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-orange-100 text-orange-700 rounded-full text-xs font-medium">
                          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                          </svg>
                          High Churn
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Timestamp & Link */}
                  <div className="flex flex-col items-end gap-2">
                    <span className="text-xs text-gray-500 whitespace-nowrap">
                      {formatDate(commit.committed_at)}
                    </span>
                    <a
                      href={commit.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 text-xs text-blue-600 hover:text-blue-700 transition"
                    >
                      View on GitHub
                      <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                      </svg>
                    </a>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Loading More */}
      {loading && commits.length > 0 && (
        <div className="flex justify-center mt-6">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      )}
    </div>
  );
};

export default CommitsAnalytics;

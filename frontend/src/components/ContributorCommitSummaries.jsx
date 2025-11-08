import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import axios from 'axios';
import { 
  UserCircleIcon, 
  CodeBracketIcon,
  PlusIcon,
  MinusIcon,
  DocumentTextIcon,
  CalendarIcon,
  ArrowTopRightOnSquareIcon,
  ChevronDownIcon,
  ChevronUpIcon,
} from '@heroicons/react/24/outline';

const ContributorCommitSummaries = () => {
  const [searchParams] = useSearchParams();
  const repoId = searchParams.get('repo_id');
  
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);
  const [expandedContributors, setExpandedContributors] = useState({});
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchCommitSummaries();
  }, [repoId]);

  const fetchCommitSummaries = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const url = repoId 
        ? `http://localhost:8000/api/commits/contributor-summaries/?repo_id=${repoId}`
        : 'http://localhost:8000/api/commits/contributor-summaries/';
      
      const response = await axios.get(url);
      
      if (response.data.success) {
        setData(response.data);
        // Expand first contributor by default
        if (response.data.contributors.length > 0) {
          setExpandedContributors({ [response.data.contributors[0].contributor.id]: true });
        }
      }
    } catch (err) {
      console.error('Failed to fetch commit summaries:', err);
      setError(err.response?.data?.error || 'Failed to load commit summaries');
    } finally {
      setLoading(false);
    }
  };

  const toggleContributor = (contributorId) => {
    setExpandedContributors(prev => ({
      ...prev,
      [contributorId]: !prev[contributorId]
    }));
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

  const getCommitSizeColor = (additions, deletions) => {
    const total = additions + deletions;
    if (total < 50) return 'text-green-400';
    if (total < 200) return 'text-yellow-400';
    return 'text-orange-400';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500"></div>
          <p className="mt-4 text-gray-400">Loading commit summaries...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-500/10 border border-red-500/50 rounded-lg p-6 text-center">
        <p className="text-red-400 text-lg">{error}</p>
        <button 
          onClick={fetchCommitSummaries}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
        >
          Try Again
        </button>
      </div>
    );
  }

  if (!data || data.contributors.length === 0) {
    return (
      <div className="bg-white/5 border border-white/10 rounded-lg p-12 text-center">
        <CodeBracketIcon className="w-16 h-16 mx-auto text-gray-500 mb-4" />
        <h3 className="text-xl font-semibold text-white mb-2">No Commits Found</h3>
        <p className="text-gray-400">Import a repository to see contributor commit summaries</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600/20 to-blue-600/20 border border-purple-500/30 rounded-lg p-6">
        <h2 className="text-3xl font-bold text-white mb-2">
          📝 Commit Summaries by Contributor
        </h2>
        <p className="text-gray-300">
          AI-powered analysis of each team member's contributions and work
        </p>
        <div className="mt-4 flex items-center gap-6 text-sm">
          <div className="flex items-center gap-2">
            <UserCircleIcon className="w-5 h-5 text-purple-400" />
            <span className="text-gray-300">{data.total_contributors} Contributors</span>
          </div>
          <div className="flex items-center gap-2">
            <CodeBracketIcon className="w-5 h-5 text-blue-400" />
            <span className="text-gray-300">
              {data.contributors.reduce((sum, c) => sum + c.stats.total_commits, 0)} Total Commits
            </span>
          </div>
        </div>
      </div>

      {/* Contributors List */}
      <div className="space-y-4">
        {data.contributors.map((item, index) => {
          const isExpanded = expandedContributors[item.contributor.id];
          const { contributor, stats, work_summary, recent_commits } = item;

          return (
            <div 
              key={contributor.id}
              className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg overflow-hidden hover:border-purple-500/30 transition-all"
            >
              {/* Contributor Header */}
              <div 
                className="p-6 cursor-pointer hover:bg-white/5 transition-colors"
                onClick={() => toggleContributor(contributor.id)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-4 flex-1">
                    {/* Avatar */}
                    <div className="relative">
                      {contributor.avatar_url ? (
                        <img 
                          src={contributor.avatar_url} 
                          alt={contributor.username}
                          className="w-16 h-16 rounded-full border-2 border-purple-500"
                        />
                      ) : (
                        <div className="w-16 h-16 rounded-full bg-gradient-to-br from-purple-600 to-blue-600 flex items-center justify-center border-2 border-purple-500">
                          <span className="text-xl font-bold text-white">
                            {contributor.username.charAt(0).toUpperCase()}
                          </span>
                        </div>
                      )}
                      <div className="absolute -bottom-1 -right-1 bg-purple-600 text-white text-xs font-bold rounded-full w-8 h-8 flex items-center justify-center border-2 border-gray-900">
                        #{index + 1}
                      </div>
                    </div>

                    {/* Info */}
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-xl font-bold text-white">
                          {contributor.username}
                        </h3>
                        {contributor.url && (
                          <a
                            href={contributor.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-purple-400 hover:text-purple-300 transition-colors"
                            onClick={(e) => e.stopPropagation()}
                          >
                            <ArrowTopRightOnSquareIcon className="w-4 h-4" />
                          </a>
                        )}
                      </div>

                      {/* Stats Row */}
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
                        <div className="bg-white/5 rounded-lg p-2">
                          <div className="text-xs text-gray-400">Commits</div>
                          <div className="text-lg font-bold text-white">{stats.total_commits}</div>
                        </div>
                        <div className="bg-white/5 rounded-lg p-2">
                          <div className="text-xs text-gray-400">Additions</div>
                          <div className="text-lg font-bold text-green-400">+{stats.total_additions}</div>
                        </div>
                        <div className="bg-white/5 rounded-lg p-2">
                          <div className="text-xs text-gray-400">Deletions</div>
                          <div className="text-lg font-bold text-red-400">-{stats.total_deletions}</div>
                        </div>
                        <div className="bg-white/5 rounded-lg p-2">
                          <div className="text-xs text-gray-400">Files Changed</div>
                          <div className="text-lg font-bold text-blue-400">{stats.total_files_changed}</div>
                        </div>
                      </div>

                      {/* Work Summary */}
                      <div className="bg-gradient-to-r from-purple-600/10 to-blue-600/10 border border-purple-500/20 rounded-lg p-4">
                        <div className="flex items-start gap-2">
                          <DocumentTextIcon className="w-5 h-5 text-purple-400 flex-shrink-0 mt-0.5" />
                          <div>
                            <div className="text-xs font-semibold text-purple-400 uppercase mb-1">
                              AI Work Summary
                            </div>
                            <p className="text-sm text-gray-300 leading-relaxed">
                              {work_summary}
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Expand/Collapse Button */}
                  <button 
                    className="ml-4 p-2 hover:bg-white/10 rounded-lg transition-colors flex-shrink-0"
                  >
                    {isExpanded ? (
                      <ChevronUpIcon className="w-6 h-6 text-gray-400" />
                    ) : (
                      <ChevronDownIcon className="w-6 h-6 text-gray-400" />
                    )}
                  </button>
                </div>
              </div>

              {/* Expanded Content - Recent Commits */}
              {isExpanded && (
                <div className="border-t border-white/10 bg-black/20 p-6">
                  <h4 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    <CodeBracketIcon className="w-5 h-5 text-purple-400" />
                    Recent Commits
                  </h4>
                  
                  <div className="space-y-3">
                    {recent_commits.map((commit) => (
                      <div 
                        key={commit.id}
                        className="bg-white/5 border border-white/10 rounded-lg p-4 hover:border-purple-500/30 transition-colors"
                      >
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex-1">
                            {/* Commit Summary */}
                            <p className="text-white font-medium mb-2 leading-relaxed">
                              {commit.summary}
                            </p>
                            
                            {/* Commit Stats */}
                            <div className="flex items-center gap-4 text-sm">
                              <span className="flex items-center gap-1 text-green-400">
                                <PlusIcon className="w-4 h-4" />
                                {commit.additions}
                              </span>
                              <span className="flex items-center gap-1 text-red-400">
                                <MinusIcon className="w-4 h-4" />
                                {commit.deletions}
                              </span>
                              <span className={`flex items-center gap-1 ${getCommitSizeColor(commit.additions, commit.deletions)}`}>
                                <DocumentTextIcon className="w-4 h-4" />
                                {commit.files_changed} files
                              </span>
                              <span className="flex items-center gap-1 text-gray-400">
                                <CalendarIcon className="w-4 h-4" />
                                {formatDate(commit.committed_at)}
                              </span>
                            </div>

                            {/* Repository */}
                            {commit.repository && (
                              <div className="mt-2 text-xs text-gray-500">
                                in <span className="text-purple-400">{commit.repository.name}</span>
                              </div>
                            )}
                          </div>

                          {/* GitHub Link */}
                          {commit.url && (
                            <a
                              href={commit.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="flex-shrink-0 p-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
                              title="View on GitHub"
                            >
                              <ArrowTopRightOnSquareIcon className="w-4 h-4" />
                            </a>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ContributorCommitSummaries;

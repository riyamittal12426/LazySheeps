import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useData } from '../context/DataContext';
import ImportRepository from '../components/ImportRepository';
import { 
  ChartBarIcon, 
  UserGroupIcon, 
  FolderIcon,
  CodeBracketIcon,
  CheckCircleIcon,
  ArrowPathIcon,
  CalendarIcon,
  SparklesIcon,
  ArrowTopRightOnSquareIcon,
  FireIcon,
  BoltIcon,
  ChartPieIcon,
  AcademicCapIcon,
  RocketLaunchIcon,
  CpuChipIcon,
  BeakerIcon,
} from '@heroicons/react/24/outline';
import { 
  ChartBarSquareIcon,
} from '@heroicons/react/20/solid';

// Format dates nicely
const formatDate = (dateString) => {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-US', { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric' 
  }).format(date);
};

export default function Dashboard() {
  const { isLoading, error, contributors, repositories } = useData();
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    totalRepos: 0,
    totalContributors: 0,
    totalCommits: 0,
    totalIssues: 0,
  });

  // Navigation cards configuration
  const navigationCards = [
    {
      title: 'Analytics',
      description: 'View comprehensive analytics and insights',
      icon: ChartPieIcon,
      gradient: 'from-purple-500 to-pink-500',
      route: '/app/analytics',
      stats: `${stats.totalCommits} commits analyzed`,
      iconBg: 'bg-purple-100',
      iconColor: 'text-purple-600',
    },
    {
      title: 'Contributors',
      description: 'Manage and view all team contributors',
      icon: UserGroupIcon,
      gradient: 'from-blue-500 to-cyan-500',
      route: '/app/contributors',
      stats: `${stats.totalContributors} active members`,
      iconBg: 'bg-white-600',
      iconColor: 'text-blue-600',
    },
    {
      title: 'Repositories',
      description: 'Browse and manage your repositories',
      icon: FolderIcon,
      gradient: 'from-indigo-500 to-purple-500',
      route: '/app/repositories',
      stats: `${stats.totalRepos} repositories`,
      iconBg: 'bg-yellow-100',
      iconColor: 'text-yellow-600',
    },
    {
      title: 'Contributor Stats',
      description: 'Detailed statistics for each contributor',
      icon: ChartBarSquareIcon,
      gradient: 'from-green-500 to-emerald-500',
      route: '/app/contributor-stats',
      stats: 'Performance metrics',
      iconBg: 'bg-green-100',
      iconColor: 'text-green-600',
    },
    {
      title: 'Enhanced Dashboard',
      description: 'Advanced visualization and reports',
      icon: RocketLaunchIcon,
      gradient: 'from-orange-500 to-red-500',
      route: '/app/enhanced-dashboard',
      stats: 'Advanced insights',
      iconBg: 'bg-orange-100',
      iconColor: 'text-orange-600',
    },
    {
      title: 'Llama Chat',
      description: 'AI-powered assistant for your projects',
      icon: CpuChipIcon,
      gradient: 'from-teal-500 to-green-500',
      route: '/app/llama-chat',
      stats: 'Ask anything',
      iconBg: 'bg-red-100',
      iconColor: 'text-orange-600',
    },
    {
      title: 'Leaderboard',
      description: 'Top performers and rankings',
      icon: AcademicCapIcon,
      gradient: 'from-yellow-500 to-orange-500',
      route: '/app/leaderboard',
      stats: 'Team rankings',
      iconBg: 'bg-yellow-100',
      iconColor: 'text-yellow-600',
    },
    {
      title: 'Test Features',
      description: 'Experimental features and testing',
      icon: BeakerIcon,
      gradient: 'from-pink-500 to-rose-500',
      route: '/app/test',
      stats: 'Try new features',
      iconBg: 'bg-pink-100',
      iconColor: 'text-pink-600',
    },
  ];

  // Calculate stats
  useEffect(() => {
    if (!isLoading && contributors && repositories) {
      const totalCommits = contributors.reduce(
        (total, contributor) => total + contributor.works.reduce(
          (acc, work) => acc + (work.commits?.length || 0), 0
        ), 0
      );

      const totalIssues = contributors.reduce(
        (total, contributor) => total + contributor.works.reduce(
          (acc, work) => acc + (work.issues?.length || 0), 0
        ), 0
      );

      setStats({
        totalRepos: repositories.length,
        totalContributors: contributors.length,
        totalCommits,
        totalIssues,
      });
    }
  }, [isLoading, contributors, repositories]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          <div className="relative mx-auto mb-4 h-16 w-16">
            <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-indigo-600"></div>
          </div>
          <h3 className="text-lg font-semibold text-gray-900">Loading Dashboard</h3>
          <p className="text-sm text-gray-600 mt-2">Preparing your insights...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto mt-12 min-h-screen p-8 bg-gray-50">
        <div className="bg-white border-2 border-red-200 rounded-lg p-6 text-center shadow-lg">
          <div className="text-red-500 text-4xl mb-3">⚠️</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Failed to Load Dashboard</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="inline-flex items-center px-4 py-2 rounded-lg transition-all duration-300 border-2 border-red-500 bg-white text-red-600 hover:bg-red-50"
          >
            <ArrowPathIcon className="h-4 w-4 mr-2" />
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Header */}
      <div className="relative overflow-hidden min-h-[400px] bg-gradient-to-r from-indigo-600 to-purple-600">
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="text-center">
            <div className="flex items-center justify-center mb-4">
              <SparklesIcon className="h-12 w-12 text-white" />
            </div>
            <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
              Welcome to Your Dashboard
            </h1>
            <p className="text-lg text-indigo-100 mb-6 max-w-2xl mx-auto">
              Explore powerful features to manage your repositories, analyze contributions, and collaborate with your team
            </p>
            <div className="flex items-center justify-center gap-4">
              <div className="flex items-center gap-2 px-4 py-2 rounded-full border-2 border-white/30 bg-white/10 backdrop-blur-sm">
                <CalendarIcon className="h-5 w-5 text-white" />
                <span className="text-sm font-medium text-white">{formatDate(new Date())}</span>
              </div>
              <ImportRepository onImportSuccess={() => window.location.reload()} />
            </div>
          </div>
        </div>
      </div>

      {/* Stats Section */}
      <div className="w-full px-4 sm:px-6 lg:px-8 py-12">
        {/* Quick Stats */}
        <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          {/* Repositories Card */}
          <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-200 hover:shadow-xl transition-all duration-300">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Repositories</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{stats.totalRepos}</p>
                <p className="text-xs text-indigo-600 mt-2 flex items-center font-semibold">
                  <FireIcon className="h-4 w-4 mr-1" />
                  {stats.totalRepos > 0 ? 'Active Projects' : 'Get Started'}
                </p>
              </div>
              <div className="h-16 w-16 bg-gradient-to-br from-indigo-500 to-purple-500 rounded-2xl flex items-center justify-center">
                <FolderIcon className="h-8 w-8 text-white" />
              </div>
            </div>
          </div>

          {/* Contributors Card */}
          <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-200 hover:shadow-xl transition-all duration-300">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Contributors</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{stats.totalContributors}</p>
                <p className="text-xs text-green-600 mt-2 flex items-center font-semibold">
                  <BoltIcon className="h-4 w-4 mr-1" />
                  Team Members
                </p>
              </div>
              <div className="h-16 w-16 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-2xl flex items-center justify-center">
                <UserGroupIcon className="h-8 w-8 text-white" />
              </div>
            </div>
          </div>

          {/* Commits Card */}
          <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-200 hover:shadow-xl transition-all duration-300">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Commits</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{stats.totalCommits.toLocaleString()}</p>
                <p className="text-xs text-blue-600 mt-2 flex items-center font-semibold">
                  <SparklesIcon className="h-4 w-4 mr-1" />
                  All Time
                </p>
              </div>
              <div className="h-16 w-16 bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center">
                <CodeBracketIcon className="h-8 w-8 text-white" />
              </div>
            </div>
          </div>

          {/* Issues Card */}
          <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-200 hover:shadow-xl transition-all duration-300">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Issues Resolved</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{stats.totalIssues.toLocaleString()}</p>
                <p className="text-xs text-green-600 mt-2 flex items-center font-semibold">
                  <CheckCircleIcon className="h-4 w-4 mr-1" />
                  Completed
                </p>
              </div>
              <div className="h-16 w-16 bg-gradient-to-br from-green-500 to-emerald-500 rounded-2xl flex items-center justify-center">
                <CheckCircleIcon className="h-8 w-8 text-white" />
              </div>
            </div>
          </div>
        </div>

        {/* Section Title */}
        <div className="max-w-7xl mx-auto text-center mb-10">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Explore Features</h2>
          <p className="text-gray-600">Click on any card to navigate to that section</p>
        </div>

        {/* Navigation Cards Grid */}
        <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {navigationCards.map((card, index) => {
            const Icon = card.icon;
            return (
              <div
                key={index}
                onClick={() => navigate(card.route)}
                className="bg-white rounded-2xl p-6 cursor-pointer shadow-lg border border-gray-200 hover:shadow-xl hover:scale-105 transition-all duration-300"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className={`${card.iconBg} p-3 rounded-xl`}>
                    <Icon className={`h-6 w-6 ${card.iconColor}`} />
                  </div>
                  <ArrowTopRightOnSquareIcon className="h-5 w-5 text-gray-400" />
                </div>
                
                <h3 className="text-lg font-bold text-gray-900 mb-2">
                  {card.title}
                </h3>
                
                <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                  {card.description}
                </p>
                
                <div className="flex items-center text-xs text-gray-500">
                  <div className={`h-2 w-2 rounded-full ${card.iconBg} mr-2`}></div>
                  {card.stats}
                </div>
              </div>
            );
          })}
        </div>

        {/* Quick Actions Banner */}
        <div className="max-w-7xl mx-auto mt-12 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-2xl p-8 text-center shadow-lg">
          <h3 className="text-2xl font-bold text-white mb-3">Ready to Get Started?</h3>
          <p className="text-indigo-100 mb-6 max-w-2xl mx-auto">
            Import your first repository to unlock powerful analytics and insights about your team's productivity
          </p>
          <div className="flex items-center justify-center gap-4">
            <ImportRepository onImportSuccess={() => window.location.reload()} />
            <Link
              to="/app/repositories"
              className="inline-flex items-center px-6 py-3 rounded-lg font-semibold transition-all duration-300 bg-white text-indigo-600 hover:bg-indigo-50"
            >
              <FolderIcon className="h-5 w-5 mr-2" />
              View Repositories
            </Link>
          </div>
        </div>

        {/* Ask About Codebase Input */}
        <div className="max-w-7xl mx-auto mt-12 mb-12">
          <div className="relative">
            <input
              type="text"
              placeholder="Ask about your codebase..."
              className="w-full px-6 py-4 pr-16 rounded-2xl bg-white border border-gray-300 text-gray-700 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent shadow-md transition-all duration-300"
            />
            <button 
              className="absolute right-3 top-1/2 transform -translate-y-1/2 p-3 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 text-white transition-all duration-300 hover:scale-110"
            >
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
              </svg>
            </button>
          </div>
          <p className="text-center text-gray-500 text-sm mt-3">
            Click on any card to navigate to that section
          </p>
        </div>
      </div>
    </div>
  );
}
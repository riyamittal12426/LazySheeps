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
      iconBg: 'bg-blue-100',
      iconColor: 'text-blue-600',
    },
    {
      title: 'Repositories',
      description: 'Browse and manage your repositories',
      icon: FolderIcon,
      gradient: 'from-indigo-500 to-purple-500',
      route: '/app/repositories',
      stats: `${stats.totalRepos} repositories`,
      iconBg: 'bg-indigo-100',
      iconColor: 'text-indigo-600',
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
      iconBg: 'bg-teal-100',
      iconColor: 'text-teal-600',
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
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <h3 className="text-lg font-semibold text-gray-900">Loading Dashboard</h3>
          <p className="text-sm text-gray-500 mt-2">Preparing your insights...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto mt-12">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <div className="text-red-600 text-4xl mb-3">⚠️</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Failed to Load Dashboard</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="inline-flex items-center px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            <ArrowPathIcon className="h-4 w-4 mr-2" />
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-indigo-50">
      {/* Hero Header */}
      <div className="relative overflow-hidden bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600">
        <div className="absolute inset-0 bg-black opacity-10"></div>
        <div className="absolute inset-0" style={{
          backgroundImage: 'url("data:image/svg+xml,%3Csvg width=\'60\' height=\'60\' viewBox=\'0 0 60 60\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cg fill=\'none\' fill-rule=\'evenodd\'%3E%3Cg fill=\'%23ffffff\' fill-opacity=\'0.05\'%3E%3Cpath d=\'M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z\'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")'
        }}></div>
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="text-center">
            <div className="flex items-center justify-center mb-4">
              <SparklesIcon className="h-12 w-12 text-yellow-300 animate-pulse" />
            </div>
            <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
              Welcome to Your Dashboard
            </h1>
            <p className="text-lg text-indigo-100 mb-6 max-w-2xl mx-auto">
              Explore powerful features to manage your repositories, analyze contributions, and collaborate with your team
            </p>
            <div className="flex items-center justify-center gap-4 text-white">
              <div className="flex items-center gap-2 bg-white/20 backdrop-blur-sm px-4 py-2 rounded-full">
                <CalendarIcon className="h-5 w-5" />
                <span className="text-sm font-medium">{formatDate(new Date())}</span>
              </div>
              <ImportRepository onImportSuccess={() => window.location.reload()} />
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6 transform hover:scale-105 transition-all duration-200 hover:shadow-xl">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Repositories</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{stats.totalRepos}</p>
                <p className="text-xs text-green-600 mt-2 flex items-center font-semibold">
                  <FireIcon className="h-4 w-4 mr-1" />
                  {stats.totalRepos > 0 ? 'Active Projects' : 'Get Started'}
                </p>
              </div>
              <div className="h-16 w-16 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg">
                <FolderIcon className="h-8 w-8 text-white" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6 transform hover:scale-105 transition-all duration-200 hover:shadow-xl">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Contributors</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{stats.totalContributors}</p>
                <p className="text-xs text-blue-600 mt-2 flex items-center font-semibold">
                  <BoltIcon className="h-4 w-4 mr-1" />
                  Team Members
                </p>
              </div>
              <div className="h-16 w-16 bg-gradient-to-br from-blue-500 to-cyan-600 rounded-2xl flex items-center justify-center shadow-lg">
                <UserGroupIcon className="h-8 w-8 text-white" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6 transform hover:scale-105 transition-all duration-200 hover:shadow-xl">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Commits</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{stats.totalCommits.toLocaleString()}</p>
                <p className="text-xs text-purple-600 mt-2 flex items-center font-semibold">
                  <SparklesIcon className="h-4 w-4 mr-1" />
                  All Time
                </p>
              </div>
              <div className="h-16 w-16 bg-gradient-to-br from-purple-500 to-pink-600 rounded-2xl flex items-center justify-center shadow-lg">
                <CodeBracketIcon className="h-8 w-8 text-white" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6 transform hover:scale-105 transition-all duration-200 hover:shadow-xl">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Issues Resolved</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{stats.totalIssues.toLocaleString()}</p>
                <p className="text-xs text-green-600 mt-2 flex items-center font-semibold">
                  <CheckCircleIcon className="h-4 w-4 mr-1" />
                  Completed
                </p>
              </div>
              <div className="h-16 w-16 bg-gradient-to-br from-green-500 to-emerald-600 rounded-2xl flex items-center justify-center shadow-lg">
                <CheckCircleIcon className="h-8 w-8 text-white" />
              </div>
            </div>
          </div>
        </div>

        {/* Section Title */}
        <div className="text-center mb-10">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Explore Features</h2>
          <p className="text-gray-600">Click on any card to navigate to that section</p>
        </div>

        {/* Navigation Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {navigationCards.map((card, index) => {
            const Icon = card.icon;
            return (
              <div
                key={index}
                onClick={() => navigate(card.route)}
                className="group relative bg-white rounded-2xl shadow-lg border border-gray-100 p-6 cursor-pointer transform hover:scale-105 transition-all duration-300 hover:shadow-2xl overflow-hidden"
              >
                {/* Gradient Background on Hover */}
                <div className={`absolute inset-0 bg-gradient-to-br ${card.gradient} opacity-0 group-hover:opacity-10 transition-opacity duration-300`}></div>
                
                {/* Content */}
                <div className="relative z-10">
                  <div className="flex items-start justify-between mb-4">
                    <div className={`${card.iconBg} p-3 rounded-xl group-hover:scale-110 transition-transform duration-300`}>
                      <Icon className={`h-6 w-6 ${card.iconColor}`} />
                    </div>
                    <ArrowTopRightOnSquareIcon className="h-5 w-5 text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                  </div>
                  
                  <h3 className="text-lg font-bold text-gray-900 mb-2 group-hover:text-indigo-600 transition-colors">
                    {card.title}
                  </h3>
                  
                  <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                    {card.description}
                  </p>
                  
                  <div className="flex items-center text-xs text-gray-500">
                    <div className={`h-2 w-2 rounded-full bg-gradient-to-r ${card.gradient} mr-2`}></div>
                    {card.stats}
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Quick Actions Banner */}
        <div className="mt-12 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl shadow-xl p-8 text-center">
          <h3 className="text-2xl font-bold text-white mb-3">Ready to Get Started?</h3>
          <p className="text-indigo-100 mb-6 max-w-2xl mx-auto">
            Import your first repository to unlock powerful analytics and insights about your team's productivity
          </p>
          <div className="flex items-center justify-center gap-4">
            <ImportRepository onImportSuccess={() => window.location.reload()} />
            <Link
              to="/app/repositories"
              className="inline-flex items-center px-6 py-3 bg-white text-indigo-600 rounded-lg font-semibold hover:bg-gray-100 transition-colors shadow-lg"
            >
              <FolderIcon className="h-5 w-5 mr-2" />
              View Repositories
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
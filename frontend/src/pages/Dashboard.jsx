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
      <div className="flex items-center justify-center min-h-screen" style={{
        background: 'linear-gradient(135deg, #000000 0%, #0a1128 25%, #001529 50%, #0a1128 75%, #000000 100%)'
      }}>
        <div className="text-center">
          <div className="relative mx-auto mb-4 h-16 w-16">
            <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-[#0095ff]" style={{
              boxShadow: '0 0 30px rgba(0, 149, 255, 0.6)'
            }}></div>
            <div className="absolute inset-0 rounded-full" style={{
              boxShadow: 'inset 0 0 20px rgba(0, 217, 255, 0.4)',
              animation: 'pulse 2s ease-in-out infinite'
            }}></div>
          </div>
          <h3 className="text-lg font-semibold text-white" style={{
            textShadow: '0 0 10px rgba(0, 217, 255, 0.5)'
          }}>Loading Dashboard</h3>
          <p className="text-sm text-gray-400 mt-2">Preparing your insights...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto mt-12 min-h-screen p-8" style={{
        background: 'linear-gradient(135deg, #000000 0%, #0a1128 25%, #001529 50%, #0a1128 75%, #000000 100%)'
      }}>
        <div className="bg-gradient-to-br from-[#1a0000] to-[#000a1f] border-2 border-[#ff0055]/50 rounded-lg p-6 text-center" style={{
          boxShadow: '0 8px 32px rgba(255, 0, 85, 0.3), inset 0 1px 0 rgba(255, 0, 85, 0.1)'
        }}>
          <div className="text-[#ff0055] text-4xl mb-3" style={{
            filter: 'drop-shadow(0 0 10px rgba(255, 0, 85, 0.6))'
          }}>⚠️</div>
          <h3 className="text-lg font-semibold text-white mb-2">Failed to Load Dashboard</h3>
          <p className="text-gray-400 mb-4">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="inline-flex items-center px-4 py-2 rounded-lg transition-all duration-300 border-2 border-[#ff0055] bg-[#ff0055]/20 text-white hover:bg-[#ff0055] hover:border-[#ff3377]"
            style={{
              boxShadow: '0 4px 15px rgba(255, 0, 85, 0.3)'
            }}
          >
            <ArrowPathIcon className="h-4 w-4 mr-2" />
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen" style={{
      background: 'linear-gradient(135deg, #000000 0%, #0a1128 25%, #001529 50%, #0a1128 75%, #000000 100%)',
      backgroundAttachment: 'fixed'
    }}>
      {/* Hero Header */}
      <div className="relative overflow-hidden min-h-[400px]" style={{
        background: 'linear-gradient(135deg, #001529 0%, #003a70 50%, #001529 100%)'
      }}>
        {/* Neural Network Background Image */}
        <div 
          className="absolute inset-0 bg-cover bg-center opacity-30"
          style={{
            backgroundImage: 'url(/images/neural-network.jpg)',
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            filter: 'blur(1px)'
          }}
        ></div>
        
        {/* Neon blue overlay with glow effect */}
        <div className="absolute inset-0" style={{
          background: 'radial-gradient(circle at 50% 50%, rgba(0, 149, 255, 0.15) 0%, transparent 70%)'
        }}></div>
        
        {/* Animated scan lines effect */}
        <div className="absolute inset-0 opacity-10" style={{
          backgroundImage: 'repeating-linear-gradient(0deg, transparent, transparent 2px, #0095ff 2px, #0095ff 4px)',
          animation: 'scan 8s linear infinite'
        }}></div>
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="text-center">
            <div className="flex items-center justify-center mb-4">
              <SparklesIcon className="h-12 w-12 text-[#00d9ff] animate-pulse" style={{
                filter: 'drop-shadow(0 0 20px rgba(0, 217, 255, 0.8))'
              }} />
            </div>
            <h1 className="text-4xl md:text-5xl font-bold text-white mb-4" style={{
              textShadow: '0 0 30px rgba(0, 217, 255, 0.5)'
            }}>
              Welcome to Your Dashboard
            </h1>
            <p className="text-lg text-gray-300 mb-6 max-w-2xl mx-auto">
              Explore powerful features to manage your repositories, analyze contributions, and collaborate with your team
            </p>
            <div className="flex items-center justify-center gap-4">
              <div className="flex items-center gap-2 px-4 py-2 rounded-full border-2 border-[#0095ff] bg-black/40 backdrop-blur-sm" style={{
                boxShadow: '0 0 20px rgba(0, 149, 255, 0.3)'
              }}>
                <CalendarIcon className="h-5 w-5 text-[#00d9ff]" />
                <span className="text-sm font-medium text-white">{formatDate(new Date())}</span>
              </div>
              <ImportRepository onImportSuccess={() => window.location.reload()} />
            </div>
          </div>
        </div>
      </div>

      {/* Remove max-width container to eliminate white borders, use full width */}
      <div className="w-full px-4 sm:px-6 lg:px-8 py-12">
        {/* Quick Stats */}
        <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          <div className="group relative bg-gradient-to-br from-[#001529] to-[#000a1f] rounded-2xl p-6 transform hover:scale-105 transition-all duration-300 border-2 border-[#0095ff]/30 hover:border-[#00d9ff] overflow-hidden" style={{
            boxShadow: '0 4px 20px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(0, 217, 255, 0.1)'
          }}>
            {/* Animated lightning border effect */}
            <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300" style={{
              background: 'linear-gradient(45deg, transparent 30%, rgba(0, 217, 255, 0.1) 50%, transparent 70%)',
              backgroundSize: '200% 200%',
              animation: 'lightning 2s linear infinite'
            }}></div>
            
            {/* Neon glow effect on hover */}
            <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300" style={{
              boxShadow: 'inset 0 0 40px rgba(0, 217, 255, 0.2), 0 0 40px rgba(0, 149, 255, 0.4)'
            }}></div>
            
            <div className="relative z-10 flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-400">Repositories</p>
                <p className="text-3xl font-bold text-white mt-2" style={{
                  textShadow: '0 0 10px rgba(0, 217, 255, 0.5)'
                }}>{stats.totalRepos}</p>
                <p className="text-xs text-[#00d9ff] mt-2 flex items-center font-semibold">
                  <FireIcon className="h-4 w-4 mr-1" />
                  {stats.totalRepos > 0 ? 'Active Projects' : 'Get Started'}
                </p>
              </div>
              <div className="h-16 w-16 bg-gradient-to-br from-[#0095ff] to-[#00d9ff] rounded-2xl flex items-center justify-center" style={{
                boxShadow: '0 0 30px rgba(0, 217, 255, 0.6)'
              }}>
                <FolderIcon className="h-8 w-8 text-white" />
              </div>
            </div>
          </div>

          <div className="group relative bg-gradient-to-br from-[#001529] to-[#000a1f] rounded-2xl p-6 transform hover:scale-105 transition-all duration-300 border-2 border-[#0095ff]/30 hover:border-[#00d9ff] overflow-hidden" style={{
            boxShadow: '0 4px 20px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(0, 217, 255, 0.1)'
          }}>
            <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300" style={{
              background: 'linear-gradient(45deg, transparent 30%, rgba(0, 217, 255, 0.1) 50%, transparent 70%)',
              backgroundSize: '200% 200%',
              animation: 'lightning 2s linear infinite'
            }}></div>
            <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300" style={{
              boxShadow: 'inset 0 0 40px rgba(0, 217, 255, 0.2), 0 0 40px rgba(0, 149, 255, 0.4)'
            }}></div>
            
            <div className="relative z-10 flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-400">Contributors</p>
                <p className="text-3xl font-bold text-white mt-2" style={{
                  textShadow: '0 0 10px rgba(0, 217, 255, 0.5)'
                }}>{stats.totalContributors}</p>
                <p className="text-xs text-[#00ffaa] mt-2 flex items-center font-semibold">
                  <BoltIcon className="h-4 w-4 mr-1" />
                  Team Members
                </p>
              </div>
              <div className="h-16 w-16 bg-gradient-to-br from-[#0095ff] to-[#00ffaa] rounded-2xl flex items-center justify-center" style={{
                boxShadow: '0 0 30px rgba(0, 255, 170, 0.5)'
              }}>
                <UserGroupIcon className="h-8 w-8 text-white" />
              </div>
            </div>
          </div>

          <div className="group relative bg-gradient-to-br from-[#001529] to-[#000a1f] rounded-2xl p-6 transform hover:scale-105 transition-all duration-300 border-2 border-[#0095ff]/30 hover:border-[#00d9ff] overflow-hidden" style={{
            boxShadow: '0 4px 20px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(0, 217, 255, 0.1)'
          }}>
            <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300" style={{
              background: 'linear-gradient(45deg, transparent 30%, rgba(0, 217, 255, 0.1) 50%, transparent 70%)',
              backgroundSize: '200% 200%',
              animation: 'lightning 2s linear infinite'
            }}></div>
            <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300" style={{
              boxShadow: 'inset 0 0 40px rgba(0, 217, 255, 0.2), 0 0 40px rgba(0, 149, 255, 0.4)'
            }}></div>
            
            <div className="relative z-10 flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-400">Total Commits</p>
                <p className="text-3xl font-bold text-white mt-2" style={{
                  textShadow: '0 0 10px rgba(0, 217, 255, 0.5)'
                }}>{stats.totalCommits.toLocaleString()}</p>
                <p className="text-xs text-[#6b9eff] mt-2 flex items-center font-semibold">
                  <SparklesIcon className="h-4 w-4 mr-1" />
                  All Time
                </p>
              </div>
              <div className="h-16 w-16 bg-gradient-to-br from-[#6b9eff] to-[#0095ff] rounded-2xl flex items-center justify-center" style={{
                boxShadow: '0 0 30px rgba(107, 158, 255, 0.5)'
              }}>
                <CodeBracketIcon className="h-8 w-8 text-white" />
              </div>
            </div>
          </div>

          <div className="group relative bg-gradient-to-br from-[#001529] to-[#000a1f] rounded-2xl p-6 transform hover:scale-105 transition-all duration-300 border-2 border-[#0095ff]/30 hover:border-[#00d9ff] overflow-hidden" style={{
            boxShadow: '0 4px 20px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(0, 217, 255, 0.1)'
          }}>
            <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300" style={{
              background: 'linear-gradient(45deg, transparent 30%, rgba(0, 217, 255, 0.1) 50%, transparent 70%)',
              backgroundSize: '200% 200%',
              animation: 'lightning 2s linear infinite'
            }}></div>
            <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300" style={{
              boxShadow: 'inset 0 0 40px rgba(0, 217, 255, 0.2), 0 0 40px rgba(0, 149, 255, 0.4)'
            }}></div>
            
            <div className="relative z-10 flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-400">Issues Resolved</p>
                <p className="text-3xl font-bold text-white mt-2" style={{
                  textShadow: '0 0 10px rgba(0, 217, 255, 0.5)'
                }}>{stats.totalIssues.toLocaleString()}</p>
                <p className="text-xs text-[#00ffaa] mt-2 flex items-center font-semibold">
                  <CheckCircleIcon className="h-4 w-4 mr-1" />
                  Completed
                </p>
              </div>
              <div className="h-16 w-16 bg-gradient-to-br from-[#00ffaa] to-[#0095ff] rounded-2xl flex items-center justify-center" style={{
                boxShadow: '0 0 30px rgba(0, 255, 170, 0.5)'
              }}>
                <CheckCircleIcon className="h-8 w-8 text-white" />
              </div>
            </div>
          </div>
        </div>

        {/* Section Title */}
        <div className="max-w-7xl mx-auto text-center mb-10">
          <h2 className="text-3xl font-bold text-white mb-2" style={{
            textShadow: '0 0 20px rgba(0, 217, 255, 0.5)'
          }}>Explore Features</h2>
          <p className="text-gray-400">Click on any card to navigate to that section</p>
        </div>

        {/* Navigation Cards Grid */}
        <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {navigationCards.map((card, index) => {
            const Icon = card.icon;
            return (
              <div
                key={index}
                onClick={() => navigate(card.route)}
                className="group relative bg-gradient-to-br from-[#001529] to-[#000a1f] rounded-2xl p-6 cursor-pointer transform hover:scale-105 transition-all duration-300 border-2 border-[#0095ff]/30 hover:border-[#00d9ff] overflow-hidden"
                style={{
                  boxShadow: '0 4px 20px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(0, 217, 255, 0.1)'
                }}
              >
                {/* Lightning border effect on hover */}
                <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300" style={{
                  background: 'linear-gradient(45deg, transparent 30%, rgba(0, 217, 255, 0.1) 50%, transparent 70%)',
                  backgroundSize: '200% 200%',
                  animation: 'lightning 2s linear infinite'
                }}></div>
                
                {/* Neon glow effect */}
                <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300" style={{
                  boxShadow: 'inset 0 0 40px rgba(0, 217, 255, 0.2), 0 0 40px rgba(0, 149, 255, 0.4)'
                }}></div>
                
                {/* Content */}
                <div className="relative z-10">
                  <div className="flex items-start justify-between mb-4">
                    <div className={`${card.iconBg} p-3 rounded-xl group-hover:scale-110 transition-transform duration-300`} style={{
                      background: 'linear-gradient(135deg, #0095ff 0%, #00d9ff 100%)',
                      boxShadow: '0 4px 15px rgba(0, 149, 255, 0.4)'
                    }}>
                      <Icon className="h-6 w-6 text-white" />
                    </div>
                    <ArrowTopRightOnSquareIcon className="h-5 w-5 text-gray-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300 group-hover:text-[#00d9ff]" />
                  </div>
                  
                  <h3 className="text-lg font-bold text-white mb-2 group-hover:text-[#00d9ff] transition-colors" style={{
                    textShadow: '0 0 10px rgba(0, 217, 255, 0)'
                  }}>
                    {card.title}
                  </h3>
                  
                  <p className="text-sm text-gray-400 mb-4 line-clamp-2">
                    {card.description}
                  </p>
                  
                  <div className="flex items-center text-xs text-gray-500">
                    <div className="h-2 w-2 rounded-full bg-gradient-to-r from-[#0095ff] to-[#00d9ff] mr-2" style={{
                      boxShadow: '0 0 10px rgba(0, 217, 255, 0.6)'
                    }}></div>
                    {card.stats}
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Quick Actions Banner */}
        <div className="max-w-7xl mx-auto mt-12 relative rounded-2xl p-8 text-center border-2 border-[#0095ff]/50 overflow-hidden" style={{
          background: 'linear-gradient(135deg, #001529 0%, #003a70 50%, #001529 100%)',
          boxShadow: '0 8px 32px rgba(0, 149, 255, 0.3), inset 0 1px 0 rgba(0, 217, 255, 0.2)'
        }}>
          {/* Animated background effect */}
          <div className="absolute inset-0 opacity-30" style={{
            background: 'radial-gradient(circle at 50% 50%, rgba(0, 217, 255, 0.2) 0%, transparent 70%)',
            animation: 'pulse 3s ease-in-out infinite'
          }}></div>
          
          <div className="relative z-10">
            <h3 className="text-2xl font-bold text-white mb-3" style={{
              textShadow: '0 0 20px rgba(0, 217, 255, 0.5)'
            }}>Ready to Get Started?</h3>
            <p className="text-gray-300 mb-6 max-w-2xl mx-auto">
              Import your first repository to unlock powerful analytics and insights about your team's productivity
            </p>
            <div className="flex items-center justify-center gap-4">
              <ImportRepository onImportSuccess={() => window.location.reload()} />
              <Link
                to="/app/repositories"
                className="inline-flex items-center px-6 py-3 rounded-lg font-semibold transition-all duration-300 border-2 border-[#0095ff] bg-black/40 text-white hover:bg-[#0095ff] hover:border-[#00d9ff]"
                style={{
                  boxShadow: '0 4px 15px rgba(0, 149, 255, 0.3)'
                }}
              >
                <FolderIcon className="h-5 w-5 mr-2" />
                View Repositories
              </Link>
            </div>
          </div>
        </div>

        {/* Ask About Codebase Input */}
        <div className="max-w-7xl mx-auto mt-12 mb-12">
          <div className="relative">
            <input
              type="text"
              placeholder="Ask about your codebase..."
              className="w-full px-6 py-4 pr-16 rounded-2xl text-gray-700 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#0095ff] transition-all duration-300"
              style={{
                background: 'linear-gradient(135deg, #ffffff 0%, #f0f9ff 100%)',
                boxShadow: '0 8px 32px rgba(0, 149, 255, 0.2)'
              }}
              onFocus={(e) => {
                e.target.style.boxShadow = '0 8px 40px rgba(0, 149, 255, 0.4), 0 0 0 3px rgba(0, 149, 255, 0.1)';
              }}
              onBlur={(e) => {
                e.target.style.boxShadow = '0 8px 32px rgba(0, 149, 255, 0.2)';
              }}
            />
            <button 
              className="absolute right-3 top-1/2 transform -translate-y-1/2 p-3 rounded-xl bg-gradient-to-r from-[#0095ff] to-[#00d9ff] text-white transition-all duration-300 hover:scale-110"
              style={{
                boxShadow: '0 4px 15px rgba(0, 149, 255, 0.4)'
              }}
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
import React, { useState, useEffect } from 'react';
import { ShieldCheckIcon, ExclamationTriangleIcon, XCircleIcon, CheckCircleIcon, ClockIcon, ArrowTrendingUpIcon, ArrowTrendingDownIcon } from '@heroicons/react/24/outline';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const ReleaseReadinessScore = ({ repositoryId }) => {
  const [readinessData, setReadinessData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedView, setSelectedView] = useState('overview'); // overview, trend, details

  useEffect(() => {
    if (repositoryId) {
      fetchReadinessData();
    }
  }, [repositoryId]);

  const fetchReadinessData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`http://127.0.0.1:8000/api/release-readiness/${repositoryId}/dashboard/`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch release readiness data');
      }
      
      const data = await response.json();
      setReadinessData(data);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching readiness data:', err);
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 75) return 'text-blue-600';
    if (score >= 60) return 'text-yellow-600';
    if (score >= 40) return 'text-orange-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (score) => {
    if (score >= 90) return 'bg-green-100';
    if (score >= 75) return 'bg-blue-100';
    if (score >= 60) return 'bg-yellow-100';
    if (score >= 40) return 'bg-orange-100';
    return 'bg-red-100';
  };

  const getProgressBarColor = (score) => {
    if (score >= 90) return 'bg-green-500';
    if (score >= 75) return 'bg-blue-500';
    if (score >= 60) return 'bg-yellow-500';
    if (score >= 40) return 'bg-orange-500';
    return 'bg-red-500';
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-8">
        <div className="flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
          <span className="ml-3 text-gray-600">Calculating Release Readiness...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 rounded-lg shadow-lg p-8">
        <div className="flex items-center">
          <XCircleIcon className="h-8 w-8 text-red-500 mr-3" />
          <div>
            <h3 className="text-lg font-semibold text-red-800">Error Loading Readiness Score</h3>
            <p className="text-red-600">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  if (!readinessData) {
    return null;
  }

  const { current, trend, action_items } = readinessData;
  const score = current.score;
  const readinessLevel = current.readiness_level;

  return (
    <div className="space-y-6">
      {/* Header with View Selector */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center">
          <ShieldCheckIcon className="h-8 w-8 mr-2 text-indigo-600" />
          Release Readiness Score
        </h2>
        
        <div className="flex space-x-2">
          <button
            onClick={() => setSelectedView('overview')}
            className={`px-4 py-2 rounded-lg font-medium transition ${
              selectedView === 'overview'
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Overview
          </button>
          <button
            onClick={() => setSelectedView('trend')}
            className={`px-4 py-2 rounded-lg font-medium transition ${
              selectedView === 'trend'
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Trend
          </button>
          <button
            onClick={() => setSelectedView('details')}
            className={`px-4 py-2 rounded-lg font-medium transition ${
              selectedView === 'details'
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Details
          </button>
        </div>
      </div>

      {/* Overview View */}
      {selectedView === 'overview' && (
        <>
          {/* Main Score Card */}
          <div className={`${getScoreBgColor(score)} rounded-lg shadow-xl p-8 border-l-8 ${getProgressBarColor(score)}`}>
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="text-sm font-semibold text-gray-600 uppercase tracking-wide mb-2">
                  Release Readiness
                </div>
                <div className={`text-6xl font-bold ${getScoreColor(score)} mb-2`}>
                  {score.toFixed(1)}
                  <span className="text-3xl text-gray-500 ml-2">/ 100</span>
                </div>
                <div className="flex items-center mt-3">
                  <span className="text-3xl mr-2">{readinessLevel.emoji}</span>
                  <span className="text-xl font-semibold text-gray-800">{readinessLevel.label}</span>
                </div>
              </div>
              
              <div className="text-right">
                <div className={`inline-flex items-center px-6 py-3 rounded-full text-lg font-bold ${
                  current.can_release ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
                }`}>
                  {current.can_release ? (
                    <>
                      <CheckCircleIcon className="h-6 w-6 mr-2" />
                      Ready to Ship
                    </>
                  ) : (
                    <>
                      <XCircleIcon className="h-6 w-6 mr-2" />
                      Not Ready
                    </>
                  )}
                </div>
                
                <div className="mt-4 text-sm text-gray-600">
                  <ClockIcon className="h-4 w-4 inline mr-1" />
                  Updated {new Date(current.calculated_at).toLocaleString()}
                </div>
              </div>
            </div>

            {/* Progress Bar */}
            <div className="mt-6">
              <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
                <div
                  className={`h-4 ${getProgressBarColor(score)} transition-all duration-500 ease-out rounded-full`}
                  style={{ width: `${score}%` }}
                />
              </div>
            </div>
          </div>

          {/* Recommendation */}
          <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg shadow-lg p-6 border-l-4 border-indigo-600">
            <h3 className="text-lg font-bold text-gray-900 mb-2">Recommendation</h3>
            <p className="text-gray-700 text-lg">{current.recommendation}</p>
          </div>

          {/* Blockers and Warnings Grid */}
          <div className="grid md:grid-cols-2 gap-6">
            {/* Blockers */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="flex items-center mb-4">
                <XCircleIcon className="h-6 w-6 text-red-500 mr-2" />
                <h3 className="text-lg font-bold text-gray-900">
                  Critical Blockers ({current.blockers.length})
                </h3>
              </div>
              
              {current.blockers.length === 0 ? (
                <p className="text-green-600 font-medium">✅ No blocking issues!</p>
              ) : (
                <ul className="space-y-2">
                  {current.blockers.map((blocker, index) => (
                    <li key={index} className="flex items-start">
                      <span className="text-red-500 mr-2">•</span>
                      <span className="text-gray-700">{blocker}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>

            {/* Warnings */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="flex items-center mb-4">
                <ExclamationTriangleIcon className="h-6 w-6 text-yellow-500 mr-2" />
                <h3 className="text-lg font-bold text-gray-900">
                  Warnings ({current.warnings.length})
                </h3>
              </div>
              
              {current.warnings.length === 0 ? (
                <p className="text-green-600 font-medium">✅ No warnings!</p>
              ) : (
                <ul className="space-y-2">
                  {current.warnings.map((warning, index) => (
                    <li key={index} className="flex items-start">
                      <span className="text-yellow-500 mr-2">•</span>
                      <span className="text-gray-700">{warning}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>

          {/* Summary Stats */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Quality Checks Summary</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-gray-900">{current.summary.total_checks}</div>
                <div className="text-sm text-gray-600">Total Checks</div>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">{current.summary.passed_checks}</div>
                <div className="text-sm text-gray-600">Passed</div>
              </div>
              <div className="text-center p-4 bg-red-50 rounded-lg">
                <div className="text-2xl font-bold text-red-600">{current.summary.failed_checks}</div>
                <div className="text-sm text-gray-600">Failed</div>
              </div>
              <div className="text-center p-4 bg-yellow-50 rounded-lg">
                <div className="text-2xl font-bold text-yellow-600">{current.summary.warnings_count}</div>
                <div className="text-sm text-gray-600">Warnings</div>
              </div>
            </div>
          </div>
        </>
      )}

      {/* Trend View */}
      {selectedView === 'trend' && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-bold text-gray-900">Readiness Score Trend</h3>
            <div className="flex items-center">
              {trend.trend_direction === 'improving' ? (
                <>
                  <ArrowTrendingUpIcon className="h-6 w-6 text-green-500 mr-2" />
                  <span className="text-green-600 font-semibold">Improving</span>
                </>
              ) : (
                <>
                  <ArrowTrendingDownIcon className="h-6 w-6 text-red-500 mr-2" />
                  <span className="text-red-600 font-semibold">Declining</span>
                </>
              )}
            </div>
          </div>

          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={trend.trend}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="date" 
                tick={{ fontSize: 12 }}
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="score" 
                stroke="#4f46e5" 
                strokeWidth={3}
                dot={{ fill: '#4f46e5', r: 5 }}
                activeDot={{ r: 8 }}
                name="Readiness Score"
              />
            </LineChart>
          </ResponsiveContainer>

          <div className="mt-6 grid grid-cols-3 gap-4">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{trend.current_score.toFixed(1)}</div>
              <div className="text-sm text-gray-600">Current Score</div>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">{trend.trend.length}</div>
              <div className="text-sm text-gray-600">Data Points</div>
            </div>
            <div className="text-center p-4 bg-indigo-50 rounded-lg">
              <div className="text-2xl font-bold text-indigo-600">
                {((trend.current_score - trend.trend[0].score)).toFixed(1)}
              </div>
              <div className="text-sm text-gray-600">Change from Start</div>
            </div>
          </div>
        </div>
      )}

      {/* Details View */}
      {selectedView === 'details' && (
        <>
          {/* Penalties Breakdown */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Score Penalties Breakdown</h3>
            
            {current.penalties.length === 0 ? (
              <p className="text-green-600 font-medium text-center py-8">
                🎉 Perfect! No penalties applied - excellent code quality!
              </p>
            ) : (
              <div className="space-y-3">
                {current.penalties.map((penalty, index) => (
                  <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border-l-4 border-red-500">
                    <div className="flex-1">
                      <div className="font-semibold text-gray-900">{penalty.message}</div>
                      <div className="text-sm text-gray-600 mt-1">
                        Type: <span className="font-mono">{penalty.type}</span>
                        {penalty.count && ` • Count: ${penalty.count}`}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-red-600">-{penalty.penalty}</div>
                      <div className="text-xs text-gray-500">points</div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Passed Checks */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Passed Quality Checks</h3>
            <div className="grid md:grid-cols-2 gap-3">
              {current.passed_checks.map((check, index) => (
                <div key={index} className="flex items-center p-3 bg-green-50 rounded-lg">
                  <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2 flex-shrink-0" />
                  <span className="text-gray-700">{check}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Action Items */}
          {action_items.next_steps && action_items.next_steps.length > 0 && (
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-xl font-bold text-gray-900 mb-4">Next Steps</h3>
              <div className="space-y-4">
                {action_items.next_steps.map((step, index) => (
                  <div key={index} className={`p-4 rounded-lg border-l-4 ${
                    step.priority === 'critical' ? 'bg-red-50 border-red-500' :
                    step.priority === 'high' ? 'bg-yellow-50 border-yellow-500' :
                    'bg-blue-50 border-blue-500'
                  }`}>
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-bold text-gray-900">{step.title}</h4>
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold uppercase ${
                        step.priority === 'critical' ? 'bg-red-200 text-red-800' :
                        step.priority === 'high' ? 'bg-yellow-200 text-yellow-800' :
                        'bg-blue-200 text-blue-800'
                      }`}>
                        {step.priority}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-3">{step.description}</p>
                    <ul className="space-y-1">
                      {step.items.map((item, itemIndex) => (
                        <li key={itemIndex} className="text-sm text-gray-700 flex items-start">
                          <span className="mr-2">→</span>
                          <span>{item}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Detailed Metrics */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Repository Metrics</h3>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {Object.entries(current.detailed_metrics).map(([key, value]) => (
                <div key={key} className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-indigo-600">{value}</div>
                  <div className="text-xs text-gray-600 mt-1">
                    {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}

      {/* Refresh Button */}
      <div className="text-center">
        <button
          onClick={fetchReadinessData}
          className="px-6 py-3 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 transition shadow-lg"
        >
          🔄 Refresh Readiness Score
        </button>
      </div>
    </div>
  );
};

export default ReleaseReadinessScore;

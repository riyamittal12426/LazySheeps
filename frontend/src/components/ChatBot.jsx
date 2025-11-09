import React, { useState } from 'react';
import {
  PaperAirplaneIcon,
  ArrowPathIcon,
  ClipboardDocumentIcon,
  CodeBracketIcon,
  HeartIcon,
  CalendarIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';
import ReactMarkdown from 'react-markdown';

const ChatBot = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [prNumber, setPrNumber] = useState('');
  const [repoName, setRepoName] = useState('owner/repo');
  const [repositoryId, setRepositoryId] = useState('');
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handlePRSummary = async () => {
    if (!prNumber || !repoName) {
      setError('Please provide PR number and repository name');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/chatbot/pr-summary/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          pr_number: parseInt(prNumber),
          repository_name: repoName,
        }),
      });

      const data = await response.json();

      if (data.success) {
        setResult(data.summary);
      } else {
        setError(data.error || 'Failed to get PR summary');
      }
    } catch (err) {
      setError('Error: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleTeamHealth = async () => {
    setLoading(true);
    setError(null);

    try {
      const url = repositoryId
        ? `http://localhost:8000/api/chatbot/team-health/?repository_id=${repositoryId}`
        : 'http://localhost:8000/api/chatbot/team-health/';

      const response = await fetch(url);
      const data = await response.json();

      if (data.success) {
        setResult(data.report);
      } else {
        setError(data.error || 'Failed to get team health');
      }
    } catch (err) {
      setError('Error: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDailyDigest = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/chatbot/daily-digest/');
      const data = await response.json();

      if (data.success) {
        setResult(data.digest);
      } else {
        setError(data.error || 'Failed to get daily digest');
      }
    } catch (err) {
      setError('Error: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleRiskAlerts = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/chatbot/risk-alerts/');
      const data = await response.json();

      if (data.success) {
        setResult(data.risks);
      } else {
        setError(data.error || 'Failed to get risk alerts');
      }
    } catch (err) {
      setError('Error: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(result);
  };

  const tabs = [
    { name: 'PR Summary', icon: CodeBracketIcon },
    { name: 'Team Health', icon: HeartIcon },
    { name: 'Daily Digest', icon: CalendarIcon },
    { name: 'Risk Alerts', icon: ExclamationTriangleIcon },
  ];

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            🤖 Katalyst ChatBot
          </h1>
          <p className="text-gray-600">
            AI-powered Slack/Discord commands for team insights
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          {/* Tabs */}
          <div className="border-b border-gray-200">
            <nav className="flex">
              {tabs.map((tab, index) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={index}
                    onClick={() => setActiveTab(index)}
                    className={`flex items-center gap-2 px-6 py-4 text-sm font-medium border-b-2 ${
                      activeTab === index
                        ? 'border-purple-500 text-purple-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    {tab.name}
                  </button>
                );
              })}
            </nav>
          </div>

          <div className="p-6">
            {/* PR Summary Tab */}
            {activeTab === 0 && (
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-2">
                  📝 PR Summary
                </h2>
                <p className="text-gray-600 mb-6">
                  Get AI-powered summary of a pull request
                </p>

                <div className="space-y-4 max-w-md">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Repository Name
                    </label>
                    <input
                      type="text"
                      value={repoName}
                      onChange={(e) => setRepoName(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                      placeholder="owner/repo"
                    />
                    <p className="text-sm text-gray-500 mt-1">Format: owner/repository</p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      PR Number
                    </label>
                    <input
                      type="number"
                      value={prNumber}
                      onChange={(e) => setPrNumber(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                      placeholder="123"
                    />
                  </div>

                  <button
                    onClick={handlePRSummary}
                    disabled={loading}
                    className="w-full bg-purple-600 text-white py-2 px-4 rounded-md hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                  >
                    {loading ? (
                      <ArrowPathIcon className="w-5 h-5 animate-spin" />
                    ) : (
                      <PaperAirplaneIcon className="w-5 h-5" />
                    )}
                    Generate PR Summary
                  </button>

                  <div className="mt-4 p-3 bg-gray-100 rounded text-sm">
                    <span className="font-medium text-gray-700">Slack Command:</span>
                    <code className="ml-2 text-purple-600">
                      /katalyst pr {prNumber || '123'} {repoName}
                    </code>
                  </div>
                </div>
              </div>
            )}

            {/* Team Health Tab */}
            {activeTab === 1 && (
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-2">
                  📊 Team Health Dashboard
                </h2>
                <p className="text-gray-600 mb-6">
                  View DORA metrics and team health indicators
                </p>

                <div className="space-y-4 max-w-md">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Repository ID (Optional)
                    </label>
                    <input
                      type="number"
                      value={repositoryId}
                      onChange={(e) => setRepositoryId(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                    />
                    <p className="text-sm text-gray-500 mt-1">Leave empty for all repositories</p>
                  </div>

                  <button
                    onClick={handleTeamHealth}
                    disabled={loading}
                    className="w-full bg-purple-600 text-white py-2 px-4 rounded-md hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                  >
                    {loading ? (
                      <ArrowPathIcon className="w-5 h-5 animate-spin" />
                    ) : (
                      <HeartIcon className="w-5 h-5" />
                    )}
                    Get Team Health
                  </button>

                  <div className="mt-4 p-3 bg-gray-100 rounded text-sm">
                    <span className="font-medium text-gray-700">Slash Command:</span>
                    <code className="ml-2 text-purple-600">
                      /katalyst team-health {repositoryId || ''}
                    </code>
                  </div>
                </div>
              </div>
            )}

            {/* Daily Digest Tab */}
            {activeTab === 2 && (
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-2">
                  📅 Daily Digest
                </h2>
                <p className="text-gray-600 mb-6">
                  Get yesterday's activity summary
                </p>

                <div className="max-w-md">
                  <button
                    onClick={handleDailyDigest}
                    disabled={loading}
                    className="w-full bg-purple-600 text-white py-2 px-4 rounded-md hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                  >
                    {loading ? (
                      <ArrowPathIcon className="w-5 h-5 animate-spin" />
                    ) : (
                      <CalendarIcon className="w-5 h-5" />
                    )}
                    Generate Daily Digest
                  </button>

                  <div className="mt-4 p-3 bg-gray-100 rounded text-sm">
                    <span className="font-medium text-gray-700">Slack Command:</span>
                    <code className="ml-2 text-purple-600">/katalyst digest</code>
                  </div>

                  <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded text-sm text-blue-800">
                    💡 Set up a cron job to automatically send daily digests to your team channel!
                  </div>
                </div>
              </div>
            )}

            {/* Risk Alerts Tab */}
            {activeTab === 3 && (
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-2">
                  ⚠️ Risk Alerts
                </h2>
                <p className="text-gray-600 mb-6">
                  Detect potential risks and issues
                </p>

                <div className="max-w-md">
                  <button
                    onClick={handleRiskAlerts}
                    disabled={loading}
                    className="w-full bg-red-600 text-white py-2 px-4 rounded-md hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                  >
                    {loading ? (
                      <ArrowPathIcon className="w-5 h-5 animate-spin" />
                    ) : (
                      <ExclamationTriangleIcon className="w-5 h-5" />
                    )}
                    Check for Risks
                  </button>

                  <div className="mt-4 p-3 bg-gray-100 rounded text-sm">
                    <span className="font-medium text-gray-700">Slack Command:</span>
                    <code className="ml-2 text-purple-600">/katalyst risks</code>
                  </div>
                </div>
              </div>
            )}

            {error && (
              <div className="mt-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                {error}
              </div>
            )}
          </div>
        </div>

        {/* Results Display */}
        {result && (
          <div className="mt-8 bg-white rounded-lg shadow-md">
            <div className="flex justify-between items-center p-6 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">Results</h3>
              <div className="flex gap-2">
                <button
                  onClick={copyToClipboard}
                  className="p-2 text-gray-400 hover:text-gray-600"
                  title="Copy to clipboard"
                >
                  <ClipboardDocumentIcon className="w-5 h-5" />
                </button>
                <button
                  onClick={() => setResult('')}
                  className="p-2 text-gray-400 hover:text-gray-600"
                  title="Clear"
                >
                  <ArrowPathIcon className="w-5 h-5" />
                </button>
              </div>
            </div>

            <div className="p-6">
              <div className="bg-gray-50 rounded-lg p-4 max-h-96 overflow-y-auto">
                <ReactMarkdown className="prose prose-sm max-w-none">
                  {result}
                </ReactMarkdown>
              </div>
            </div>
          </div>
        )}

        {/* Setup Instructions */}
        <div className="mt-8 bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            🔧 Setup Instructions
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-gray-900 mb-3">Slack Setup:</h4>
              <ol className="list-decimal list-inside text-sm text-gray-600 space-y-1">
                <li>Create a Slack app at api.slack.com/apps</li>
                <li>Enable "Slash Commands" and add <code className="bg-gray-100 px-1 rounded">/katalyst</code></li>
                <li>Set Request URL to: <code className="bg-gray-100 px-1 rounded text-xs">https://your-domain.com/api/webhooks/slack/</code></li>
                <li>Add webhook URL to .env: <code className="bg-gray-100 px-1 rounded text-xs">SLACK_WEBHOOK_URL=...</code></li>
                <li>Install app to your workspace</li>
              </ol>
            </div>

            <div>
              <h4 className="font-medium text-gray-900 mb-3">Discord Setup:</h4>
              <ol className="list-decimal list-inside text-sm text-gray-600 space-y-1">
                <li>Create a Discord bot at discord.com/developers</li>
                <li>Add webhook to your channel</li>
                <li>Add webhook URL to .env: <code className="bg-gray-100 px-1 rounded text-xs">DISCORD_WEBHOOK_URL=...</code></li>
                <li>Use commands with <code className="bg-gray-100 px-1 rounded">!katalyst</code> prefix</li>
              </ol>
            </div>
          </div>

          <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded">
            <h5 className="font-medium text-blue-900 mb-2">Environment Variables Needed:</h5>
            <div className="text-sm text-blue-800 space-y-1">
              <div>- SLACK_WEBHOOK_URL</div>
              <div>- SLACK_BOT_TOKEN</div>
              <div>- DISCORD_WEBHOOK_URL</div>
              <div>- GEMINI_API_KEY</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatBot;

import React, { useState } from 'react';
import {
  BugAntIcon,
  ChartBarIcon,
  CodeBracketIcon,
  DocumentTextIcon,
  ShieldExclamationIcon,
  QuestionMarkCircleIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  UserIcon,
  ClipboardDocumentIcon,
  ArrowPathIcon,
} from '@heroicons/react/24/outline';

const AutoTriage = () => {
  const [issueData, setIssueData] = useState({
    title: '',
    body: '',
    repository_id: '',
  });
  const [triageResult, setTriageResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleTriageIssue = async () => {
    if (!issueData.title || !issueData.repository_id) {
      setError('Please provide both title and repository ID');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/triage/issue/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          repository_id: parseInt(issueData.repository_id),
          issue_data: {
            title: issueData.title,
            body: issueData.body,
            labels: [],
          },
        }),
      });

      const data = await response.json();

      if (data.success) {
        setTriageResult(data.triage_result);
      } else {
        setError(data.error || 'Failed to triage issue');
      }
    } catch (err) {
      setError('Error connecting to server: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleClassifyOnly = async () => {
    if (!issueData.title) {
      setError('Please provide an issue title');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/triage/classify/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: issueData.title,
          body: issueData.body,
          labels: [],
        }),
      });

      const data = await response.json();

      if (data.success) {
        setTriageResult({
          classification: data.classification,
          duplicate_detection: null,
          assignment: null,
        });
      } else {
        setError(data.error || 'Failed to classify issue');
      }
    } catch (err) {
      setError('Error connecting to server: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const getPriorityColor = (priority) => {
    const colors = {
      critical: 'bg-red-100 text-red-800 border-red-300',
      high: 'bg-orange-100 text-orange-800 border-orange-300',
      medium: 'bg-blue-100 text-blue-800 border-blue-300',
      low: 'bg-green-100 text-green-800 border-green-300',
    };
    return colors[priority] || 'bg-gray-100 text-gray-800 border-gray-300';
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">🤖 Auto-Triage & Labeling</h1>
        <p className="text-gray-600">
          AI-powered issue classification, duplicate detection, and assignee suggestion
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Section */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Issue Details</h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Repository ID
              </label>
              <input
                type="number"
                value={issueData.repository_id}
                onChange={(e) =>
                  setIssueData({ ...issueData, repository_id: e.target.value })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                placeholder="Enter repository ID"
              />
              <p className="text-sm text-gray-500 mt-1">Enter the repository ID from your database</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Issue Title
              </label>
              <input
                type="text"
                value={issueData.title}
                onChange={(e) =>
                  setIssueData({ ...issueData, title: e.target.value })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                placeholder="e.g., Bug in login form validation"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Issue Description
              </label>
              <textarea
                value={issueData.body}
                onChange={(e) =>
                  setIssueData({ ...issueData, body: e.target.value })
                }
                rows={6}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                placeholder="Describe the issue in detail..."
              />
            </div>

            <div className="flex gap-3">
              <button
                onClick={handleTriageIssue}
                disabled={loading}
                className="flex-1 bg-purple-600 text-white py-2 px-4 rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? '⌛ Processing...' : 'Full Triage'}
              </button>
              <button
                onClick={handleClassifyOnly}
                disabled={loading}
                className="flex-1 border border-purple-600 text-purple-600 py-2 px-4 rounded-lg hover:bg-purple-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Classify Only
              </button>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg">
                {error}
              </div>
            )}
          </div>
        </div>

        {/* Results Section */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Triage Results</h2>

          {triageResult ? (
            <div className="space-y-4">
              {/* Classification */}
              {triageResult.classification && (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="font-semibold mb-3">📊 Classification</h3>

                  <div className="flex flex-wrap gap-2 mb-3">
                    <span className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm font-medium">
                      {triageResult.classification.type.toUpperCase()}
                    </span>
                    <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                      Component: {triageResult.classification.component}
                    </span>
                    <span className={`px-3 py-1 rounded-full text-sm border ${getPriorityColor(triageResult.classification.priority)}`}>
                      Priority: {triageResult.classification.priority}
                    </span>
                    <span className="px-3 py-1 bg-gray-100 text-gray-800 rounded-full text-sm">
                      {triageResult.classification.complexity}
                    </span>
                  </div>

                  <p className="text-sm text-gray-600 mb-2">
                    <strong>Reasoning:</strong> {triageResult.classification.reasoning}
                  </p>

                  <p className="text-sm text-gray-600 mb-2">
                    <strong>Confidence:</strong>{' '}
                    {(triageResult.classification.confidence * 100).toFixed(0)}%
                  </p>

                  <p className="text-sm text-gray-600">
                    <strong>Estimated Effort:</strong>{' '}
                    {triageResult.classification.estimated_effort} hours
                  </p>
                </div>
              )}

              {/* Suggested Labels */}
              {triageResult.labels && triageResult.labels.length > 0 && (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="font-semibold mb-3">🏷️ Suggested Labels</h3>
                  <div className="flex flex-wrap gap-2">
                    {triageResult.labels.map((label, index) => (
                      <span
                        key={index}
                        className="px-2 py-1 bg-white border border-gray-300 rounded text-sm"
                      >
                        {label}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Duplicate Detection */}
              {triageResult.duplicate_detection && (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="font-semibold mb-3">🔍 Duplicate Detection</h3>
                  {triageResult.duplicate_detection.is_duplicate ? (
                    <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-3 rounded">
                      ⚠️ Potential duplicate of issue #
                      {triageResult.duplicate_detection.duplicate_of}
                    </div>
                  ) : (
                    <div className="bg-green-50 border border-green-200 text-green-800 px-4 py-3 rounded">
                      ✅ No duplicates detected
                    </div>
                  )}
                </div>
              )}

              {/* Assignment Suggestion */}
              {triageResult.assignment && (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="font-semibold mb-3">👤 Suggested Assignee</h3>
                  {triageResult.assignment.assignee ? (
                    <>
                      <div className="flex items-center gap-2 mb-2">
                        <span className="font-medium">{triageResult.assignment.assignee}</span>
                        <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs">
                          {(triageResult.assignment.confidence * 100).toFixed(0)}% match
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mb-3">
                        {triageResult.assignment.reasoning}
                      </p>

                      {triageResult.assignment.alternatives &&
                        triageResult.assignment.alternatives.length > 0 && (
                          <div>
                            <p className="text-sm font-medium mb-2">Alternatives:</p>
                            <div className="flex flex-wrap gap-2">
                              {triageResult.assignment.alternatives.map((alt, index) => (
                                <span
                                  key={index}
                                  className="px-2 py-1 bg-white border border-gray-300 rounded text-sm"
                                >
                                  {alt.username}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                    </>
                  ) : (
                    <p className="text-sm text-gray-600">No suitable assignee found</p>
                  )}
                </div>
              )}

              {/* Auto Actions */}
              {triageResult.auto_actions && triageResult.auto_actions.length > 0 && (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="font-semibold mb-3">⚡ Recommended Actions</h3>
                  <ul className="space-y-2">
                    {triageResult.auto_actions.map((action, index) => (
                      <li key={index} className="flex items-center gap-2 text-sm">
                        <span className="text-green-600">✓</span>
                        <span className="text-gray-700">
                          {action.replace(/_/g, ' ').toUpperCase()}
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-12 text-gray-500">
              <p>Enter issue details and click "Full Triage" to see AI-powered analysis</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AutoTriage;

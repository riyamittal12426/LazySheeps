import { useState } from 'react';
import axios from 'axios';

const ImportRepository = ({ onImportSuccess }) => {
  const [repoUrl, setRepoUrl] = useState('');
  const [githubToken, setGithubToken] = useState('');
  const [isImporting, setIsImporting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [importDetails, setImportDetails] = useState(null);

  const validateGitHubUrl = (url) => {
    const patterns = [
      /^https?:\/\/github\.com\/[\w-]+\/[\w.-]+$/,
      /^github\.com\/[\w-]+\/[\w.-]+$/,
      /^[\w-]+\/[\w.-]+$/
    ];
    return patterns.some(pattern => pattern.test(url.trim()));
  };

  const handleImport = async () => {
    setError('');
    setSuccess('');
    setImportDetails(null);

    // Validate URL
    if (!repoUrl.trim()) {
      setError('Please enter a GitHub repository URL');
      return;
    }

    if (!validateGitHubUrl(repoUrl)) {
      setError('Invalid GitHub URL. Format: https://github.com/owner/repo or owner/repo');
      return;
    }

    setIsImporting(true);

    try {
      const response = await axios.post('http://localhost:8000/api/repositories/import/', {
        repo_url: repoUrl.trim(),
        github_token: githubToken.trim() || undefined
      });

      if (response.data.success) {
        setSuccess(`Successfully imported ${response.data.repository.name}!`);
        setImportDetails(response.data.repository);
        setRepoUrl('');
        setGithubToken('');
        
        // Call success callback if provided
        if (onImportSuccess) {
          onImportSuccess(response.data.repository);
        }

        // Close modal after 2 seconds
        setTimeout(() => {
          setShowModal(false);
          setSuccess('');
        }, 2000);
      }
    } catch (err) {
      console.error('Import error:', err);
      console.error('Error response:', err.response);
      console.error('Error data:', err.response?.data);
      
      let errorMessage = 'Failed to import repository. Please check the URL and try again.';
      
      if (err.response?.data?.error) {
        errorMessage = err.response.data.error;
      } else if (err.response?.status === 0) {
        errorMessage = 'Cannot connect to server. Make sure Django backend is running on http://localhost:8000';
      } else if (err.response?.status) {
        errorMessage = `Server error (${err.response.status}): ${err.message}`;
      }
      
      setError(errorMessage);
    } finally {
      setIsImporting(false);
    }
  };

  return (
    <>
      {/* Import Button */}
      <button
        onClick={() => setShowModal(true)}
        className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all shadow-lg hover:shadow-xl"
      >
        <span className="flex items-center gap-2">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Import Repository
        </span>
      </button>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full p-6 transform transition-all">
            {/* Header */}
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-gray-800">Import GitHub Repository</h2>
              <button
                onClick={() => {
                  setShowModal(false);
                  setError('');
                  setSuccess('');
                }}
                className="text-gray-500 hover:text-gray-700 transition"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Form */}
            <div className="space-y-4">
              {/* Repository URL Input */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Repository URL *
                </label>
                <input
                  type="text"
                  value={repoUrl}
                  onChange={(e) => setRepoUrl(e.target.value)}
                  placeholder="https://github.com/owner/repository or owner/repository"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  disabled={isImporting}
                />
                <p className="text-xs text-gray-500 mt-1">
                  Supports formats: https://github.com/owner/repo, github.com/owner/repo, or owner/repo
                </p>
              </div>

              {/* GitHub Token Input (Optional) */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  GitHub Personal Access Token (Optional)
                </label>
                <input
                  type="password"
                  value={githubToken}
                  onChange={(e) => setGithubToken(e.target.value)}
                  placeholder="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  disabled={isImporting}
                />
                <p className="text-xs text-gray-500 mt-1">
                  Recommended for private repos or to avoid rate limits. 
                  <a 
                    href="https://github.com/settings/tokens" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline ml-1"
                  >
                    Generate token
                  </a>
                </p>
              </div>

              {/* Error Message */}
              {error && (
                <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
                  <svg className="w-5 h-5 text-red-600 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                  <p className="text-sm text-red-800">{error}</p>
                </div>
              )}

              {/* Success Message */}
              {success && (
                <div className="p-4 bg-green-50 border border-green-200 rounded-lg flex items-start gap-3">
                  <svg className="w-5 h-5 text-green-600 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <div className="flex-1">
                    <p className="text-sm text-green-800 font-medium">{success}</p>
                    {importDetails && (
                      <div className="mt-2 text-xs text-green-700 space-y-1">
                        <p>✓ {importDetails.contributors_count} contributors</p>
                        <p>✓ {importDetails.commits_count} commits</p>
                        <p>✓ {importDetails.issues_count} issues</p>
                        <p>✓ {importDetails.stars} stars • {importDetails.forks} forks</p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Import Progress */}
              {isImporting && (
                <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-blue-800">Importing repository...</p>
                      <p className="text-xs text-blue-600 mt-1">
                        Fetching repository data, contributors, commits, and issues. This may take a moment.
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3 mt-6">
              <button
                onClick={() => {
                  setShowModal(false);
                  setError('');
                  setSuccess('');
                }}
                className="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition"
                disabled={isImporting}
              >
                Cancel
              </button>
              <button
                onClick={handleImport}
                disabled={isImporting || !repoUrl.trim()}
                className="flex-1 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isImporting ? 'Importing...' : 'Import Repository'}
              </button>
            </div>

            {/* Info Box */}
            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <h3 className="text-sm font-semibold text-gray-700 mb-2">What happens when you import?</h3>
              <ul className="text-xs text-gray-600 space-y-1">
                <li>• Fetches repository metadata (stars, forks, language)</li>
                <li>• Imports all contributors with their profiles</li>
                <li>• Retrieves up to 500 recent commits with statistics</li>
                <li>• Imports all issues (excludes pull requests)</li>
                <li>• Calculates contributor scores and collaboration patterns</li>
                <li>• Generates AI-powered burnout risk analysis</li>
              </ul>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default ImportRepository;

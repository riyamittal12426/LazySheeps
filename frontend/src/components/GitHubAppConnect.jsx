import { useState, useEffect } from 'react';
import axios from 'axios';

const GitHubAppConnect = () => {
  const [installations, setInstallations] = useState([]);
  const [selectedInstallation, setSelectedInstallation] = useState(null);
  const [repositories, setRepositories] = useState([]);
  const [selectedRepos, setSelectedRepos] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isImporting, setIsImporting] = useState(false);
  const [showRepoModal, setShowRepoModal] = useState(false);
  const [importProgress, setImportProgress] = useState(null);

  useEffect(() => {
    fetchInstallations();
  }, []);

  const fetchInstallations = async () => {
    try {
      setIsLoading(true);
      const token = localStorage.getItem('token');
      const response = await axios.get('http://localhost:8000/api/github-app/installations/', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setInstallations(response.data.installations);
    } catch (error) {
      console.error('Failed to fetch installations:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleConnectApp = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/github-app/install-url/');
      if (response.data.install_url) {
        window.location.href = response.data.install_url;
      } else {
        alert('GitHub App is not configured. Please set up GITHUB_APP_SLUG in your .env file.');
      }
    } catch (error) {
      console.error('Failed to get install URL:', error);
      alert('GitHub App is not configured yet. Please check the setup guide in GITHUB_APP_ACTIVATION_GUIDE.md');
    }
  };

  const fetchRepositories = async (installation) => {
    try {
      setIsLoading(true);
      setSelectedInstallation(installation);
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `http://localhost:8000/api/github-app/installations/${installation.id}/repositories/`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setRepositories(response.data.repositories);
      setShowRepoModal(true);
    } catch (error) {
      console.error('Failed to fetch repositories:', error);
      alert('Failed to fetch repositories');
    } finally {
      setIsLoading(false);
    }
  };

  const toggleRepoSelection = (repoId) => {
    setSelectedRepos(prev => 
      prev.includes(repoId) 
        ? prev.filter(id => id !== repoId)
        : [...prev, repoId]
    );
  };

  const selectAllRepos = () => {
    if (selectedRepos.length === repositories.length) {
      setSelectedRepos([]);
    } else {
      setSelectedRepos(repositories.map(r => r.id));
    }
  };

  const handleBulkImport = async () => {
    if (selectedRepos.length === 0) {
      alert('Please select at least one repository');
      return;
    }

    try {
      setIsImporting(true);
      setImportProgress({ current: 0, total: selectedRepos.length });

      const token = localStorage.getItem('token');
      const response = await axios.post(
        `http://localhost:8000/api/github-app/installations/${selectedInstallation.id}/bulk-import/`,
        {
          repository_ids: selectedRepos,
          auto_webhook: true
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      setImportProgress(response.data.summary);
      
      // Refresh the repository list
      setTimeout(() => {
        fetchRepositories(selectedInstallation);
        setSelectedRepos([]);
      }, 2000);

    } catch (error) {
      console.error('Bulk import failed:', error);
      alert('Failed to import repositories');
    } finally {
      setIsImporting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold mb-2">🚀 GitHub App Integration</h2>
            <p className="text-purple-100">
              One-click import of ALL organization repositories with automatic webhook setup
            </p>
          </div>
          <button
            onClick={handleConnectApp}
            className="px-6 py-3 bg-white text-purple-600 rounded-lg font-semibold hover:bg-purple-50 transition-all shadow-lg"
          >
            Connect GitHub App
          </button>
        </div>
      </div>

      {/* Feature Highlights */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg p-4 shadow border border-purple-100">
          <div className="text-3xl mb-2">⚡</div>
          <h3 className="font-semibold text-gray-800 mb-1">Instant Org Access</h3>
          <p className="text-sm text-gray-600">
            Import all org repositories with a single click
          </p>
        </div>
        <div className="bg-white rounded-lg p-4 shadow border border-blue-100">
          <div className="text-3xl mb-2">🔗</div>
          <h3 className="font-semibold text-gray-800 mb-1">Auto Webhooks</h3>
          <p className="text-sm text-gray-600">
            Automatically configure webhooks for all repos
          </p>
        </div>
        <div className="bg-white rounded-lg p-4 shadow border border-green-100">
          <div className="text-3xl mb-2">🏢</div>
          <h3 className="font-semibold text-gray-800 mb-1">Enterprise Grade</h3>
          <p className="text-sm text-gray-600">
            Secure organization-wide integration
          </p>
        </div>
      </div>

      {/* Installations List */}
      {isLoading && installations.length === 0 ? (
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
        </div>
      ) : installations.length === 0 ? (
        <div className="bg-white rounded-lg p-12 text-center border-2 border-dashed border-gray-300">
          <div className="text-6xl mb-4">📦</div>
          <h3 className="text-xl font-semibold text-gray-800 mb-2">
            No GitHub App Connected
          </h3>
          <p className="text-gray-600 mb-6">
            Connect your GitHub organization to import repositories instantly
          </p>
          <button
            onClick={handleConnectApp}
            className="px-8 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg font-semibold hover:from-purple-700 hover:to-blue-700 transition-all shadow-lg"
          >
            Connect Now
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-800">Connected Organizations</h3>
          {installations.map(installation => (
            <div
              key={installation.id}
              className="bg-white rounded-lg p-6 shadow hover:shadow-lg transition-all border border-gray-200"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  {installation.account_avatar_url && (
                    <img
                      src={installation.account_avatar_url}
                      alt={installation.account_login}
                      className="w-16 h-16 rounded-lg"
                    />
                  )}
                  <div>
                    <h4 className="text-xl font-semibold text-gray-800">
                      {installation.account_login}
                    </h4>
                    <div className="flex items-center gap-3 mt-1">
                      <span className="text-sm text-gray-600">
                        {installation.account_type}
                      </span>
                      <span className="text-gray-300">•</span>
                      <span className="text-sm text-gray-500">
                        Connected {new Date(installation.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                </div>
                <button
                  onClick={() => fetchRepositories(installation)}
                  className="px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg font-semibold hover:from-purple-700 hover:to-blue-700 transition-all shadow-md"
                >
                  Import Repositories
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Repository Selection Modal */}
      {showRepoModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-6xl w-full max-h-[90vh] overflow-hidden flex flex-col">
            {/* Modal Header */}
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold text-gray-800">
                    Select Repositories to Import
                  </h2>
                  <p className="text-gray-600 mt-1">
                    {selectedInstallation?.account_login} • {repositories.length} repositories available
                  </p>
                </div>
                <button
                  onClick={() => {
                    setShowRepoModal(false);
                    setSelectedRepos([]);
                  }}
                  className="text-gray-500 hover:text-gray-700 transition"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              {/* Selection Controls */}
              <div className="flex items-center gap-4 mt-4">
                <button
                  onClick={selectAllRepos}
                  className="px-4 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg transition"
                >
                  {selectedRepos.length === repositories.length ? 'Deselect All' : 'Select All'}
                </button>
                <span className="text-sm text-gray-600">
                  {selectedRepos.length} of {repositories.length} selected
                </span>
              </div>
            </div>

            {/* Repository List */}
            <div className="flex-1 overflow-y-auto p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {repositories.map(repo => (
                  <div
                    key={repo.id}
                    onClick={() => !repo.is_imported && toggleRepoSelection(repo.id)}
                    className={`
                      p-4 rounded-lg border-2 transition-all cursor-pointer
                      ${repo.is_imported 
                        ? 'bg-gray-50 border-gray-200 opacity-60 cursor-not-allowed' 
                        : selectedRepos.includes(repo.id)
                          ? 'border-purple-500 bg-purple-50'
                          : 'border-gray-200 hover:border-purple-300 hover:bg-purple-50/50'
                      }
                    `}
                  >
                    <div className="flex items-start gap-3">
                      <input
                        type="checkbox"
                        checked={selectedRepos.includes(repo.id)}
                        disabled={repo.is_imported}
                        onChange={() => {}}
                        className="mt-1"
                      />
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="font-semibold text-gray-800 truncate">
                            {repo.name}
                          </h4>
                          {repo.private && (
                            <span className="text-xs px-2 py-0.5 bg-yellow-100 text-yellow-800 rounded">
                              Private
                            </span>
                          )}
                          {repo.is_imported && (
                            <span className="text-xs px-2 py-0.5 bg-green-100 text-green-800 rounded">
                              ✓ Imported
                            </span>
                          )}
                        </div>
                        <p className="text-sm text-gray-600 line-clamp-2 mb-2">
                          {repo.description || 'No description'}
                        </p>
                        <div className="flex items-center gap-4 text-xs text-gray-500">
                          {repo.language && (
                            <span className="flex items-center gap-1">
                              <span className="w-3 h-3 rounded-full bg-blue-500"></span>
                              {repo.language}
                            </span>
                          )}
                          <span>⭐ {repo.stargazers_count}</span>
                          <span>🔱 {repo.forks_count}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Import Progress */}
            {importProgress && (
              <div className="p-4 bg-blue-50 border-t border-blue-200">
                <div className="flex items-center gap-3">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-blue-800">
                      Importing {importProgress.success} / {importProgress.total} repositories
                    </p>
                    {importProgress.failed > 0 && (
                      <p className="text-xs text-red-600 mt-1">
                        {importProgress.failed} failed
                      </p>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Modal Footer */}
            <div className="p-6 border-t border-gray-200 bg-gray-50">
              <div className="flex items-center justify-between">
                <div className="text-sm text-gray-600">
                  <span className="font-semibold">Pro Tip:</span> Webhooks will be automatically configured for real-time updates
                </div>
                <div className="flex gap-3">
                  <button
                    onClick={() => {
                      setShowRepoModal(false);
                      setSelectedRepos([]);
                    }}
                    className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-100 transition"
                    disabled={isImporting}
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleBulkImport}
                    disabled={isImporting || selectedRepos.length === 0}
                    className="px-8 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg font-semibold hover:from-purple-700 hover:to-blue-700 transition-all shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isImporting 
                      ? 'Importing...' 
                      : `Import ${selectedRepos.length} ${selectedRepos.length === 1 ? 'Repository' : 'Repositories'}`
                    }
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default GitHubAppConnect;

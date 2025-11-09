import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const RepositorySelection = () => {
  const [repositories, setRepositories] = useState([]);
  const [selectedRepos, setSelectedRepos] = useState(new Set());
  const [loading, setLoading] = useState(true);
  const [importing, setImporting] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filter, setFilter] = useState('all'); // all, public, private
  const navigate = useNavigate();

  useEffect(() => {
    fetchRepositories();
  }, []);

  const fetchRepositories = async () => {
    try {
      const githubToken = localStorage.getItem('github_token');
      const accessToken = localStorage.getItem('access_token');
      
      const response = await axios.get('http://localhost:8000/api/github/repositories/', {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'X-GitHub-Token': githubToken
        }
      });
      
      setRepositories(response.data.repositories);
    } catch (error) {
      console.error('Failed to fetch repositories:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleRepo = (repoId) => {
    const newSelected = new Set(selectedRepos);
    if (newSelected.has(repoId)) {
      newSelected.delete(repoId);
    } else {
      newSelected.add(repoId);
    }
    setSelectedRepos(newSelected);
  };

  const selectAll = () => {
    const filtered = getFilteredRepos();
    setSelectedRepos(new Set(filtered.map(r => r.id)));
  };

  const deselectAll = () => {
    setSelectedRepos(new Set());
  };

  const handleImport = async () => {
    if (selectedRepos.size === 0) return;

    setImporting(true);
    try {
      const githubToken = localStorage.getItem('github_token');
      const accessToken = localStorage.getItem('access_token');
      
      const repoNames = repositories
        .filter(r => selectedRepos.has(r.id))
        .map(r => r.full_name);

      const response = await axios.post(
        'http://localhost:8000/api/github/import/',
        { repositories: repoNames },
        {
          headers: {
            'Authorization': `Bearer ${accessToken}`,
            'X-GitHub-Token': githubToken
          }
        }
      );

      console.log('Import results:', response.data);
      navigate('/dashboard');
    } catch (error) {
      console.error('Import failed:', error);
      alert('Failed to import repositories. Please try again.');
    } finally {
      setImporting(false);
    }
  };

  const skipImport = () => {
    navigate('/dashboard');
  };

  const getFilteredRepos = () => {
    return repositories.filter(repo => {
      const matchesSearch = repo.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           repo.full_name.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesFilter = filter === 'all' || 
                           (filter === 'public' && !repo.private) ||
                           (filter === 'private' && repo.private);
      return matchesSearch && matchesFilter;
    });
  };

  const filteredRepos = getFilteredRepos();

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading your repositories...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Import Git Repositories
          </h1>
          <p className="text-lg text-gray-600">
            Select the repositories you'd like to import to Katalyst
          </p>
        </div>

        {/* Search and Filter Bar */}
        <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <input
                type="text"
                placeholder="Search repositories..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setFilter('all')}
                className={`px-4 py-2 rounded-lg ${
                  filter === 'all'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                All
              </button>
              <button
                onClick={() => setFilter('public')}
                className={`px-4 py-2 rounded-lg ${
                  filter === 'public'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Public
              </button>
              <button
                onClick={() => setFilter('private')}
                className={`px-4 py-2 rounded-lg ${
                  filter === 'private'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Private
              </button>
            </div>
          </div>

          {/* Selection Controls */}
          <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-200">
            <div className="text-sm text-gray-600">
              {selectedRepos.size} of {filteredRepos.length} repositories selected
            </div>
            <div className="flex gap-2">
              <button
                onClick={selectAll}
                className="text-sm text-blue-600 hover:text-blue-700 font-medium"
              >
                Select All
              </button>
              <span className="text-gray-400">|</span>
              <button
                onClick={deselectAll}
                className="text-sm text-blue-600 hover:text-blue-700 font-medium"
              >
                Deselect All
              </button>
            </div>
          </div>
        </div>

        {/* Repository List */}
        <div className="grid gap-4 mb-6">
          {filteredRepos.map((repo) => (
            <div
              key={repo.id}
              onClick={() => toggleRepo(repo.id)}
              className={`bg-white rounded-lg shadow-sm p-6 cursor-pointer transition-all ${
                selectedRepos.has(repo.id)
                  ? 'ring-2 ring-blue-500 bg-blue-50'
                  : 'hover:shadow-md'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <input
                      type="checkbox"
                      checked={selectedRepos.has(repo.id)}
                      onChange={() => {}}
                      className="h-5 w-5 text-blue-600 rounded focus:ring-blue-500"
                    />
                    <h3 className="text-lg font-semibold text-gray-900">
                      {repo.name}
                    </h3>
                    {repo.private && (
                      <span className="px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 rounded">
                        Private
                      </span>
                    )}
                    {repo.language && (
                      <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-700 rounded">
                        {repo.language}
                      </span>
                    )}
                  </div>
                  <p className="text-gray-600 text-sm mb-3">
                    {repo.description || 'No description available'}
                  </p>
                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    <span className="flex items-center gap-1">
                      ⭐ {repo.stars}
                    </span>
                    <span className="flex items-center gap-1">
                      🔀 {repo.forks}
                    </span>
                    <span>Updated {new Date(repo.updated_at).toLocaleDateString()}</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Action Buttons */}
        <div className="flex justify-between items-center bg-white rounded-lg shadow-sm p-6 sticky bottom-6">
          <button
            onClick={skipImport}
            className="px-6 py-3 text-gray-700 hover:text-gray-900 font-medium"
            disabled={importing}
          >
            Skip for now
          </button>
          <button
            onClick={handleImport}
            disabled={selectedRepos.size === 0 || importing}
            className={`px-8 py-3 rounded-lg font-medium transition-colors ${
              selectedRepos.size === 0 || importing
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            {importing ? (
              <span className="flex items-center gap-2">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                Importing...
              </span>
            ) : (
              `Import ${selectedRepos.size} ${selectedRepos.size === 1 ? 'Repository' : 'Repositories'}`
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default RepositorySelection;

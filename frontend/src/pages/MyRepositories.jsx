import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  FolderIcon, 
  PlusIcon, 
  ClockIcon,
  CodeBracketIcon,
  LockClosedIcon,
  GlobeAltIcon
} from '@heroicons/react/24/outline';
import CreateRepository from '../components/CreateRepository';

const MyRepositories = () => {
  const [repositories, setRepositories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);

  useEffect(() => {
    fetchCurrentUser();
  }, []);

  useEffect(() => {
    if (currentUser) {
      fetchRepositories();
    }
  }, [currentUser]);

  const fetchCurrentUser = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8000/api/auth/profile/', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setCurrentUser(data.user);
      }
    } catch (err) {
      console.error('Failed to fetch user:', err);
    }
  };

  const fetchRepositories = async () => {
    if (!currentUser) return;
    
    setLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:8000/api/git/${currentUser.username}/repositories/`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch repositories');
      }

      const data = await response.json();
      setRepositories(data.repositories || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    
    if (days > 30) {
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    } else if (days > 0) {
      return `${days} day${days > 1 ? 's' : ''} ago`;
    } else if (hours > 0) {
      return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    } else if (minutes > 0) {
      return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    } else {
      return 'Just now';
    }
  };

  const handleRepositoryCreated = (repo) => {
    setShowCreateForm(false);
    fetchRepositories();
  };

  if (showCreateForm) {
    return (
      <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
        <div className="max-w-3xl mx-auto">
          <button
            onClick={() => setShowCreateForm(false)}
            className="mb-4 text-indigo-600 hover:text-indigo-700 font-medium"
          >
            ← Back to Repositories
          </button>
          <CreateRepository onRepositoryCreated={handleRepositoryCreated} />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">My Repositories</h1>
            <p className="text-gray-600 mt-2">
              Self-hosted Git repositories on your LazySheeps instance
            </p>
          </div>
          <button
            onClick={() => setShowCreateForm(true)}
            className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            New Repository
          </button>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        )}

        {/* Empty State */}
        {!loading && repositories.length === 0 && (
          <div className="text-center py-12 bg-white rounded-lg shadow">
            <FolderIcon className="h-16 w-16 mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              No repositories yet
            </h3>
            <p className="text-gray-600 mb-6">
              Create your first repository to start hosting code on LazySheeps
            </p>
            <button
              onClick={() => setShowCreateForm(true)}
              className="inline-flex items-center px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
            >
              <PlusIcon className="h-5 w-5 mr-2" />
              Create Repository
            </button>
          </div>
        )}

        {/* Repository List */}
        {!loading && repositories.length > 0 && (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {repositories.map((repo) => (
              <Link
                key={repo.id}
                to={`/git/${currentUser?.username}/${repo.name}`}
                className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-6 border border-gray-200 hover:border-indigo-300"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center">
                    <FolderIcon className="h-6 w-6 text-indigo-600 mr-2" />
                    <h3 className="text-lg font-semibold text-gray-900">
                      {repo.name}
                    </h3>
                  </div>
                  {repo.is_private ? (
                    <LockClosedIcon className="h-5 w-5 text-gray-400" title="Private" />
                  ) : (
                    <GlobeAltIcon className="h-5 w-5 text-gray-400" title="Public" />
                  )}
                </div>

                {repo.description && (
                  <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                    {repo.description}
                  </p>
                )}

                <div className="flex items-center text-xs text-gray-500 space-x-4">
                  <div className="flex items-center">
                    <CodeBracketIcon className="h-4 w-4 mr-1" />
                    <span>{repo.default_branch || 'main'}</span>
                  </div>
                  <div className="flex items-center">
                    <ClockIcon className="h-4 w-4 mr-1" />
                    <span>Updated {formatDate(repo.updated_at)}</span>
                  </div>
                </div>

                {repo.commit_count !== undefined && (
                  <div className="mt-3 pt-3 border-t border-gray-100">
                    <span className="text-xs text-gray-500">
                      {repo.commit_count} commit{repo.commit_count !== 1 ? 's' : ''}
                    </span>
                  </div>
                )}
              </Link>
            ))}
          </div>
        )}

        {/* Info Card */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h4 className="text-sm font-semibold text-blue-900 mb-2">
            💡 How to use your repositories
          </h4>
          <div className="text-sm text-blue-800 space-y-2">
            <p>
              <strong>1. Clone your repository:</strong> Use the HTTPS or SSH URL from the repository page
            </p>
            <p>
              <strong>2. Push your code:</strong> Just like GitHub, use <code className="bg-blue-100 px-1 rounded">git push origin main</code>
            </p>
            <p>
              <strong>3. Browse your code:</strong> Click any repository to view files, commits, and branches
            </p>
            <p>
              <strong>4. Collaborate:</strong> Share repository URLs with your team members
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MyRepositories;

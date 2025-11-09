import React, { useState, useEffect } from 'react';
import { FolderIcon, DocumentIcon, ClockIcon, CodeBracketIcon } from '@heroicons/react/24/outline';

const GitRepositoryBrowser = ({ username, repoName }) => {
  const [repository, setRepository] = useState(null);
  const [files, setFiles] = useState([]);
  const [currentPath, setCurrentPath] = useState('');
  const [currentBranch, setCurrentBranch] = useState('main');
  const [fileContent, setFileContent] = useState(null);
  const [commits, setCommits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchRepositoryData();
  }, [username, repoName, currentBranch, currentPath]);

  const fetchRepositoryData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      
      const response = await fetch(
        `http://localhost:8000/api/git/${username}/${repoName}/browse/?branch=${currentBranch}&path=${currentPath}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch repository data');
      }

      const data = await response.json();
      setRepository(data.repository);
      setFiles(data.files);
      setCommits(data.recent_commits);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const openFile = async (file) => {
    if (file.type === 'directory') {
      setCurrentPath(file.path);
      setFileContent(null);
    } else {
      try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(
          `http://localhost:8000/api/git/${username}/${repoName}/file/?branch=${currentBranch}&path=${file.path}`,
          {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          }
        );

        if (!response.ok) {
          throw new Error('Failed to fetch file content');
        }

        const data = await response.json();
        setFileContent(data);
      } catch (err) {
        setError(err.message);
      }
    }
  };

  const navigateUp = () => {
    const parts = currentPath.split('/');
    parts.pop();
    setCurrentPath(parts.join('/'));
    setFileContent(null);
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp * 1000).toLocaleString();
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-600">Error: {error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Repository Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-gray-900">
            {username} / {repoName}
          </h2>
          
          {/* Branch Selector */}
          <select
            value={currentBranch}
            onChange={(e) => setCurrentBranch(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
          >
            {repository?.branches.map(branch => (
              <option key={branch} value={branch}>{branch}</option>
            ))}
          </select>
        </div>

        {/* Breadcrumb */}
        <div className="flex items-center space-x-2 text-sm text-gray-600">
          <button
            onClick={() => setCurrentPath('')}
            className="hover:text-indigo-600"
          >
            {repoName}
          </button>
          {currentPath && currentPath.split('/').map((part, index, arr) => (
            <React.Fragment key={index}>
              <span>/</span>
              <button
                onClick={() => {
                  const newPath = arr.slice(0, index + 1).join('/');
                  setCurrentPath(newPath);
                }}
                className="hover:text-indigo-600"
              >
                {part}
              </button>
            </React.Fragment>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* File Browser */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow">
            {/* Navigation */}
            {currentPath && (
              <div className="border-b border-gray-200 p-4">
                <button
                  onClick={navigateUp}
                  className="text-indigo-600 hover:text-indigo-700 font-medium"
                >
                  ← Back
                </button>
              </div>
            )}

            {/* File Content View */}
            {fileContent ? (
              <div className="p-6">
                <div className="mb-4 flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-gray-900">
                    {fileContent.path.split('/').pop()}
                  </h3>
                  <span className="text-sm text-gray-500">
                    {formatFileSize(fileContent.size)}
                  </span>
                </div>
                <pre className="bg-gray-50 rounded-lg p-4 overflow-x-auto">
                  <code className="text-sm">{fileContent.content}</code>
                </pre>
                <button
                  onClick={() => setFileContent(null)}
                  className="mt-4 text-indigo-600 hover:text-indigo-700"
                >
                  ← Back to files
                </button>
              </div>
            ) : (
              /* File List */
              <div className="divide-y divide-gray-200">
                {files.length === 0 ? (
                  <div className="p-8 text-center text-gray-500">
                    <p>No files found</p>
                  </div>
                ) : (
                  files.map((file) => (
                    <button
                      key={file.path}
                      onClick={() => openFile(file)}
                      className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors text-left"
                    >
                      <div className="flex items-center space-x-3">
                        {file.type === 'directory' ? (
                          <FolderIcon className="h-5 w-5 text-blue-500" />
                        ) : (
                          <DocumentIcon className="h-5 w-5 text-gray-400" />
                        )}
                        <span className="text-gray-900 font-medium">{file.name}</span>
                      </div>
                      {file.type === 'file' && (
                        <span className="text-sm text-gray-500">
                          {formatFileSize(file.size)}
                        </span>
                      )}
                    </button>
                  ))
                )}
              </div>
            )}
          </div>
        </div>

        {/* Recent Commits */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <ClockIcon className="h-5 w-5 mr-2" />
              Recent Commits
            </h3>
            <div className="space-y-4">
              {commits.length === 0 ? (
                <p className="text-gray-500 text-sm">No commits yet</p>
              ) : (
                commits.map((commit) => (
                  <div key={commit.sha} className="border-l-2 border-indigo-500 pl-4">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {commit.message}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      {commit.author}
                    </p>
                    <p className="text-xs text-gray-400 mt-1">
                      {formatTimestamp(commit.timestamp)}
                    </p>
                    <p className="text-xs text-gray-400 font-mono">
                      {commit.sha.substring(0, 7)}
                    </p>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GitRepositoryBrowser;

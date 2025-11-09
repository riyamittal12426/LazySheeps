import React, { useState } from 'react';
import { PlusIcon, DocumentDuplicateIcon, CheckIcon } from '@heroicons/react/24/outline';

const CreateRepository = ({ onRepositoryCreated }) => {
  const [formData, setFormData] = useState({
    name: '',
    description: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [createdRepo, setCreatedRepo] = useState(null);
  const [copied, setCopied] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8000/api/git/create/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Failed to create repository');
      }

      const data = await response.json();
      setCreatedRepo(data.repository);
      
      // Reset form
      setFormData({ name: '', description: '' });
      
      if (onRepositoryCreated) {
        onRepositoryCreated(data.repository);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (createdRepo) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-8">
        <div className="text-center mb-6">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
            <CheckIcon className="h-8 w-8 text-green-600" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Repository Created!
          </h2>
          <p className="text-gray-600">
            Your repository <span className="font-semibold">{createdRepo.name}</span> is ready to use
          </p>
        </div>

        <div className="space-y-4">
          {/* Clone URL */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Clone URL (HTTPS)
            </label>
            <div className="flex">
              <input
                type="text"
                value={createdRepo.clone_url}
                readOnly
                className="flex-1 px-4 py-2 border border-gray-300 rounded-l-lg bg-gray-50 text-sm font-mono"
              />
              <button
                onClick={() => copyToClipboard(createdRepo.clone_url)}
                className="px-4 py-2 bg-indigo-600 text-white rounded-r-lg hover:bg-indigo-700 transition-colors"
              >
                {copied ? <CheckIcon className="h-5 w-5" /> : <DocumentDuplicateIcon className="h-5 w-5" />}
              </button>
            </div>
          </div>

          {/* SSH URL */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Clone URL (SSH)
            </label>
            <div className="flex">
              <input
                type="text"
                value={createdRepo.ssh_url}
                readOnly
                className="flex-1 px-4 py-2 border border-gray-300 rounded-l-lg bg-gray-50 text-sm font-mono"
              />
              <button
                onClick={() => copyToClipboard(createdRepo.ssh_url)}
                className="px-4 py-2 bg-indigo-600 text-white rounded-r-lg hover:bg-indigo-700 transition-colors"
              >
                {copied ? <CheckIcon className="h-5 w-5" /> : <DocumentDuplicateIcon className="h-5 w-5" />}
              </button>
            </div>
          </div>

          {/* Setup Commands */}
          <div className="bg-gray-900 rounded-lg p-6 text-white">
            <h3 className="text-sm font-semibold mb-3">Quick Setup</h3>
            <div className="space-y-3">
              <div>
                <p className="text-xs text-gray-400 mb-1">Create a new repository:</p>
                <code className="block text-sm font-mono bg-gray-800 p-2 rounded">
                  <div>git init</div>
                  <div>git add .</div>
                  <div>git commit -m "Initial commit"</div>
                  <div>git remote add origin {createdRepo.clone_url}</div>
                  <div>git push -u origin main</div>
                </code>
              </div>
              <div>
                <p className="text-xs text-gray-400 mb-1">Push an existing repository:</p>
                <code className="block text-sm font-mono bg-gray-800 p-2 rounded">
                  <div>git remote add origin {createdRepo.clone_url}</div>
                  <div>git push -u origin main</div>
                </code>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-6 flex justify-center">
          <button
            onClick={() => setCreatedRepo(null)}
            className="px-6 py-2 text-indigo-600 hover:text-indigo-700 font-medium"
          >
            Create Another Repository
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-8">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Create a New Repository
        </h2>
        <p className="text-gray-600">
          Create a local Git repository hosted on your LazySheeps instance
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Repository Name */}
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
            Repository Name *
          </label>
          <input
            type="text"
            id="name"
            required
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            placeholder="my-awesome-project"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          />
          <p className="mt-1 text-sm text-gray-500">
            Will be converted to lowercase with dashes
          </p>
        </div>

        {/* Description */}
        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
            Description (optional)
          </label>
          <textarea
            id="description"
            rows="3"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            placeholder="A brief description of your repository..."
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          />
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        )}

        {/* Submit Button */}
        <div className="flex justify-end space-x-4">
          <button
            type="button"
            onClick={() => setFormData({ name: '', description: '' })}
            className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Creating...
              </>
            ) : (
              <>
                <PlusIcon className="h-5 w-5 mr-2" />
                Create Repository
              </>
            )}
          </button>
        </div>
      </form>

      {/* Info Box */}
      <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="text-sm font-semibold text-blue-900 mb-2">ℹ️ What happens next?</h4>
        <ul className="text-sm text-blue-800 space-y-1 list-disc list-inside">
          <li>A bare Git repository will be created on the server</li>
          <li>You'll receive URLs for cloning via HTTPS or SSH</li>
          <li>Push your code just like you would to GitHub</li>
          <li>All commits and files will be stored locally on your server</li>
          <li>View and browse your code through the LazySheeps dashboard</li>
        </ul>
      </div>
    </div>
  );
};

export default CreateRepository;

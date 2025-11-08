import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import axios from 'axios';

const GitHubAppCallback = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [status, setStatus] = useState('connecting');
  const [error, setError] = useState(null);

  useEffect(() => {
    const handleCallback = async () => {
      const installation_id = searchParams.get('installation_id');
      const setup_action = searchParams.get('setup_action');
      
      if (!installation_id) {
        setError('No installation ID provided');
        setStatus('error');
        return;
      }

      try {
        setStatus('connecting');
        const token = localStorage.getItem('token');
        
        const response = await axios.get(`http://localhost:8000/api/github-app/callback/`, {
          params: { installation_id, setup_action },
          headers: { Authorization: `Bearer ${token}` }
        });

        if (response.data.success) {
          setStatus('success');
          setTimeout(() => {
            navigate('/dashboard?app_connected=true');
          }, 2000);
        } else {
          setError('Failed to connect GitHub App');
          setStatus('error');
        }
      } catch (error) {
        console.error('Connection failed:', error);
        setError(error.response?.data?.error || 'Failed to connect GitHub App');
        setStatus('error');
        setTimeout(() => {
          navigate('/dashboard?error=connection_failed');
        }, 3000);
      }
    };

    handleCallback();
  }, [searchParams, navigate]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        <div className="bg-white rounded-2xl shadow-2xl p-8">
          {status === 'connecting' && (
            <div className="text-center">
              <div className="relative inline-flex mb-6">
                <div className="animate-spin rounded-full h-20 w-20 border-b-4 border-purple-600"></div>
                <div className="absolute inset-0 flex items-center justify-center">
                  <svg className="w-10 h-10 text-purple-600" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                  </svg>
                </div>
              </div>
              <h2 className="text-2xl font-bold text-gray-800 mb-2">
                Connecting GitHub App
              </h2>
              <p className="text-gray-600 mb-6">
                Setting up organization access and configuring webhooks...
              </p>
              <div className="space-y-2 text-sm text-gray-500">
                <div className="flex items-center justify-center gap-2">
                  <div className="animate-pulse w-2 h-2 bg-purple-600 rounded-full"></div>
                  <span>Authenticating with GitHub</span>
                </div>
                <div className="flex items-center justify-center gap-2">
                  <div className="animate-pulse w-2 h-2 bg-purple-600 rounded-full" style={{ animationDelay: '0.2s' }}></div>
                  <span>Fetching organization details</span>
                </div>
                <div className="flex items-center justify-center gap-2">
                  <div className="animate-pulse w-2 h-2 bg-purple-600 rounded-full" style={{ animationDelay: '0.4s' }}></div>
                  <span>Configuring permissions</span>
                </div>
              </div>
            </div>
          )}

          {status === 'success' && (
            <div className="text-center">
              <div className="mb-6">
                <div className="inline-flex items-center justify-center w-20 h-20 bg-green-100 rounded-full">
                  <svg className="w-10 h-10 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
              </div>
              <h2 className="text-2xl font-bold text-gray-800 mb-2">
                Successfully Connected! 🎉
              </h2>
              <p className="text-gray-600 mb-4">
                Your GitHub organization is now connected
              </p>
              <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-sm text-left">
                <p className="font-semibold text-green-800 mb-2">What's next?</p>
                <ul className="space-y-1 text-green-700">
                  <li>✓ Import repositories with one click</li>
                  <li>✓ Automatic webhook configuration</li>
                  <li>✓ Real-time sync enabled</li>
                </ul>
              </div>
              <p className="text-sm text-gray-500 mt-4">
                Redirecting to dashboard...
              </p>
            </div>
          )}

          {status === 'error' && (
            <div className="text-center">
              <div className="mb-6">
                <div className="inline-flex items-center justify-center w-20 h-20 bg-red-100 rounded-full">
                  <svg className="w-10 h-10 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </div>
              </div>
              <h2 className="text-2xl font-bold text-gray-800 mb-2">
                Connection Failed
              </h2>
              <p className="text-gray-600 mb-4">
                {error || 'An error occurred while connecting'}
              </p>
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-sm text-left mb-4">
                <p className="font-semibold text-red-800 mb-2">Troubleshooting:</p>
                <ul className="space-y-1 text-red-700">
                  <li>• Make sure you're logged in</li>
                  <li>• Check your organization permissions</li>
                  <li>• Try connecting again</li>
                </ul>
              </div>
              <button
                onClick={() => navigate('/dashboard')}
                className="px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg font-semibold hover:from-purple-700 hover:to-blue-700 transition-all shadow-lg"
              >
                Return to Dashboard
              </button>
            </div>
          )}
        </div>

        {/* Additional Info */}
        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600">
            Having trouble?{' '}
            <a href="/help" className="text-purple-600 hover:text-purple-700 font-medium">
              Get help
            </a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default GitHubAppCallback;

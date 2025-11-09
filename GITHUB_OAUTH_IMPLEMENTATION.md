# GitHub OAuth Implementation - Complete Guide

This guide shows how to implement GitHub OAuth with full repository access, allowing users to browse and import their GitHub repositories directly into Katalyst (similar to Vercel's workflow).

## Part 1: GitHub OAuth App Setup

### Create GitHub OAuth Application

1. **Go to GitHub Developer Settings**
   - URL: https://github.com/settings/developers
   - Click **"OAuth Apps"** (left sidebar)
   - Click **"New OAuth App"** button

2. **Configure OAuth App Settings**

   **Application name:**
   ```
   Katalyst
   ```

   **Homepage URL:**
   ```
   Development: http://localhost:5173
   Production: https://your-domain.com
   ```

   **Application description:** (optional)
   ```
   GitHub Repository Analytics and Collaboration Platform
   ```

   **Authorization callback URL:**
   ```
   https://your-clerk-frontend-api.clerk.accounts.dev/v1/oauth_callback
   ```
   ⚠️ Get this exact URL from: Clerk Dashboard → User & Authentication → Social Connections → GitHub

3. **Save Credentials**
   - Click **"Register application"**
   - Copy the **Client ID**
   - Click **"Generate a new client secret"**
   - Copy the **Client Secret** (shown only once!)

## Part 2: Clerk Configuration

### Configure GitHub in Clerk Dashboard

1. **Enable GitHub Provider**
   - Go to Clerk Dashboard: https://dashboard.clerk.com
   - Navigate to: **User & Authentication** → **Social Connections**
   - Find **GitHub** and toggle it **ON**

2. **Add GitHub Credentials**
   - Click **"Configure"** on GitHub
   - Paste your **Client ID** from GitHub
   - Paste your **Client Secret** from GitHub

3. **Configure OAuth Scopes** ⚠️ CRITICAL STEP
   
   In the GitHub OAuth configuration, set these scopes:
   ```
   user:email read:user repo
   ```

   **What each scope does:**
   - `user:email` - Access user's email address
   - `read:user` - Read user profile information  
   - `repo` - **Full access to public and private repositories**

   💡 The `repo` scope is what gives access to all repositories!

4. **Copy Callback URL**
   - Clerk will show an **Authorization callback URL**
   - Copy this URL
   - Go back to your GitHub OAuth App settings
   - Paste it as the callback URL
   - Click **"Update application"**

### Create JWT Template for GitHub Token

1. **Go to JWT Templates**
   - Clerk Dashboard → **JWT Templates**
   - Click **"New template"** → **"Blank"**

2. **Configure Template**
   - **Name:** `oauth_github`
   - **Token lifetime:** 3600 (1 hour)

3. **Add Token Configuration**
   Paste this JSON:
   ```json
   {
     "aud": "authenticated",
     "azp": "{{app.id}}",
     "exp": {{session.expire_at}},
     "iat": {{session.created_at}},
     "iss": "{{app.frontend_api}}",
     "nbf": {{session.created_at}},
     "sid": "{{session.id}}",
     "sub": "{{user.id}}",
     "github_token": "{{user.external_accounts.github.token}}"
   }
   ```

4. **Save template**

This makes the GitHub OAuth token accessible via `getToken({ template: 'oauth_github' })` in your frontend.

## Part 3: Backend Implementation

### Install Required Packages

```bash
cd backend
pip install PyGithub==2.1.1 requests==2.31.0
```

Add to `requirements.txt`:
```
PyGithub==2.1.1
requests==2.31.0
```

### Create GitHub OAuth API File

Create `backend/api/github_oauth.py`:

```python
import requests
import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import Repository, Contributor, Commit
from .github_importer import import_repository_data

@csrf_exempt
@require_http_methods(["POST"])
def get_user_github_repos(request):
    """
    Fetch all repositories for the authenticated user using their GitHub OAuth token.
    This endpoint receives the GitHub token from Clerk and fetches the user's repos.
    """
    try:
        data = json.loads(request.body)
        github_token = data.get('github_token')
        
        if not github_token:
            return JsonResponse({
                'success': False,
                'error': 'GitHub token not provided'
            }, status=400)
        
        # Set up GitHub API headers
        headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # Fetch user's repositories (with pagination support)
        all_repos = []
        page = 1
        per_page = 100
        
        while True:
            response = requests.get(
                'https://api.github.com/user/repos',
                headers=headers,
                params={
                    'per_page': per_page,
                    'page': page,
                    'sort': 'updated',
                    'affiliation': 'owner,collaborator,organization_member'
                }
            )
            
            if response.status_code != 200:
                return JsonResponse({
                    'success': False,
                    'error': f'Failed to fetch repositories: {response.json().get("message", "Unknown error")}'
                }, status=response.status_code)
            
            repos = response.json()
            if not repos:
                break
                
            all_repos.extend(repos)
            
            # Check if there are more pages
            if len(repos) < per_page:
                break
            page += 1
        
        # Format repository data
        formatted_repos = []
        for repo in all_repos:
            formatted_repos.append({
                'id': repo['id'],
                'name': repo['name'],
                'full_name': repo['full_name'],
                'description': repo.get('description', ''),
                'url': repo['html_url'],
                'clone_url': repo['clone_url'],
                'private': repo['private'],
                'language': repo.get('language', 'Unknown'),
                'stars': repo['stargazers_count'],
                'forks': repo['forks_count'],
                'open_issues': repo['open_issues_count'],
                'size': repo['size'],
                'created_at': repo['created_at'],
                'updated_at': repo['updated_at'],
                'default_branch': repo['default_branch'],
                'owner': {
                    'login': repo['owner']['login'],
                    'avatar_url': repo['owner']['avatar_url'],
                    'type': repo['owner']['type']
                },
                'topics': repo.get('topics', []),
                'archived': repo.get('archived', False),
                'disabled': repo.get('disabled', False),
            })
        
        return JsonResponse({
            'success': True,
            'repositories': formatted_repos,
            'total': len(formatted_repos)
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON in request body'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def import_github_repo(request):
    """
    Import a specific GitHub repository into Katalyst.
    Fetches commits, contributors, and generates analytics.
    """
    try:
        data = json.loads(request.body)
        github_token = data.get('github_token')
        repo_full_name = data.get('repo_full_name')  # Format: "owner/repo"
        
        if not github_token or not repo_full_name:
            return JsonResponse({
                'success': False,
                'error': 'Missing required parameters: github_token and repo_full_name'
            }, status=400)
        
        # Validate repo name format
        if '/' not in repo_full_name:
            return JsonResponse({
                'success': False,
                'error': 'Invalid repository name format. Use "owner/repo"'
            }, status=400)
        
        # Check if repository already exists
        existing_repo = Repository.objects.filter(full_name=repo_full_name).first()
        if existing_repo:
            return JsonResponse({
                'success': False,
                'error': f'Repository "{repo_full_name}" is already imported',
                'repository_id': existing_repo.id
            }, status=409)
        
        # Import the repository using existing importer
        try:
            result = import_repository_data(repo_full_name, github_token)
            
            return JsonResponse({
                'success': True,
                'message': f'Repository "{repo_full_name}" imported successfully',
                'repository': {
                    'id': result.get('id'),
                    'name': result.get('name'),
                    'full_name': result.get('full_name'),
                    'commits_count': result.get('commits_count', 0),
                    'contributors_count': result.get('contributors_count', 0)
                }
            })
        except Exception as import_error:
            return JsonResponse({
                'success': False,
                'error': f'Failed to import repository: {str(import_error)}'
            }, status=500)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON in request body'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def check_github_connection(request):
    """
    Check if the user's GitHub connection is valid.
    """
    try:
        github_token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not github_token:
            return JsonResponse({
                'success': False,
                'connected': False,
                'error': 'No GitHub token provided'
            })
        
        # Test the token by fetching user info
        headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        response = requests.get('https://api.github.com/user', headers=headers)
        
        if response.status_code == 200:
            user_data = response.json()
            return JsonResponse({
                'success': True,
                'connected': True,
                'user': {
                    'login': user_data['login'],
                    'name': user_data.get('name'),
                    'avatar_url': user_data['avatar_url'],
                    'public_repos': user_data['public_repos'],
                    'total_private_repos': user_data.get('total_private_repos', 0)
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'connected': False,
                'error': 'Invalid or expired GitHub token'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'connected': False,
            'error': str(e)
        }, status=500)
```

### Update URL Configuration

Edit `backend/config/urls.py`:

```python
from django.contrib import admin
from django.urls import path, include
from api import views, github_oauth

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Existing API endpoints
    path('api/repositories/', views.repository_list, name='repository_list'),
    # ... other existing routes ...
    
    # GitHub OAuth endpoints
    path('api/github/repos/', github_oauth.get_user_github_repos, name='github_repos'),
    path('api/github/import/', github_oauth.import_github_repo, name='import_repo'),
    path('api/github/check/', github_oauth.check_github_connection, name='check_github'),
]
```

## Part 4: Frontend Implementation

### Create GitHub Repository Browser Component

Create `frontend/src/components/GitHubRepoBrowser.jsx`:

```jsx
import React, { useState, useEffect } from 'react';
import { useAuth } from '@clerk/clerk-react';
import axios from 'axios';
import { 
  FolderIcon, 
  LockClosedIcon, 
  StarIcon, 
  ArrowPathIcon,
  CheckCircleIcon 
} from '@heroicons/react/24/outline';

const GitHubRepoBrowser = () => {
  const { getToken } = useAuth();
  const [repos, setRepos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [importing, setImporting] = useState({});
  const [imported, setImported] = useState({});
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all'); // 'all', 'public', 'private'

  useEffect(() => {
    fetchGitHubRepos();
  }, []);

  const fetchGitHubRepos = async () => {
    try {
      setLoading(true);
      setError(null);

      // Get GitHub OAuth token from Clerk
      const githubToken = await getToken({ template: 'oauth_github' });

      if (!githubToken) {
        setError('GitHub account not connected. Please connect your GitHub account in profile settings.');
        setLoading(false);
        return;
      }

      // Fetch repos from backend
      const response = await axios.post('http://localhost:8000/api/github/repos/', {
        github_token: githubToken
      });

      if (response.data.success) {
        setRepos(response.data.repositories);
      } else {
        setError(response.data.error || 'Failed to fetch repositories');
      }
    } catch (err) {
      console.error('Error fetching repos:', err);
      if (err.response?.status === 401) {
        setError('GitHub token expired. Please reconnect your GitHub account.');
      } else {
        setError('Failed to fetch repositories. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleImport = async (repo) => {
    try {
      setImporting(prev => ({ ...prev, [repo.id]: true }));

      const githubToken = await getToken({ template: 'oauth_github' });

      const response = await axios.post('http://localhost:8000/api/github/import/', {
        github_token: githubToken,
        repo_full_name: repo.full_name
      });

      if (response.data.success) {
        setImported(prev => ({ ...prev, [repo.id]: true }));
        alert(`✅ Repository "${repo.name}" imported successfully!`);
      } else {
        alert(`❌ Failed to import: ${response.data.error}`);
      }
    } catch (err) {
      console.error('Import error:', err);
      if (err.response?.status === 409) {
        alert('This repository is already imported.');
        setImported(prev => ({ ...prev, [repo.id]: true }));
      } else {
        alert('Failed to import repository. Please try again.');
      }
    } finally {
      setImporting(prev => ({ ...prev, [repo.id]: false }));
    }
  };

  const filteredRepos = repos.filter(repo => {
    if (filter === 'public') return !repo.private;
    if (filter === 'private') return repo.private;
    return true;
  });

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <ArrowPathIcon className="w-12 h-12 text-purple-500 animate-spin mb-4" />
        <div className="text-white text-lg">Loading your GitHub repositories...</div>
        <div className="text-gray-400 text-sm mt-2">This may take a moment</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-500/10 border border-red-500 rounded-lg p-6 text-red-400">
        <p className="font-semibold text-lg mb-2">⚠️ Error</p>
        <p className="text-sm mb-4">{error}</p>
        <button
          onClick={fetchGitHubRepos}
          className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Your GitHub Repositories</h2>
          <p className="text-gray-400 text-sm mt-1">
            Found {filteredRepos.length} {filter !== 'all' && filter} repositories
          </p>
        </div>
        <button
          onClick={fetchGitHubRepos}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50"
        >
          <ArrowPathIcon className="w-5 h-5" />
          Refresh
        </button>
      </div>

      {/* Filter Buttons */}
      <div className="flex items-center gap-2">
        <button
          onClick={() => setFilter('all')}
          className={`px-4 py-2 rounded-lg transition-colors ${
            filter === 'all' 
              ? 'bg-purple-600 text-white' 
              : 'bg-white/5 text-gray-400 hover:bg-white/10'
          }`}
        >
          All ({repos.length})
        </button>
        <button
          onClick={() => setFilter('public')}
          className={`px-4 py-2 rounded-lg transition-colors ${
            filter === 'public' 
              ? 'bg-purple-600 text-white' 
              : 'bg-white/5 text-gray-400 hover:bg-white/10'
          }`}
        >
          Public ({repos.filter(r => !r.private).length})
        </button>
        <button
          onClick={() => setFilter('private')}
          className={`px-4 py-2 rounded-lg transition-colors ${
            filter === 'private' 
              ? 'bg-purple-600 text-white' 
              : 'bg-white/5 text-gray-400 hover:bg-white/10'
          }`}
        >
          Private ({repos.filter(r => r.private).length})
        </button>
      </div>

      {/* Repository List */}
      {filteredRepos.length === 0 ? (
        <div className="text-center py-12 text-gray-400">
          <FolderIcon className="w-16 h-16 mx-auto mb-4 opacity-50" />
          <p className="text-lg">No {filter !== 'all' && filter} repositories found</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {filteredRepos.map((repo) => (
            <div
              key={repo.id}
              className={`bg-white/5 backdrop-blur-lg border rounded-lg p-5 hover:bg-white/10 transition-all ${
                imported[repo.id] ? 'border-green-500/50' : 'border-white/10'
              }`}
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  {/* Title Row */}
                  <div className="flex items-center gap-2 mb-2 flex-wrap">
                    <h3 className="text-lg font-semibold text-white truncate">
                      {repo.name}
                    </h3>
                    {repo.private && (
                      <span className="flex items-center gap-1 px-2 py-0.5 bg-yellow-500/20 text-yellow-400 text-xs rounded">
                        <LockClosedIcon className="w-3 h-3" />
                        Private
                      </span>
                    )}
                    {repo.language && (
                      <span className="px-2 py-0.5 bg-blue-500/20 text-blue-400 text-xs rounded">
                        {repo.language}
                      </span>
                    )}
                    {repo.archived && (
                      <span className="px-2 py-0.5 bg-gray-500/20 text-gray-400 text-xs rounded">
                        Archived
                      </span>
                    )}
                    {imported[repo.id] && (
                      <span className="flex items-center gap-1 px-2 py-0.5 bg-green-500/20 text-green-400 text-xs rounded">
                        <CheckCircleIcon className="w-3 h-3" />
                        Imported
                      </span>
                    )}
                  </div>

                  {/* Description */}
                  <p className="text-gray-400 text-sm mb-3 line-clamp-2">
                    {repo.description || 'No description provided'}
                  </p>

                  {/* Stats Row */}
                  <div className="flex items-center gap-4 text-sm text-gray-500 flex-wrap">
                    <span className="flex items-center gap-1">
                      <StarIcon className="w-4 h-4" />
                      {repo.stars.toLocaleString()}
                    </span>
                    <span>Forks: {repo.forks.toLocaleString()}</span>
                    <span>Issues: {repo.open_issues}</span>
                    <span>Size: {(repo.size / 1024).toFixed(1)} MB</span>
                    <span className="text-gray-600">•</span>
                    <span>Updated: {new Date(repo.updated_at).toLocaleDateString()}</span>
                  </div>

                  {/* Topics */}
                  {repo.topics && repo.topics.length > 0 && (
                    <div className="flex items-center gap-2 mt-3 flex-wrap">
                      {repo.topics.slice(0, 5).map(topic => (
                        <span 
                          key={topic}
                          className="px-2 py-1 bg-purple-500/10 text-purple-400 text-xs rounded"
                        >
                          {topic}
                        </span>
                      ))}
                      {repo.topics.length > 5 && (
                        <span className="text-gray-500 text-xs">
                          +{repo.topics.length - 5} more
                        </span>
                      )}
                    </div>
                  )}
                </div>

                {/* Import Button */}
                <button
                  onClick={() => handleImport(repo)}
                  disabled={importing[repo.id] || imported[repo.id] || repo.archived}
                  className={`flex-shrink-0 px-5 py-2.5 rounded-lg font-medium transition-all disabled:cursor-not-allowed ${
                    imported[repo.id]
                      ? 'bg-green-600/20 text-green-400 cursor-default'
                      : importing[repo.id]
                      ? 'bg-purple-600/50 text-white cursor-wait'
                      : repo.archived
                      ? 'bg-gray-600/20 text-gray-500'
                      : 'bg-gradient-to-r from-purple-600 to-blue-600 text-white hover:from-purple-700 hover:to-blue-700'
                  }`}
                >
                  {imported[repo.id] 
                    ? '✓ Imported' 
                    : importing[repo.id] 
                    ? 'Importing...' 
                    : repo.archived
                    ? 'Archived'
                    : 'Import'}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default GitHubRepoBrowser;
```

### Update Import Repository Page

Update `frontend/src/components/ImportRepository.jsx`:

```jsx
import React, { useState } from 'react';
import { useUser } from '@clerk/clerk-react';
import GitHubRepoBrowser from './GitHubRepoBrowser';
import { CodeBracketIcon, FolderArrowDownIcon } from '@heroicons/react/24/outline';

const ImportRepository = () => {
  const { user } = useUser();
  const [viewMode, setViewMode] = useState('options'); // 'options', 'browse', 'manual'

  // Check if user has connected GitHub
  const hasGitHubConnected = user?.externalAccounts?.some(
    account => account.provider === 'oauth_github'
  );

  return (
    <div className="space-y-6">
      {/* Back Button */}
      {viewMode !== 'options' && (
        <button
          onClick={() => setViewMode('options')}
          className="text-purple-400 hover:text-purple-300 flex items-center gap-2"
        >
          ← Back to options
        </button>
      )}

      {/* GitHub Connection Warning */}
      {!hasGitHubConnected && viewMode === 'options' && (
        <div className="bg-yellow-500/10 border border-yellow-500 rounded-lg p-4">
          <p className="font-semibold text-yellow-400">⚠️ GitHub Not Connected</p>
          <p className="text-sm text-yellow-400/80 mt-1">
            To browse and import your repositories, please sign in with GitHub or connect your GitHub account in profile settings.
          </p>
        </div>
      )}

      {/* Import Options */}
      {viewMode === 'options' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Browse GitHub Repos */}
          <button
            onClick={() => setViewMode('browse')}
            disabled={!hasGitHubConnected}
            className="group p-8 bg-gradient-to-br from-purple-600 to-blue-600 rounded-2xl text-white hover:from-purple-700 hover:to-blue-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed text-left"
          >
            <FolderArrowDownIcon className="w-12 h-12 mb-4 group-hover:scale-110 transition-transform" />
            <h3 className="text-2xl font-bold mb-2">Browse GitHub Repos</h3>
            <p className="text-sm opacity-90">
              View all your GitHub repositories and import with one click
            </p>
            {hasGitHubConnected && (
              <div className="mt-4 text-xs opacity-75">
                ✓ GitHub connected
              </div>
            )}
          </button>

          {/* Import by URL */}
          <button
            onClick={() => setViewMode('manual')}
            className="group p-8 bg-gradient-to-br from-gray-700 to-gray-800 rounded-2xl text-white hover:from-gray-600 hover:to-gray-700 transition-all text-left"
          >
            <CodeBracketIcon className="w-12 h-12 mb-4 group-hover:scale-110 transition-transform" />
            <h3 className="text-2xl font-bold mb-2">Import by URL</h3>
            <p className="text-sm opacity-90">
              Enter a GitHub repository URL or owner/repo name manually
            </p>
          </button>
        </div>
      )}

      {/* GitHub Repository Browser */}
      {viewMode === 'browse' && hasGitHubConnected && (
        <div className="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6">
          <GitHubRepoBrowser />
        </div>
      )}

      {/* Manual URL Import (existing component or form) */}
      {viewMode === 'manual' && (
        <div className="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6">
          <h2 className="text-2xl font-bold text-white mb-4">Import by URL</h2>
          <p className="text-gray-400 mb-6">Enter a GitHub repository URL or owner/repo format</p>
          {/* Add your existing manual import form here */}
        </div>
      )}
    </div>
  );
};

export default ImportRepository;
```

## Part 5: Testing

### Test GitHub OAuth Flow

1. **Sign out and sign back in with GitHub**
   ```
   http://localhost:5173/sign-in
   → Click "Continue with GitHub"
   → GitHub shows permission screen
   → Authorize
   → Redirected back to app
   ```

2. **Verify token is available**
   Open browser console and run:
   ```javascript
   const { getToken } = useAuth();
   const token = await getToken({ template: 'oauth_github' });
   console.log(token ? '✅ Token available' : '❌ No token');
   ```

3. **Test repository browser**
   - Navigate to import page
   - Click "Browse GitHub Repos"
   - Should see all your repositories
   - Try importing one

## Security Best Practices

1. **Never log tokens**
   ```javascript
   // ❌ DON'T DO THIS
   console.log('Token:', githubToken);
   
   // ✅ DO THIS
   console.log('Token status:', githubToken ? 'present' : 'missing');
   ```

2. **Handle token expiration**
   ```javascript
   try {
     const response = await axios.post('/api/github/repos/', { github_token });
   } catch (error) {
     if (error.response?.status === 401) {
       alert('Please reconnect your GitHub account');
       // Redirect to profile/settings
     }
   }
   ```

3. **Rate limit handling**
   ```python
   # In backend
   if response.headers.get('X-RateLimit-Remaining') == '0':
       reset_time = int(response.headers.get('X-RateLimit-Reset'))
       return JsonResponse({
           'error': 'Rate limit exceeded',
           'reset_at': reset_time
       }, status=429)
   ```

## Troubleshooting

### Issue: "Token not available"
- Check JWT template is named `oauth_github`
- Verify user signed in with GitHub
- Check template includes `github_token` field

### Issue: "403 Forbidden"
- Verify `repo` scope is enabled in Clerk
- Check GitHub OAuth app has correct callback URL
- User may need to re-authorize with new scopes

### Issue: "No repositories shown"
- Check backend logs for errors
- Verify GitHub token has `repo` scope
- Test token with GitHub API directly

## What Users Will See

1. **Sign in page:** "Continue with GitHub" button
2. **GitHub permission screen:** "Katalyst requests access to your repositories"
3. **Import page:** Grid of all their repos
4. **Each repo card:** Name, description, stats, "Import" button
5. **After import:** Success message + repo appears in dashboard

---

**Result:** Full Vercel-style GitHub repository import experience! 🎉

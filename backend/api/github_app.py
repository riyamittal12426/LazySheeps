"""
GitHub App Integration
Enterprise-grade GitHub App for one-click org-wide repository imports and webhook management
"""
import jwt
import time
import requests
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .models import GitHubAppInstallation, Repository
from .github_importer import GitHubImporter
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class GitHubAppClient:
    """
    GitHub App API Client
    Handles authentication and API calls for GitHub App
    """
    
    def __init__(self):
        self.app_id = settings.GITHUB_APP_ID
        self.private_key = settings.GITHUB_APP_PRIVATE_KEY
        self.client_id = settings.GITHUB_APP_CLIENT_ID
        self.client_secret = settings.GITHUB_APP_CLIENT_SECRET
        
    def generate_jwt(self):
        """Generate JWT for GitHub App authentication"""
        now = int(time.time())
        payload = {
            'iat': now,
            'exp': now + 600,  # JWT expires in 10 minutes
            'iss': self.app_id
        }
        
        token = jwt.encode(payload, self.private_key, algorithm='RS256')
        return token
    
    def get_installation_token(self, installation_id):
        """Get installation access token for making API calls"""
        jwt_token = self.generate_jwt()
        
        headers = {
            'Authorization': f'Bearer {jwt_token}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28'
        }
        
        url = f'https://api.github.com/app/installations/{installation_id}/access_tokens'
        response = requests.post(url, headers=headers)
        
        if response.status_code == 201:
            return response.json()['token']
        else:
            logger.error(f"Failed to get installation token: {response.text}")
            raise Exception("Failed to get installation access token")
    
    def get_installation_repositories(self, installation_id):
        """Fetch all repositories accessible to the installation"""
        token = self.get_installation_token(installation_id)
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28'
        }
        
        all_repos = []
        page = 1
        per_page = 100
        
        while True:
            url = f'https://api.github.com/installation/repositories?per_page={per_page}&page={page}'
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch repositories: {response.text}")
                break
            
            data = response.json()
            repos = data.get('repositories', [])
            
            if not repos:
                break
            
            all_repos.extend(repos)
            
            if len(repos) < per_page:
                break
            
            page += 1
        
        return all_repos
    
    def create_webhook(self, installation_id, repo_full_name):
        """Create webhook for a repository"""
        token = self.get_installation_token(installation_id)
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28'
        }
        
        webhook_url = settings.GITHUB_WEBHOOK_URL
        webhook_secret = settings.GITHUB_WEBHOOK_SECRET
        
        webhook_config = {
            'name': 'web',
            'active': True,
            'events': [
                'push',
                'pull_request',
                'issues',
                'issue_comment',
                'commit_comment',
                'create',
                'delete',
                'fork',
                'star',
                'watch',
                'release'
            ],
            'config': {
                'url': webhook_url,
                'content_type': 'json',
                'secret': webhook_secret,
                'insecure_ssl': '0'
            }
        }
        
        url = f'https://api.github.com/repos/{repo_full_name}/hooks'
        response = requests.post(url, json=webhook_config, headers=headers)
        
        if response.status_code == 201:
            return response.json()
        elif response.status_code == 422:
            # Webhook might already exist
            logger.warning(f"Webhook already exists for {repo_full_name}")
            return {'status': 'exists'}
        else:
            logger.error(f"Failed to create webhook: {response.text}")
            raise Exception(f"Failed to create webhook: {response.text}")


@api_view(['GET'])
@permission_classes([AllowAny])
def github_app_manifest(request):
    """
    Generate GitHub App manifest for easy app creation
    Users can use this to create a GitHub App automatically
    """
    base_url = settings.GITHUB_APP_BASE_URL
    
    manifest = {
        "name": "LazyShēps Analytics",
        "url": "https://github.com/yourusername/lazysheeps",
        "hook_attributes": {
            "url": f"{base_url}/api/github-app/webhook/",
            "active": True
        },
        "redirect_url": f"{base_url}/auth/github-app/callback",
        "callback_urls": [
            f"{base_url}/auth/github-app/callback"
        ],
        "setup_url": f"{base_url}/setup",
        "description": "Enterprise GitHub Analytics Platform with AI-powered insights",
        "public": False,
        "default_permissions": {
            "contents": "read",
            "issues": "read",
            "metadata": "read",
            "pull_requests": "read",
            "members": "read",
            "administration": "read",
            "statuses": "read",
            "commit_statuses": "read",
            "deployments": "read"
        },
        "default_events": [
            "push",
            "pull_request",
            "issues",
            "issue_comment",
            "commit_comment",
            "create",
            "delete",
            "fork",
            "star",
            "watch",
            "release"
        ]
    }
    
    return Response({
        'manifest': manifest,
        'instructions': [
            '1. Go to https://github.com/settings/apps/new',
            '2. Paste this manifest in the form',
            '3. Click "Create GitHub App from manifest"',
            '4. Save your App ID, Client ID, Client Secret, and Private Key',
            '5. Add them to your .env file'
        ]
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def github_app_install_url(request):
    """
    Get GitHub App installation URL
    Users click this to install the app on their org/account
    """
    client_id = settings.GITHUB_APP_CLIENT_ID
    redirect_uri = settings.GITHUB_APP_REDIRECT_URI
    
    # State parameter for security
    state = request.GET.get('state', 'random_state_string')
    
    install_url = (
        f"https://github.com/apps/{settings.GITHUB_APP_SLUG}/installations/new"
    )
    
    return Response({
        'install_url': install_url,
        'client_id': client_id,
        'redirect_uri': redirect_uri
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def github_app_callback(request):
    """
    Handle GitHub App installation callback
    This is called after user installs the app
    """
    installation_id = request.GET.get('installation_id')
    setup_action = request.GET.get('setup_action')
    code = request.GET.get('code')
    
    if not installation_id:
        return Response({'error': 'No installation_id provided'}, status=400)
    
    try:
        # Store installation
        installation, created = GitHubAppInstallation.objects.get_or_create(
            installation_id=installation_id,
            defaults={
                'user': request.user,
                'setup_action': setup_action
            }
        )
        
        if not created:
            installation.user = request.user
            installation.setup_action = setup_action
            installation.save()
        
        # Fetch installation details
        client = GitHubAppClient()
        token = client.get_installation_token(installation_id)
        
        # Get installation info
        jwt_token = client.generate_jwt()
        headers = {
            'Authorization': f'Bearer {jwt_token}',
            'Accept': 'application/vnd.github+json'
        }
        
        response = requests.get(
            f'https://api.github.com/app/installations/{installation_id}',
            headers=headers
        )
        
        if response.status_code == 200:
            install_data = response.json()
            installation.account_login = install_data['account']['login']
            installation.account_type = install_data['account']['type']
            installation.account_avatar_url = install_data['account']['avatar_url']
            installation.target_type = install_data.get('target_type', 'User')
            installation.save()
        
        return Response({
            'success': True,
            'installation': {
                'id': installation.id,
                'installation_id': installation.installation_id,
                'account_login': installation.account_login,
                'account_type': installation.account_type,
                'account_avatar_url': installation.account_avatar_url,
                'created_at': installation.created_at
            },
            'message': f'Successfully connected GitHub App to {installation.account_login}'
        })
        
    except Exception as e:
        logger.error(f"Installation callback error: {str(e)}")
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def list_installations(request):
    """List all GitHub App installations for the current user"""
    # If user is authenticated, show only their installations
    # Otherwise, show all installations (for demo/testing)
    if request.user.is_authenticated:
        installations = GitHubAppInstallation.objects.filter(user=request.user)
    else:
        installations = GitHubAppInstallation.objects.all()
    
    data = []
    for installation in installations:
        data.append({
            'id': installation.id,
            'installation_id': installation.installation_id,
            'account_login': installation.account_login,
            'account_type': installation.account_type,
            'account_avatar_url': installation.account_avatar_url,
            'target_type': installation.target_type,
            'created_at': installation.created_at
        })
    
    return Response({
        'installations': data,
        'count': len(data)
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def installation_repositories(request, installation_id):
    """
    Fetch all repositories accessible through this installation
    """
    try:
        # If user is authenticated, filter by user
        if request.user.is_authenticated:
            installation = GitHubAppInstallation.objects.get(
                id=installation_id,
                user=request.user
            )
        else:
            installation = GitHubAppInstallation.objects.get(id=installation_id)
    except GitHubAppInstallation.DoesNotExist:
        return Response({'error': 'Installation not found'}, status=404)
    
    try:
        client = GitHubAppClient()
        repos = client.get_installation_repositories(installation.installation_id)
        
        formatted_repos = []
        for repo in repos:
            # Check if already imported
            is_imported = Repository.objects.filter(
                github_id=repo['id']
            ).exists()
            
            formatted_repos.append({
                'id': repo['id'],
                'name': repo['name'],
                'full_name': repo['full_name'],
                'description': repo['description'],
                'private': repo['private'],
                'html_url': repo['html_url'],
                'language': repo['language'],
                'stargazers_count': repo['stargazers_count'],
                'forks_count': repo['forks_count'],
                'open_issues_count': repo['open_issues_count'],
                'updated_at': repo['updated_at'],
                'is_imported': is_imported,
                'owner': {
                    'login': repo['owner']['login'],
                    'avatar_url': repo['owner']['avatar_url']
                }
            })
        
        return Response({
            'repositories': formatted_repos,
            'total': len(formatted_repos),
            'installation': {
                'account_login': installation.account_login,
                'account_type': installation.account_type
            }
        })
        
    except Exception as e:
        logger.error(f"Error fetching repositories: {str(e)}")
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
def bulk_import_repositories(request, installation_id):
    """
    Bulk import repositories with automatic webhook setup
    This is the WOW feature - import 50+ repos with one click!
    """
    try:
        # If user is authenticated, filter by user
        if request.user.is_authenticated:
            installation = GitHubAppInstallation.objects.get(
                id=installation_id,
                user=request.user
            )
        else:
            installation = GitHubAppInstallation.objects.get(id=installation_id)
    except GitHubAppInstallation.DoesNotExist:
        return Response({'error': 'Installation not found'}, status=404)
    
    repo_ids = request.data.get('repository_ids', [])
    auto_webhook = request.data.get('auto_webhook', True)
    
    if not repo_ids:
        return Response({'error': 'No repositories selected'}, status=400)
    
    try:
        client = GitHubAppClient()
        token = client.get_installation_token(installation.installation_id)
        
        # Fetch all repos to get their details
        all_repos = client.get_installation_repositories(installation.installation_id)
        selected_repos = [r for r in all_repos if r['id'] in repo_ids]
        
        results = []
        success_count = 0
        error_count = 0
        
        for repo in selected_repos:
            try:
                # Import repository
                importer = GitHubImporter(token)
                repo_data = importer.import_repository(repo['full_name'])
                
                # Create webhook if requested
                webhook_status = None
                if auto_webhook:
                    try:
                        webhook = client.create_webhook(
                            installation.installation_id,
                            repo['full_name']
                        )
                        webhook_status = 'created'
                    except Exception as webhook_error:
                        webhook_status = f'failed: {str(webhook_error)}'
                
                results.append({
                    'repository': repo['full_name'],
                    'status': 'success',
                    'webhook': webhook_status,
                    'data': {
                        'name': repo_data.get('name'),
                        'contributors': repo_data.get('contributors_count', 0),
                        'commits': repo_data.get('commits_count', 0),
                        'issues': repo_data.get('issues_count', 0)
                    }
                })
                success_count += 1
                
            except Exception as e:
                logger.error(f"Failed to import {repo['full_name']}: {str(e)}")
                results.append({
                    'repository': repo['full_name'],
                    'status': 'error',
                    'error': str(e)
                })
                error_count += 1
        
        return Response({
            'success': True,
            'results': results,
            'summary': {
                'total': len(repo_ids),
                'success': success_count,
                'failed': error_count
            },
            'message': f'Imported {success_count} of {len(repo_ids)} repositories'
        })
        
    except Exception as e:
        logger.error(f"Bulk import error: {str(e)}")
        return Response({'error': str(e)}, status=500)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def github_app_webhook(request):
    """
    Handle GitHub App webhook events
    This receives real-time updates from all installed repositories
    """
    # Verify webhook signature
    signature = request.headers.get('X-Hub-Signature-256')
    event_type = request.headers.get('X-GitHub-Event')
    delivery_id = request.headers.get('X-GitHub-Delivery')
    
    # TODO: Verify signature with WEBHOOK_SECRET
    
    logger.info(f"Received GitHub App webhook: {event_type} - {delivery_id}")
    
    payload = request.data
    
    # Handle different event types
    if event_type == 'installation':
        action = payload.get('action')
        installation_id = payload['installation']['id']
        account = payload['installation']['account']
        
        if action == 'created':
            logger.info(f"New installation: {installation_id} for {account['login']}")
        elif action == 'deleted':
            logger.info(f"Installation deleted: {installation_id}")
            # Clean up installation record
            GitHubAppInstallation.objects.filter(
                installation_id=installation_id
            ).delete()
    
    elif event_type == 'installation_repositories':
        action = payload.get('action')
        installation_id = payload['installation']['id']
        
        if action == 'added':
            repos_added = payload.get('repositories_added', [])
            logger.info(f"Repositories added to installation {installation_id}: {len(repos_added)}")
        elif action == 'removed':
            repos_removed = payload.get('repositories_removed', [])
            logger.info(f"Repositories removed from installation {installation_id}: {len(repos_removed)}")
    
    elif event_type == 'push':
        # Handle push events (same as existing webhook handler)
        repo_full_name = payload['repository']['full_name']
        logger.info(f"Push event for {repo_full_name}")
        # TODO: Update commit data
    
    elif event_type == 'pull_request':
        # Handle PR events
        action = payload.get('action')
        pr_number = payload['pull_request']['number']
        repo_full_name = payload['repository']['full_name']
        logger.info(f"PR {action}: #{pr_number} in {repo_full_name}")
    
    return JsonResponse({'status': 'success'})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_installation(request, installation_id):
    """Delete/disconnect a GitHub App installation"""
    try:
        installation = GitHubAppInstallation.objects.get(
            id=installation_id,
            user=request.user
        )
        installation.delete()
        
        return Response({
            'success': True,
            'message': 'Installation disconnected successfully'
        })
    except GitHubAppInstallation.DoesNotExist:
        return Response({'error': 'Installation not found'}, status=404)

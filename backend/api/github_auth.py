"""
GitHub OAuth authentication views
Handles GitHub OAuth flow and repository access
"""
import requests
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
import json


@api_view(['GET'])
@permission_classes([AllowAny])
def github_auth_url(request):
    """
    Get GitHub OAuth authorization URL
    """
    scope = 'read:user user:email repo'
    auth_url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={settings.GITHUB_CLIENT_ID}"
        f"&redirect_uri={settings.GITHUB_REDIRECT_URI}"
        f"&scope={scope}"
        f"&state=random_state_string"
    )
    
    return Response({
        'url': auth_url,
        'client_id': settings.GITHUB_CLIENT_ID
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def github_callback(request):
    """
    Handle GitHub OAuth callback
    Exchange code for access token and get user info
    """
    code = request.data.get('code')
    
    if not code:
        return Response({'error': 'No code provided'}, status=400)
    
    # Exchange code for access token
    token_url = 'https://github.com/login/oauth/access_token'
    token_data = {
        'client_id': settings.GITHUB_CLIENT_ID,
        'client_secret': settings.GITHUB_CLIENT_SECRET,
        'code': code,
        'redirect_uri': settings.GITHUB_REDIRECT_URI
    }
    
    headers = {'Accept': 'application/json'}
    token_response = requests.post(token_url, data=token_data, headers=headers)
    
    if token_response.status_code != 200:
        return Response({'error': 'Failed to get access token'}, status=400)
    
    token_json = token_response.json()
    access_token = token_json.get('access_token')
    
    if not access_token:
        return Response({'error': 'No access token received'}, status=400)
    
    # Get user info from GitHub
    user_url = 'https://api.github.com/user'
    user_headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }
    user_response = requests.get(user_url, headers=user_headers)
    
    if user_response.status_code != 200:
        return Response({'error': 'Failed to get user info'}, status=400)
    
    github_user = user_response.json()
    
    # Get user emails
    emails_url = 'https://api.github.com/user/emails'
    emails_response = requests.get(emails_url, headers=user_headers)
    emails = emails_response.json() if emails_response.status_code == 200 else []
    primary_email = next((e['email'] for e in emails if e['primary']), github_user.get('email'))
    
    # Create or get user
    username = github_user['login']
    email = primary_email or f"{username}@github.local"
    
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': email,
            'first_name': github_user.get('name', '').split()[0] if github_user.get('name') else '',
        }
    )
    
    # Store GitHub access token in user profile (you may want to create a UserProfile model)
    # For now, we'll return it to the frontend
    
    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'github_token': access_token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'github_username': github_user['login'],
            'github_avatar': github_user['avatar_url'],
            'github_name': github_user.get('name', ''),
        },
        'is_new_user': created
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def github_repositories(request):
    """
    Fetch user's GitHub repositories
    Requires GitHub access token
    """
    github_token = request.headers.get('X-GitHub-Token')
    
    if not github_token:
        return Response({'error': 'GitHub token required'}, status=400)
    
    headers = {
        'Authorization': f'Bearer {github_token}',
        'Accept': 'application/vnd.github+json'
    }
    
    # Fetch user's repositories
    repos_url = 'https://api.github.com/user/repos'
    params = {
        'per_page': 100,
        'sort': 'updated',
        'affiliation': 'owner,collaborator,organization_member'
    }
    
    all_repos = []
    page = 1
    
    while True:
        params['page'] = page
        response = requests.get(repos_url, headers=headers, params=params)
        
        if response.status_code != 200:
            return Response({'error': 'Failed to fetch repositories'}, status=400)
        
        repos = response.json()
        if not repos:
            break
            
        all_repos.extend(repos)
        page += 1
        
        if len(repos) < 100:  # Last page
            break
    
    # Format repositories for frontend
    formatted_repos = []
    for repo in all_repos:
        formatted_repos.append({
            'id': repo['id'],
            'name': repo['name'],
            'full_name': repo['full_name'],
            'description': repo['description'],
            'private': repo['private'],
            'url': repo['html_url'],
            'language': repo['language'],
            'stars': repo['stargazers_count'],
            'forks': repo['forks_count'],
            'updated_at': repo['updated_at'],
            'owner': {
                'login': repo['owner']['login'],
                'avatar_url': repo['owner']['avatar_url']
            }
        })
    
    return Response({
        'repositories': formatted_repos,
        'total': len(formatted_repos)
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def import_repositories(request):
    """
    Import selected repositories to the platform
    """
    from .github_importer import GitHubImporter
    
    github_token = request.headers.get('X-GitHub-Token')
    repo_names = request.data.get('repositories', [])
    
    if not github_token:
        return Response({'error': 'GitHub token required'}, status=400)
    
    if not repo_names:
        return Response({'error': 'No repositories selected'}, status=400)
    
    importer = GitHubImporter(github_token)
    results = []
    
    for repo_name in repo_names:
        try:
            result = importer.import_repository(repo_name)
            results.append({
                'repository': repo_name,
                'status': 'success',
                'data': result
            })
        except Exception as e:
            results.append({
                'repository': repo_name,
                'status': 'error',
                'error': str(e)
            })
    
    return Response({
        'results': results,
        'success_count': sum(1 for r in results if r['status'] == 'success'),
        'error_count': sum(1 for r in results if r['status'] == 'error')
    })

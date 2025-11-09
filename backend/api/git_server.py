"""
Git Server - Handle Git Push/Pull operations
Allows users to push code directly to our app like GitHub/GitLab
"""
import os
import subprocess
import shutil
from pathlib import Path
from django.conf import settings
from django.http import HttpResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import logging

logger = logging.getLogger(__name__)

# Base directory for storing repositories
REPOS_BASE_DIR = Path(settings.BASE_DIR) / 'git_repositories'
REPOS_BASE_DIR.mkdir(exist_ok=True)


class GitRepository:
    """Handle Git repository operations"""
    
    def __init__(self, repo_path):
        self.repo_path = Path(repo_path)
        self.bare_path = self.repo_path / '.git'
        
    def initialize_bare_repo(self):
        """Initialize a bare Git repository"""
        try:
            if not self.repo_path.exists():
                self.repo_path.mkdir(parents=True)
            
            # Initialize bare repo
            result = subprocess.run(
                ['git', 'init', '--bare', str(self.repo_path)],
                capture_output=True,
                text=True,
                cwd=str(self.repo_path.parent)
            )
            
            if result.returncode == 0:
                # Set up hooks
                self._setup_hooks()
                logger.info(f"Initialized bare repo at {self.repo_path}")
                return True
            else:
                logger.error(f"Failed to init repo: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error initializing repo: {str(e)}")
            return False
    
    def _setup_hooks(self):
        """Set up Git hooks for post-receive processing"""
        hooks_dir = self.repo_path / 'hooks'
        hooks_dir.mkdir(exist_ok=True)
        
        # Create post-receive hook
        post_receive = hooks_dir / 'post-receive'
        post_receive.write_text("""#!/bin/sh
# Post-receive hook to trigger analysis
echo "Code received! Processing..."
# Trigger Django management command or API endpoint
curl -X POST http://localhost:8000/api/git/webhook/post-receive/ \
  -H "Content-Type: application/json" \
  -d "{\\"repository\\": \\"$PWD\\"}"
""")
        
        # Make executable
        os.chmod(post_receive, 0o755)
    
    def handle_git_request(self, service, request):
        """
        Handle git-upload-pack (fetch/pull) and git-receive-pack (push)
        """
        try:
            # Set up environment
            env = os.environ.copy()
            env['GIT_PROJECT_ROOT'] = str(self.repo_path.parent)
            env['GIT_HTTP_EXPORT_ALL'] = '1'
            
            # Build command
            cmd = [service, '--stateless-rpc', str(self.repo_path)]
            
            # Run git command
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env
            )
            
            # Stream input/output
            stdout, stderr = process.communicate(request.body)
            
            if process.returncode == 0:
                return stdout
            else:
                logger.error(f"Git command failed: {stderr.decode()}")
                return None
                
        except Exception as e:
            logger.error(f"Error handling git request: {str(e)}")
            return None
    
    def get_file_tree(self, branch='main', path=''):
        """Get file tree structure from repository"""
        try:
            # Clone to temp directory to read files
            temp_dir = self.repo_path.parent / f'{self.repo_path.name}_temp'
            
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            
            # Clone bare repo to temp
            result = subprocess.run(
                ['git', 'clone', str(self.repo_path), str(temp_dir)],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return None
            
            # Get file tree
            target_path = temp_dir / path
            if not target_path.exists():
                shutil.rmtree(temp_dir)
                return None
            
            files = []
            for item in target_path.iterdir():
                if item.name == '.git':
                    continue
                    
                files.append({
                    'name': item.name,
                    'path': str(item.relative_to(temp_dir)),
                    'type': 'directory' if item.is_dir() else 'file',
                    'size': item.stat().st_size if item.is_file() else 0
                })
            
            # Cleanup
            shutil.rmtree(temp_dir)
            
            return sorted(files, key=lambda x: (x['type'] != 'directory', x['name']))
            
        except Exception as e:
            logger.error(f"Error getting file tree: {str(e)}")
            return None
    
    def get_file_content(self, branch='main', file_path=''):
        """Get content of a specific file"""
        try:
            result = subprocess.run(
                ['git', 'show', f'{branch}:{file_path}'],
                cwd=str(self.repo_path),
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting file content: {str(e)}")
            return None
    
    def get_commits(self, branch='main', limit=50):
        """Get commit history"""
        try:
            result = subprocess.run(
                ['git', 'log', branch, f'--max-count={limit}', 
                 '--pretty=format:%H|%an|%ae|%at|%s'],
                cwd=str(self.repo_path),
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                commits = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        sha, author, email, timestamp, message = line.split('|')
                        commits.append({
                            'sha': sha,
                            'author': author,
                            'email': email,
                            'timestamp': int(timestamp),
                            'message': message
                        })
                return commits
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error getting commits: {str(e)}")
            return []
    
    def get_branches(self):
        """Get all branches"""
        try:
            result = subprocess.run(
                ['git', 'branch', '-r'],
                cwd=str(self.repo_path),
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                branches = []
                for line in result.stdout.strip().split('\n'):
                    branch = line.strip().replace('origin/', '')
                    if branch and branch != 'HEAD':
                        branches.append(branch)
                return branches
            else:
                return ['main']
                
        except Exception as e:
            logger.error(f"Error getting branches: {str(e)}")
            return ['main']


@csrf_exempt
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def git_http_backend(request, username, repo_name, service):
    """
    Git HTTP Smart Protocol handler
    Handles: /git/<username>/<repo_name>/git-upload-pack (pull)
             /git/<username>/<repo_name>/git-receive-pack (push)
    """
    # Construct repo path
    repo_path = REPOS_BASE_DIR / username / f'{repo_name}.git'
    git_repo = GitRepository(repo_path)
    
    # Initialize if doesn't exist
    if not repo_path.exists():
        git_repo.initialize_bare_repo()
    
    # Validate service
    if service not in ['git-upload-pack', 'git-receive-pack']:
        return HttpResponse('Invalid service', status=400)
    
    # Handle info/refs request (discovery)
    if request.method == 'GET':
        cmd = [service, '--stateless-rpc', '--advertise-refs', str(repo_path)]
        result = subprocess.run(cmd, capture_output=True)
        
        if result.returncode == 0:
            response = HttpResponse(
                result.stdout,
                content_type=f'application/x-{service}-advertisement'
            )
            response['Cache-Control'] = 'no-cache'
            return response
        else:
            return HttpResponse('Error', status=500)
    
    # Handle actual push/pull
    elif request.method == 'POST':
        output = git_repo.handle_git_request(service, request)
        
        if output:
            response = HttpResponse(
                output,
                content_type=f'application/x-{service}-result'
            )
            response['Cache-Control'] = 'no-cache'
            return response
        else:
            return HttpResponse('Error processing request', status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_repository(request):
    """Create a new Git repository"""
    try:
        repo_name = request.data.get('name')
        description = request.data.get('description', '')
        
        if not repo_name:
            return Response({'error': 'Repository name is required'}, status=400)
        
        # Sanitize repo name
        repo_name = repo_name.replace(' ', '-').lower()
        username = request.user.username
        
        # Create repo path
        repo_path = REPOS_BASE_DIR / username / f'{repo_name}.git'
        
        if repo_path.exists():
            return Response({'error': 'Repository already exists'}, status=400)
        
        # Initialize repository
        git_repo = GitRepository(repo_path)
        if git_repo.initialize_bare_repo():
            # Create database entry
            from api.models import Repository
            
            # Use a default avatar for local repos
            default_avatar = 'https://ui-avatars.com/api/?name=' + repo_name + '&background=random'
            
            db_repo = Repository.objects.create(
                name=repo_name,
                full_name=f'{username}/{repo_name}',
                description=description or f'Local repository: {repo_name}',
                summary=description or f'Self-hosted Git repository',
                avatar_url=default_avatar,
                url=f'http://localhost:8000/git/{username}/{repo_name}.git',
                is_local=True,
                local_path=str(repo_path),
                default_branch='main'
            )
            
            return Response({
                'status': 'success',
                'message': 'Repository created successfully',
                'repository': {
                    'id': db_repo.id,
                    'name': repo_name,
                    'description': db_repo.description,
                    'clone_url': f'http://localhost:8000/git/{username}/{repo_name}.git',
                    'ssh_url': f'git@localhost:{username}/{repo_name}.git',
                    'default_branch': 'main'
                }
            })
        else:
            return Response({'error': 'Failed to initialize repository'}, status=500)
            
    except Exception as e:
        logger.error(f"Error creating repository: {str(e)}")
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def browse_repository(request, username, repo_name):
    """Browse repository files and folders"""
    try:
        branch = request.GET.get('branch', 'main')
        path = request.GET.get('path', '')
        
        repo_path = REPOS_BASE_DIR / username / f'{repo_name}.git'
        
        if not repo_path.exists():
            return Response({'error': 'Repository not found'}, status=404)
        
        git_repo = GitRepository(repo_path)
        
        # Get file tree
        files = git_repo.get_file_tree(branch, path)
        
        if files is None:
            return Response({'error': 'Path not found'}, status=404)
        
        # Get recent commits
        commits = git_repo.get_commits(branch, limit=10)
        
        # Get branches
        branches = git_repo.get_branches()
        
        return Response({
            'repository': {
                'name': repo_name,
                'owner': username,
                'current_branch': branch,
                'branches': branches
            },
            'path': path,
            'files': files,
            'recent_commits': commits
        })
        
    except Exception as e:
        logger.error(f"Error browsing repository: {str(e)}")
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_file(request, username, repo_name):
    """Get file content"""
    try:
        branch = request.GET.get('branch', 'main')
        file_path = request.GET.get('path', '')
        
        if not file_path:
            return Response({'error': 'File path is required'}, status=400)
        
        repo_path = REPOS_BASE_DIR / username / f'{repo_name}.git'
        
        if not repo_path.exists():
            return Response({'error': 'Repository not found'}, status=404)
        
        git_repo = GitRepository(repo_path)
        content = git_repo.get_file_content(branch, file_path)
        
        if content is None:
            return Response({'error': 'File not found'}, status=404)
        
        return Response({
            'path': file_path,
            'branch': branch,
            'content': content,
            'size': len(content)
        })
        
    except Exception as e:
        logger.error(f"Error getting file: {str(e)}")
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def repository_commits(request, username, repo_name):
    """Get commit history"""
    try:
        branch = request.GET.get('branch', 'main')
        limit = int(request.GET.get('limit', 50))
        
        repo_path = REPOS_BASE_DIR / username / f'{repo_name}.git'
        
        if not repo_path.exists():
            return Response({'error': 'Repository not found'}, status=404)
        
        git_repo = GitRepository(repo_path)
        commits = git_repo.get_commits(branch, limit)
        
        return Response({
            'repository': repo_name,
            'branch': branch,
            'commits': commits,
            'total': len(commits)
        })
        
    except Exception as e:
        logger.error(f"Error getting commits: {str(e)}")
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def post_receive_webhook(request):
    """Handle post-receive hook from Git"""
    try:
        repo_path = request.data.get('repository')
        
        if not repo_path:
            return Response({'error': 'Repository path required'}, status=400)
        
        logger.info(f"Post-receive hook triggered for: {repo_path}")
        
        # Trigger background analysis/import
        # You can call your existing github_importer here to analyze the repo
        
        return Response({'success': True, 'message': 'Post-receive hook processed'})
        
    except Exception as e:
        logger.error(f"Error in post-receive: {str(e)}")
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_user_repositories(request, username):
    """List all repositories for a user"""
    try:
        user_repos_dir = REPOS_BASE_DIR / username
        
        if not user_repos_dir.exists():
            return Response({'repositories': []})
        
        repos = []
        for repo_dir in user_repos_dir.iterdir():
            if repo_dir.is_dir() and repo_dir.name.endswith('.git'):
                repo_name = repo_dir.name[:-4]  # Remove .git
                git_repo = GitRepository(repo_dir)
                
                # Get basic info
                branches = git_repo.get_branches()
                commits = git_repo.get_commits(limit=1)
                
                repos.append({
                    'name': repo_name,
                    'owner': username,
                    'clone_url': f'http://localhost:8000/git/{username}/{repo_name}.git',
                    'branches': branches,
                    'last_commit': commits[0] if commits else None
                })
        
        return Response({
            'username': username,
            'repositories': repos,
            'total': len(repos)
        })
        
    except Exception as e:
        logger.error(f"Error listing repositories: {str(e)}")
        return Response({'error': str(e)}, status=500)

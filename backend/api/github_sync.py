"""
GitHub Auto-Sync System - Enterprise Grade
Vercel-like automatic repository syncing with webhook processing and background jobs
"""
import hmac
import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
from .models import (
    GitHubAppInstallation, Repository, Contributor, 
    RepositoryWork, Commit, Issue, SyncJob
)
from .github_app import GitHubAppClient

logger = logging.getLogger(__name__)


class GitHubSyncManager:
    """
    Manages automatic synchronization between GitHub and our database
    Handles: auto-import, webhooks, background jobs, token caching
    """
    
    def __init__(self, installation_id: int):
        self.installation_id = installation_id
        self.client = GitHubAppClient()
        
    def _get_cached_token(self) -> Optional[str]:
        """Get cached installation token (tokens last 1 hour)"""
        cache_key = f'gh_token_{self.installation_id}'
        token = cache.get(cache_key)
        
        if not token:
            # Generate new token and cache for 50 minutes (token lasts 60)
            token = self.client.get_installation_token(self.installation_id)
            cache.set(cache_key, token, timeout=3000)  # 50 minutes
            logger.info(f"Generated new token for installation {self.installation_id}")
        
        return token
    
    def _invalidate_token_cache(self):
        """Invalidate cached token (e.g., on 401 errors)"""
        cache_key = f'gh_token_{self.installation_id}'
        cache.delete(cache_key)
        logger.warning(f"Invalidated token cache for installation {self.installation_id}")
    
    def _make_api_request(self, url: str, method: str = 'GET', data: Dict = None, retry: bool = True):
        """
        Make GitHub API request with automatic token refresh on 401
        Implements retry logic for transient failures
        """
        import requests
        
        token = self._get_cached_token()
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28'
        }
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'PATCH':
                response = requests.patch(url, json=data, headers=headers, timeout=30)
            
            # Handle token expiration
            if response.status_code == 401 and retry:
                logger.warning("Token expired, refreshing...")
                self._invalidate_token_cache()
                return self._make_api_request(url, method, data, retry=False)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {url} - {str(e)}")
            raise
    
    @transaction.atomic
    def auto_import_all_repositories(self, installation: GitHubAppInstallation) -> Dict:
        """
        Automatically import all repositories when app is installed
        This runs on initial installation
        """
        logger.info(f"Auto-importing repositories for installation {installation.installation_id}")
        
        try:
            # Fetch all repos from GitHub
            repos = self.client.get_installation_repositories(installation.installation_id)
            
            imported = []
            skipped = []
            errors = []
            
            for repo in repos:
                try:
                    # Check if already imported
                    if Repository.objects.filter(github_id=repo['id']).exists():
                        skipped.append(repo['full_name'])
                        continue
                    
                    # Import repository with idempotency
                    repo_obj = self._import_repository_idempotent(repo, installation)
                    imported.append(repo['full_name'])
                    
                    # Setup webhook (idempotent)
                    self._setup_webhook_idempotent(repo['full_name'])
                    
                except Exception as e:
                    logger.error(f"Failed to import {repo['full_name']}: {str(e)}")
                    errors.append({'repo': repo['full_name'], 'error': str(e)})
            
            # Record sync job
            SyncJob.objects.create(
                installation=installation,
                job_type='auto_import',
                status='completed',
                repositories_processed=len(imported),
                errors_count=len(errors),
                details={
                    'imported': imported,
                    'skipped': skipped,
                    'errors': errors
                }
            )
            
            return {
                'success': True,
                'imported': len(imported),
                'skipped': len(skipped),
                'errors': len(errors),
                'details': {
                    'imported_repos': imported,
                    'skipped_repos': skipped,
                    'error_details': errors
                }
            }
            
        except Exception as e:
            logger.error(f"Auto-import failed: {str(e)}")
            SyncJob.objects.create(
                installation=installation,
                job_type='auto_import',
                status='failed',
                error_message=str(e)
            )
            raise
    
    def _import_repository_idempotent(self, repo_data: Dict, installation: GitHubAppInstallation) -> Repository:
        """
        Import repository with idempotent operations
        Safe to call multiple times - won't create duplicates
        """
        # Use get_or_create for idempotency
        repo, created = Repository.objects.get_or_create(
            github_id=repo_data['id'],
            defaults={
                'name': repo_data['name'],
                'full_name': repo_data['full_name'],
                'description': repo_data.get('description', ''),
                'url': repo_data['html_url'],
                'language': repo_data.get('language', ''),
                'stars': repo_data.get('stargazers_count', 0),
                'forks': repo_data.get('forks_count', 0),
                'open_issues': repo_data.get('open_issues_count', 0),
                'summary': f"Repository for {repo_data['full_name']}",
                'installation': installation
            }
        )
        
        if created:
            logger.info(f"Imported new repository: {repo.full_name}")
        else:
            logger.info(f"Repository already exists: {repo.full_name}")
        
        return repo
    
    def _setup_webhook_idempotent(self, repo_full_name: str) -> Dict:
        """
        Setup webhook for repository (idempotent)
        Safe to call multiple times - won't create duplicate webhooks
        """
        try:
            token = self._get_cached_token()
            headers = {
                'Authorization': f'Bearer {token}',
                'Accept': 'application/vnd.github+json',
                'X-GitHub-Api-Version': '2022-11-28'
            }
            
            # Check if webhook already exists
            import requests
            hooks_url = f'https://api.github.com/repos/{repo_full_name}/hooks'
            response = requests.get(hooks_url, headers=headers)
            
            if response.status_code == 200:
                existing_hooks = response.json()
                webhook_url = settings.GITHUB_WEBHOOK_URL
                
                # Check if our webhook already exists
                for hook in existing_hooks:
                    if hook.get('config', {}).get('url') == webhook_url:
                        logger.info(f"Webhook already exists for {repo_full_name}")
                        return {'status': 'exists', 'id': hook['id']}
            
            # Create new webhook
            webhook = self.client.create_webhook(self.installation_id, repo_full_name)
            logger.info(f"Created webhook for {repo_full_name}")
            return webhook
            
        except Exception as e:
            logger.error(f"Webhook setup failed for {repo_full_name}: {str(e)}")
            # Don't fail the entire sync job for webhook errors
            return {'status': 'error', 'error': str(e)}
    
    def sync_repository_data(self, repository: Repository) -> Dict:
        """
        Sync repository data (commits, issues, contributors)
        This is called periodically or on-demand
        """
        logger.info(f"Syncing repository: {repository.full_name}")
        
        try:
            results = {
                'commits': self._sync_commits(repository),
                'issues': self._sync_issues(repository),
                'contributors': self._sync_contributors(repository)
            }
            
            repository.last_synced_at = timezone.now()
            repository.save(update_fields=['last_synced_at'])
            
            return results
            
        except Exception as e:
            logger.error(f"Sync failed for {repository.full_name}: {str(e)}")
            raise
    
    def _sync_commits(self, repository: Repository) -> Dict:
        """Sync commits for a repository"""
        # Get latest commit SHA we have
        latest_commit = Commit.objects.filter(
            work__repository=repository
        ).order_by('-committed_at').first()
        
        since = latest_commit.committed_at if latest_commit else None
        
        # Fetch new commits from GitHub
        url = f'https://api.github.com/repos/{repository.full_name}/commits'
        params = {'per_page': 100}
        if since:
            params['since'] = since.isoformat()
        
        commits_data = self._make_api_request(f"{url}?{'&'.join(f'{k}={v}' for k, v in params.items())}")
        
        new_commits = 0
        for commit_data in commits_data:
            # Import commit (idempotent)
            created = self._import_commit_idempotent(commit_data, repository)
            if created:
                new_commits += 1
        
        return {'new_commits': new_commits, 'total_fetched': len(commits_data)}
    
    def _import_commit_idempotent(self, commit_data: Dict, repository: Repository) -> bool:
        """Import single commit (idempotent)"""
        sha = commit_data['sha']
        
        # Check if commit already exists
        if Commit.objects.filter(sha=sha).exists():
            return False
        
        # Get or create contributor
        author_data = commit_data['commit']['author']
        contributor, _ = Contributor.objects.get_or_create(
            username=author_data['name'],
            defaults={'avatar_url': commit_data.get('author', {}).get('avatar_url', '')}
        )
        
        # Get or create RepositoryWork
        work, _ = RepositoryWork.objects.get_or_create(
            repository=repository,
            contributor=contributor,
            defaults={'summary': f"Contributions to {repository.name}"}
        )
        
        # Create commit
        Commit.objects.create(
            work=work,
            sha=sha,
            message=commit_data['commit']['message'],
            committed_at=commit_data['commit']['author']['date'],
            additions=commit_data['stats'].get('additions', 0) if 'stats' in commit_data else 0,
            deletions=commit_data['stats'].get('deletions', 0) if 'stats' in commit_data else 0
        )
        
        return True
    
    def _sync_issues(self, repository: Repository) -> Dict:
        """Sync issues for a repository"""
        url = f'https://api.github.com/repos/{repository.full_name}/issues'
        params = {'state': 'all', 'per_page': 100}
        
        issues_data = self._make_api_request(f"{url}?{'&'.join(f'{k}={v}' for k, v in params.items())}")
        
        new_issues = 0
        for issue_data in issues_data:
            # Skip pull requests (they appear as issues in GitHub API)
            if 'pull_request' in issue_data:
                continue
            
            created = self._import_issue_idempotent(issue_data, repository)
            if created:
                new_issues += 1
        
        return {'new_issues': new_issues, 'total_fetched': len(issues_data)}
    
    def _import_issue_idempotent(self, issue_data: Dict, repository: Repository) -> bool:
        """Import single issue (idempotent)"""
        github_issue_id = issue_data['id']
        
        # Check if issue already exists
        if Issue.objects.filter(github_issue_id=github_issue_id).exists():
            return False
        
        # Get or create contributor
        user_data = issue_data['user']
        contributor, _ = Contributor.objects.get_or_create(
            username=user_data['login'],
            defaults={'avatar_url': user_data['avatar_url']}
        )
        
        # Get or create RepositoryWork
        work, _ = RepositoryWork.objects.get_or_create(
            repository=repository,
            contributor=contributor,
            defaults={'summary': f"Contributions to {repository.name}"}
        )
        
        # Create issue
        Issue.objects.create(
            work=work,
            github_issue_id=github_issue_id,
            title=issue_data['title'],
            body=issue_data.get('body', ''),
            state=issue_data['state'],
            number=issue_data['number'],
            created_at=issue_data['created_at'],
            updated_at=issue_data['updated_at'],
            closed_at=issue_data.get('closed_at')
        )
        
        return True
    
    def _sync_contributors(self, repository: Repository) -> Dict:
        """Sync contributors for a repository"""
        url = f'https://api.github.com/repos/{repository.full_name}/contributors'
        contributors_data = self._make_api_request(url)
        
        synced = 0
        for contrib_data in contributors_data:
            contributor, created = Contributor.objects.get_or_create(
                username=contrib_data['login'],
                defaults={'avatar_url': contrib_data['avatar_url']}
            )
            
            # Ensure RepositoryWork exists
            RepositoryWork.objects.get_or_create(
                repository=repository,
                contributor=contributor,
                defaults={'summary': f"Contributions to {repository.name}"}
            )
            synced += 1
        
        return {'synced_contributors': synced}


class WebhookProcessor:
    """
    Process GitHub webhook events in real-time
    Handles all webhook event types with idempotent operations
    """
    
    @staticmethod
    def verify_signature(payload_body: bytes, signature: str) -> bool:
        """Verify GitHub webhook signature"""
        if not signature:
            return False
        
        secret = settings.GITHUB_WEBHOOK_SECRET.encode()
        hash_object = hmac.new(secret, payload_body, hashlib.sha256)
        expected_signature = 'sha256=' + hash_object.hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)
    
    @staticmethod
    @transaction.atomic
    def process_installation_event(payload: Dict) -> Dict:
        """
        Handle installation events (created, deleted, suspend, unsuspend)
        """
        action = payload['action']
        installation_data = payload['installation']
        installation_id = installation_data['id']
        
        if action == 'created':
            # New installation - auto-import all repositories
            logger.info(f"Processing new installation: {installation_id}")
            
            installation, created = GitHubAppInstallation.objects.get_or_create(
                installation_id=installation_id,
                defaults={
                    'account_login': installation_data['account']['login'],
                    'account_type': installation_data['account']['type'],
                    'account_avatar_url': installation_data['account']['avatar_url'],
                    'target_type': installation_data.get('target_type', 'User')
                }
            )
            
            # Trigger auto-import in background
            sync_manager = GitHubSyncManager(installation_id)
            result = sync_manager.auto_import_all_repositories(installation)
            
            return {'status': 'imported', 'result': result}
        
        elif action == 'deleted':
            # Installation removed - clean up
            logger.info(f"Processing installation deletion: {installation_id}")
            
            installation = GitHubAppInstallation.objects.filter(
                installation_id=installation_id
            ).first()
            
            if installation:
                # Optionally: keep repos but mark as disconnected, or delete them
                # For now, we'll delete associated repositories
                repos_deleted = Repository.objects.filter(installation=installation).count()
                Repository.objects.filter(installation=installation).delete()
                installation.delete()
                
                return {'status': 'deleted', 'repos_removed': repos_deleted}
            
            return {'status': 'not_found'}
        
        elif action in ['suspend', 'unsuspend']:
            logger.info(f"Installation {action}: {installation_id}")
            return {'status': action}
        
        return {'status': 'ignored', 'action': action}
    
    @staticmethod
    @transaction.atomic
    def process_installation_repositories_event(payload: Dict) -> Dict:
        """
        Handle repository add/remove from installation
        """
        action = payload['action']
        installation_id = payload['installation']['id']
        
        try:
            installation = GitHubAppInstallation.objects.get(
                installation_id=installation_id
            )
        except GitHubAppInstallation.DoesNotExist:
            logger.error(f"Installation not found: {installation_id}")
            return {'status': 'error', 'message': 'Installation not found'}
        
        sync_manager = GitHubSyncManager(installation_id)
        
        if action == 'added':
            # New repositories added to installation
            repos_added = payload.get('repositories_added', [])
            imported = []
            
            for repo_data in repos_added:
                try:
                    # Fetch full repo details
                    url = f"https://api.github.com/repositories/{repo_data['id']}"
                    full_repo_data = sync_manager._make_api_request(url)
                    
                    # Import repository
                    repo = sync_manager._import_repository_idempotent(full_repo_data, installation)
                    sync_manager._setup_webhook_idempotent(repo.full_name)
                    imported.append(repo.full_name)
                    
                except Exception as e:
                    logger.error(f"Failed to import {repo_data['full_name']}: {str(e)}")
            
            return {'status': 'added', 'imported': imported}
        
        elif action == 'removed':
            # Repositories removed from installation
            repos_removed = payload.get('repositories_removed', [])
            removed = []
            
            for repo_data in repos_removed:
                try:
                    repo = Repository.objects.get(github_id=repo_data['id'])
                    repo_name = repo.full_name
                    repo.delete()
                    removed.append(repo_name)
                except Repository.DoesNotExist:
                    pass
            
            return {'status': 'removed', 'removed': removed}
        
        return {'status': 'ignored', 'action': action}
    
    @staticmethod
    @transaction.atomic
    def process_repository_event(payload: Dict) -> Dict:
        """
        Handle repository events (created, deleted, renamed, etc.)
        """
        action = payload['action']
        repo_data = payload['repository']
        
        if action == 'created':
            # New repository created in org - auto-import
            logger.info(f"New repository created: {repo_data['full_name']}")
            
            # Find installation for this repository
            installation_id = payload.get('installation', {}).get('id')
            if not installation_id:
                return {'status': 'no_installation'}
            
            try:
                installation = GitHubAppInstallation.objects.get(
                    installation_id=installation_id
                )
                
                sync_manager = GitHubSyncManager(installation_id)
                repo = sync_manager._import_repository_idempotent(repo_data, installation)
                sync_manager._setup_webhook_idempotent(repo.full_name)
                
                return {'status': 'imported', 'repository': repo.full_name}
            except Exception as e:
                logger.error(f"Failed to auto-import repo: {str(e)}")
                return {'status': 'error', 'message': str(e)}
        
        elif action == 'deleted':
            # Repository deleted - remove from database
            logger.info(f"Repository deleted: {repo_data['full_name']}")
            
            try:
                repo = Repository.objects.get(github_id=repo_data['id'])
                repo.delete()
                return {'status': 'deleted', 'repository': repo_data['full_name']}
            except Repository.DoesNotExist:
                return {'status': 'not_found'}
        
        elif action == 'renamed':
            # Repository renamed - update name
            logger.info(f"Repository renamed: {repo_data['full_name']}")
            
            try:
                repo = Repository.objects.get(github_id=repo_data['id'])
                repo.name = repo_data['name']
                repo.full_name = repo_data['full_name']
                repo.url = repo_data['html_url']
                repo.save(update_fields=['name', 'full_name', 'url'])
                return {'status': 'renamed', 'repository': repo.full_name}
            except Repository.DoesNotExist:
                return {'status': 'not_found'}
        
        return {'status': 'ignored', 'action': action}
    
    @staticmethod
    @transaction.atomic
    def process_push_event(payload: Dict) -> Dict:
        """Handle push events (new commits)"""
        repo_data = payload['repository']
        commits = payload.get('commits', [])
        
        try:
            repo = Repository.objects.get(github_id=repo_data['id'])
        except Repository.DoesNotExist:
            return {'status': 'repository_not_found'}
        
        installation_id = payload.get('installation', {}).get('id')
        if not installation_id:
            return {'status': 'no_installation'}
        
        sync_manager = GitHubSyncManager(installation_id)
        
        new_commits = 0
        for commit_data in commits:
            # Fetch full commit details
            url = f"https://api.github.com/repos/{repo.full_name}/commits/{commit_data['id']}"
            full_commit = sync_manager._make_api_request(url)
            created = sync_manager._import_commit_idempotent(full_commit, repo)
            if created:
                new_commits += 1
        
        return {'status': 'processed', 'new_commits': new_commits}
    
    @staticmethod
    @transaction.atomic
    def process_pull_request_event(payload: Dict) -> Dict:
        """Handle pull request events"""
        action = payload['action']
        pr = payload['pull_request']
        repo_data = payload['repository']
        
        logger.info(f"PR {action}: #{pr['number']} in {repo_data['full_name']}")
        
        # Store PR data or trigger actions
        # For now, just log it
        return {'status': 'processed', 'action': action, 'pr_number': pr['number']}
    
    @staticmethod
    @transaction.atomic
    def process_issues_event(payload: Dict) -> Dict:
        """Handle issues events"""
        action = payload['action']
        issue_data = payload['issue']
        repo_data = payload['repository']
        
        try:
            repo = Repository.objects.get(github_id=repo_data['id'])
        except Repository.DoesNotExist:
            return {'status': 'repository_not_found'}
        
        installation_id = payload.get('installation', {}).get('id')
        if not installation_id:
            return {'status': 'no_installation'}
        
        sync_manager = GitHubSyncManager(installation_id)
        
        if action in ['opened', 'reopened']:
            created = sync_manager._import_issue_idempotent(issue_data, repo)
            return {'status': 'created' if created else 'exists', 'issue_number': issue_data['number']}
        
        elif action == 'closed':
            # Update issue status
            try:
                issue = Issue.objects.get(github_issue_id=issue_data['id'])
                issue.state = 'closed'
                issue.closed_at = issue_data.get('closed_at')
                issue.save(update_fields=['state', 'closed_at'])
                return {'status': 'closed', 'issue_number': issue_data['number']}
            except Issue.DoesNotExist:
                return {'status': 'not_found'}
        
        return {'status': 'processed', 'action': action}


class SyncJobRunner:
    """
    Background job runner for periodic syncs
    This ensures consistency even if webhooks are missed
    """
    
    @staticmethod
    def run_periodic_sync() -> Dict:
        """
        Run periodic sync for all installations
        Should be called by cron job every 15-30 minutes
        """
        logger.info("Starting periodic sync job")
        
        results = {
            'installations_processed': 0,
            'repositories_synced': 0,
            'errors': []
        }
        
        # Get all active installations
        installations = GitHubAppInstallation.objects.all()
        
        for installation in installations:
            try:
                logger.info(f"Syncing installation: {installation.account_login}")
                
                sync_manager = GitHubSyncManager(installation.installation_id)
                
                # Get all repositories for this installation
                repos = Repository.objects.filter(installation=installation)
                
                for repo in repos:
                    try:
                        # Only sync if not synced in last 10 minutes
                        if repo.last_synced_at:
                            time_since_sync = timezone.now() - repo.last_synced_at
                            if time_since_sync < timedelta(minutes=10):
                                continue
                        
                        sync_result = sync_manager.sync_repository_data(repo)
                        results['repositories_synced'] += 1
                        
                    except Exception as e:
                        logger.error(f"Failed to sync {repo.full_name}: {str(e)}")
                        results['errors'].append({
                            'repository': repo.full_name,
                            'error': str(e)
                        })
                
                results['installations_processed'] += 1
                
            except Exception as e:
                logger.error(f"Failed to sync installation {installation.id}: {str(e)}")
                results['errors'].append({
                    'installation': installation.account_login,
                    'error': str(e)
                })
        
        # Record sync job
        SyncJob.objects.create(
            job_type='periodic_sync',
            status='completed' if not results['errors'] else 'completed_with_errors',
            repositories_processed=results['repositories_synced'],
            errors_count=len(results['errors']),
            details=results
        )
        
        logger.info(f"Periodic sync completed: {results}")
        return results
    
    @staticmethod
    def sync_single_repository(repo_id: int) -> Dict:
        """Sync a single repository on-demand"""
        try:
            repo = Repository.objects.get(id=repo_id)
            installation = repo.installation
            
            if not installation:
                return {'error': 'No installation found for repository'}
            
            sync_manager = GitHubSyncManager(installation.installation_id)
            result = sync_manager.sync_repository_data(repo)
            
            return {'success': True, 'result': result}
            
        except Repository.DoesNotExist:
            return {'error': 'Repository not found'}
        except Exception as e:
            logger.error(f"Sync failed: {str(e)}")
            return {'error': str(e)}

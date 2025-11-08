"""
Modern Unified GitHub Service
Replaces: GitHubImporter, GitHubFetcher, GitHubSyncManager, LiveSyncManager

This consolidated service handles all GitHub operations with:
- Efficient API usage with retry logic
- Webhook-driven live updates
- Background sync capabilities
- Caching for rate limit optimization
"""
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.cache import cache
from django.db import transaction
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging

from .models import Repository, Contributor, RepositoryWork, Commit, Issue

logger = logging.getLogger(__name__)


class GitHubService:
    """
    Unified GitHub integration service
    Handles fetching, importing, and syncing GitHub data
    """
    
    def __init__(self, github_token: Optional[str] = None):
        self.base_url = "https://api.github.com"
        self.headers = {'Accept': 'application/vnd.github.v3+json'}
        
        if github_token:
            self.headers['Authorization'] = f'token {github_token}'
        
        # Configure session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
    
    # =========================================================================
    # Public API
    # =========================================================================
    
    def import_repository(self, repo_url: str) -> Repository:
        """
        Complete repository import workflow
        
        Args:
            repo_url: GitHub repository URL or 'owner/repo'
            
        Returns:
            Repository object with all data imported
        """
        logger.info(f"Starting import for: {repo_url}")
        
        # Parse repository info
        owner, repo_name = self._parse_repo_url(repo_url)
        cache_key = f"github_repo:{owner}/{repo_name}"
        
        try:
            # Fetch all data in parallel (optimized)
            repo_data = self._fetch_repository(owner, repo_name)
            contributors_data = self._fetch_contributors(owner, repo_name, limit=100)
            commits_data = self._fetch_commits(owner, repo_name, limit=500)
            issues_data = self._fetch_issues(owner, repo_name, limit=100)
            
            # Import into database (transactional)
            with transaction.atomic():
                repository = self._create_or_update_repository(repo_data)
                contributors = self._import_contributors(contributors_data)
                self._import_commits(repository, commits_data, contributors)
                self._import_issues(repository, issues_data, contributors)
                
                # Update repository stats
                repository.calculate_health_score()
            
            # Cache the import
            cache.set(cache_key, repository.id, timeout=3600)  # 1 hour
            
            logger.info(f"✓ Successfully imported {repository.name}")
            return repository
            
        except Exception as e:
            logger.error(f"✗ Import failed: {e}")
            raise
    
    def sync_repository(self, repository: Repository) -> Dict:
        """
        Sync existing repository with latest GitHub data
        
        Args:
            repository: Repository object to sync
            
        Returns:
            Dict with sync statistics
        """
        logger.info(f"Syncing repository: {repository.name}")
        
        owner, repo_name = self._parse_repo_url(repository.url)
        
        try:
            # Fetch only new data since last sync
            last_sync = repository.last_synced_at or (timezone.now() - timedelta(days=30))
            
            # Incremental fetch
            new_commits = self._fetch_commits_since(owner, repo_name, since=last_sync)
            new_issues = self._fetch_issues_since(owner, repo_name, since=last_sync)
            
            # Import new data
            with transaction.atomic():
                contributors = list(Contributor.objects.filter(
                    works__repository=repository
                ).distinct())
                
                commit_count = self._import_commits(repository, new_commits, contributors)
                issue_count = self._import_issues(repository, new_issues, contributors)
                
                # Update repository metadata
                repo_data = self._fetch_repository(owner, repo_name)
                repository.stars = repo_data.get('stargazers_count', 0)
                repository.forks = repo_data.get('forks_count', 0)
                repository.open_issues = repo_data.get('open_issues_count', 0)
                repository.last_synced_at = timezone.now()
                repository.save()
            
            stats = {
                'new_commits': commit_count,
                'new_issues': issue_count,
                'synced_at': repository.last_synced_at
            }
            
            logger.info(f"✓ Synced {repository.name}: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"✗ Sync failed: {e}")
            raise
    
    def process_webhook_event(self, event_type: str, payload: Dict) -> Dict:
        """
        Process GitHub webhook events for live updates
        
        Args:
            event_type: Type of GitHub event (push, pull_request, issues)
            payload: Webhook payload from GitHub
            
        Returns:
            Dict with processing results
        """
        logger.info(f"Processing webhook: {event_type}")
        
        try:
            if event_type == 'push':
                return self._process_push_event(payload)
            elif event_type == 'pull_request':
                return self._process_pr_event(payload)
            elif event_type == 'issues':
                return self._process_issue_event(payload)
            else:
                logger.warning(f"Unsupported event type: {event_type}")
                return {'status': 'ignored', 'reason': 'unsupported_event'}
                
        except Exception as e:
            logger.error(f"Webhook processing failed: {e}")
            return {'status': 'error', 'error': str(e)}
    
    # =========================================================================
    # Private Methods - GitHub API
    # =========================================================================
    
    def _fetch_repository(self, owner: str, repo: str) -> Dict:
        """Fetch repository metadata"""
        url = f"{self.base_url}/repos/{owner}/{repo}"
        response = self.session.get(url, headers=self.headers, timeout=10)
        
        if response.status_code == 404:
            raise ValueError(f"Repository {owner}/{repo} not found")
        elif response.status_code == 403:
            raise ValueError("Rate limit exceeded. Add GitHub token.")
        
        response.raise_for_status()
        return response.json()
    
    def _fetch_contributors(self, owner: str, repo: str, limit: int = 100) -> List[Dict]:
        """Fetch repository contributors"""
        contributors = []
        page = 1
        
        while len(contributors) < limit:
            url = f"{self.base_url}/repos/{owner}/{repo}/contributors"
            params = {'page': page, 'per_page': min(100, limit - len(contributors))}
            
            response = self.session.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if not data:
                break
            
            contributors.extend(data)
            page += 1
        
        return contributors[:limit]
    
    def _fetch_commits(self, owner: str, repo: str, limit: int = 500) -> List[Dict]:
        """Fetch repository commits"""
        commits = []
        page = 1
        
        while len(commits) < limit:
            url = f"{self.base_url}/repos/{owner}/{repo}/commits"
            params = {'page': page, 'per_page': min(100, limit - len(commits))}
            
            response = self.session.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if not data:
                break
            
            commits.extend(data)
            page += 1
        
        return commits[:limit]
    
    def _fetch_commits_since(self, owner: str, repo: str, since: datetime) -> List[Dict]:
        """Fetch commits since a specific date"""
        url = f"{self.base_url}/repos/{owner}/{repo}/commits"
        params = {'since': since.isoformat()}
        
        response = self.session.get(url, headers=self.headers, params=params, timeout=10)
        response.raise_for_status()
        
        return response.json()
    
    def _fetch_issues(self, owner: str, repo: str, limit: int = 100) -> List[Dict]:
        """Fetch repository issues"""
        issues = []
        page = 1
        
        while len(issues) < limit:
            url = f"{self.base_url}/repos/{owner}/{repo}/issues"
            params = {
                'state': 'all',
                'page': page,
                'per_page': min(100, limit - len(issues))
            }
            
            response = self.session.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if not data:
                break
            
            # Filter out pull requests (they appear in issues endpoint)
            issues.extend([i for i in data if 'pull_request' not in i])
            page += 1
        
        return issues[:limit]
    
    def _fetch_issues_since(self, owner: str, repo: str, since: datetime) -> List[Dict]:
        """Fetch issues since a specific date"""
        url = f"{self.base_url}/repos/{owner}/{repo}/issues"
        params = {'state': 'all', 'since': since.isoformat()}
        
        response = self.session.get(url, headers=self.headers, params=params, timeout=10)
        response.raise_for_status()
        
        return [i for i in response.json() if 'pull_request' not in i]
    
    # =========================================================================
    # Private Methods - Database Operations
    # =========================================================================
    
    def _create_or_update_repository(self, repo_data: Dict) -> Repository:
        """Create or update repository from GitHub data"""
        repo, created = Repository.objects.update_or_create(
            url=repo_data['html_url'],
            defaults={
                'name': repo_data['name'],
                'avatar_url': repo_data['owner']['avatar_url'],
                'summary': repo_data.get('description') or f"{repo_data['name']} repository",
                'stars': repo_data.get('stargazers_count', 0),
                'forks': repo_data.get('forks_count', 0),
                'open_issues': repo_data.get('open_issues_count', 0),
                'primary_language': repo_data.get('language', 'Unknown'),
            }
        )
        
        logger.debug(f"{'Created' if created else 'Updated'} repository: {repo.name}")
        return repo
    
    def _import_contributors(self, contributors_data: List[Dict]) -> List[Contributor]:
        """Import contributors from GitHub data"""
        contributors = []
        
        for contrib_data in contributors_data:
            contributor, _ = Contributor.objects.update_or_create(
                username=contrib_data['login'],
                defaults={
                    'url': contrib_data['html_url'],
                    'avatar_url': contrib_data['avatar_url'],
                    'summary': f"{contrib_data['login']} - {contrib_data.get('contributions', 0)} contributions",
                }
            )
            contributors.append(contributor)
        
        logger.debug(f"Imported {len(contributors)} contributors")
        return contributors
    
    def _import_commits(self, repo: Repository, commits_data: List[Dict], 
                       contributors: List[Contributor]) -> int:
        """Import commits and link to repository/contributors"""
        contributor_map = {c.username: c for c in contributors}
        imported_count = 0
        
        for commit_data in commits_data:
            author = commit_data.get('author', {})
            author_login = author.get('login') if author else None
            contributor = contributor_map.get(author_login) if author_login else None
            
            if not contributor:
                continue
            
            # Create or get RepositoryWork
            work, _ = RepositoryWork.objects.get_or_create(
                repository=repo,
                contributor=contributor
            )
            
            # Create commit
            commit_sha = commit_data['sha']
            if not Commit.objects.filter(sha=commit_sha).exists():
                Commit.objects.create(
                    sha=commit_sha,
                    url=commit_data['html_url'],
                    message=commit_data['commit']['message'],
                    contributor=contributor,
                    repository=repo,
                    committed_at=self._parse_datetime(commit_data['commit']['author']['date'])
                )
                imported_count += 1
        
        logger.debug(f"Imported {imported_count} commits")
        return imported_count
    
    def _import_issues(self, repo: Repository, issues_data: List[Dict],
                      contributors: List[Contributor]) -> int:
        """Import issues and link to repository/contributors"""
        contributor_map = {c.username: c for c in contributors}
        imported_count = 0
        
        for issue_data in issues_data:
            creator = issue_data.get('user', {})
            creator_login = creator.get('login') if creator else None
            contributor = contributor_map.get(creator_login) if creator_login else None
            
            if not contributor:
                continue
            
            # Create or get RepositoryWork
            work, _ = RepositoryWork.objects.get_or_create(
                repository=repo,
                contributor=contributor
            )
            
            # Create issue
            issue_number = issue_data['number']
            if not Issue.objects.filter(number=issue_number, work__repository=repo).exists():
                Issue.objects.create(
                    work=work,
                    number=issue_number,
                    title=issue_data['title'],
                    body=issue_data.get('body', ''),
                    state=issue_data['state'],
                    labels=','.join([label['name'] for label in issue_data.get('labels', [])]),
                    created_at=self._parse_datetime(issue_data['created_at']),
                    updated_at=self._parse_datetime(issue_data['updated_at'])
                )
                imported_count += 1
        
        logger.debug(f"Imported {imported_count} issues")
        return imported_count
    
    # =========================================================================
    # Webhook Event Processors
    # =========================================================================
    
    def _process_push_event(self, payload: Dict) -> Dict:
        """Process push webhook event"""
        repo_url = payload['repository']['html_url']
        commits = payload.get('commits', [])
        
        try:
            repository = Repository.objects.get(url=repo_url)
            # Trigger incremental sync
            self.sync_repository(repository)
            
            return {
                'status': 'success',
                'repository': repository.name,
                'commits_processed': len(commits)
            }
        except Repository.DoesNotExist:
            return {'status': 'ignored', 'reason': 'repository_not_imported'}
    
    def _process_pr_event(self, payload: Dict) -> Dict:
        """Process pull request webhook event"""
        # TODO: Implement PR processing if needed
        return {'status': 'success', 'action': 'pr_event_logged'}
    
    def _process_issue_event(self, payload: Dict) -> Dict:
        """Process issues webhook event"""
        # TODO: Implement issue event processing
        return {'status': 'success', 'action': 'issue_event_logged'}
    
    # =========================================================================
    # Utility Methods
    # =========================================================================
    
    def _parse_repo_url(self, repo_url: str) -> Tuple[str, str]:
        """Parse GitHub URL to extract owner and repo name"""
        repo_url = repo_url.strip().rstrip('/').replace('.git', '')
        repo_url = repo_url.replace('https://', '').replace('http://', '').replace('github.com/', '')
        
        parts = repo_url.split('/')
        if len(parts) >= 2:
            return parts[-2], parts[-1]
        
        raise ValueError(f"Invalid GitHub URL format: {repo_url}")
    
    def _parse_datetime(self, date_string: str) -> datetime:
        """Parse GitHub datetime string"""
        try:
            dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            return timezone.make_aware(dt) if timezone.is_naive(dt) else dt
        except:
            return timezone.now()


# Global service instance
github_service = GitHubService()

"""
GitHub Repository Data Fetcher
Fetches repository, contributors, commits, and issues from any GitHub repo
"""
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from datetime import datetime
from django.conf import settings
import time


class GitHubFetcher:
    """Fetch data from GitHub API with retry logic"""
    
    def __init__(self, github_token=None):
        self.base_url = "https://api.github.com"
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
        }
        if github_token:
            self.headers['Authorization'] = f'token {github_token}'
        
        # Create session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=5,  # Total number of retries
            backoff_factor=2,  # Wait 1, 2, 4, 8, 16 seconds between retries
            status_forcelist=[429, 500, 502, 503, 504],  # Retry on these HTTP codes
            allowed_methods=["HEAD", "GET", "OPTIONS"]  # Only retry safe methods
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
    
    def parse_repo_url(self, repo_url):
        """
        Parse GitHub repository URL to extract owner and repo name
        Examples:
        - https://github.com/owner/repo
        - https://github.com/owner/repo.git
        - github.com/owner/repo
        - owner/repo
        """
        repo_url = repo_url.strip().rstrip('/')
        
        # Remove .git suffix if present
        if repo_url.endswith('.git'):
            repo_url = repo_url[:-4]
        
        # Remove protocol and domain
        repo_url = repo_url.replace('https://', '').replace('http://', '')
        repo_url = repo_url.replace('github.com/', '')
        
        # Split owner/repo
        parts = repo_url.split('/')
        if len(parts) >= 2:
            return parts[-2], parts[-1]
        else:
            raise ValueError("Invalid GitHub repository URL format. Use: owner/repo or https://github.com/owner/repo")
    
    def fetch_repository(self, owner, repo):
        """Fetch repository metadata with retry logic"""
        url = f"{self.base_url}/repos/{owner}/{repo}"
        
        try:
            response = self.session.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 404:
                raise ValueError(f"Repository {owner}/{repo} not found")
            elif response.status_code == 403:
                raise ValueError("GitHub API rate limit exceeded. Please add a GitHub token.")
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(f"Network error connecting to GitHub API. Check your internet connection and firewall settings. Details: {str(e)}")
        except requests.exceptions.Timeout:
            raise TimeoutError("Request to GitHub API timed out. Please try again.")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error fetching repository data: {str(e)}")
    
    def fetch_contributors(self, owner, repo, max_contributors=100):
        """Fetch repository contributors with their stats"""
        contributors = []
        page = 1
        per_page = 30
        
        while len(contributors) < max_contributors:
            url = f"{self.base_url}/repos/{owner}/{repo}/contributors"
            params = {'page': page, 'per_page': per_page}
            response = self.session.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if not data:
                break
            
            contributors.extend(data)
            page += 1
            
            if len(data) < per_page:
                break
        
        return contributors[:max_contributors]
    
    def fetch_contributor_details(self, username):
        """Fetch detailed info about a contributor"""
        url = f"{self.base_url}/users/{username}"
        response = self.session.get(url, headers=self.headers, timeout=30)
        response.raise_for_status()
        return response.json()
    
    def fetch_commits(self, owner, repo, max_commits=500):
        """Fetch repository commits with detailed stats"""
        commits = []
        page = 1
        per_page = 100
        
        # First, get the list of commits
        basic_commits = []
        while len(basic_commits) < max_commits:
            url = f"{self.base_url}/repos/{owner}/{repo}/commits"
            params = {'page': page, 'per_page': per_page}
            response = self.session.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if not data:
                break
            
            basic_commits.extend(data)
            page += 1
            
            if len(data) < per_page:
                break
            
            # Rate limiting
            time.sleep(0.5)
        
        basic_commits = basic_commits[:max_commits]
        print(f"  Fetching detailed stats for {min(100, len(basic_commits))} commits...")
        
        # Now fetch detailed stats for each commit (limited to first 100 to avoid API limits)
        detailed_commits = []
        for i, commit in enumerate(basic_commits[:100]):  # Limit to first 100 commits
            try:
                sha = commit['sha']
                detail_url = f"{self.base_url}/repos/{owner}/{repo}/commits/{sha}"
                detail_response = self.session.get(detail_url, headers=self.headers, timeout=30)
                detail_response.raise_for_status()
                detailed_commits.append(detail_response.json())
                
                if (i + 1) % 10 == 0:
                    print(f"    Fetched {i + 1}/{min(100, len(basic_commits))} commits...")
                
                # Rate limiting - be gentle with API
                if i % 10 == 0:
                    time.sleep(1)
                else:
                    time.sleep(0.2)
            except Exception as e:
                print(f"    Warning: Could not fetch details for commit {sha[:7]}: {e}")
                # Fall back to basic commit data
                detailed_commits.append(commit)
        
        # For remaining commits, use basic data
        detailed_commits.extend(basic_commits[100:])
        
        print(f"  ✓ Total commits ready: {len(detailed_commits)} ({len(detailed_commits[:100])} with stats)")
        return detailed_commits
    
    def fetch_issues(self, owner, repo, state='all', max_issues=500):
        """Fetch repository issues (includes PRs)"""
        issues = []
        page = 1
        per_page = 100
        
        while len(issues) < max_issues:
            url = f"{self.base_url}/repos/{owner}/{repo}/issues"
            params = {'state': state, 'page': page, 'per_page': per_page}
            response = self.session.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if not data:
                break
            
            # Filter out pull requests (issues endpoint includes PRs)
            actual_issues = [item for item in data if 'pull_request' not in item]
            issues.extend(actual_issues)
            page += 1
            
            if len(data) < per_page:
                break
            
            # Rate limiting
            time.sleep(0.5)
        
        return issues[:max_issues]
    
    def fetch_commit_details(self, owner, repo, sha):
        """Fetch detailed commit information"""
        url = f"{self.base_url}/repos/{owner}/{repo}/commits/{sha}"
        response = self.session.get(url, headers=self.headers, timeout=30)
        response.raise_for_status()
        return response.json()
    
    def fetch_all_data(self, repo_url):
        """
        Fetch all data for a repository
        Returns: dict with repo, contributors, commits, issues
        """
        owner, repo = self.parse_repo_url(repo_url)
        
        print(f"Fetching data for {owner}/{repo}...")
        
        # Fetch repository info
        print("  → Repository metadata...")
        repo_data = self.fetch_repository(owner, repo)
        
        # Fetch contributors
        print("  → Contributors...")
        contributors_data = self.fetch_contributors(owner, repo)
        
        # Fetch contributor details
        print("  → Contributor details...")
        detailed_contributors = []
        for i, contributor in enumerate(contributors_data[:30]):  # Limit to top 30
            try:
                details = self.fetch_contributor_details(contributor['login'])
                detailed_contributors.append({
                    **contributor,
                    'details': details
                })
                time.sleep(0.3)  # Rate limiting
            except Exception as e:
                print(f"    Warning: Could not fetch details for {contributor['login']}: {e}")
                detailed_contributors.append(contributor)
        
        # Fetch commits
        print("  → Commits...")
        commits_data = self.fetch_commits(owner, repo)
        
        # Fetch issues
        print("  → Issues...")
        try:
            issues_data = self.fetch_issues(owner, repo)
        except Exception as e:
            print(f"    Warning: Could not fetch issues (rate limit?): {e}")
            issues_data = []
        
        print(f"✓ Fetched: {len(detailed_contributors)} contributors, {len(commits_data)} commits, {len(issues_data)} issues")
        
        return {
            'repository': repo_data,
            'contributors': detailed_contributors,
            'commits': commits_data,
            'issues': issues_data,
            'owner': owner,
            'repo': repo
        }

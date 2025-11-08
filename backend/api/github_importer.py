"""
Import GitHub data into database
"""
from django.utils import timezone
from datetime import datetime
from api.models import (
    Repository, Contributor, RepositoryWork, Commit, Issue,
    ActivityLog, Collaboration
)
from api.github_fetcher import GitHubFetcher
import json


class GitHubImporter:
    """Import GitHub data into database"""
    
    def __init__(self, github_token=None):
        self.fetcher = GitHubFetcher(github_token)
    
    def import_repository(self, repo_url):
        """
        Import a GitHub repository and all its data
        Returns: Repository object
        """
        # Fetch all data from GitHub
        data = self.fetcher.fetch_all_data(repo_url)
        
        # Create or update repository
        repo = self._create_repository(data['repository'])
        
        # Import contributors
        contributors = self._import_contributors(data['contributors'])
        
        # Import commits and link to contributors
        self._import_commits(repo, data['commits'], contributors)
        
        # Import issues
        self._import_issues(repo, data['issues'], contributors)
        
        # Update contributor stats
        self._update_contributor_stats(contributors)
        
        # Create collaborations
        self._create_collaborations(repo, contributors)
        
        # Update repository health
        repo.calculate_health_score()
        
        return repo
    
    def _create_repository(self, repo_data):
        """Create or update repository from GitHub data"""
        repo, created = Repository.objects.update_or_create(
            url=repo_data['html_url'],
            defaults={
                'name': repo_data['name'],
                'avatar_url': repo_data['owner']['avatar_url'],
                'summary': repo_data['description'] or f"{repo_data['name']} repository",
                'raw_data': json.dumps(repo_data),
                'stars': repo_data.get('stargazers_count', 0),
                'forks': repo_data.get('forks_count', 0),
                'open_issues': repo_data.get('open_issues_count', 0),
                'primary_language': repo_data.get('language', 'Unknown'),
                'created_at': self._parse_github_date(repo_data['created_at']),
                'updated_at': self._parse_github_date(repo_data['updated_at']),
            }
        )
        
        print(f"{'Created' if created else 'Updated'} repository: {repo.name}")
        return repo
    
    def _import_contributors(self, contributors_data):
        """Import contributors from GitHub data"""
        contributors = []
        
        for contrib_data in contributors_data:
            details = contrib_data.get('details', contrib_data)
            
            contributor, created = Contributor.objects.update_or_create(
                username=contrib_data['login'],
                defaults={
                    'url': contrib_data['html_url'],
                    'avatar_url': contrib_data['avatar_url'],
                    'summary': f"{contrib_data['login']} - {contrib_data.get('contributions', 0)} contributions",
                    'bio': details.get('bio', ''),
                    'company': details.get('company', ''),
                    'location': details.get('location', ''),
                }
            )
            contributors.append(contributor)
            
            if created:
                print(f"  + Added contributor: {contributor.username}")
        
        print(f"Imported {len(contributors)} contributors")
        return contributors
    
    def _import_commits(self, repo, commits_data, contributors):
        """Import commits from GitHub data"""
        contributor_map = {c.username: c for c in contributors}
        commit_count = 0
        
        print(f"  Importing {len(commits_data)} commits...")
        for commit_data in commits_data:
            try:
                # Get or create contributor
                author_login = commit_data.get('author', {}).get('login') if commit_data.get('author') else None
                
                if not author_login:
                    # Try committer if author not available
                    author_login = commit_data.get('committer', {}).get('login') if commit_data.get('committer') else None
                
                if not author_login:
                    continue
                
                contributor = contributor_map.get(author_login)
                if not contributor:
                    # Create contributor if not exists
                    author_data = commit_data.get('author') or commit_data.get('committer')
                    contributor, _ = Contributor.objects.get_or_create(
                        username=author_login,
                        defaults={
                            'url': author_data.get('html_url', f'https://github.com/{author_login}'),
                            'avatar_url': author_data.get('avatar_url', ''),
                            'summary': f"{author_login} contributor",
                        }
                    )
                    contributor_map[author_login] = contributor
                
                # Get or create repository work
                work, _ = RepositoryWork.objects.get_or_create(
                    repository=repo,
                    contributor=contributor,
                    defaults={
                        'summary': f"{contributor.username} contributions to {repo.name}",
                    }
                )
                
                # Create commit
                commit_info = commit_data.get('commit', {})
                commit_date = commit_info.get('author', {}).get('date') or commit_info.get('committer', {}).get('date')
                
                # Debug: Check if stats are present
                has_stats = 'stats' in commit_data
                has_files = 'files' in commit_data
                if not has_stats or not has_files:
                    print(f"    ⚠ Commit {commit_data.get('sha', 'unknown')[:7]} missing stats:{not has_stats} files:{not has_files}")
                
                commit, created = Commit.objects.get_or_create(
                    url=commit_data['html_url'],
                    defaults={
                        'work': work,
                        'repository': repo,
                        'contributor': contributor,
                        'raw_data': commit_data,
                        'summary': commit_info.get('message', 'No message')[:500],
                        'committed_at': self._parse_github_date(commit_date) if commit_date else timezone.now(),
                        'additions': commit_data.get('stats', {}).get('additions', 0),
                        'deletions': commit_data.get('stats', {}).get('deletions', 0),
                        'files_changed': len(commit_data.get('files', [])),
                    }
                )
                
                if created:
                    commit.calculate_churn()
                    commit_count += 1
                    
                    # Create activity log
                    ActivityLog.objects.create(
                        contributor=contributor,
                        repository=repo,
                        activity_type='commit',
                        timestamp=commit.committed_at,
                        metadata={'sha': commit_data['sha'][:7]}
                    )
            
            except Exception as e:
                print(f"    Warning: Could not import commit {commit_data.get('sha', 'unknown')[:7]}: {e}")
        
        print(f"Imported {commit_count} commits")
    
    def _import_issues(self, repo, issues_data, contributors):
        """Import issues from GitHub data"""
        contributor_map = {c.username: c for c in contributors}
        issue_count = 0
        
        for issue_data in issues_data:
            try:
                # Get or create contributor
                creator_login = issue_data.get('user', {}).get('login')
                if not creator_login:
                    continue
                
                contributor = contributor_map.get(creator_login)
                if not contributor:
                    user_data = issue_data.get('user', {})
                    contributor, _ = Contributor.objects.get_or_create(
                        username=creator_login,
                        defaults={
                            'url': user_data.get('html_url', f'https://github.com/{creator_login}'),
                            'avatar_url': user_data.get('avatar_url', ''),
                            'summary': f"{creator_login} contributor",
                        }
                    )
                    contributor_map[creator_login] = contributor
                
                # Get or create repository work
                work, _ = RepositoryWork.objects.get_or_create(
                    repository=repo,
                    contributor=contributor,
                    defaults={
                        'summary': f"{contributor.username} contributions to {repo.name}",
                    }
                )
                
                # Determine issue type
                is_bug = any(label.get('name', '').lower() in ['bug', 'bugfix'] 
                           for label in issue_data.get('labels', []))
                is_feature = any(label.get('name', '').lower() in ['feature', 'enhancement'] 
                               for label in issue_data.get('labels', []))
                
                # Create issue
                issue, created = Issue.objects.get_or_create(
                    url=issue_data['html_url'],
                    defaults={
                        'work': work,
                        'raw_data': issue_data,
                        'summary': issue_data.get('title', 'No title')[:500],
                        'state': issue_data.get('state', 'open'),
                        'is_bug': is_bug,
                        'is_feature': is_feature,
                        'priority': 'medium',  # Default
                        'created_at': self._parse_github_date(issue_data['created_at']),
                        'updated_at': self._parse_github_date(issue_data['updated_at']),
                    }
                )
                
                if created:
                    issue_count += 1
                    
                    # Create activity logs
                    ActivityLog.objects.create(
                        contributor=contributor,
                        repository=repo,
                        activity_type='issue_created',
                        timestamp=issue.created_at,
                        metadata={'number': issue_data['number']}
                    )
                    
                    if issue.state == 'closed':
                        ActivityLog.objects.create(
                            contributor=contributor,
                            repository=repo,
                            activity_type='issue_closed',
                            timestamp=issue.updated_at,
                            metadata={'number': issue_data['number']}
                        )
            
            except Exception as e:
                print(f"    Warning: Could not import issue #{issue_data.get('number', 'unknown')}: {e}")
        
        print(f"Imported {issue_count} issues")
    
    def _update_contributor_stats(self, contributors):
        """Update contributor statistics"""
        for contributor in contributors:
            contributor.total_commits = contributor.commits.count()
            contributor.total_issues_closed = Issue.objects.filter(
                work__contributor=contributor,
                state='closed'
            ).count()
            contributor.last_activity = timezone.now()
            
            # Analyze work pattern
            contributor.analyze_work_pattern()
            
            # Calculate score
            contributor.calculate_score()
            
            contributor.save()
        
        print(f"Updated stats for {len(contributors)} contributors")
    
    def _create_collaborations(self, repo, contributors):
        """Create collaboration relationships"""
        # Simple approach: contributors who both work on the same repo collaborate
        from itertools import combinations
        
        collab_count = 0
        for c1, c2 in combinations(contributors, 2):
            # Check if both have commits
            c1_commits = Commit.objects.filter(repository=repo, contributor=c1).count()
            c2_commits = Commit.objects.filter(repository=repo, contributor=c2).count()
            
            if c1_commits > 0 and c2_commits > 0:
                collab, created = Collaboration.objects.get_or_create(
                    contributor_1=c1,
                    contributor_2=c2,
                    repository=repo,
                    defaults={
                        'shared_commits': min(c1_commits, c2_commits),
                        'code_reviews': 0,
                        'issue_discussions': 0,
                    }
                )
                
                if created:
                    collab.calculate_strength()
                    collab_count += 1
        
        print(f"Created {collab_count} collaborations")
    
    def _parse_github_date(self, date_string):
        """Parse GitHub date string to Django datetime"""
        if not date_string:
            return timezone.now()
        
        try:
            # GitHub uses ISO format: 2021-01-01T00:00:00Z
            dt = datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%SZ')
            return timezone.make_aware(dt, timezone.utc)
        except:
            return timezone.now()

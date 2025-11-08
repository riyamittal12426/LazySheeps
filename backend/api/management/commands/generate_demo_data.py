"""
Sample Data Generator for Hackathon Demo
Populates the database with realistic data to showcase all features
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random
from api.models import (
    Contributor, Repository, RepositoryWork, Commit, Issue,
    Badge, Collaboration, ActivityLog
)


class Command(BaseCommand):
    help = 'Generate sample data for hackathon demo'

    def handle(self, *args, **kwargs):
        self.stdout.write('🚀 Generating hackathon demo data...\n')
        
        # Create sample contributors
        contributors = self.create_contributors()
        self.stdout.write(f'✅ Created {len(contributors)} contributors\n')
        
        # Create sample repositories
        repositories = self.create_repositories()
        self.stdout.write(f'✅ Created {len(repositories)} repositories\n')
        
        # Create repository works (connections)
        works = self.create_repository_works(contributors, repositories)
        self.stdout.write(f'✅ Created {len(works)} repository works\n')
        
        # Create commits and issues
        commits, issues = self.create_commits_and_issues(works)
        self.stdout.write(f'✅ Created {len(commits)} commits and {len(issues)} issues\n')
        
        # Update contributor stats
        self.update_contributor_stats(contributors)
        self.stdout.write(f'✅ Updated contributor statistics\n')
        
        # Create collaborations
        collaborations = self.create_collaborations(contributors, repositories)
        self.stdout.write(f'✅ Created {len(collaborations)} collaborations\n')
        
        # Award badges
        badges = self.award_sample_badges(contributors)
        self.stdout.write(f'✅ Awarded {len(badges)} badges\n')
        
        # Create activity logs
        activities = self.create_activity_logs(contributors, repositories)
        self.stdout.write(f'✅ Created {len(activities)} activity logs\n')
        
        # Update repository health
        self.update_repository_health(repositories)
        self.stdout.write(f'✅ Updated repository health scores\n')
        
        self.stdout.write(self.style.SUCCESS('\n🎉 Demo data generation complete!'))
        self.stdout.write('\n📊 Summary:')
        self.stdout.write(f'   - Contributors: {Contributor.objects.count()}')
        self.stdout.write(f'   - Repositories: {Repository.objects.count()}')
        self.stdout.write(f'   - Commits: {Commit.objects.count()}')
        self.stdout.write(f'   - Issues: {Issue.objects.count()}')
        self.stdout.write(f'   - Badges: {Badge.objects.count()}')
        self.stdout.write(f'   - Collaborations: {Collaboration.objects.count()}')
        self.stdout.write(f'   - Activities: {ActivityLog.objects.count()}')

    def create_contributors(self):
        contributors_data = [
            {
                'username': 'alice_dev',
                'bio': 'Full-stack developer passionate about open source',
                'company': 'Tech Corp',
                'location': 'San Francisco, CA',
                'skill_tags': ['Python', 'React', 'Django', 'API Design'],
            },
            {
                'username': 'bob_backend',
                'bio': 'Backend specialist, loves databases',
                'company': 'DataCo',
                'location': 'New York, NY',
                'skill_tags': ['Python', 'Django', 'PostgreSQL', 'Redis'],
            },
            {
                'username': 'charlie_frontend',
                'bio': 'UI/UX enthusiast, React wizard',
                'company': 'DesignHub',
                'location': 'Austin, TX',
                'skill_tags': ['React', 'JavaScript', 'CSS', 'Design'],
            },
            {
                'username': 'diana_ml',
                'bio': 'Machine learning engineer',
                'company': 'AI Labs',
                'location': 'Boston, MA',
                'skill_tags': ['Python', 'TensorFlow', 'ML', 'Data Science'],
            },
            {
                'username': 'eve_devops',
                'bio': 'DevOps engineer, automation lover',
                'company': 'CloudFirst',
                'location': 'Seattle, WA',
                'skill_tags': ['Docker', 'Kubernetes', 'CI/CD', 'AWS'],
            },
        ]
        
        contributors = []
        for data in contributors_data:
            contributor, created = Contributor.objects.get_or_create(
                username=data['username'],
                defaults={
                    'url': f'https://github.com/{data["username"]}',
                    'avatar_url': f'https://api.dicebear.com/7.x/avataaars/svg?seed={data["username"]}',
                    'summary': f'{data["bio"]} - {data["company"]}',
                    'bio': data['bio'],
                    'company': data['company'],
                    'location': data['location'],
                    'skill_tags': data['skill_tags'],
                }
            )
            contributors.append(contributor)
        
        return contributors

    def create_repositories(self):
        repos_data = [
            {
                'name': 'awesome-api',
                'primary_language': 'Python',
                'stars': 1250,
                'forks': 320,
            },
            {
                'name': 'react-dashboard',
                'primary_language': 'JavaScript',
                'stars': 890,
                'forks': 150,
            },
            {
                'name': 'ml-toolkit',
                'primary_language': 'Python',
                'stars': 2100,
                'forks': 450,
            },
        ]
        
        repositories = []
        for data in repos_data:
            repo, created = Repository.objects.get_or_create(
                name=data['name'],
                defaults={
                    'avatar_url': f'https://api.dicebear.com/7.x/identicon/svg?seed={data["name"]}',
                    'url': f'https://github.com/org/{data["name"]}',
                    'summary': f'A {data["primary_language"]} project for {data["name"].replace("-", " ")}',
                    'primary_language': data['primary_language'],
                    'stars': data['stars'],
                    'forks': data['forks'],
                    'created_at': timezone.now() - timedelta(days=365),
                    'updated_at': timezone.now(),
                }
            )
            repositories.append(repo)
        
        return repositories

    def create_repository_works(self, contributors, repositories):
        works = []
        for repo in repositories:
            # Each repo has 3-4 contributors
            selected_contributors = random.sample(contributors, k=random.randint(3, 4))
            for contributor in selected_contributors:
                work, created = RepositoryWork.objects.get_or_create(
                    repository=repo,
                    contributor=contributor,
                    defaults={
                        'summary': f'{contributor.username} contributions to {repo.name}',
                    }
                )
                works.append(work)
        
        return works

    def create_commits_and_issues(self, works):
        commits = []
        issues = []
        
        for work in works:
            # Create 10-30 commits per work
            commit_count = random.randint(10, 30)
            for i in range(commit_count):
                days_ago = random.randint(1, 90)
                commit_time = timezone.now() - timedelta(days=days_ago, hours=random.randint(0, 23))
                
                commit = Commit.objects.create(
                    work=work,
                    repository=work.repository,
                    contributor=work.contributor,
                    url=f'https://github.com/org/{work.repository.name}/commit/{i}',
                    raw_data={'sha': f'abc{i}def'},
                    summary=f'Fix: {random.choice(["bug fix", "feature", "refactor", "docs", "test"])} in {work.repository.name}',
                    additions=random.randint(10, 200),
                    deletions=random.randint(5, 100),
                    files_changed=random.randint(1, 10),
                    committed_at=commit_time,
                )
                commit.calculate_churn()
                commits.append(commit)
            
            # Update work metrics
            work.commit_count = commit_count
            work.lines_added = sum(c.additions for c in commits if c.work == work)
            work.lines_removed = sum(c.deletions for c in commits if c.work == work)
            work.save()
            
            # Create 3-10 issues per work
            issue_count = random.randint(3, 10)
            for i in range(issue_count):
                days_ago = random.randint(1, 60)
                issue = Issue.objects.create(
                    work=work,
                    url=f'https://github.com/org/{work.repository.name}/issues/{i}',
                    raw_data={'number': i, 'state': random.choice(['open', 'closed'])},
                    summary=f'Issue: {random.choice(["Bug in", "Feature request for", "Question about"])} {work.repository.name}',
                    state=random.choice(['open', 'closed', 'closed', 'closed']),  # More closed
                    is_bug=random.choice([True, False]),
                    is_feature=random.choice([True, False]),
                    priority=random.choice(['low', 'medium', 'high']),
                    created_at=timezone.now() - timedelta(days=days_ago),
                )
                issues.append(issue)
            
            work.issue_count = issue_count
            work.save()
        
        return commits, issues

    def update_contributor_stats(self, contributors):
        for contributor in contributors:
            contributor.total_commits = contributor.commits.count()
            contributor.total_issues_closed = Issue.objects.filter(
                work__contributor=contributor,
                state='closed'
            ).count()
            contributor.total_prs_reviewed = random.randint(10, 50)
            contributor.activity_streak = random.randint(0, 45)
            contributor.last_activity = timezone.now() - timedelta(days=random.randint(0, 3))
            
            # Analyze work pattern
            contributor.analyze_work_pattern()
            
            # Calculate score
            contributor.calculate_score()
            
            contributor.save()

    def create_collaborations(self, contributors, repositories):
        collaborations = []
        for repo in repositories:
            # Get contributors for this repo
            repo_contributors = list(Contributor.objects.filter(works__repository=repo))
            
            # Create collaborations between pairs
            for i, c1 in enumerate(repo_contributors):
                for c2 in repo_contributors[i+1:]:
                    collab, created = Collaboration.objects.get_or_create(
                        contributor_1=c1,
                        contributor_2=c2,
                        repository=repo,
                        defaults={
                            'shared_commits': random.randint(5, 30),
                            'code_reviews': random.randint(2, 15),
                            'issue_discussions': random.randint(3, 20),
                        }
                    )
                    collab.calculate_strength()
                    collaborations.append(collab)
        
        return collaborations

    def award_sample_badges(self, contributors):
        badges = []
        badge_types = ['early_bird', 'night_owl', 'bug_hunter', 'code_reviewer', 'streak_master']
        
        for contributor in contributors:
            # Award 2-3 random badges to each contributor
            for badge_type in random.sample(badge_types, k=random.randint(2, 3)):
                badge, created = Badge.objects.get_or_create(
                    contributor=contributor,
                    badge_type=badge_type,
                    defaults={
                        'description': f'Earned for exceptional {badge_type.replace("_", " ")}!',
                    }
                )
                if created:
                    badges.append(badge)
        
        return badges

    def create_activity_logs(self, contributors, repositories):
        activities = []
        activity_types = ['commit', 'issue_created', 'issue_closed', 'pr_opened', 'pr_reviewed']
        
        for _ in range(100):  # Create 100 activity logs
            contributor = random.choice(contributors)
            repository = random.choice(repositories)
            activity_type = random.choice(activity_types)
            
            activity = ActivityLog.objects.create(
                contributor=contributor,
                repository=repository,
                activity_type=activity_type,
                timestamp=timezone.now() - timedelta(days=random.randint(0, 30)),
                metadata={'sample': True},
            )
            activities.append(activity)
        
        return activities

    def update_repository_health(self, repositories):
        for repo in repositories:
            repo.calculate_health_score()
            repo.activity_trend = random.choice(['up', 'stable', 'down'])
            repo.save()

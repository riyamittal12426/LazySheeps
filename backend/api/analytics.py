"""
Advanced Analytics & AI Features
"""
from django.db.models import Count, Avg, Sum, Q, F
from django.utils import timezone
from datetime import timedelta
from .models import Contributor, Repository, Commit, Issue, Badge, Collaboration, ActivityLog
import json


class ContributorAnalytics:
    """Analytics for contributor insights"""
    
    @staticmethod
    def get_leaderboard(limit=10):
        """Get top contributors by score"""
        return Contributor.objects.all()[:limit].values(
            'id', 'username', 'avatar_url', 'total_score', 
            'level', 'activity_streak', 'total_commits',
            'total_issues_closed', 'total_prs_reviewed'
        )
    
    @staticmethod
    def get_contributor_stats(contributor_id):
        """Detailed stats for a contributor"""
        contributor = Contributor.objects.get(id=contributor_id)
        
        # Recent activity (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_commits = contributor.commits.filter(committed_at__gte=thirty_days_ago).count()
        
        # Repository diversity
        repos_contributed = contributor.works.count()
        
        # Collaboration count
        collaborations = Collaboration.objects.filter(
            Q(contributor_1=contributor) | Q(contributor_2=contributor)
        ).count()
        
        # Badge collection
        badges = contributor.badges.all().values('badge_type', 'earned_date', 'description')
        
        return {
            'contributor': {
                'id': contributor.id,
                'username': contributor.username,
                'avatar_url': contributor.avatar_url,
                'level': contributor.level,
                'total_score': contributor.total_score,
                'experience_points': contributor.experience_points,
                'activity_streak': contributor.activity_streak,
                'preferred_work_hours': contributor.preferred_work_hours,
                'skill_tags': contributor.skill_tags,
                'burnout_risk_score': contributor.burnout_risk_score,
            },
            'metrics': {
                'total_commits': contributor.total_commits,
                'total_issues_closed': contributor.total_issues_closed,
                'total_prs_reviewed': contributor.total_prs_reviewed,
                'recent_commits_30d': recent_commits,
                'repositories_count': repos_contributed,
                'collaborations_count': collaborations,
            },
            'badges': list(badges),
            'coding_pattern': contributor.coding_pattern,
        }
    
    @staticmethod
    def award_badges(contributor_id):
        """Check and award badges to contributor"""
        contributor = Contributor.objects.get(id=contributor_id)
        awarded = []
        
        # Early Bird badge (50+ commits before 9 AM)
        morning_commits = contributor.commits.filter(
            committed_at__hour__lt=9
        ).count()
        if morning_commits >= 50:
            badge, created = Badge.objects.get_or_create(
                contributor=contributor,
                badge_type='early_bird',
                defaults={'description': f'{morning_commits} commits before 9 AM!'}
            )
            if created:
                awarded.append('early_bird')
        
        # Night Owl badge (50+ commits after 10 PM)
        night_commits = contributor.commits.filter(
            committed_at__hour__gte=22
        ).count()
        if night_commits >= 50:
            badge, created = Badge.objects.get_or_create(
                contributor=contributor,
                badge_type='night_owl',
                defaults={'description': f'{night_commits} commits after 10 PM!'}
            )
            if created:
                awarded.append('night_owl')
        
        # Bug Hunter badge (50+ issues closed)
        if contributor.total_issues_closed >= 50:
            badge, created = Badge.objects.get_or_create(
                contributor=contributor,
                badge_type='bug_hunter',
                defaults={'description': f'Closed {contributor.total_issues_closed} issues!'}
            )
            if created:
                awarded.append('bug_hunter')
        
        # Code Reviewer badge (100+ PR reviews)
        if contributor.total_prs_reviewed >= 100:
            badge, created = Badge.objects.get_or_create(
                contributor=contributor,
                badge_type='code_reviewer',
                defaults={'description': f'Reviewed {contributor.total_prs_reviewed} PRs!'}
            )
            if created:
                awarded.append('code_reviewer')
        
        # Streak Master badge (30+ day streak)
        if contributor.activity_streak >= 30:
            badge, created = Badge.objects.get_or_create(
                contributor=contributor,
                badge_type='streak_master',
                defaults={'description': f'{contributor.activity_streak} day streak!'}
            )
            if created:
                awarded.append('streak_master')
        
        # Team Player badge (10+ collaborations)
        collab_count = Collaboration.objects.filter(
            Q(contributor_1=contributor) | Q(contributor_2=contributor)
        ).count()
        if collab_count >= 10:
            badge, created = Badge.objects.get_or_create(
                contributor=contributor,
                badge_type='team_player',
                defaults={'description': f'{collab_count} collaborations!'}
            )
            if created:
                awarded.append('team_player')
        
        return awarded
    
    @staticmethod
    def predict_burnout(contributor_id):
        """Predict burnout risk based on activity patterns"""
        contributor = Contributor.objects.get(id=contributor_id)
        
        # Get activity logs for last 60 days
        sixty_days_ago = timezone.now() - timedelta(days=60)
        activities = ActivityLog.objects.filter(
            contributor=contributor,
            timestamp__gte=sixty_days_ago
        ).order_by('timestamp')
        
        if activities.count() < 10:
            return {'risk_score': 0.0, 'risk_level': 'low', 'recommendations': []}
        
        # Calculate activity intensity
        weekly_activities = []
        current_week_count = 0
        current_week_start = activities.first().timestamp
        
        for activity in activities:
            if (activity.timestamp - current_week_start).days >= 7:
                weekly_activities.append(current_week_count)
                current_week_count = 0
                current_week_start = activity.timestamp
            current_week_count += 1
        
        if current_week_count > 0:
            weekly_activities.append(current_week_count)
        
        # Burnout indicators
        risk_score = 0.0
        recommendations = []
        
        # 1. Sustained high intensity (70+ activities per week for 4+ weeks)
        if len(weekly_activities) >= 4:
            high_intensity_weeks = sum(1 for count in weekly_activities[-4:] if count >= 70)
            if high_intensity_weeks >= 3:
                risk_score += 0.3
                recommendations.append("Consider reducing workload - sustained high activity detected")
        
        # 2. Increasing trend
        if len(weekly_activities) >= 4:
            recent_avg = sum(weekly_activities[-2:]) / 2
            older_avg = sum(weekly_activities[-4:-2]) / 2
            if recent_avg > older_avg * 1.5:
                risk_score += 0.2
                recommendations.append("Activity is increasing rapidly")
        
        # 3. No breaks (activity every day for 30+ days)
        if contributor.activity_streak >= 30:
            risk_score += 0.2
            recommendations.append("No breaks detected - consider taking time off")
        
        # 4. Work pattern irregularity (working at all hours)
        work_hours = contributor.commits.values_list('committed_at__hour', flat=True)
        unique_hours = len(set(work_hours))
        if unique_hours >= 16:  # Working across 16+ different hours
            risk_score += 0.15
            recommendations.append("Irregular work hours detected")
        
        # 5. High code churn (lots of revisions)
        high_churn_commits = contributor.commits.filter(code_churn_ratio__gte=0.5).count()
        total_commits = contributor.commits.count()
        if total_commits > 0 and (high_churn_commits / total_commits) > 0.3:
            risk_score += 0.15
            recommendations.append("High code churn - code quality may be suffering")
        
        # Normalize risk score
        risk_score = min(risk_score, 1.0)
        
        # Update contributor
        contributor.burnout_risk_score = risk_score
        contributor.save()
        
        # Determine risk level
        if risk_score < 0.3:
            risk_level = 'low'
        elif risk_score < 0.6:
            risk_level = 'medium'
        else:
            risk_level = 'high'
        
        return {
            'risk_score': round(risk_score, 2),
            'risk_level': risk_level,
            'recommendations': recommendations,
            'weekly_activity': weekly_activities,
        }


class RepositoryAnalytics:
    """Analytics for repository insights"""
    
    @staticmethod
    def get_repository_health(repo_id):
        """Comprehensive repository health metrics"""
        repo = Repository.objects.get(id=repo_id)
        
        # Calculate health score
        health = repo.calculate_health_score()
        
        # Contributor count
        contributor_count = repo.works.values('contributor').distinct().count()
        
        # Activity in last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_commits = repo.commits.filter(committed_at__gte=thirty_days_ago).count()
        recent_issues = repo.issues.filter(created_at__gte=thirty_days_ago).count()
        
        # Issue metrics
        open_issues = repo.issues.filter(state='open').count()
        closed_issues = repo.issues.filter(state='closed').count()
        total_issues = open_issues + closed_issues
        
        if total_issues > 0:
            issue_close_rate = closed_issues / total_issues
        else:
            issue_close_rate = 0.0
        
        # Top contributors
        top_contributors = repo.works.order_by('-commit_count')[:5].values(
            'contributor__id', 'contributor__username', 
            'contributor__avatar_url', 'commit_count', 'lines_added'
        )
        
        return {
            'repository': {
                'id': repo.id,
                'name': repo.name,
                'health_score': health,
                'activity_trend': repo.activity_trend,
                'stars': repo.stars,
                'forks': repo.forks,
            },
            'metrics': {
                'contributor_count': contributor_count,
                'recent_commits_30d': recent_commits,
                'recent_issues_30d': recent_issues,
                'open_issues': open_issues,
                'closed_issues': closed_issues,
                'issue_close_rate': round(issue_close_rate, 2),
                'total_commits': repo.commits.count(),
            },
            'top_contributors': list(top_contributors),
        }
    
    @staticmethod
    def predict_completion(repo_id):
        """Predict project completion based on velocity"""
        repo = Repository.objects.get(id=repo_id)
        
        # Get issue velocity (issues closed per week)
        weeks = 8
        weeks_ago = timezone.now() - timedelta(weeks=weeks)
        closed_per_week = repo.issues.filter(
            state='closed',
            updated_at__gte=weeks_ago
        ).count() / weeks
        
        # Open issues
        open_issues = repo.issues.filter(state='open').count()
        
        if closed_per_week > 0 and open_issues > 0:
            weeks_to_completion = open_issues / closed_per_week
            estimated_date = timezone.now() + timedelta(weeks=weeks_to_completion)
            
            repo.predicted_completion_date = estimated_date.date()
            repo.velocity_score = closed_per_week
            repo.save()
            
            return {
                'estimated_completion_date': estimated_date.date().isoformat(),
                'weeks_remaining': round(weeks_to_completion, 1),
                'velocity': round(closed_per_week, 2),
                'open_issues': open_issues,
            }
        
        return {
            'estimated_completion_date': None,
            'message': 'Insufficient data for prediction',
        }


class CollaborationAnalytics:
    """Analytics for team collaboration"""
    
    @staticmethod
    def get_collaboration_network(repo_id=None):
        """Get collaboration network for visualization"""
        nodes = []
        edges = []
        
        if repo_id:
            # Get collaborations for specific repo
            collaborations = Collaboration.objects.filter(repository_id=repo_id)
            contributors = Contributor.objects.filter(
                Q(collaborations_from__repository_id=repo_id) | 
                Q(collaborations_to__repository_id=repo_id)
            ).distinct()
        else:
            # Get all collaborations
            collaborations = Collaboration.objects.all()
            contributors = Contributor.objects.all()
        
        # Create nodes
        for contributor in contributors:
            nodes.append({
                'id': contributor.id,
                'name': contributor.username,
                'avatar': contributor.avatar_url,
                'score': contributor.total_score,
                'level': contributor.level,
            })
        
        # Create edges
        for collab in collaborations:
            edges.append({
                'source': collab.contributor_1.id,
                'target': collab.contributor_2.id,
                'strength': collab.collaboration_strength,
                'interactions': collab.shared_commits + collab.code_reviews + collab.issue_discussions,
            })
        
        return {
            'nodes': nodes,
            'edges': edges,
        }
    
    @staticmethod
    def detect_collaboration_patterns(repo_id):
        """Detect collaboration patterns and team clusters"""
        collaborations = Collaboration.objects.filter(repository_id=repo_id)
        
        if not collaborations.exists():
            return {'clusters': [], 'insights': []}
        
        # Strong collaborations (strength > 0.5)
        strong_collabs = collaborations.filter(collaboration_strength__gte=0.5)
        
        insights = []
        
        if strong_collabs.count() > 0:
            insights.append(f"Found {strong_collabs.count()} strong collaboration pairs")
        
        # Find most collaborative contributor
        from django.db.models import Count
        most_collaborative = Contributor.objects.filter(
            Q(collaborations_from__repository_id=repo_id) | 
            Q(collaborations_to__repository_id=repo_id)
        ).annotate(
            collab_count=Count('collaborations_from') + Count('collaborations_to')
        ).order_by('-collab_count').first()
        
        if most_collaborative:
            insights.append(f"{most_collaborative.username} is the most collaborative contributor")
        
        return {
            'strong_collaboration_count': strong_collabs.count(),
            'insights': insights,
        }

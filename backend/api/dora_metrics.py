"""
DORA Metrics Calculator
Calculate DevOps Research and Assessment metrics for repositories
"""
from django.utils import timezone
from datetime import timedelta
from api.models import Repository, Commit
from django.db.models import Count, Avg, Q
import logging

logger = logging.getLogger(__name__)


class DORAMetricsCalculator:
    """
    Calculate DORA metrics for a repository
    """
    
    def __init__(self, repository):
        self.repository = repository
        self.days = 90  # Default to 90 days
    
    def calculate_all_metrics(self, days=90):
        """
        Calculate all DORA metrics
        Returns dict with all 4 metrics
        """
        self.days = days
        cutoff_date = timezone.now() - timedelta(days=days)
        
        return {
            'deployment_frequency': self.calculate_deployment_frequency(cutoff_date),
            'lead_time_for_changes': self.calculate_lead_time(cutoff_date),
            'change_failure_rate': self.calculate_change_failure_rate(cutoff_date),
            'mttr': self.calculate_mttr(cutoff_date),
            'calculated_at': timezone.now().isoformat(),
            'period_days': days,
            'performance_tier': self.get_performance_tier(),
        }
    
    def calculate_deployment_frequency(self, cutoff_date):
        """
        Calculate deployment frequency (deploys per day)
        
        Method:
        - Count releases/tags created in the period
        - Divide by number of days
        
        Benchmarks (DORA):
        - Elite: On-demand (multiple per day)
        - High: Between once per day and once per week
        - Medium: Between once per week and once per month
        - Low: Fewer than once per month
        """
        # Use commits as proxy (less accurate but works without release tracking)
        # Assume main branch commits = deployments
        commits_count = Commit.objects.filter(
            repository=self.repository,
            committed_at__gte=cutoff_date
        ).count()
        
        # For demo, assume 10% of commits are deployments
        estimated_deployments = commits_count * 0.1
        
        deployment_frequency = estimated_deployments / self.days if self.days > 0 else 0
        
        logger.info(
            f"Deployment Frequency: {deployment_frequency:.2f} deploys/day "
            f"({estimated_deployments} deployments in {self.days} days)"
        )
        
        return round(deployment_frequency, 2)
    
    def calculate_lead_time(self, cutoff_date):
        """
        Calculate lead time for changes (hours)
        
        Method:
        - Time from first commit to deployment (release)
        - Average across all deployments
        
        Benchmarks (DORA):
        - Elite: Less than one hour
        - High: Between one day and one week
        - Medium: Between one week and one month
        - Low: More than one month
        """
        # Simplified calculation:
        # Time between commit and next release
        # For demo, use average time between commits as proxy
        
        recent_commits = Commit.objects.filter(
            repository=self.repository,
            committed_at__gte=cutoff_date
        ).order_by('committed_at')
        
        if recent_commits.count() < 2:
            return 0.0
        
        # Calculate average time between consecutive commits
        time_diffs = []
        commits_list = list(recent_commits)
        
        for i in range(len(commits_list) - 1):
            time_diff = (
                commits_list[i + 1].committed_at - commits_list[i].committed_at
            ).total_seconds() / 3600  # Convert to hours
            time_diffs.append(time_diff)
        
        if not time_diffs:
            return 0.0
        
        avg_lead_time = sum(time_diffs) / len(time_diffs)
        
        logger.info(f"Lead Time: {avg_lead_time:.2f} hours")
        
        return round(avg_lead_time, 2)
    
    def calculate_change_failure_rate(self, cutoff_date):
        """
        Calculate change failure rate (percentage)
        
        Method:
        - Count failed deployments vs total deployments
        - Failed = rollback, hotfix, incident
        
        Benchmarks (DORA):
        - Elite: 0-15%
        - High: 16-30%
        - Medium: 31-45%
        - Low: 46-60%
        """
        # Count "failure" keywords in commit messages
        all_commits = Commit.objects.filter(
            repository=self.repository,
            committed_at__gte=cutoff_date
        )
        
        total_commits = all_commits.count()
        if total_commits == 0:
            return 0.0
        
        # Count "failure" keywords in commit messages
        failed_commits = all_commits.filter(
            Q(summary__icontains='fix') |
            Q(summary__icontains='bug') |
            Q(summary__icontains='hotfix') |
            Q(summary__icontains='revert')
        ).count()
        
        failure_rate = (failed_commits / total_commits) * 100
        
        logger.info(
            f"Change Failure Rate: {failure_rate:.2f}% "
            f"({failed_commits}/{total_commits} commits)"
        )
        
        return round(failure_rate, 2)
    
    def calculate_mttr(self, cutoff_date):
        """
        Calculate Mean Time to Restore (hours)
        
        Method:
        - Average time to resolve incidents/outages
        - Time from failure detection to resolution
        
        Benchmarks (DORA):
        - Elite: Less than one hour
        - High: Less than one day
        - Medium: Between one day and one week
        - Low: More than one week
        """
        # For demo, estimate from issue resolution time
        # Simplified: Use average time to close critical issues
        # For now, return a calculated placeholder based on commit patterns
        
        # Look for "fix" commits and measure time between them
        fix_commits = Commit.objects.filter(
            repository=self.repository,
            committed_at__gte=cutoff_date,
            summary__icontains='fix'
        ).order_by('committed_at')
        
        if fix_commits.count() < 2:
            return 24.0  # Default: 24 hours
        
        # Calculate average time between fix commits
        time_diffs = []
        commits_list = list(fix_commits)
        
        for i in range(len(commits_list) - 1):
            time_diff = (
                commits_list[i + 1].committed_at - commits_list[i].committed_at
            ).total_seconds() / 3600  # Convert to hours
            time_diffs.append(time_diff)
        
        mttr_hours = sum(time_diffs) / len(time_diffs) if time_diffs else 24.0
        
        logger.info(f"MTTR: {mttr_hours:.2f} hours")
        
        return round(mttr_hours, 2)
    
    def get_performance_tier(self):
        """
        Determine DORA performance tier
        Based on all 4 metrics combined
        
        Returns: 'elite', 'high', 'medium', or 'low'
        """
        df = self.repository.deployment_frequency
        lt = self.repository.lead_time_for_changes
        cfr = self.repository.change_failure_rate
        mttr = self.repository.mean_time_to_recovery
        
        # Elite benchmarks
        if (df > 1 and  # Multiple deploys per day
            lt < 24 and  # Less than 1 day
            cfr < 15 and  # < 15% failure rate
            mttr < 1):  # < 1 hour to restore
            return 'elite'
        
        # High benchmarks
        elif (df >= 0.14 and  # At least weekly
              lt < 168 and  # Less than 1 week
              cfr < 30 and
              mttr < 24):
            return 'high'
        
        # Medium benchmarks
        elif (df >= 0.03 and  # At least monthly
              lt < 720 and  # Less than 1 month
              cfr < 45):
            return 'medium'
        
        # Low performance
        else:
            return 'low'
    
    def update_repository_metrics(self):
        """
        Calculate and save metrics to repository
        """
        metrics = self.calculate_all_metrics()
        
        self.repository.deployment_frequency = metrics['deployment_frequency']
        self.repository.lead_time_for_changes = metrics['lead_time_for_changes']
        self.repository.change_failure_rate = metrics['change_failure_rate']
        self.repository.mean_time_to_recovery = metrics['mttr']
        
        self.repository.save()
        
        logger.info(
            f"Updated DORA metrics for {self.repository.name}: "
            f"Tier = {metrics['performance_tier']}"
        )
        
        return metrics


def calculate_dora_for_all_repositories():
    """
    Batch calculate DORA metrics for all repositories
    Run this as a periodic task (e.g., daily cron job)
    """
    repositories = Repository.objects.all()
    results = []
    
    for repo in repositories:
        try:
            calculator = DORAMetricsCalculator(repo)
            metrics = calculator.update_repository_metrics()
            results.append({
                'repository': repo.name,
                'metrics': metrics,
                'success': True
            })
        except Exception as e:
            logger.error(f"Error calculating DORA for {repo.name}: {e}")
            results.append({
                'repository': repo.name,
                'error': str(e),
                'success': False
            })
    
    return results

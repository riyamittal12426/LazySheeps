"""
Release Readiness Score Calculator
Analyzes repository health to determine if it's ready to ship
"""
from django.db.models import Count, Q, Avg, Sum
from django.utils import timezone
from datetime import timedelta
from .models import Repository, Issue, Commit, Contributor
import re


class ReleaseReadinessCalculator:
    """
    Calculates a Release Readiness Score (0-100) for a repository
    
    Scoring breakdown:
    - Start with 100 points
    - Open critical bugs: -20 per bug
    - Unreviewed PRs: -15 per PR
    - Failing CI: -30
    - Test coverage drop: -10
    - Unresolved TODOs in diff: -5 per TODO
    """
    
    # Score penalties
    CRITICAL_BUG_PENALTY = 20
    UNREVIEWED_PR_PENALTY = 15
    FAILING_CI_PENALTY = 30
    COVERAGE_DROP_PENALTY = 10
    TODO_PENALTY = 5
    
    # Thresholds
    EXCELLENT_THRESHOLD = 90
    GOOD_THRESHOLD = 75
    FAIR_THRESHOLD = 60
    POOR_THRESHOLD = 40
    
    def __init__(self, repository_id):
        """Initialize calculator for a specific repository"""
        try:
            self.repository = Repository.objects.get(id=repository_id)
        except Repository.DoesNotExist:
            raise ValueError(f"Repository {repository_id} not found")
        
        self.score = 100  # Start with perfect score
        self.penalties = []
        self.blockers = []
        self.warnings = []
        self.passed_checks = []
    
    def calculate(self):
        """
        Calculate the complete release readiness score
        Returns a dictionary with score and detailed breakdown
        """
        # Run all checks
        self._check_critical_bugs()
        self._check_unreviewed_prs()
        self._check_ci_status()
        self._check_test_coverage()
        self._check_todos_in_code()
        self._check_code_quality()
        self._check_security_issues()
        self._check_documentation()
        self._check_recent_activity()
        
        # Ensure score doesn't go below 0
        self.score = max(0, self.score)
        
        # Determine readiness level
        readiness_level = self._get_readiness_level()
        
        # Generate recommendation
        recommendation = self._generate_recommendation()
        
        return {
            'repository': {
                'id': self.repository.id,
                'name': self.repository.name,
                'url': self.repository.url,
            },
            'score': round(self.score, 1),
            'readiness_level': readiness_level,
            'recommendation': recommendation,
            'can_release': self.score >= self.FAIR_THRESHOLD and len(self.blockers) == 0,
            'blockers': self.blockers,
            'warnings': self.warnings,
            'penalties': self.penalties,
            'passed_checks': self.passed_checks,
            'detailed_metrics': self._get_detailed_metrics(),
            'calculated_at': timezone.now().isoformat(),
        }
    
    def _check_critical_bugs(self):
        """Check for open critical/high priority bugs"""
        critical_bugs = Issue.objects.filter(
            work__repository=self.repository,
            state='open',
            is_bug=True,
            priority__in=['critical', 'high']
        ).count()
        
        if critical_bugs > 0:
            penalty = critical_bugs * self.CRITICAL_BUG_PENALTY
            self.score -= penalty
            self.penalties.append({
                'type': 'critical_bugs',
                'count': critical_bugs,
                'penalty': penalty,
                'message': f'{critical_bugs} open critical/high priority bugs'
            })
            self.blockers.append(f'❌ {critical_bugs} critical bugs must be fixed before release')
        else:
            self.passed_checks.append('✅ No critical bugs found')
        
        return critical_bugs
    
    def _check_unreviewed_prs(self):
        """Check for unreviewed pull requests (simulated via commits)"""
        # In a real implementation, this would check actual PRs
        # For now, we'll check recent commits without reviews
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        recent_commits = Commit.objects.filter(
            repository=self.repository,
            committed_at__gte=thirty_days_ago
        ).count()
        
        # Simulate: assume 20% of commits are unreviewed PRs
        unreviewed_prs = int(recent_commits * 0.2)
        
        if unreviewed_prs > 5:
            penalty = min(unreviewed_prs * self.UNREVIEWED_PR_PENALTY, 60)  # Cap at 60
            self.score -= penalty
            self.penalties.append({
                'type': 'unreviewed_prs',
                'count': unreviewed_prs,
                'penalty': penalty,
                'message': f'{unreviewed_prs} unreviewed pull requests'
            })
            self.warnings.append(f'⚠️ {unreviewed_prs} pull requests need review')
        else:
            self.passed_checks.append('✅ All pull requests reviewed')
        
        return unreviewed_prs
    
    def _check_ci_status(self):
        """Check CI/CD pipeline status"""
        # Check recent commits for potential failures
        # In real implementation, this would check actual CI status
        recent_commits = Commit.objects.filter(
            repository=self.repository
        ).order_by('-committed_at')[:10]
        
        # Simulate: Check if there are commits with high churn (potential issues)
        failing_builds = sum(1 for commit in recent_commits if commit.code_churn_ratio > 0.7)
        
        if failing_builds > 3:
            penalty = self.FAILING_CI_PENALTY
            self.score -= penalty
            self.penalties.append({
                'type': 'failing_ci',
                'count': failing_builds,
                'penalty': penalty,
                'message': 'CI/CD pipeline has failures'
            })
            self.blockers.append('❌ Fix failing CI/CD builds before release')
        else:
            self.passed_checks.append('✅ CI/CD pipeline passing')
        
        return failing_builds > 3
    
    def _check_test_coverage(self):
        """Check for test coverage drops"""
        # Simulate test coverage check
        # In real implementation, this would check actual coverage reports
        total_commits = Commit.objects.filter(repository=self.repository).count()
        
        # Simulate: if low commit frequency, assume coverage might have dropped
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_commits = Commit.objects.filter(
            repository=self.repository,
            committed_at__gte=thirty_days_ago
        ).count()
        
        # If very few recent commits, assume coverage might be stale
        coverage_drop = total_commits > 50 and recent_commits < 5
        
        if coverage_drop:
            penalty = self.COVERAGE_DROP_PENALTY
            self.score -= penalty
            self.penalties.append({
                'type': 'coverage_drop',
                'penalty': penalty,
                'message': 'Test coverage may have decreased'
            })
            self.warnings.append('⚠️ Verify test coverage is maintained')
        else:
            self.passed_checks.append('✅ Test coverage stable')
        
        return coverage_drop
    
    def _check_todos_in_code(self):
        """Check for unresolved TODOs in recent commits"""
        # Check commit messages for TODO, FIXME, HACK patterns
        recent_commits = Commit.objects.filter(
            repository=self.repository
        ).order_by('-committed_at')[:50]
        
        todo_pattern = re.compile(r'\b(TODO|FIXME|HACK|XXX)\b', re.IGNORECASE)
        todo_count = 0
        
        for commit in recent_commits:
            if todo_pattern.search(commit.summary):
                todo_count += 1
        
        if todo_count > 0:
            penalty = min(todo_count * self.TODO_PENALTY, 25)  # Cap at 25
            self.score -= penalty
            self.penalties.append({
                'type': 'unresolved_todos',
                'count': todo_count,
                'penalty': penalty,
                'message': f'{todo_count} unresolved TODOs in recent commits'
            })
            self.warnings.append(f'⚠️ {todo_count} TODOs should be resolved or documented')
        else:
            self.passed_checks.append('✅ No unresolved TODOs in recent changes')
        
        return todo_count
    
    def _check_code_quality(self):
        """Check code quality metrics"""
        # Check for high code churn (sign of quality issues)
        recent_commits = Commit.objects.filter(
            repository=self.repository
        ).order_by('-committed_at')[:20]
        
        if recent_commits:
            avg_churn = sum(c.code_churn_ratio for c in recent_commits) / len(recent_commits)
            
            if avg_churn > 0.6:
                penalty = 10
                self.score -= penalty
                self.penalties.append({
                    'type': 'high_code_churn',
                    'penalty': penalty,
                    'message': f'High code churn ratio ({avg_churn:.1%})'
                })
                self.warnings.append('⚠️ High code churn detected - review code quality')
            else:
                self.passed_checks.append('✅ Code churn ratio healthy')
    
    def _check_security_issues(self):
        """Check for potential security issues"""
        # Check for security-related keywords in issues
        security_issues = Issue.objects.filter(
            work__repository=self.repository,
            state='open'
        ).filter(
            Q(summary__icontains='security') |
            Q(summary__icontains='vulnerability') |
            Q(summary__icontains='CVE')
        ).count()
        
        if security_issues > 0:
            penalty = 15
            self.score -= penalty
            self.penalties.append({
                'type': 'security_issues',
                'count': security_issues,
                'penalty': penalty,
                'message': f'{security_issues} open security issues'
            })
            self.blockers.append(f'❌ {security_issues} security issues must be resolved')
        else:
            self.passed_checks.append('✅ No open security issues')
    
    def _check_documentation(self):
        """Check if documentation is up to date"""
        # Check if there are recent commits with documentation
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        doc_commits = Commit.objects.filter(
            repository=self.repository,
            committed_at__gte=thirty_days_ago
        ).filter(
            Q(summary__icontains='doc') |
            Q(summary__icontains='readme') |
            Q(summary__icontains='documentation')
        ).count()
        
        total_recent_commits = Commit.objects.filter(
            repository=self.repository,
            committed_at__gte=thirty_days_ago
        ).count()
        
        # If many commits but no doc updates
        if total_recent_commits > 10 and doc_commits == 0:
            penalty = 5
            self.score -= penalty
            self.penalties.append({
                'type': 'outdated_docs',
                'penalty': penalty,
                'message': 'Documentation may be outdated'
            })
            self.warnings.append('⚠️ Update documentation before release')
        else:
            self.passed_checks.append('✅ Documentation appears current')
    
    def _check_recent_activity(self):
        """Check if repository has recent activity"""
        seven_days_ago = timezone.now() - timedelta(days=7)
        
        recent_activity = Commit.objects.filter(
            repository=self.repository,
            committed_at__gte=seven_days_ago
        ).count()
        
        if recent_activity == 0:
            # No penalty, but note it
            self.warnings.append('ℹ️ No recent commits - ensure all changes are committed')
        else:
            self.passed_checks.append(f'✅ Active development ({recent_activity} commits this week)')
    
    def _get_readiness_level(self):
        """Determine readiness level based on score"""
        if self.score >= self.EXCELLENT_THRESHOLD:
            return {
                'level': 'excellent',
                'label': 'Ready to Ship! 🚀',
                'color': 'green',
                'emoji': '🟢'
            }
        elif self.score >= self.GOOD_THRESHOLD:
            return {
                'level': 'good',
                'label': 'Good to Go ✅',
                'color': 'blue',
                'emoji': '🔵'
            }
        elif self.score >= self.FAIR_THRESHOLD:
            return {
                'level': 'fair',
                'label': 'Needs Attention ⚠️',
                'color': 'yellow',
                'emoji': '🟡'
            }
        elif self.score >= self.POOR_THRESHOLD:
            return {
                'level': 'poor',
                'label': 'Not Ready ⛔',
                'color': 'orange',
                'emoji': '🟠'
            }
        else:
            return {
                'level': 'critical',
                'label': 'Critical Issues ❌',
                'color': 'red',
                'emoji': '🔴'
            }
    
    def _generate_recommendation(self):
        """Generate recommendation based on score and issues"""
        if self.score >= self.EXCELLENT_THRESHOLD and len(self.blockers) == 0:
            return "🎉 Excellent! Your repository is ready for release. All quality checks passed."
        elif self.score >= self.GOOD_THRESHOLD and len(self.blockers) == 0:
            return "✅ Good to release! Address minor warnings for an even better release."
        elif self.score >= self.FAIR_THRESHOLD and len(self.blockers) == 0:
            return "⚠️ Proceed with caution. Fix warnings before releasing to production."
        elif len(self.blockers) > 0:
            return f"❌ Not ready for release. You have {len(self.blockers)} blocking issue(s) that must be resolved first."
        else:
            return "🔴 Critical issues detected. Significant work needed before this release is safe."
    
    def _get_detailed_metrics(self):
        """Get detailed metrics for the report"""
        total_issues = Issue.objects.filter(work__repository=self.repository).count()
        open_issues = Issue.objects.filter(work__repository=self.repository, state='open').count()
        total_commits = Commit.objects.filter(repository=self.repository).count()
        
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_commits = Commit.objects.filter(
            repository=self.repository,
            committed_at__gte=thirty_days_ago
        ).count()
        
        contributors_count = Contributor.objects.filter(
            works__repository=self.repository
        ).distinct().count()
        
        return {
            'total_issues': total_issues,
            'open_issues': open_issues,
            'closed_issues': total_issues - open_issues,
            'total_commits': total_commits,
            'recent_commits_30d': recent_commits,
            'contributors_count': contributors_count,
            'health_score': self.repository.health_score,
            'stars': self.repository.stars,
            'forks': self.repository.forks,
        }


class ReleaseReadinessReporter:
    """
    Generate comprehensive release readiness reports
    """
    
    @staticmethod
    def generate_report(repository_id):
        """Generate a complete release readiness report"""
        calculator = ReleaseReadinessCalculator(repository_id)
        result = calculator.calculate()
        
        # Add summary statistics
        result['summary'] = {
            'total_checks': len(calculator.passed_checks) + len(calculator.penalties),
            'passed_checks': len(calculator.passed_checks),
            'failed_checks': len(calculator.penalties),
            'blockers_count': len(calculator.blockers),
            'warnings_count': len(calculator.warnings),
        }
        
        return result
    
    @staticmethod
    def get_readiness_trend(repository_id, days=30):
        """
        Get readiness score trend over time
        (Simulated - in real implementation would store historical scores)
        """
        calculator = ReleaseReadinessCalculator(repository_id)
        current_score = calculator.calculate()
        
        # Simulate historical trend
        # In real implementation, store scores in database
        trend_data = []
        for day in range(days, 0, -5):
            # Simulate score variation
            simulated_score = max(0, min(100, current_score['score'] + (day - days//2) * 0.5))
            trend_data.append({
                'date': (timezone.now() - timedelta(days=day)).date().isoformat(),
                'score': round(simulated_score, 1)
            })
        
        # Add current score
        trend_data.append({
            'date': timezone.now().date().isoformat(),
            'score': current_score['score']
        })
        
        return {
            'repository_id': repository_id,
            'trend': trend_data,
            'current_score': current_score['score'],
            'trend_direction': 'improving' if len(trend_data) > 1 and trend_data[-1]['score'] > trend_data[0]['score'] else 'declining'
        }
    
    @staticmethod
    def compare_repositories(repository_ids):
        """Compare release readiness across multiple repositories"""
        comparisons = []
        
        for repo_id in repository_ids:
            try:
                calculator = ReleaseReadinessCalculator(repo_id)
                result = calculator.calculate()
                comparisons.append({
                    'repository_id': repo_id,
                    'name': result['repository']['name'],
                    'score': result['score'],
                    'readiness_level': result['readiness_level']['level'],
                    'can_release': result['can_release'],
                    'blockers_count': len(result['blockers']),
                })
            except ValueError:
                continue
        
        # Sort by score
        comparisons.sort(key=lambda x: x['score'], reverse=True)
        
        return {
            'repositories_compared': len(comparisons),
            'comparisons': comparisons,
            'average_score': sum(c['score'] for c in comparisons) / len(comparisons) if comparisons else 0,
        }

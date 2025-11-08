"""
Team Health Radar - Board-level view of team risks
Analyzes workload, burnout, review latency, and code quality
"""
from django.db.models import Count, Q, Avg, Sum, Max
from django.utils import timezone
from datetime import timedelta
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import Contributor, Repository, Commit, Issue
import logging

logger = logging.getLogger(__name__)


def calculate_workload_score(contributor):
    """
    Calculate workload score (0-100)
    Based on commits and recent activity
    """
    now = timezone.now()
    # Look at last 180 days (6 months) instead of 30 days for better data coverage
    lookback_days = 180
    last_period = now - timedelta(days=lookback_days)
    
    # Get recent activity
    recent_commits = contributor.commits.filter(
        created_at__gte=last_period
    ).count()
    
    # Count recent issues from RepositoryWork
    recent_issues = Issue.objects.filter(
        work__contributor=contributor,
        created_at__gte=last_period
    ).count()
    
    # Calculate score (normalized to 0-100)
    # Adjusted thresholds for 180-day window
    # Thresholds: 0-60 commits = light, 60-150 = moderate, 150+ = heavy
    workload = (recent_commits * 1.5) + (recent_issues * 2)
    score = min(100, (workload / 200) * 100)  # Adjusted for 180-day window
    
    status = 'green' if score < 40 else 'yellow' if score < 70 else 'red'
    
    return {
        'score': round(score, 1),
        'status': status,
        'recent_commits': recent_commits,
        'recent_issues': recent_issues,
        'recommendation': get_workload_recommendation(score)
    }


def calculate_burnout_risk(contributor):
    """
    Calculate burnout risk score (0-100)
    Based on activity patterns, work hours, and intensity
    """
    now = timezone.now()
    # Use 180-day window for better data coverage
    lookback_days = 180
    last_period = now - timedelta(days=lookback_days)
    last_30_days = now - timedelta(days=30)
    
    # Get activity patterns - use committed_at if available, otherwise created_at
    recent_commits = contributor.commits.filter(created_at__gte=last_period)
    
    # Calculate metrics
    total_commits = recent_commits.count()
    
    if total_commits == 0:
        return {
            'score': 0,
            'status': 'green',
            'weekend_work_ratio': 0,
            'late_night_ratio': 0,
            'activity_spike': False,
            'recommendation': '✅ Low burnout risk. No recent activity to analyze.'
        }
    
    # Check for weekend work - use committed_at or fallback to created_at
    weekend_commits = 0
    late_night_commits = 0
    
    for c in recent_commits:
        commit_time = c.committed_at if c.committed_at else c.created_at
        if commit_time:
            if commit_time.weekday() >= 5:  # Saturday = 5, Sunday = 6
                weekend_commits += 1
            if commit_time.hour >= 22 or commit_time.hour <= 6:
                late_night_commits += 1
    
    weekend_ratio = weekend_commits / max(total_commits, 1)
    late_night_ratio = late_night_commits / max(total_commits, 1)
    
    # Check for activity spikes (working too much in short periods)
    # Look at last 30 days vs the entire period
    week_commits = contributor.commits.filter(created_at__gte=last_30_days).count()
    activity_spike = week_commits > (total_commits / 6)  # More than 1/6 of all activity in last 30 days
    
    # Calculate risk score
    risk_score = 0
    
    # High workload increases burnout risk
    if total_commits > 50:
        risk_score += 30
    elif total_commits > 30:
        risk_score += 15
    
    # Weekend work is a red flag
    risk_score += weekend_ratio * 25
    
    # Late night work is concerning
    risk_score += late_night_ratio * 25
    
    # Activity spikes indicate crunch time
    if activity_spike:
        risk_score += 20
    
    risk_score = min(100, risk_score)
    status = 'green' if risk_score < 30 else 'yellow' if risk_score < 60 else 'red'
    
    return {
        'score': round(risk_score, 1),
        'status': status,
        'weekend_work_ratio': round(weekend_ratio * 100, 1),
        'late_night_ratio': round(late_night_ratio * 100, 1),
        'activity_spike': activity_spike,
        'recommendation': get_burnout_recommendation(risk_score)
    }


def calculate_review_latency(contributor):
    """
    Calculate average time to review/respond to issues
    Lower is better (0-100, inverted)
    """
    # Get issues from RepositoryWork
    assigned_issues = Issue.objects.filter(work__contributor=contributor)
    
    if not assigned_issues.exists():
        return {
            'score': 0,
            'status': 'green',
            'avg_response_days': 0,
            'pending_reviews': 0,
            'recommendation': 'No pending reviews'
        }
    
    # Calculate average response time
    total_days = 0
    responded_count = 0
    pending_count = 0
    
    for issue in assigned_issues:
        if issue.state == 'closed':
            # Calculate time from creation to update (approximation)
            if issue.updated_at and issue.created_at:
                delta = issue.updated_at - issue.created_at
                total_days += delta.days
                responded_count += 1
        else:
            pending_count += 1
    
    avg_days = total_days / max(responded_count, 1)
    
    # Score based on response time
    # 0-2 days = excellent (0-20)
    # 2-5 days = good (20-40)
    # 5-10 days = concerning (40-70)
    # 10+ days = poor (70-100)
    if avg_days <= 2:
        score = avg_days * 10
    elif avg_days <= 5:
        score = 20 + ((avg_days - 2) * 6.67)
    elif avg_days <= 10:
        score = 40 + ((avg_days - 5) * 6)
    else:
        score = 70 + min((avg_days - 10) * 3, 30)
    
    score = min(100, score)
    status = 'green' if score < 30 else 'yellow' if score < 60 else 'red'
    
    return {
        'score': round(score, 1),
        'status': status,
        'avg_response_days': round(avg_days, 1),
        'pending_reviews': pending_count,
        'recommendation': get_review_recommendation(score, pending_count)
    }


def calculate_code_churn(contributor):
    """
    Calculate code churn (rewrites, deletions)
    High churn might indicate quality issues or unclear requirements
    """
    now = timezone.now()
    # Use 180-day window for better data coverage
    lookback_days = 180
    last_period = now - timedelta(days=lookback_days)
    
    recent_commits = contributor.commits.filter(created_at__gte=last_period)
    
    if not recent_commits.exists():
        return {
            'score': 0,
            'status': 'green',
            'total_additions': 0,
            'total_deletions': 0,
            'churn_ratio': 0,
            'recommendation': 'No recent activity'
        }
    
    total_additions = sum(c.additions for c in recent_commits)
    total_deletions = sum(c.deletions for c in recent_commits)
    
    # Calculate churn ratio (deletions / additions)
    # High ratio means rewriting code frequently
    churn_ratio = total_deletions / max(total_additions, 1)
    
    # Score based on churn ratio
    # 0-0.3 = healthy (0-30)
    # 0.3-0.6 = moderate (30-60)
    # 0.6+ = high churn (60-100)
    if churn_ratio <= 0.3:
        score = churn_ratio * 100
    elif churn_ratio <= 0.6:
        score = 30 + ((churn_ratio - 0.3) * 100)
    else:
        score = 60 + min((churn_ratio - 0.6) * 100, 40)
    
    score = min(100, score)
    status = 'green' if score < 40 else 'yellow' if score < 70 else 'red'
    
    return {
        'score': round(score, 1),
        'status': status,
        'total_additions': total_additions,
        'total_deletions': total_deletions,
        'churn_ratio': round(churn_ratio, 2),
        'recommendation': get_churn_recommendation(score, churn_ratio)
    }


def calculate_collaboration_health(contributor):
    """
    Calculate collaboration score based on issues and work
    """
    now = timezone.now()
    # Use 180-day window for better data coverage
    lookback_days = 180
    last_period = now - timedelta(days=lookback_days)
    
    # Count collaborative activities
    issues_participated = Issue.objects.filter(
        work__contributor=contributor,
        created_at__gte=last_period
    ).count()
    
    # Calculate collaboration score
    collaboration_score = min(100, issues_participated * 5)
    
    status = 'green' if collaboration_score > 40 else 'yellow' if collaboration_score > 20 else 'red'
    
    return {
        'score': round(collaboration_score, 1),
        'status': status,
        'issues_created': issues_participated,
        'recommendation': get_collaboration_recommendation(collaboration_score)
    }


# Recommendation functions
def get_workload_recommendation(score):
    if score < 40:
        return "✅ Healthy workload. Could take on more tasks if needed."
    elif score < 70:
        return "⚠️ Moderate workload. Monitor for signs of overload."
    else:
        return "🚨 Heavy workload! Consider redistributing tasks or extending deadlines."


def get_burnout_recommendation(score):
    if score < 30:
        return "✅ Low burnout risk. Maintain current work-life balance."
    elif score < 60:
        return "⚠️ Moderate risk. Encourage breaks and time off."
    else:
        return "🚨 High burnout risk! Immediate action needed - reduce workload, mandatory time off."


def get_review_recommendation(score, pending):
    if score < 30:
        return f"✅ Excellent response time! {pending} pending reviews."
    elif score < 60:
        return f"⚠️ Could improve response time. {pending} pending reviews to address."
    else:
        return f"🚨 Review latency is concerning! {pending} pending - prioritize reviews."


def get_churn_recommendation(score, ratio):
    if score < 40:
        return "✅ Healthy code stability. Changes are well-planned."
    elif score < 70:
        return f"⚠️ Moderate churn (ratio: {ratio:.2f}). Review requirements clarity."
    else:
        return f"🚨 High code churn (ratio: {ratio:.2f})! Unclear requirements or quality issues."


def get_collaboration_recommendation(score):
    if score > 40:
        return "✅ Good collaboration. Active in team discussions."
    elif score > 20:
        return "⚠️ Could improve collaboration. Encourage more team interaction."
    else:
        return "🚨 Low collaboration. May need support or clearer communication."


def calculate_overall_health(metrics):
    """Calculate overall team member health score"""
    # Weight different factors
    weights = {
        'workload': 0.25,
        'burnout_risk': 0.35,  # Most important
        'review_latency': 0.20,
        'code_churn': 0.15,
        'collaboration': 0.05
    }
    
    # Invert scores where lower is better
    adjusted_workload = min(100, metrics['workload']['score'] * 0.8)  # Slight discount
    adjusted_burnout = metrics['burnout_risk']['score']  # Direct
    adjusted_review = metrics['review_latency']['score']  # Direct
    adjusted_churn = metrics['code_churn']['score']  # Direct
    adjusted_collab = 100 - metrics['collaboration']['score']  # Invert (higher is better)
    
    overall = (
        adjusted_workload * weights['workload'] +
        adjusted_burnout * weights['burnout_risk'] +
        adjusted_review * weights['review_latency'] +
        adjusted_churn * weights['code_churn'] +
        adjusted_collab * weights['collaboration']
    )
    
    status = 'green' if overall < 40 else 'yellow' if overall < 65 else 'red'
    
    return {
        'score': round(overall, 1),
        'status': status,
        'health_grade': get_health_grade(overall)
    }


def get_health_grade(score):
    if score < 20:
        return 'A+'
    elif score < 35:
        return 'A'
    elif score < 50:
        return 'B'
    elif score < 65:
        return 'C'
    elif score < 80:
        return 'D'
    else:
        return 'F'


@api_view(['GET'])
@permission_classes([AllowAny])
def team_health_radar(request):
    """
    Get comprehensive team health metrics
    Returns board-level view with risk indicators
    """
    try:
        contributors = Contributor.objects.all()
        
        team_health = []
        overall_stats = {
            'total_members': 0,
            'at_risk_count': 0,
            'warning_count': 0,
            'healthy_count': 0,
            'avg_workload': 0,
            'avg_burnout_risk': 0,
        }
        
        for contributor in contributors:
            # Calculate all health metrics
            workload = calculate_workload_score(contributor)
            burnout_risk = calculate_burnout_risk(contributor)
            review_latency = calculate_review_latency(contributor)
            code_churn = calculate_code_churn(contributor)
            collaboration = calculate_collaboration_health(contributor)
            
            metrics = {
                'workload': workload,
                'burnout_risk': burnout_risk,
                'review_latency': review_latency,
                'code_churn': code_churn,
                'collaboration': collaboration
            }
            
            overall_health = calculate_overall_health(metrics)
            
            member_data = {
                'id': contributor.id,
                'username': contributor.username,
                'avatar_url': contributor.avatar_url,
                'metrics': metrics,
                'overall_health': overall_health,
                'priority': 1 if overall_health['status'] == 'red' else 2 if overall_health['status'] == 'yellow' else 3
            }
            
            team_health.append(member_data)
            
            # Update overall stats
            overall_stats['total_members'] += 1
            overall_stats['avg_workload'] += workload['score']
            overall_stats['avg_burnout_risk'] += burnout_risk['score']
            
            if overall_health['status'] == 'red':
                overall_stats['at_risk_count'] += 1
            elif overall_health['status'] == 'yellow':
                overall_stats['warning_count'] += 1
            else:
                overall_stats['healthy_count'] += 1
        
        # Calculate averages
        if overall_stats['total_members'] > 0:
            overall_stats['avg_workload'] = round(
                overall_stats['avg_workload'] / overall_stats['total_members'], 1
            )
            overall_stats['avg_burnout_risk'] = round(
                overall_stats['avg_burnout_risk'] / overall_stats['total_members'], 1
            )
        
        # Sort by priority (red first, then yellow, then green)
        team_health.sort(key=lambda x: x['priority'])
        
        # Generate team-level recommendations
        team_recommendations = generate_team_recommendations(overall_stats, team_health)
        
        return Response({
            'success': True,
            'team_health': team_health,
            'overall_stats': overall_stats,
            'team_recommendations': team_recommendations,
            'last_updated': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error calculating team health: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


def generate_team_recommendations(stats, team_health):
    """Generate actionable recommendations for the team"""
    recommendations = []
    
    # Check for widespread burnout
    if stats['at_risk_count'] > stats['total_members'] * 0.3:
        recommendations.append({
            'priority': 'high',
            'category': 'burnout',
            'message': f"🚨 {stats['at_risk_count']} team members at high risk! Team-wide intervention needed.",
            'actions': [
                'Schedule mandatory time off',
                'Reduce sprint commitments',
                'Consider hiring support',
                'Review project deadlines'
            ]
        })
    
    # Check average workload
    if stats['avg_workload'] > 70:
        recommendations.append({
            'priority': 'high',
            'category': 'workload',
            'message': f"⚠️ Team average workload is {stats['avg_workload']}. Redistribution needed.",
            'actions': [
                'Redistribute tasks more evenly',
                'Defer non-critical features',
                'Increase team capacity'
            ]
        })
    
    # Check for individuals needing attention
    red_status = [m for m in team_health if m['overall_health']['status'] == 'red']
    if red_status:
        for member in red_status[:3]:  # Top 3 at-risk
            recommendations.append({
                'priority': 'high',
                'category': 'individual',
                'message': f"🚨 {member['username']} needs immediate attention (Grade: {member['overall_health']['health_grade']})",
                'actions': [
                    f"1-on-1 check-in with {member['username']}",
                    'Reduce their current workload',
                    'Offer support or mentoring'
                ]
            })
    
    # Positive reinforcement
    if stats['healthy_count'] == stats['total_members']:
        recommendations.append({
            'priority': 'info',
            'category': 'positive',
            'message': "✅ Entire team is healthy! Great job maintaining work-life balance.",
            'actions': ['Maintain current practices', 'Share what\'s working']
        })
    
    return recommendations


@api_view(['GET'])
@permission_classes([AllowAny])
def contributor_health_detail(request, contributor_id):
    """
    Get detailed health metrics for a specific contributor
    """
    try:
        contributor = Contributor.objects.get(id=contributor_id)
        
        workload = calculate_workload_score(contributor)
        burnout_risk = calculate_burnout_risk(contributor)
        review_latency = calculate_review_latency(contributor)
        code_churn = calculate_code_churn(contributor)
        collaboration = calculate_collaboration_health(contributor)
        
        metrics = {
            'workload': workload,
            'burnout_risk': burnout_risk,
            'review_latency': review_latency,
            'code_churn': code_churn,
            'collaboration': collaboration
        }
        
        overall_health = calculate_overall_health(metrics)
        
        # Get historical data (last 90 days, weekly snapshots)
        # This would require storing historical data - simplified for now
        
        return Response({
            'success': True,
            'contributor': {
                'id': contributor.id,
                'username': contributor.username,
                'avatar_url': contributor.avatar_url
            },
            'metrics': metrics,
            'overall_health': overall_health,
            'detailed_recommendations': generate_individual_recommendations(metrics, overall_health)
        })
        
    except Contributor.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Contributor not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error getting contributor health: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


def generate_individual_recommendations(metrics, overall):
    """Generate detailed recommendations for individual"""
    recommendations = []
    
    # Workload recommendations
    if metrics['workload']['status'] == 'red':
        recommendations.append({
            'category': 'Workload',
            'status': 'critical',
            'message': metrics['workload']['recommendation'],
            'actions': [
                'Defer 2-3 non-critical tasks',
                'Decline new assignments this sprint',
                'Request help from team members'
            ]
        })
    
    # Burnout recommendations
    if metrics['burnout_risk']['status'] in ['red', 'yellow']:
        recommendations.append({
            'category': 'Burnout Risk',
            'status': 'critical' if metrics['burnout_risk']['status'] == 'red' else 'warning',
            'message': metrics['burnout_risk']['recommendation'],
            'actions': [
                'Take 2-3 days off immediately' if metrics['burnout_risk']['status'] == 'red' else 'Schedule time off soon',
                'Avoid weekend/late-night work',
                'Set clear work hour boundaries',
                'Consider flexible schedule'
            ]
        })
    
    # Review latency
    if metrics['review_latency']['status'] != 'green':
        recommendations.append({
            'category': 'Review Latency',
            'status': 'warning',
            'message': metrics['review_latency']['recommendation'],
            'actions': [
                'Block time for reviews daily',
                'Use review checklists',
                'Ask for help if overwhelmed'
            ]
        })
    
    # Code churn
    if metrics['code_churn']['status'] != 'green':
        recommendations.append({
            'category': 'Code Quality',
            'status': 'warning',
            'message': metrics['code_churn']['recommendation'],
            'actions': [
                'Clarify requirements before coding',
                'Use design docs for complex features',
                'Pair program on uncertain areas',
                'Request architecture review'
            ]
        })
    
    return recommendations

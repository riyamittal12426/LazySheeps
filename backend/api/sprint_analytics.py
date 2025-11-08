"""
Sprint Planning Analytics & AI
"""
from django.db.models import Avg, Sum, Count, Q, F
from django.utils import timezone
from datetime import timedelta, date
from .models import Repository, Contributor, Issue, Commit
from .sprint_models import Sprint, SprintIssue, TeamMemberCapacity, SprintVelocityHistory
import json


class SprintAnalytics:
    """Analytics for sprint planning and predictions"""
    
    @staticmethod
    def calculate_team_velocity(repository_id, sprints_to_analyze=3):
        """
        Calculate average team velocity based on recent sprints
        """
        recent_sprints = Sprint.objects.filter(
            repository_id=repository_id,
            status='completed'
        ).order_by('-end_date')[:sprints_to_analyze]
        
        if not recent_sprints:
            return {
                'average_velocity': 0,
                'velocity_trend': 'unknown',
                'sprints_analyzed': 0,
                'velocities': [],
            }
        
        velocities = [sprint.actual_velocity for sprint in recent_sprints]
        average_velocity = sum(velocities) / len(velocities)
        
        # Determine trend
        if len(velocities) >= 2:
            recent_avg = sum(velocities[:2]) / 2
            older_avg = sum(velocities[2:]) / len(velocities[2:]) if len(velocities) > 2 else velocities[0]
            
            if recent_avg > older_avg * 1.1:
                trend = 'improving'
            elif recent_avg < older_avg * 0.9:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'unknown'
        
        return {
            'average_velocity': round(average_velocity, 2),
            'velocity_trend': trend,
            'sprints_analyzed': len(velocities),
            'velocities': velocities,
        }
    
    @staticmethod
    def calculate_contributor_capacity(contributor_id, sprint_duration_days=14):
        """
        Calculate contributor capacity based on historical data
        """
        contributor = Contributor.objects.get(id=contributor_id)
        
        # Get historical sprint performance
        past_capacities = TeamMemberCapacity.objects.filter(
            contributor=contributor,
            sprint__status='completed'
        ).order_by('-sprint__end_date')[:5]
        
        if past_capacities:
            avg_velocity = sum(c.average_velocity for c in past_capacities) / len(past_capacities)
            avg_hours_per_point = sum(c.average_hours_per_point for c in past_capacities) / len(past_capacities)
        else:
            # Default estimates
            avg_velocity = 15  # Default story points per 2-week sprint
            avg_hours_per_point = 4  # Default 4 hours per story point
        
        # Calculate available hours (assuming 8 hours per work day, 5 days per week)
        work_days = (sprint_duration_days / 7) * 5
        total_hours = work_days * 8 * 0.75  # 75% utilization for realistic capacity
        
        return {
            'contributor_id': contributor_id,
            'contributor_name': contributor.username,
            'total_capacity_hours': round(total_hours, 2),
            'estimated_velocity': round(avg_velocity, 2),
            'hours_per_story_point': round(avg_hours_per_point, 2),
            'max_story_points': round(total_hours / avg_hours_per_point, 2),
        }
    
    @staticmethod
    def analyze_issue_priority(repository_id):
        """
        Analyze and prioritize issues for sprint planning
        Returns issues with priority scores
        """
        # Get open issues
        open_issues = Issue.objects.filter(
            work__repository_id=repository_id,
            state='open'
        ).select_related('work__contributor', 'work__repository')
        
        prioritized_issues = []
        
        for issue in open_issues:
            priority_score = 0
            factors = []
            
            # Factor 1: Issue type (bugs have higher priority)
            if issue.is_bug:
                priority_score += 30
                factors.append("Bug fix")
            elif issue.is_feature:
                priority_score += 20
                factors.append("Feature request")
            else:
                priority_score += 10
                factors.append("General issue")
            
            # Factor 2: Existing priority field
            priority_weights = {
                'critical': 40,
                'high': 30,
                'medium': 15,
                'low': 5,
            }
            priority_score += priority_weights.get(issue.priority, 10)
            
            # Factor 3: Age of issue (older issues get higher priority)
            age_days = (timezone.now() - issue.created_at).days
            if age_days > 90:
                priority_score += 20
                factors.append("Old issue (90+ days)")
            elif age_days > 30:
                priority_score += 10
                factors.append("Moderately old (30+ days)")
            
            # Factor 4: Issue engagement (comments, reactions, etc.)
            # This would need to be tracked in your system
            
            prioritized_issues.append({
                'issue_id': issue.id,
                'title': issue.summary[:100],
                'priority_score': priority_score,
                'priority_level': issue.priority,
                'is_bug': issue.is_bug,
                'is_feature': issue.is_feature,
                'age_days': age_days,
                'factors': factors,
                'created_at': issue.created_at,
            })
        
        # Sort by priority score
        prioritized_issues.sort(key=lambda x: x['priority_score'], reverse=True)
        
        return prioritized_issues
    
    @staticmethod
    def predict_issue_effort(issue_data):
        """
        Predict effort required for an issue
        Returns estimated story points and hours
        """
        # Simple heuristic-based estimation
        base_points = 3  # Default story points
        
        title_length = len(issue_data.get('title', ''))
        
        # Adjust based on issue type
        if issue_data.get('is_bug'):
            base_points = 2  # Bugs tend to be smaller
        elif issue_data.get('is_feature'):
            base_points = 5  # Features tend to be larger
        
        # Adjust based on priority
        if issue_data.get('priority_level') == 'critical':
            base_points += 2  # Critical issues often more complex
        
        # In a real implementation, you would use ML here
        # For now, we'll use simple heuristics
        
        estimated_points = max(1, min(base_points, 13))  # Fibonacci scale: 1,2,3,5,8,13
        estimated_hours = estimated_points * 4  # 4 hours per story point
        
        return {
            'estimated_story_points': estimated_points,
            'estimated_hours': estimated_hours,
            'confidence': 'medium',  # low, medium, high
        }
    
    @staticmethod
    def assign_issues_to_team(issues, team_members, team_capacity):
        """
        AI-powered issue assignment to team members
        Uses workload balancing and skill matching
        """
        assignments = []
        member_workloads = {member['contributor_id']: 0 for member in team_members}
        member_capacities = {
            member['contributor_id']: member['max_story_points'] 
            for member in team_members
        }
        
        for issue in issues:
            # Estimate effort for this issue
            effort = SprintAnalytics.predict_issue_effort(issue)
            story_points = effort['estimated_story_points']
            
            # Find best assignee based on capacity and workload
            best_assignee = None
            best_score = -1
            reasoning = ""
            
            for member in team_members:
                member_id = member['contributor_id']
                
                # Check if member has capacity
                if member_workloads[member_id] + story_points > member_capacities[member_id]:
                    continue  # Skip if over capacity
                
                # Calculate assignment score
                # Lower current workload = higher score
                capacity_remaining = member_capacities[member_id] - member_workloads[member_id]
                score = capacity_remaining
                
                # Prefer members with moderate utilization (not too busy, not idle)
                utilization = member_workloads[member_id] / member_capacities[member_id] if member_capacities[member_id] > 0 else 0
                if 0.3 <= utilization <= 0.7:
                    score += 10  # Bonus for balanced utilization
                
                if score > best_score:
                    best_score = score
                    best_assignee = member_id
                    reasoning = f"Balanced workload ({round(utilization * 100, 1)}% utilized), capacity available"
            
            # Make assignment if found
            if best_assignee:
                member_workloads[best_assignee] += story_points
                assignments.append({
                    'issue': issue,
                    'assigned_to': best_assignee,
                    'assigned_to_name': next(
                        m['contributor_name'] for m in team_members 
                        if m['contributor_id'] == best_assignee
                    ),
                    'story_points': story_points,
                    'estimated_hours': effort['estimated_hours'],
                    'reasoning': reasoning,
                })
            else:
                # No capacity available
                assignments.append({
                    'issue': issue,
                    'assigned_to': None,
                    'assigned_to_name': 'Unassigned (No capacity)',
                    'story_points': story_points,
                    'estimated_hours': effort['estimated_hours'],
                    'reasoning': 'Team capacity exceeded',
                })
        
        return assignments
    
    @staticmethod
    def forecast_sprint_completion(repository_id, sprint_duration_days=14):
        """
        Forecast when current sprint backlog will be completed
        """
        # Get team velocity
        velocity_data = SprintAnalytics.calculate_team_velocity(repository_id)
        avg_velocity = velocity_data['average_velocity']
        
        if avg_velocity == 0:
            return {
                'forecast_date': None,
                'message': 'Insufficient historical data for forecast',
            }
        
        # Get prioritized backlog
        backlog = SprintAnalytics.analyze_issue_priority(repository_id)
        
        # Estimate total story points in backlog
        total_points = 0
        for issue in backlog[:20]:  # Consider top 20 issues
            effort = SprintAnalytics.predict_issue_effort(issue)
            total_points += effort['estimated_story_points']
        
        # Calculate sprints needed
        sprints_needed = total_points / avg_velocity if avg_velocity > 0 else 0
        days_needed = sprints_needed * sprint_duration_days
        
        forecast_date = date.today() + timedelta(days=days_needed)
        
        return {
            'forecast_date': forecast_date.isoformat(),
            'sprints_needed': round(sprints_needed, 1),
            'total_story_points': round(total_points, 1),
            'average_velocity': avg_velocity,
            'top_issues_count': len(backlog[:20]),
        }


class SprintPlannerAI:
    """
    AI-powered sprint planning system
    """
    
    @staticmethod
    def generate_sprint_plan(repository_id, sprint_duration_days=14, team_member_ids=None):
        """
        Generate a complete sprint plan with AI suggestions
        
        Args:
            repository_id: Repository to plan sprint for
            sprint_duration_days: Sprint duration (default 14 days)
            team_member_ids: List of contributor IDs on the team
        
        Returns:
            Complete sprint plan with assignments and forecasts
        """
        # Step 1: Calculate team capacity
        team_capacity_data = []
        if team_member_ids:
            for member_id in team_member_ids:
                capacity = SprintAnalytics.calculate_contributor_capacity(
                    member_id, 
                    sprint_duration_days
                )
                team_capacity_data.append(capacity)
        else:
            # Get active contributors from repository
            active_contributors = Contributor.objects.filter(
                works__repository_id=repository_id
            ).distinct()[:5]  # Top 5 active contributors
            
            for contributor in active_contributors:
                capacity = SprintAnalytics.calculate_contributor_capacity(
                    contributor.id,
                    sprint_duration_days
                )
                team_capacity_data.append(capacity)
        
        # Calculate total team capacity
        total_team_velocity = sum(m['max_story_points'] for m in team_capacity_data)
        total_team_hours = sum(m['total_capacity_hours'] for m in team_capacity_data)
        
        # Step 2: Get and prioritize issues
        prioritized_issues = SprintAnalytics.analyze_issue_priority(repository_id)
        
        # Step 3: Select issues for sprint based on capacity
        selected_issues = []
        total_points = 0
        
        for issue in prioritized_issues:
            effort = SprintAnalytics.predict_issue_effort(issue)
            if total_points + effort['estimated_story_points'] <= total_team_velocity:
                selected_issues.append({
                    **issue,
                    'estimated_story_points': effort['estimated_story_points'],
                    'estimated_hours': effort['estimated_hours'],
                })
                total_points += effort['estimated_story_points']
            
            if len(selected_issues) >= 15:  # Max 15 issues per sprint
                break
        
        # Step 4: Assign issues to team members
        assignments = SprintAnalytics.assign_issues_to_team(
            selected_issues,
            team_capacity_data,
            total_team_velocity
        )
        
        # Step 5: Get velocity trends
        velocity_data = SprintAnalytics.calculate_team_velocity(repository_id)
        
        # Step 6: Forecast completion
        forecast = SprintAnalytics.forecast_sprint_completion(
            repository_id,
            sprint_duration_days
        )
        
        # Step 7: Generate sprint dates
        start_date = date.today() + timedelta(days=1)  # Start tomorrow
        end_date = start_date + timedelta(days=sprint_duration_days)
        
        # Compile complete sprint plan
        sprint_plan = {
            'sprint_info': {
                'suggested_name': f"Sprint {start_date.strftime('%Y-%m-%d')}",
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'duration_days': sprint_duration_days,
            },
            'team_capacity': {
                'total_story_points': round(total_team_velocity, 2),
                'total_hours': round(total_team_hours, 2),
                'team_size': len(team_capacity_data),
                'members': team_capacity_data,
            },
            'velocity_analysis': velocity_data,
            'selected_issues': {
                'total_issues': len(selected_issues),
                'total_story_points': round(total_points, 2),
                'capacity_utilization': round((total_points / total_team_velocity * 100), 1) if total_team_velocity > 0 else 0,
                'issues': selected_issues[:10],  # Top 10 for preview
            },
            'assignments': assignments[:10],  # Top 10 for preview
            'forecast': forecast,
            'recommendations': SprintPlannerAI._generate_recommendations(
                velocity_data,
                total_points,
                total_team_velocity,
                len(selected_issues)
            ),
        }
        
        return sprint_plan
    
    @staticmethod
    def _generate_recommendations(velocity_data, planned_points, capacity_points, issue_count):
        """Generate AI recommendations for the sprint"""
        recommendations = []
        
        # Check capacity utilization
        utilization = (planned_points / capacity_points * 100) if capacity_points > 0 else 0
        
        if utilization > 90:
            recommendations.append({
                'type': 'warning',
                'message': f'Sprint is {round(utilization, 1)}% utilized - consider reducing scope to avoid overcommitment',
            })
        elif utilization < 60:
            recommendations.append({
                'type': 'info',
                'message': f'Sprint is only {round(utilization, 1)}% utilized - team can take on more work',
            })
        else:
            recommendations.append({
                'type': 'success',
                'message': f'Sprint capacity utilization is optimal at {round(utilization, 1)}%',
            })
        
        # Check velocity trend
        if velocity_data['velocity_trend'] == 'improving':
            recommendations.append({
                'type': 'success',
                'message': 'Team velocity is improving - consider slightly increasing sprint scope',
            })
        elif velocity_data['velocity_trend'] == 'declining':
            recommendations.append({
                'type': 'warning',
                'message': 'Team velocity is declining - consider investigating blockers or reducing scope',
            })
        
        # Check issue count
        if issue_count > 12:
            recommendations.append({
                'type': 'info',
                'message': f'Sprint has {issue_count} issues - consider breaking down larger tasks',
            })
        elif issue_count < 5:
            recommendations.append({
                'type': 'info',
                'message': f'Sprint has only {issue_count} issues - ensure tasks are appropriately sized',
            })
        
        return recommendations
    
    @staticmethod
    def generate_ai_sprint_summary(sprint_plan, gemini_model=None):
        """
        Generate natural language summary of sprint plan using AI
        """
        if not gemini_model:
            return "AI summary unavailable - Gemini API not configured"
        
        try:
            prompt = f"""Generate a concise 3-4 sentence summary of this sprint plan for a team standup:

Sprint: {sprint_plan['sprint_info']['suggested_name']}
Duration: {sprint_plan['sprint_info']['duration_days']} days
Team Size: {sprint_plan['team_capacity']['team_size']} members
Total Capacity: {sprint_plan['team_capacity']['total_story_points']} story points
Planned Work: {sprint_plan['selected_issues']['total_story_points']} story points across {sprint_plan['selected_issues']['total_issues']} issues
Capacity Utilization: {sprint_plan['selected_issues']['capacity_utilization']}%
Team Velocity Trend: {sprint_plan['velocity_analysis']['velocity_trend']}

Focus on what the team will accomplish and key highlights."""

            response = gemini_model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Error generating AI summary: {str(e)}"

"""
Sprint Planning API Views
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta, date

from .models import Repository, Contributor, Issue, User
from .sprint_models import Sprint, SprintIssue, TeamMemberCapacity, SprintVelocityHistory
from .sprint_analytics import SprintAnalytics, SprintPlannerAI
from .serializers import SprintSerializer, SprintIssueSerializer

import google.generativeai as genai
from django.conf import settings

# Initialize Gemini for AI summaries
try:
    if settings.GEMINI_API_KEY:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        gemini_model = genai.GenerativeModel('gemini-2.5-pro')
    else:
        gemini_model = None
except Exception as e:
    print(f"Error initializing Gemini for sprint planning: {e}")
    gemini_model = None


# ============================================
# SPRINT PLANNING AI - MAIN ENDPOINT
# ============================================

@api_view(['POST'])
def suggest_sprint_plan(request):
    """
    AI suggests next sprint backlog
    
    POST /api/sprints/suggest/
    Body: {
        "repository_id": 1,
        "sprint_duration_days": 14,
        "team_member_ids": [1, 2, 3] (optional)
    }
    """
    repository_id = request.data.get('repository_id')
    sprint_duration_days = request.data.get('sprint_duration_days', 14)
    team_member_ids = request.data.get('team_member_ids', None)
    
    if not repository_id:
        return Response({
            'error': 'repository_id is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Verify repository exists
        repository = Repository.objects.get(id=repository_id)
        
        # Generate sprint plan
        sprint_plan = SprintPlannerAI.generate_sprint_plan(
            repository_id=repository_id,
            sprint_duration_days=sprint_duration_days,
            team_member_ids=team_member_ids
        )
        
        # Generate AI summary
        ai_summary = SprintPlannerAI.generate_ai_sprint_summary(
            sprint_plan,
            gemini_model
        )
        
        sprint_plan['ai_summary'] = ai_summary
        
        return Response({
            'success': True,
            'message': 'Sprint plan generated successfully',
            'repository': {
                'id': repository.id,
                'name': repository.name,
            },
            'sprint_plan': sprint_plan,
        })
    
    except Repository.DoesNotExist:
        return Response({
            'error': 'Repository not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error generating sprint plan: {e}")
        import traceback
        traceback.print_exc()
        
        return Response({
            'error': f'Failed to generate sprint plan: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================
# SPRINT CRUD OPERATIONS
# ============================================

@api_view(['POST'])
def create_sprint(request):
    """
    Create a new sprint
    
    POST /api/sprints/
    Body: {
        "name": "Sprint 1",
        "repository_id": 1,
        "start_date": "2024-01-01",
        "end_date": "2024-01-14",
        "description": "...",
        "planned_velocity": 40,
        "team_capacity": 160
    }
    """
    try:
        repository_id = request.data.get('repository_id')
        repository = Repository.objects.get(id=repository_id)
        
        sprint = Sprint.objects.create(
            name=request.data.get('name'),
            description=request.data.get('description', ''),
            repository=repository,
            start_date=request.data.get('start_date'),
            end_date=request.data.get('end_date'),
            planned_velocity=request.data.get('planned_velocity', 0),
            team_capacity=request.data.get('team_capacity', 0),
            created_by=request.user if request.user.is_authenticated else None,
        )
        
        return Response({
            'success': True,
            'message': 'Sprint created successfully',
            'sprint': {
                'id': sprint.id,
                'name': sprint.name,
                'start_date': sprint.start_date,
                'end_date': sprint.end_date,
                'status': sprint.status,
            }
        }, status=status.HTTP_201_CREATED)
    
    except Repository.DoesNotExist:
        return Response({
            'error': 'Repository not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': f'Failed to create sprint: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_sprint(request, sprint_id):
    """Get sprint details with all issues and assignments"""
    try:
        sprint = Sprint.objects.get(id=sprint_id)
        
        # Get sprint issues
        sprint_issues = sprint.sprint_issues.all().select_related('assigned_to')
        
        issues_data = []
        for si in sprint_issues:
            issues_data.append({
                'id': si.id,
                'title': si.title,
                'description': si.description,
                'issue_type': si.issue_type,
                'status': si.status,
                'priority': si.priority,
                'story_points': si.story_points,
                'estimated_hours': si.estimated_hours,
                'actual_hours': si.actual_hours,
                'assigned_to': {
                    'id': si.assigned_to.id if si.assigned_to else None,
                    'username': si.assigned_to.username if si.assigned_to else None,
                    'avatar_url': si.assigned_to.avatar_url if si.assigned_to else None,
                } if si.assigned_to else None,
                'ai_assigned': si.ai_assigned,
                'ai_reasoning': si.ai_reasoning,
            })
        
        # Get team capacities
        team_capacities = sprint.team_capacities.all().select_related('contributor')
        capacities_data = []
        for tc in team_capacities:
            capacities_data.append({
                'contributor': {
                    'id': tc.contributor.id,
                    'username': tc.contributor.username,
                    'avatar_url': tc.contributor.avatar_url,
                },
                'total_capacity_hours': tc.total_capacity_hours,
                'allocated_hours': tc.allocated_hours,
                'available_hours': tc.available_hours,
                'remaining_hours': tc.remaining_hours,
                'utilization_percentage': tc.utilization_percentage,
            })
        
        # Calculate progress
        progress = sprint.calculate_progress()
        
        return Response({
            'success': True,
            'sprint': {
                'id': sprint.id,
                'name': sprint.name,
                'description': sprint.description,
                'start_date': sprint.start_date,
                'end_date': sprint.end_date,
                'duration_days': sprint.duration_days,
                'status': sprint.status,
                'planned_velocity': sprint.planned_velocity,
                'actual_velocity': sprint.actual_velocity,
                'team_capacity': sprint.team_capacity,
                'allocated_hours': sprint.allocated_hours,
                'completion_rate': round(sprint.completion_rate, 2),
                'velocity_accuracy': round(sprint.velocity_accuracy, 2),
                'repository': {
                    'id': sprint.repository.id,
                    'name': sprint.repository.name,
                },
            },
            'progress': progress,
            'issues': issues_data,
            'team_capacities': capacities_data,
        })
    
    except Sprint.DoesNotExist:
        return Response({
            'error': 'Sprint not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def list_sprints(request):
    """List all sprints with filtering"""
    repository_id = request.GET.get('repository_id')
    sprint_status = request.GET.get('status')
    
    sprints = Sprint.objects.all().select_related('repository')
    
    if repository_id:
        sprints = sprints.filter(repository_id=repository_id)
    
    if sprint_status:
        sprints = sprints.filter(status=sprint_status)
    
    sprints = sprints.order_by('-start_date')
    
    sprints_data = []
    for sprint in sprints:
        sprints_data.append({
            'id': sprint.id,
            'name': sprint.name,
            'start_date': sprint.start_date,
            'end_date': sprint.end_date,
            'status': sprint.status,
            'planned_velocity': sprint.planned_velocity,
            'actual_velocity': sprint.actual_velocity,
            'completion_rate': round(sprint.completion_rate, 2),
            'total_issues': sprint.total_issues,
            'completed_issues': sprint.completed_issues,
            'repository': {
                'id': sprint.repository.id,
                'name': sprint.repository.name,
            },
        })
    
    return Response({
        'success': True,
        'sprints': sprints_data,
        'total': len(sprints_data),
    })


@api_view(['PUT', 'PATCH'])
def update_sprint(request, sprint_id):
    """Update sprint details"""
    try:
        sprint = Sprint.objects.get(id=sprint_id)
        
        # Update fields
        if 'name' in request.data:
            sprint.name = request.data['name']
        if 'description' in request.data:
            sprint.description = request.data['description']
        if 'status' in request.data:
            sprint.status = request.data['status']
        if 'planned_velocity' in request.data:
            sprint.planned_velocity = request.data['planned_velocity']
        
        sprint.save()
        
        return Response({
            'success': True,
            'message': 'Sprint updated successfully',
            'sprint': {
                'id': sprint.id,
                'name': sprint.name,
                'status': sprint.status,
            }
        })
    
    except Sprint.DoesNotExist:
        return Response({
            'error': 'Sprint not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
def delete_sprint(request, sprint_id):
    """Delete a sprint"""
    try:
        sprint = Sprint.objects.get(id=sprint_id)
        sprint_name = sprint.name
        sprint.delete()
        
        return Response({
            'success': True,
            'message': f'Sprint "{sprint_name}" deleted successfully'
        })
    
    except Sprint.DoesNotExist:
        return Response({
            'error': 'Sprint not found'
        }, status=status.HTTP_404_NOT_FOUND)


# ============================================
# SPRINT ISSUES MANAGEMENT
# ============================================

@api_view(['POST'])
def add_issue_to_sprint(request, sprint_id):
    """
    Add an issue to a sprint
    
    POST /api/sprints/{sprint_id}/issues/
    Body: {
        "issue_id": 1 (optional - if linking existing issue),
        "title": "Task title",
        "description": "...",
        "issue_type": "task",
        "story_points": 5,
        "estimated_hours": 20,
        "priority": "high",
        "assigned_to_id": 2 (optional)
    }
    """
    try:
        sprint = Sprint.objects.get(id=sprint_id)
        
        # Get or create issue
        issue_id = request.data.get('issue_id')
        issue_obj = None
        if issue_id:
            issue_obj = Issue.objects.get(id=issue_id)
        
        # Get assignee
        assigned_to = None
        assigned_to_id = request.data.get('assigned_to_id')
        if assigned_to_id:
            assigned_to = Contributor.objects.get(id=assigned_to_id)
        
        # Create sprint issue
        sprint_issue = SprintIssue.objects.create(
            sprint=sprint,
            issue=issue_obj,
            title=request.data.get('title', issue_obj.summary if issue_obj else ''),
            description=request.data.get('description', ''),
            issue_type=request.data.get('issue_type', 'task'),
            story_points=request.data.get('story_points', 3),
            estimated_hours=request.data.get('estimated_hours', 12),
            priority=request.data.get('priority', 'medium'),
            assigned_to=assigned_to,
        )
        
        # Update sprint totals
        sprint.total_issues = sprint.sprint_issues.count()
        sprint.save()
        
        return Response({
            'success': True,
            'message': 'Issue added to sprint',
            'sprint_issue': {
                'id': sprint_issue.id,
                'title': sprint_issue.title,
                'story_points': sprint_issue.story_points,
                'status': sprint_issue.status,
            }
        }, status=status.HTTP_201_CREATED)
    
    except Sprint.DoesNotExist:
        return Response({
            'error': 'Sprint not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': f'Failed to add issue: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
def update_sprint_issue(request, sprint_id, issue_id):
    """Update a sprint issue"""
    try:
        sprint_issue = SprintIssue.objects.get(sprint_id=sprint_id, id=issue_id)
        
        # Update fields
        if 'status' in request.data:
            sprint_issue.status = request.data['status']
        if 'story_points' in request.data:
            sprint_issue.story_points = request.data['story_points']
        if 'actual_hours' in request.data:
            sprint_issue.actual_hours = request.data['actual_hours']
        if 'assigned_to_id' in request.data:
            contributor_id = request.data['assigned_to_id']
            sprint_issue.assigned_to = Contributor.objects.get(id=contributor_id) if contributor_id else None
        
        sprint_issue.save()
        
        # Recalculate sprint progress
        sprint_issue.sprint.calculate_progress()
        
        return Response({
            'success': True,
            'message': 'Sprint issue updated',
            'sprint_issue': {
                'id': sprint_issue.id,
                'status': sprint_issue.status,
                'story_points': sprint_issue.story_points,
                'actual_hours': sprint_issue.actual_hours,
            }
        })
    
    except SprintIssue.DoesNotExist:
        return Response({
            'error': 'Sprint issue not found'
        }, status=status.HTTP_404_NOT_FOUND)


# ============================================
# ANALYTICS & INSIGHTS
# ============================================

@api_view(['GET'])
def sprint_velocity_trends(request, repository_id):
    """Get velocity trends for a repository"""
    try:
        repository = Repository.objects.get(id=repository_id)
        
        # Get velocity history
        velocity_records = SprintVelocityHistory.objects.filter(
            repository=repository
        ).order_by('-sprint_start')[:10]
        
        trends_data = []
        for record in velocity_records:
            trends_data.append({
                'sprint_name': record.sprint.name,
                'sprint_start': record.sprint_start,
                'sprint_end': record.sprint_end,
                'planned_velocity': record.planned_velocity,
                'actual_velocity': record.actual_velocity,
                'completion_rate': record.completion_rate,
                'team_size': record.team_size,
            })
        
        # Calculate overall stats
        velocity_data = SprintAnalytics.calculate_team_velocity(repository_id)
        
        return Response({
            'success': True,
            'repository': {
                'id': repository.id,
                'name': repository.name,
            },
            'velocity_analysis': velocity_data,
            'history': trends_data,
        })
    
    except Repository.DoesNotExist:
        return Response({
            'error': 'Repository not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def team_capacity_analysis(request):
    """Analyze team capacity for sprint planning"""
    contributor_ids = request.GET.getlist('contributor_ids')
    sprint_duration = int(request.GET.get('sprint_duration_days', 14))
    
    if not contributor_ids:
        return Response({
            'error': 'contributor_ids are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    capacity_data = []
    total_capacity = 0
    
    for contributor_id in contributor_ids:
        try:
            capacity = SprintAnalytics.calculate_contributor_capacity(
                int(contributor_id),
                sprint_duration
            )
            capacity_data.append(capacity)
            total_capacity += capacity['total_capacity_hours']
        except Contributor.DoesNotExist:
            continue
    
    return Response({
        'success': True,
        'team_capacity': {
            'total_hours': round(total_capacity, 2),
            'team_size': len(capacity_data),
            'sprint_duration_days': sprint_duration,
            'members': capacity_data,
        }
    })


@api_view(['GET'])
def forecast_completion(request, repository_id):
    """Forecast when backlog will be completed"""
    try:
        sprint_duration = int(request.GET.get('sprint_duration_days', 14))
        
        forecast = SprintAnalytics.forecast_sprint_completion(
            repository_id,
            sprint_duration
        )
        
        return Response({
            'success': True,
            'forecast': forecast,
        })
    
    except Repository.DoesNotExist:
        return Response({
            'error': 'Repository not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def complete_sprint(request, sprint_id):
    """
    Mark a sprint as completed and save velocity history
    """
    try:
        sprint = Sprint.objects.get(id=sprint_id)
        
        # Calculate final metrics
        sprint.calculate_progress()
        
        # Update status
        sprint.status = 'completed'
        sprint.save()
        
        # Save velocity history
        team_size = sprint.team_capacities.count()
        
        SprintVelocityHistory.objects.create(
            repository=sprint.repository,
            team=sprint.team,
            sprint=sprint,
            planned_velocity=sprint.planned_velocity,
            actual_velocity=sprint.actual_velocity,
            team_size=team_size,
            total_issues=sprint.total_issues,
            completed_issues=sprint.completed_issues,
            completion_rate=sprint.completion_rate,
            planned_hours=sprint.team_capacity,
            actual_hours=sprint.allocated_hours,
            sprint_start=sprint.start_date,
            sprint_end=sprint.end_date,
        )
        
        return Response({
            'success': True,
            'message': 'Sprint completed successfully',
            'sprint': {
                'id': sprint.id,
                'name': sprint.name,
                'actual_velocity': sprint.actual_velocity,
                'completion_rate': round(sprint.completion_rate, 2),
                'velocity_accuracy': round(sprint.velocity_accuracy, 2),
            }
        })
    
    except Sprint.DoesNotExist:
        return Response({
            'error': 'Sprint not found'
        }, status=status.HTTP_404_NOT_FOUND)

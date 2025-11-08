"""
Release Readiness API Views
RESTful endpoints for release readiness scoring
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from .release_readiness import ReleaseReadinessCalculator, ReleaseReadinessReporter
from .models import Repository


@api_view(['GET'])
def get_release_readiness(request, repo_id):
    """
    GET /api/release-readiness/{repo_id}/
    
    Get comprehensive release readiness score and report
    
    Response:
    {
        "score": 85.5,
        "readiness_level": {"level": "good", "label": "Good to Go ✅", ...},
        "can_release": true,
        "blockers": [...],
        "warnings": [...],
        "penalties": [...],
        "passed_checks": [...],
        "detailed_metrics": {...},
        ...
    }
    """
    try:
        report = ReleaseReadinessReporter.generate_report(repo_id)
        return Response(report, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to calculate readiness: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_release_readiness_score_only(request, repo_id):
    """
    GET /api/release-readiness/{repo_id}/score/
    
    Get just the release readiness score (lightweight endpoint)
    
    Response:
    {
        "repository_id": 1,
        "score": 85.5,
        "readiness_level": "good",
        "can_release": true
    }
    """
    try:
        calculator = ReleaseReadinessCalculator(repo_id)
        result = calculator.calculate()
        
        return Response({
            'repository_id': repo_id,
            'repository_name': result['repository']['name'],
            'score': result['score'],
            'readiness_level': result['readiness_level']['level'],
            'label': result['readiness_level']['label'],
            'emoji': result['readiness_level']['emoji'],
            'can_release': result['can_release'],
            'blockers_count': len(result['blockers']),
            'warnings_count': len(result['warnings']),
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to calculate score: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_release_blockers(request, repo_id):
    """
    GET /api/release-readiness/{repo_id}/blockers/
    
    Get only the blocking issues preventing release
    
    Response:
    {
        "repository_id": 1,
        "blockers": ["❌ 3 critical bugs must be fixed", ...],
        "warnings": ["⚠️ 5 pull requests need review", ...],
        "has_blockers": true
    }
    """
    try:
        calculator = ReleaseReadinessCalculator(repo_id)
        result = calculator.calculate()
        
        return Response({
            'repository_id': repo_id,
            'repository_name': result['repository']['name'],
            'blockers': result['blockers'],
            'warnings': result['warnings'],
            'has_blockers': len(result['blockers']) > 0,
            'blockers_count': len(result['blockers']),
            'warnings_count': len(result['warnings']),
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to get blockers: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_readiness_trend(request, repo_id):
    """
    GET /api/release-readiness/{repo_id}/trend/
    
    Get release readiness score trend over time
    
    Query params:
    - days: Number of days to look back (default: 30)
    
    Response:
    {
        "repository_id": 1,
        "current_score": 85.5,
        "trend_direction": "improving",
        "trend": [
            {"date": "2025-10-09", "score": 75.0},
            {"date": "2025-10-14", "score": 78.5},
            ...
        ]
    }
    """
    try:
        days = int(request.GET.get('days', 30))
        trend_data = ReleaseReadinessReporter.get_readiness_trend(repo_id, days)
        return Response(trend_data, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to get trend: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def compare_repositories_readiness(request):
    """
    POST /api/release-readiness/compare/
    
    Compare release readiness across multiple repositories
    
    Request body:
    {
        "repository_ids": [1, 2, 3]
    }
    
    Response:
    {
        "repositories_compared": 3,
        "average_score": 78.5,
        "comparisons": [
            {
                "repository_id": 1,
                "name": "repo1",
                "score": 85.5,
                "readiness_level": "good",
                "can_release": true,
                "blockers_count": 0
            },
            ...
        ]
    }
    """
    try:
        repository_ids = request.data.get('repository_ids', [])
        
        if not repository_ids:
            return Response(
                {'error': 'repository_ids array is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        comparison = ReleaseReadinessReporter.compare_repositories(repository_ids)
        return Response(comparison, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {'error': f'Failed to compare repositories: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_all_repositories_readiness(request):
    """
    GET /api/release-readiness/all/
    
    Get release readiness scores for all repositories
    
    Response:
    {
        "repositories": [
            {
                "repository_id": 1,
                "name": "repo1",
                "score": 85.5,
                "readiness_level": "good",
                "can_release": true
            },
            ...
        ],
        "average_score": 78.5,
        "ready_to_release_count": 3,
        "total_count": 5
    }
    """
    try:
        repositories = Repository.objects.all()
        results = []
        
        for repo in repositories:
            try:
                calculator = ReleaseReadinessCalculator(repo.id)
                result = calculator.calculate()
                results.append({
                    'repository_id': repo.id,
                    'name': repo.name,
                    'score': result['score'],
                    'readiness_level': result['readiness_level']['level'],
                    'label': result['readiness_level']['label'],
                    'emoji': result['readiness_level']['emoji'],
                    'can_release': result['can_release'],
                    'blockers_count': len(result['blockers']),
                })
            except Exception:
                # Skip repositories that fail
                continue
        
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        avg_score = sum(r['score'] for r in results) / len(results) if results else 0
        ready_count = sum(1 for r in results if r['can_release'])
        
        return Response({
            'repositories': results,
            'total_count': len(results),
            'ready_to_release_count': ready_count,
            'average_score': round(avg_score, 1),
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {'error': f'Failed to get readiness scores: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_readiness_dashboard(request, repo_id):
    """
    GET /api/release-readiness/{repo_id}/dashboard/
    
    Get complete dashboard data including score, trend, and recommendations
    
    Response:
    {
        "current": {score, readiness_level, can_release, ...},
        "trend": {trend data over 30 days},
        "action_items": {blockers, warnings, recommendations}
    }
    """
    try:
        # Get current readiness
        current = ReleaseReadinessReporter.generate_report(repo_id)
        
        # Get trend
        trend = ReleaseReadinessReporter.get_readiness_trend(repo_id, days=30)
        
        # Compile action items
        action_items = {
            'blockers': current['blockers'],
            'warnings': current['warnings'],
            'recommendation': current['recommendation'],
            'next_steps': _generate_next_steps(current),
        }
        
        return Response({
            'current': current,
            'trend': trend,
            'action_items': action_items,
            'last_updated': current['calculated_at'],
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to get dashboard: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def _generate_next_steps(readiness_result):
    """Generate prioritized next steps based on readiness result"""
    next_steps = []
    
    # Prioritize blockers first
    if readiness_result['blockers']:
        next_steps.append({
            'priority': 'critical',
            'category': 'blockers',
            'title': 'Resolve Blocking Issues',
            'description': 'These issues must be fixed before release',
            'items': readiness_result['blockers']
        })
    
    # Then warnings
    if readiness_result['warnings']:
        next_steps.append({
            'priority': 'high',
            'category': 'warnings',
            'title': 'Address Warnings',
            'description': 'These issues should be fixed for a better release',
            'items': readiness_result['warnings']
        })
    
    # Suggest improvements based on penalties
    improvements = []
    for penalty in readiness_result['penalties']:
        if penalty['type'] == 'critical_bugs':
            improvements.append(f"Fix {penalty['count']} critical bugs")
        elif penalty['type'] == 'unreviewed_prs':
            improvements.append(f"Review {penalty['count']} pull requests")
        elif penalty['type'] == 'failing_ci':
            improvements.append("Fix CI/CD pipeline failures")
        elif penalty['type'] == 'coverage_drop':
            improvements.append("Improve test coverage")
        elif penalty['type'] == 'unresolved_todos':
            improvements.append(f"Resolve {penalty['count']} TODOs")
    
    if improvements:
        next_steps.append({
            'priority': 'medium',
            'category': 'improvements',
            'title': 'Quality Improvements',
            'description': 'These will increase your release readiness score',
            'items': improvements
        })
    
    return next_steps

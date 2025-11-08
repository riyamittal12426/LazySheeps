"""
DORA Metrics Views
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from api.models import Repository


# --- DORA Metrics Views ---

@api_view(['GET'])
@permission_classes([AllowAny])
def repository_dora_metrics(request, repo_id):
    """
    Get DORA metrics for a specific repository
    """
    try:
        from api.dora_metrics import DORAMetricsCalculator
        
        repository = Repository.objects.get(id=repo_id)
        
        # Recalculate if requested
        recalculate = request.query_params.get('recalculate', 'false').lower() == 'true'
        days = int(request.query_params.get('days', 90))
        
        if recalculate:
            calculator = DORAMetricsCalculator(repository)
            metrics = calculator.calculate_all_metrics(days=days)
            # Save to database
            calculator.update_repository_metrics()
        else:
            # Return stored metrics
            calculator = DORAMetricsCalculator(repository)
            metrics = {
                'deployment_frequency': repository.deployment_frequency,
                'lead_time_for_changes': repository.lead_time_for_changes,
                'change_failure_rate': repository.change_failure_rate,
                'mttr': repository.mean_time_to_recovery,
                'repository': repository.name,
                'repository_id': repository.id,
                'performance_tier': calculator.get_performance_tier(),
                'period_days': days,
            }
        
        return Response(metrics)
    
    except Repository.DoesNotExist:
        return Response(
            {'error': 'Repository not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def calculate_all_dora_metrics(request):
    """
    Trigger DORA calculation for all repositories
    Admin endpoint
    """
    try:
        from api.dora_metrics import calculate_dora_for_all_repositories
        
        results = calculate_dora_for_all_repositories()
        
        success_count = sum(1 for r in results if r['success'])
        
        return Response({
            'status': 'completed',
            'total_repositories': len(results),
            'successful': success_count,
            'failed': len(results) - success_count,
            'results': results
        })
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

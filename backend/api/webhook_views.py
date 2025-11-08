"""
Enhanced GitHub App Webhook Handler
Enterprise-grade webhook processing with signature verification and background processing
"""
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .github_sync import WebhookProcessor, GitHubSyncManager, SyncJobRunner
from .models import GitHubAppInstallation, SyncJob
from django.utils import timezone

logger = logging.getLogger(__name__)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def github_webhook_handler(request):
    """
    Main webhook handler - receives ALL GitHub events
    Verifies signature and routes to appropriate processor
    """
    # Get headers
    signature = request.headers.get('X-Hub-Signature-256')
    event_type = request.headers.get('X-GitHub-Event')
    delivery_id = request.headers.get('X-GitHub-Delivery')
    
    # Verify webhook signature
    payload_body = request.body
    if not WebhookProcessor.verify_signature(payload_body, signature):
        logger.error(f"Invalid webhook signature for delivery {delivery_id}")
        return JsonResponse({'error': 'Invalid signature'}, status=401)
    
    logger.info(f"✅ Webhook received: {event_type} (delivery: {delivery_id})")
    
    # Parse payload
    payload = request.data
    
    try:
        # Route to appropriate handler
        if event_type == 'installation':
            result = WebhookProcessor.process_installation_event(payload)
            return JsonResponse({
                'status': 'success',
                'event': event_type,
                'result': result
            })
        
        elif event_type == 'installation_repositories':
            result = WebhookProcessor.process_installation_repositories_event(payload)
            return JsonResponse({
                'status': 'success',
                'event': event_type,
                'result': result
            })
        
        elif event_type == 'repository':
            result = WebhookProcessor.process_repository_event(payload)
            return JsonResponse({
                'status': 'success',
                'event': event_type,
                'result': result
            })
        
        elif event_type == 'push':
            result = WebhookProcessor.process_push_event(payload)
            return JsonResponse({
                'status': 'success',
                'event': event_type,
                'result': result
            })
        
        elif event_type == 'pull_request':
            result = WebhookProcessor.process_pull_request_event(payload)
            return JsonResponse({
                'status': 'success',
                'event': event_type,
                'result': result
            })
        
        elif event_type == 'issues':
            result = WebhookProcessor.process_issues_event(payload)
            return JsonResponse({
                'status': 'success',
                'event': event_type,
                'result': result
            })
        
        elif event_type == 'ping':
            # Webhook health check
            return JsonResponse({
                'status': 'success',
                'message': 'Webhook endpoint is healthy',
                'zen': payload.get('zen', '')
            })
        
        else:
            # Log but don't fail for unhandled events
            logger.info(f"Unhandled event type: {event_type}")
            return JsonResponse({
                'status': 'success',
                'event': event_type,
                'message': 'Event received but not processed'
            })
    
    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}", exc_info=True)
        return JsonResponse({
            'status': 'error',
            'event': event_type,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
def trigger_periodic_sync(request):
    """
    Trigger periodic sync job
    This should be called by a cron job every 15-30 minutes
    Can also be triggered manually for testing
    """
    try:
        logger.info("🔄 Starting periodic sync job...")
        result = SyncJobRunner.run_periodic_sync()
        
        return Response({
            'success': True,
            'message': 'Periodic sync completed',
            'result': result
        })
    
    except Exception as e:
        logger.error(f"Periodic sync failed: {str(e)}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
def sync_repository_endpoint(request, repo_id):
    """
    Manually trigger sync for a single repository
    Useful for testing or on-demand updates
    """
    try:
        result = SyncJobRunner.sync_single_repository(repo_id)
        
        if 'error' in result:
            return Response(result, status=400)
        
        return Response({
            'success': True,
            'message': f'Repository {repo_id} synced successfully',
            'result': result
        })
    
    except Exception as e:
        logger.error(f"Manual sync failed: {str(e)}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def sync_jobs_list(request):
    """
    Get list of all sync jobs for monitoring
    Shows system health and performance
    """
    # Get query parameters
    limit = int(request.GET.get('limit', 50))
    job_type = request.GET.get('type')
    status = request.GET.get('status')
    installation_id = request.GET.get('installation_id')
    
    # Build query
    jobs = SyncJob.objects.all()
    
    if job_type:
        jobs = jobs.filter(job_type=job_type)
    if status:
        jobs = jobs.filter(status=status)
    if installation_id:
        jobs = jobs.filter(installation__id=installation_id)
    
    jobs = jobs[:limit]
    
    # Format response
    jobs_data = []
    for job in jobs:
        jobs_data.append({
            'id': job.id,
            'job_type': job.job_type,
            'status': job.status,
            'repositories_processed': job.repositories_processed,
            'errors_count': job.errors_count,
            'started_at': job.started_at,
            'completed_at': job.completed_at,
            'duration_seconds': job.duration_seconds(),
            'installation': {
                'id': job.installation.id if job.installation else None,
                'account_login': job.installation.account_login if job.installation else None
            } if job.installation else None,
            'details': job.details
        })
    
    # Calculate stats
    total_jobs = SyncJob.objects.count()
    successful = SyncJob.objects.filter(status='completed').count()
    failed = SyncJob.objects.filter(status='failed').count()
    
    return Response({
        'jobs': jobs_data,
        'stats': {
            'total_jobs': total_jobs,
            'successful': successful,
            'failed': failed,
            'success_rate': (successful / total_jobs * 100) if total_jobs > 0 else 0
        }
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def webhook_health_check(request):
    """
    Health check endpoint for webhook system
    Shows if auto-sync is working properly
    """
    # Get recent sync jobs
    recent_jobs = SyncJob.objects.all()[:10]
    
    # Check last sync time
    last_sync = SyncJob.objects.filter(
        job_type='periodic_sync'
    ).order_by('-started_at').first()
    
    # Calculate uptime metrics
    total_installations = GitHubAppInstallation.objects.count()
    
    from .models import Repository
    total_repos = Repository.objects.count()
    synced_repos = Repository.objects.filter(
        last_synced_at__isnull=False
    ).count()
    
    # Recent webhook activity
    webhook_jobs = SyncJob.objects.filter(
        job_type='webhook_triggered'
    ).order_by('-started_at')[:5]
    
    return Response({
        'status': 'healthy',
        'system': {
            'total_installations': total_installations,
            'total_repositories': total_repos,
            'synced_repositories': synced_repos,
            'sync_coverage': (synced_repos / total_repos * 100) if total_repos > 0 else 0
        },
        'last_periodic_sync': {
            'time': last_sync.started_at if last_sync else None,
            'status': last_sync.status if last_sync else None,
            'repos_processed': last_sync.repositories_processed if last_sync else 0
        } if last_sync else None,
        'recent_jobs': [
            {
                'id': job.id,
                'type': job.job_type,
                'status': job.status,
                'started_at': job.started_at
            } for job in recent_jobs
        ],
        'recent_webhooks': [
            {
                'id': job.id,
                'status': job.status,
                'started_at': job.started_at,
                'details': job.details
            } for job in webhook_jobs
        ]
    })

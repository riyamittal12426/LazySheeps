"""
GitHub Webhooks Handler
Real-time sync for repositories
"""
import hmac
import hashlib
import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from api.models import Repository, Contributor, Commit, Issue
from api.github_importer import GitHubImporter
import logging

logger = logging.getLogger(__name__)


def verify_webhook_signature(request):
    """
    Verify GitHub webhook signature
    """
    signature = request.headers.get('X-Hub-Signature-256', '')
    if not signature:
        return False
    
    # Get secret from settings
    secret = getattr(settings, 'GITHUB_WEBHOOK_SECRET', '').encode()
    if not secret:
        logger.warning("GITHUB_WEBHOOK_SECRET not configured")
        return True  # Allow for development
    
    # Calculate expected signature
    mac = hmac.new(secret, msg=request.body, digestmod=hashlib.sha256)
    expected_signature = 'sha256=' + mac.hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)


@csrf_exempt
@require_http_methods(["POST"])
def github_webhook(request):
    """
    Handle GitHub webhook events
    """
    try:
        # Verify signature
        if not verify_webhook_signature(request):
            logger.error("Invalid webhook signature")
            return JsonResponse({'error': 'Invalid signature'}, status=401)
        
        # Get event type
        event = request.headers.get('X-GitHub-Event', '')
        delivery_id = request.headers.get('X-GitHub-Delivery', '')
        
        logger.info(f"Received webhook: {event} (ID: {delivery_id})")
        
        # Parse payload
        payload = json.loads(request.body)
        
        # Route to appropriate handler
        handlers = {
            'push': handle_push_event,
            'pull_request': handle_pull_request_event,
            'issues': handle_issues_event,
            'issue_comment': handle_issue_comment_event,
            'pull_request_review': handle_pr_review_event,
            'release': handle_release_event,
            'repository': handle_repository_event,
        }
        
        handler = handlers.get(event)
        if handler:
            result = handler(payload)
            logger.info(f"Webhook {event} processed successfully")
            return JsonResponse(result)
        else:
            logger.warning(f"Unhandled webhook event: {event}")
            return JsonResponse({'status': 'ignored', 'event': event})
    
    except json.JSONDecodeError:
        logger.error("Invalid JSON in webhook payload")
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return JsonResponse({'error': str(e)}, status=500)


def handle_push_event(payload):
    """
    Handle push events (new commits)
    """
    repo_name = payload['repository']['full_name']
    ref = payload['ref']  # e.g., refs/heads/main
    commits = payload['commits']
    
    logger.info(f"Push to {repo_name} on {ref}: {len(commits)} commits")
    
    # Get repository from database
    try:
        repo = Repository.objects.get(full_name=repo_name)
    except Repository.DoesNotExist:
        logger.warning(f"Repository {repo_name} not found in database")
        return {'status': 'repository_not_found'}
    
    # Process commits
    importer = GitHubImporter()
    for commit_data in commits:
        try:
            # Get or create contributor
            author = commit_data.get('author', {})
            contributor, _ = Contributor.objects.get_or_create(
                username=author.get('username', author.get('name', 'unknown')),
                defaults={
                    'url': f"https://github.com/{author.get('username', '')}",
                    'avatar_url': '',
                    'summary': f"Contributor {author.get('username', 'unknown')}",
                }
            )
            
            # Create or update commit
            Commit.objects.update_or_create(
                url=commit_data['url'],
                defaults={
                    'repository': repo,
                    'contributor': contributor,
                    'summary': commit_data['message'][:200],
                    'raw_data': commit_data,
                    'committed_at': commit_data['timestamp'],
                }
            )
            
            logger.info(f"Processed commit: {commit_data['id'][:7]}")
        
        except Exception as e:
            logger.error(f"Error processing commit {commit_data.get('id', 'unknown')}: {e}")
    
    # Update repository stats
    repo.calculate_health_score()
    
    return {
        'status': 'success',
        'repository': repo_name,
        'commits_processed': len(commits)
    }


def handle_pull_request_event(payload):
    """
    Handle pull request events
    """
    action = payload['action']  # opened, closed, reopened, etc.
    pr = payload['pull_request']
    repo_name = payload['repository']['full_name']
    
    logger.info(f"PR {action}: {pr['title']} in {repo_name}")
    
    # TODO: Store PR data in database
    # For now, just log it
    
    return {
        'status': 'success',
        'action': action,
        'pr_number': pr['number'],
        'repository': repo_name
    }


def handle_issues_event(payload):
    """
    Handle issues events
    """
    action = payload['action']  # opened, closed, reopened, etc.
    issue = payload['issue']
    repo_name = payload['repository']['full_name']
    
    logger.info(f"Issue {action}: {issue['title']} in {repo_name}")
    
    try:
        repo = Repository.objects.get(full_name=repo_name)
        
        # Get or create contributor (issue author)
        author = issue.get('user', {})
        contributor, _ = Contributor.objects.get_or_create(
            username=author.get('login', 'unknown'),
            defaults={
                'url': author.get('html_url', ''),
                'avatar_url': author.get('avatar_url', ''),
                'summary': f"Contributor {author.get('login', 'unknown')}",
            }
        )
        
        # Create or update issue
        Issue.objects.update_or_create(
            url=issue['html_url'],
            defaults={
                'title': issue['title'],
                'state': issue['state'],
                'created_at': issue['created_at'],
                'raw_data': issue,
            }
        )
        
        logger.info(f"Processed issue: #{issue['number']}")
    
    except Repository.DoesNotExist:
        logger.warning(f"Repository {repo_name} not found")
    except Exception as e:
        logger.error(f"Error processing issue: {e}")
    
    return {
        'status': 'success',
        'action': action,
        'issue_number': issue['number'],
        'repository': repo_name
    }


def handle_issue_comment_event(payload):
    """
    Handle issue comment events
    """
    action = payload['action']
    comment = payload['comment']
    issue = payload['issue']
    repo_name = payload['repository']['full_name']
    
    logger.info(f"Comment {action} on issue #{issue['number']} in {repo_name}")
    
    # TODO: Store comment data
    
    return {
        'status': 'success',
        'action': action,
        'issue_number': issue['number']
    }


def handle_pr_review_event(payload):
    """
    Handle pull request review events
    """
    action = payload['action']
    review = payload['review']
    pr = payload['pull_request']
    repo_name = payload['repository']['full_name']
    
    logger.info(f"PR review {action}: {pr['number']} in {repo_name}")
    
    # TODO: Store review data for AI code review analysis
    
    return {
        'status': 'success',
        'action': action,
        'pr_number': pr['number'],
        'review_state': review.get('state')
    }


def handle_release_event(payload):
    """
    Handle release events (for DORA metrics)
    """
    action = payload['action']
    release = payload['release']
    repo_name = payload['repository']['full_name']
    
    logger.info(f"Release {action}: {release['tag_name']} in {repo_name}")
    
    try:
        repo = Repository.objects.get(full_name=repo_name)
        
        # Calculate DORA metrics on every release
        from api.dora_metrics import DORAMetricsCalculator
        calculator = DORAMetricsCalculator(repo)
        metrics = calculator.update_repository_metrics()
        
        logger.info(
            f"Updated DORA metrics for {repo_name}: "
            f"Deployment Freq = {metrics['deployment_frequency']}, "
            f"Performance = {metrics['performance_tier']}"
        )
    
    except Repository.DoesNotExist:
        logger.warning(f"Repository {repo_name} not found")
    
    return {
        'status': 'success',
        'action': action,
        'tag': release['tag_name'],
        'dora_updated': True
    }


def handle_repository_event(payload):
    """
    Handle repository events (created, deleted, etc.)
    """
    action = payload['action']
    repo_data = payload['repository']
    
    logger.info(f"Repository {action}: {repo_data['full_name']}")
    
    if action == 'deleted':
        try:
            repo = Repository.objects.get(full_name=repo_data['full_name'])
            repo.delete()
            logger.info(f"Deleted repository: {repo_data['full_name']}")
        except Repository.DoesNotExist:
            pass
    
    return {
        'status': 'success',
        'action': action,
        'repository': repo_data['full_name']
    }


@csrf_exempt
@require_http_methods(["GET"])
def webhook_health(request):
    """
    Webhook health check endpoint
    """
    return JsonResponse({
        'status': 'healthy',
        'service': 'github-webhook-handler',
        'version': '1.0.0'
    })

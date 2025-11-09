"""
API Views for Auto-Triage and ChatBot features
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
import logging

from api.issue_triage import triage_service
from api.chatbot import slack_bot, discord_bot
from api.models import Repository, Issue

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
def auto_triage_issue(request):
    """
    Auto-triage a new issue
    
    POST /api/triage/issue/
    Body:
    {
        "repository_id": 1,
        "issue_data": {
            "title": "Bug in login form",
            "body": "User cannot login...",
            "labels": ["bug"],
            "number": 123
        }
    }
    """
    try:
        repository_id = request.data.get('repository_id')
        issue_data = request.data.get('issue_data')
        
        if not repository_id or not issue_data:
            return Response(
                {'error': 'repository_id and issue_data are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get repository
        try:
            repository = Repository.objects.get(id=repository_id)
        except Repository.DoesNotExist:
            return Response(
                {'error': 'Repository not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Perform triage
        triage_result = triage_service.triage_issue(issue_data, repository)
        
        return Response({
            'success': True,
            'triage_result': triage_result
        })
        
    except Exception as e:
        logger.error(f"Error in auto-triage: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def classify_issue(request):
    """
    Classify an issue without full triage
    
    POST /api/triage/classify/
    Body:
    {
        "title": "Feature request: Add dark mode",
        "body": "Would love to have dark mode support...",
        "labels": []
    }
    """
    try:
        issue_data = request.data
        
        classification = triage_service.classify_issue(issue_data)
        
        return Response({
            'success': True,
            'classification': classification
        })
        
    except Exception as e:
        logger.error(f"Error classifying issue: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def detect_duplicate_issue(request):
    """
    Detect duplicate issues
    
    POST /api/triage/detect-duplicate/
    Body:
    {
        "repository_id": 1,
        "title": "Login broken",
        "body": "Cannot login to app"
    }
    """
    try:
        repository_id = request.data.get('repository_id')
        issue_data = {
            'title': request.data.get('title', ''),
            'body': request.data.get('body', '')
        }
        
        if not repository_id:
            return Response(
                {'error': 'repository_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            repository = Repository.objects.get(id=repository_id)
        except Repository.DoesNotExist:
            return Response(
                {'error': 'Repository not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        is_duplicate, duplicate_id = triage_service.detect_duplicates(issue_data, repository)
        
        return Response({
            'success': True,
            'is_duplicate': is_duplicate,
            'duplicate_of': duplicate_id
        })
        
    except Exception as e:
        logger.error(f"Error detecting duplicates: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def suggest_assignee(request, repository_id):
    """
    Suggest assignee for an issue
    
    GET /api/triage/suggest-assignee/<repository_id>/?component=frontend
    """
    try:
        component = request.GET.get('component', 'backend')
        
        try:
            repository = Repository.objects.get(id=repository_id)
        except Repository.DoesNotExist:
            return Response(
                {'error': 'Repository not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        issue_data = {'title': '', 'body': ''}  # Minimal data
        assignee_info = triage_service.suggest_assignee(issue_data, repository, component)
        
        return Response({
            'success': True,
            'assignee': assignee_info
        })
        
    except Exception as e:
        logger.error(f"Error suggesting assignee: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ============================================================================
# ChatBot Endpoints
# ============================================================================

@api_view(['POST'])
@permission_classes([AllowAny])
def chatbot_command(request):
    """
    Handle chatbot commands
    
    POST /api/chatbot/command/
    Body:
    {
        "platform": "slack|discord",
        "command": "pr|team-health|digest|risks",
        "args": ["123", "owner/repo"]
    }
    """
    try:
        platform = request.data.get('platform', 'slack')
        command = request.data.get('command')
        args = request.data.get('args', [])
        
        if not command:
            return Response(
                {'error': 'command is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Select bot
        bot = slack_bot if platform == 'slack' else discord_bot
        
        # Handle command
        result = bot.handle_command(command, args)
        
        return Response({
            'success': True,
            'response': result
        })
        
    except Exception as e:
        logger.error(f"Error handling chatbot command: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def pr_summary(request):
    """
    Get AI summary of a PR
    
    POST /api/chatbot/pr-summary/
    Body:
    {
        "pr_number": 123,
        "repository_name": "owner/repo"
    }
    """
    try:
        pr_number = request.data.get('pr_number')
        repository_name = request.data.get('repository_name')
        
        if not pr_number or not repository_name:
            return Response(
                {'error': 'pr_number and repository_name are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        summary = slack_bot.generate_pr_summary(pr_number, repository_name)
        
        return Response({
            'success': True,
            'summary': summary
        })
        
    except Exception as e:
        logger.error(f"Error generating PR summary: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def team_health(request):
    """
    Get team health metrics
    
    GET /api/chatbot/team-health/?repository_id=1
    """
    try:
        repository_id = request.GET.get('repository_id')
        
        if repository_id:
            repository_id = int(repository_id)
        
        health_report = slack_bot.get_team_health(repository_id)
        
        return Response({
            'success': True,
            'report': health_report
        })
        
    except Exception as e:
        logger.error(f"Error getting team health: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def daily_digest(request):
    """
    Get daily activity digest
    
    GET /api/chatbot/daily-digest/
    """
    try:
        digest = slack_bot.generate_daily_digest()
        
        return Response({
            'success': True,
            'digest': digest
        })
        
    except Exception as e:
        logger.error(f"Error generating daily digest: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def risk_alerts(request):
    """
    Get risk alerts
    
    GET /api/chatbot/risk-alerts/
    """
    try:
        risks = slack_bot.detect_risks()
        
        return Response({
            'success': True,
            'risks': risks
        })
        
    except Exception as e:
        logger.error(f"Error detecting risks: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
def slack_webhook(request):
    """
    Slack webhook endpoint for slash commands
    
    POST /api/webhooks/slack/
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        # Parse Slack payload
        payload = json.loads(request.body) if request.content_type == 'application/json' else request.POST
        
        command_text = payload.get('text', '')
        parts = command_text.split()
        
        if not parts:
            response = slack_bot._help_message()
        else:
            command = parts[0]
            args = parts[1:]
            response = slack_bot.handle_command(command, args)
        
        return JsonResponse({
            'response_type': 'in_channel',
            'text': response
        })
        
    except Exception as e:
        logger.error(f"Error handling Slack webhook: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def discord_webhook(request):
    """
    Discord webhook endpoint
    
    POST /api/webhooks/discord/
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        payload = json.loads(request.body)
        
        # Discord bot command format: !katalyst <command> <args>
        content = payload.get('content', '')
        
        if content.startswith('!katalyst '):
            command_text = content[9:].strip()  # Remove '!katalyst '
            parts = command_text.split()
            
            if not parts:
                response = discord_bot._help_message()
            else:
                command = parts[0]
                args = parts[1:]
                response = discord_bot.handle_command(command, args)
            
            # Send response
            discord_bot.send_message(response)
            
            return JsonResponse({'success': True})
        
        return JsonResponse({'success': True, 'message': 'Not a bot command'})
        
    except Exception as e:
        logger.error(f"Error handling Discord webhook: {e}")
        return JsonResponse({'error': str(e)}, status=500)

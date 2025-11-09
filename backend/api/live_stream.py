"""
Real-Time Activity Stream using Server-Sent Events (SSE)
Broadcasts GitHub webhook events to connected clients in real-time
"""
import json
import time
from django.http import StreamingHttpResponse, HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
import logging

logger = logging.getLogger(__name__)

# In-memory list to store recent events (last 100)
recent_events = []
max_events = 100


def add_event(event_type, data):
    """
    Add an event to the recent events list
    
    Args:
        event_type: Type of event (push, pull_request, issues, etc.)
        data: Event data dictionary
    """
    global recent_events
    
    event = {
        'type': event_type,
        'data': data,
        'timestamp': int(time.time())
    }
    
    recent_events.insert(0, event)  # Add to beginning
    
    # Keep only last max_events
    if len(recent_events) > max_events:
        recent_events = recent_events[:max_events]
    
    logger.info(f"📡 Added {event_type} event to stream")


def event_generator():
    """
    Generator that yields Server-Sent Events
    Sends initial connection message, recent events, and heartbeats
    """
    # Send initial connection message
    yield f"data: {json.dumps({'type': 'connected', 'message': 'Connected to live activity stream', 'timestamp': int(time.time())})}\n\n"
    
    # Send recent events
    for event in reversed(recent_events[-10:]):  # Send last 10 events
        yield f"data: {json.dumps(event)}\n\n"
    
    # Send heartbeats to keep connection alive
    for i in range(30):  # Keep connection alive for 30 seconds
        time.sleep(1)
        yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': int(time.time())})}\n\n"


@api_view(['GET'])
@permission_classes([AllowAny])
def live_event_stream(request):
    """
    SSE endpoint for live activity feed
    GET /api/events/stream/
    
    Streams real-time events to connected clients using Server-Sent Events
    """
    try:
        logger.info("📱 New client connected to live event stream")
        
        # Create streaming response
        response = StreamingHttpResponse(
            event_generator(),
            content_type='text/event-stream'
        )
        
        # SSE headers
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        response['Connection'] = 'keep-alive'
        response['Access-Control-Allow-Origin'] = '*'  # For CORS
        
        return response
        
    except Exception as e:
        logger.error(f"Error in live_event_stream: {str(e)}", exc_info=True)
        return HttpResponse(f"Error: {str(e)}", status=500)


def broadcast_push_event(payload):
    """
    Broadcast push event when commits are pushed
    
    Args:
        payload: GitHub webhook payload
    """
    try:
        commits = payload.get('commits', [])
        pusher = payload.get('pusher', {}).get('name', 'Unknown')
        repository = payload.get('repository', {}).get('name', 'Unknown')
        
        add_event('push', {
            'author': pusher,
            'commits': len(commits),
            'repository': repository,
            'branch': payload.get('ref', '').split('/')[-1],
            'commit_messages': [c.get('message', '')[:100] for c in commits[:3]]
        })
    except Exception as e:
        logger.error(f"Error broadcasting push event: {str(e)}")


def broadcast_pull_request_event(payload):
    """
    Broadcast pull request event
    
    Args:
        payload: GitHub webhook payload
    """
    try:
        action = payload.get('action', 'unknown')
        pr = payload.get('pull_request', {})
        
        add_event('pull_request', {
            'author': pr.get('user', {}).get('login', 'Unknown'),
            'action': action,
            'number': pr.get('number', 0),
            'title': pr.get('title', 'Untitled'),
            'repository': payload.get('repository', {}).get('name', 'Unknown'),
            'state': pr.get('state', 'unknown')
        })
    except Exception as e:
        logger.error(f"Error broadcasting PR event: {str(e)}")


def broadcast_issues_event(payload):
    """
    Broadcast issues event
    
    Args:
        payload: GitHub webhook payload
    """
    try:
        action = payload.get('action', 'unknown')
        issue = payload.get('issue', {})
        
        add_event('issues', {
            'action': action,
            'issue_number': issue.get('number', 0),
            'title': issue.get('title', 'Untitled'),
            'repository': payload.get('repository', {}).get('name', 'Unknown'),
            'author': issue.get('user', {}).get('login', 'Unknown'),
            'state': issue.get('state', 'open')
        })
    except Exception as e:
        logger.error(f"Error broadcasting issue event: {str(e)}")


def broadcast_custom_event(event_type, data):
    """
    Broadcast a custom event
    
    Args:
        event_type: Custom event type
        data: Event data dictionary
    """
    try:
        add_event(event_type, data)
    except Exception as e:
        logger.error(f"Error broadcasting custom event: {str(e)}")
